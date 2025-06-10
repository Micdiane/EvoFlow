#!/bin/bash

# EvoFlow 停止脚本

echo "Stopping EvoFlow services..."

# 停止所有服务
docker-compose down

echo "EvoFlow services stopped successfully!"
