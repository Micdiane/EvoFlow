"""
API v1模块
"""
from fastapi import APIRouter

from .workflows import router as workflows_router
from .agents import router as agents_router
from .executions import router as executions_router

api_router = APIRouter()

# 注册子路由
api_router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(executions_router, prefix="/executions", tags=["executions"])
