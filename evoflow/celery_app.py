"""
Celery应用配置
"""
from celery import Celery

from .config import settings

# 创建Celery应用
celery_app = Celery(
    "evoflow",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["evoflow.tasks"]
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟
    task_soft_time_limit=25 * 60,  # 25分钟
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 任务路由配置
celery_app.conf.task_routes = {
    "evoflow.tasks.workflow.*": {"queue": "workflow"},
    "evoflow.tasks.agent.*": {"queue": "agent"},
}

if __name__ == "__main__":
    celery_app.start()
