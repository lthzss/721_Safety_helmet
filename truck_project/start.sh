#!/bin/bash
cd /home/lthzss/721/truck_project/truck_project
source venv/bin/activate
systemctl --user stop pipewire.socket pipewire.service wireplumber.service 2>/dev/null
nohup python web_demo/app.py > server.log 2>&1 &
echo $! > server.pid
echo "服务已启动，PID: $(cat server.pid)"
echo "访问 http://$(hostname -I | awk '{print $1}'):5000"
