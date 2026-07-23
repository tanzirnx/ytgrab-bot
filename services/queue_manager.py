"""
YTGrab Bot - Download Queue Manager
Manages concurrent downloads with queuing.
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable
from collections import defaultdict
from loguru import logger

from config import Config


class TaskStatus(Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadTask:
    """Represents a single download task."""
    task_id: int
    user_id: int
    url: str
    title: str = ""
    format: str = ""
    quality: str = ""
    status: TaskStatus = TaskStatus.QUEUED
    progress: float = 0.0
    file_size: int = 0
    error: str = ""
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retries: int = 0
    max_retries: int = 3


class QueueManager:
    """Manages download queue per user and globally."""

    def __init__(self):
        self._queues: dict[int, list[DownloadTask]] = defaultdict(list)
        self._active_tasks: dict[int, list[DownloadTask]] = defaultdict(list)
        self._task_counter: int = 0
        self._lock = asyncio.Lock()
        self._global_active: int = 0

    async def add_task(
        self,
        user_id: int,
        url: str,
        title: str = "",
        format: str = "",
        quality: str = "",
    ) -> Optional[DownloadTask]:
        """Add a download task to the queue."""
        async with self._lock:
            # Check queue size
            current_queue = len(self._queues[user_id])
            current_active = len(self._active_tasks[user_id])

            if current_queue + current_active >= Config.MAX_QUEUE_SIZE:
                logger.warning(f"Queue full for user {user_id}")
                return None

            self._task_counter += 1
            task = DownloadTask(
                task_id=self._task_counter,
                user_id=user_id,
                url=url,
                title=title,
                format=format,
                quality=quality,
            )
            self._queues[user_id].append(task)
            logger.info(f"📋 Task #{task.task_id} queued for user {user_id}: {url}")
            return task

    async def get_next_task(self, user_id: int) -> Optional[DownloadTask]:
        """Get next task from queue if slots available."""
        async with self._lock:
            # Check global concurrent limit
            if self._global_active >= Config.MAX_CONCURRENT_DOWNLOADS:
                return None

            # Check per-user active limit
            if len(self._active_tasks[user_id]) >= 2:
                return None

            # Get next queued task
            if self._queues[user_id]:
                task = self._queues[user_id].pop(0)
                task.status = TaskStatus.DOWNLOADING
                task.started_at = time.time()
                self._active_tasks[user_id].append(task)
                self._global_active += 1
                return task

            return None

    async def complete_task(self, user_id: int, task_id: int, success: bool = True):
        """Mark task as completed or failed."""
        async with self._lock:
            for task in self._active_tasks[user_id]:
                if task.task_id == task_id:
                    task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                    task.completed_at = time.time()
                    self._active_tasks[user_id].remove(task)
                    self._global_active = max(0, self._global_active - 1)
                    logger.info(
                        f"{'✅' if success else '❌'} Task #{task_id} "
                        f"{'completed' if success else 'failed'} for user {user_id}"
                    )
                    return
            logger.warning(f"Task #{task_id} not found in active tasks")

    async def cancel_task(self, user_id: int, task_id: int) -> bool:
        """Cancel a specific task."""
        async with self._lock:
            # Check queue
            for i, task in enumerate(self._queues[user_id]):
                if task.task_id == task_id:
                    task.status = TaskStatus.CANCELLED
                    self._queues[user_id].pop(i)
                    logger.info(f"🚫 Task #{task_id} cancelled (was queued)")
                    return True

            # Check active
            for task in self._active_tasks[user_id]:
                if task.task_id == task_id:
                    task.status = TaskStatus.CANCELLED
                    self._active_tasks[user_id].remove(task)
                    self._global_active = max(0, self._global_active - 1)
                    logger.info(f"🚫 Task #{task_id} cancelled (was active)")
                    return True

            return False

    async def cancel_all(self, user_id: int) -> int:
        """Cancel all tasks for a user."""
        async with self._lock:
            count = 0

            # Cancel queued
            for task in self._queues[user_id]:
                task.status = TaskStatus.CANCELLED
                count += 1
            self._queues[user_id].clear()

            # Cancel active
            for task in self._active_tasks[user_id]:
                task.status = TaskStatus.CANCELLED
                self._global_active = max(0, self._global_active - 1)
                count += 1
            self._active_tasks[user_id].clear()

            if count > 0:
                logger.info(f"🚫 Cancelled {count} tasks for user {user_id}")
            return count

    async def get_queue_status(self, user_id: int) -> dict:
        """Get queue status for a user."""
        queued = self._queues.get(user_id, [])
        active = self._active_tasks.get(user_id, [])

        return {
            "queued": [
                {
                    "id": t.task_id,
                    "title": t.title or t.url[:50],
                    "format": t.format,
                    "status": t.status.value,
                }
                for t in queued
            ],
            "active": [
                {
                    "id": t.task_id,
                    "title": t.title or t.url[:50],
                    "format": t.format,
                    "progress": t.progress,
                    "status": t.status.value,
                }
                for t in active
            ],
            "total_queued": len(queued),
            "total_active": len(active),
            "max_queue": Config.MAX_QUEUE_SIZE,
        }

    async def get_global_stats(self) -> dict:
        """Get global queue statistics."""
        total_queued = sum(len(q) for q in self._queues.values())
        total_active = self._global_active
        return {
            "total_queued": total_queued,
            "total_active": total_active,
            "max_concurrent": Config.MAX_CONCURRENT_DOWNLOADS,
            "users_with_queue": len([q for q in self._queues.values() if q]),
        }

    def is_queue_full(self, user_id: int) -> bool:
        """Check if user's queue is full."""
        current = len(self._queues.get(user_id, [])) + len(self._active_tasks.get(user_id, []))
        return current >= Config.MAX_QUEUE_SIZE


# Singleton
queue_manager = QueueManager()
