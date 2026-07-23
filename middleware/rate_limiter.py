"""
YTGrab Bot - Rate Limiter Middleware
Prevents abuse with per-user and global rate limits.
"""

import time
from collections import defaultdict
from typing import Tuple
from loguru import logger

from config import Config


class RateLimiter:
    """In-memory rate limiter with sliding window."""

    def __init__(self):
        # user_id -> list of timestamps
        self._requests: dict[int, list[float]] = defaultdict(list)
        # user_id -> violation count
        self._violations: dict[int, int] = defaultdict(int)
        # user_id -> ban_until timestamp
        self._temp_bans: dict[int, float] = {}
        # Global request tracking
        self._global_requests: list[float] = []

    def check_rate_limit(self, user_id: int) -> Tuple[bool, str]:
        """
        Check if user is within rate limits.
        Returns (allowed: bool, message: str)
        """
        now = time.time()

        # Check temp ban
        if user_id in self._temp_bans:
            if now < self._temp_bans[user_id]:
                remaining = int(self._temp_bans[user_id] - now)
                minutes = remaining // 60
                seconds = remaining % 60
                return False, f"🚫 You're temporarily blocked. Try again in {minutes}m {seconds}s."
            else:
                del self._temp_bans[user_id]

        # Clean old entries (older than 1 hour)
        self._requests[user_id] = [
            t for t in self._requests[user_id] if now - t < 3600
        ]

        # Check per-minute limit
        recent_minute = [t for t in self._requests[user_id] if now - t < 60]
        if len(recent_minute) >= Config.RATE_LIMIT_PER_MINUTE:
            self._record_violation(user_id, now)
            wait = 60 - (now - recent_minute[0])
            return False, f"⏳ Too fast! Wait {int(wait)}s before next request."

        # Check per-hour limit
        recent_hour = [t for t in self._requests[user_id] if now - t < 3600]
        if len(recent_hour) >= Config.RATE_LIMIT_PER_HOUR:
            self._record_violation(user_id, now)
            wait = 3600 - (now - recent_hour[0])
            minutes = int(wait // 60)
            return False, f"⏳ Hourly limit reached. Wait {minutes} minutes."

        # Check global limit
        self._global_requests = [t for t in self._global_requests if now - t < 3600]
        if len(self._global_requests) >= 500:
            return False, "⏳ Server is busy. Please try again in a few minutes."

        # All good - record request
        self._requests[user_id].append(now)
        self._global_requests.append(now)
        return True, "OK"

    def _record_violation(self, user_id: int, now: float):
        """Track violations and apply temp bans."""
        self._violations[user_id] += 1
        count = self._violations[user_id]

        if count >= 5:
            # Permanent-ish ban (24 hours)
            self._temp_bans[user_id] = now + 86400
            logger.warning(f"🚫 User {user_id} banned for 24h (5 violations)")
        elif count >= 3:
            # 1 hour ban
            self._temp_bans[user_id] = now + 3600
            logger.warning(f"🚫 User {user_id} banned for 1h (3 violations)")
        elif count >= 2:
            # 5 minute cooldown
            self._temp_bans[user_id] = now + 300
            logger.warning(f"⚠️ User {user_id} cooldown 5min (2 violations)")

    def reset_violations(self, user_id: int):
        """Reset violation count (e.g., after successful download)."""
        self._violations.pop(user_id, None)

    def is_whitelisted(self, user_id: int) -> bool:
        """Check if user is whitelisted (admin)."""
        return user_id == Config.ADMIN_ID

    def get_user_stats(self, user_id: int) -> dict:
        """Get rate limit stats for a user."""
        now = time.time()
        requests = self._requests.get(user_id, [])
        return {
            "requests_last_minute": len([t for t in requests if now - t < 60]),
            "requests_last_hour": len([t for t in requests if now - t < 3600]),
            "violations": self._violations.get(user_id, 0),
            "is_banned": user_id in self._temp_bans and now < self._temp_bans[user_id],
        }


# Singleton
rate_limiter = RateLimiter()
