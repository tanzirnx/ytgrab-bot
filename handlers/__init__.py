from handlers.start_handler import (
    start_command, help_command, faq_command,
    settings_command, ping_command, version_command,
    callback_handler,
)
from handlers.download_handler import (
    url_handler, mp3_command, mp4_command,
    info_command, best_command, search_command,
)
from handlers.playlist_handler import (
    playlist_command, plinfo_command, plrange_command,
    playlist_callback_handler,
)
from handlers.audio_handler import (
    m4a_command, flac_command, ogg_command,
    wav_command, opus_command, aac_command,
)
from handlers.video_handler import (
    webm_command, mkv_command, worst_command,
    gif_command, clip_command, noaudio_command,
)
from handlers.admin_handler import (
    admin_command, stats_command, broadcast_command,
    ban_command, unban_command, setlimit_command,
    maintenance_command, logs_command, update_command,
    restart_command, admin_callback_handler,
)
from handlers.settings_handler import (
    setquality_command, setformat_command, setlang_command,
    setthumb_command, setsubs_command, setnotify_command,
    setfilename_command, reset_command, mydefaults_command,
)
from handlers.utility_handler import (
    queue_command, cancel_command, clearqueue_command,
    trending_command, shorts_command, batch_command,
    report_command, feedback_command, suggest_command,
)
