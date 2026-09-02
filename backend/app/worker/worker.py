from arq import cron
from arq.connections import RedisSettings

from ..core.config import settings
from .tasks import task_background_cache_warm, task_morning_commute_digest


class WorkerSettings:
    functions = [task_morning_commute_digest, task_background_cache_warm]
    cron_jobs = [
        cron(task_morning_commute_digest, hour={1}, minute={45}, run_at_startup=False),
        cron(task_background_cache_warm, minute={0, 15, 30, 45}),
    ]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
    job_timeout = 120
