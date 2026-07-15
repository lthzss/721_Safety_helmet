#!/bin/bash
cd /home/lthzss/721/truck_project/truck_project
if [ -f server.pid ]; then
    kill $(cat server.pid) 2>/dev/null && echo "服务已关闭" || echo "进程不存在"
    rm -f server.pid
else
    echo "未找到 server.pid，尝试查找进程..."
    pkill -f "python web_demo/app.py" && echo "已关闭" || echo "未找到运行中的服务"
fi
