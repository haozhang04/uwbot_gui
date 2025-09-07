#!/bin/bash

#等待网口初始化
LIDAR_PORT="enp2s0";
echo "[INFO] waiting for lidar network interface";
while ! ip link show "$LIDAR_PORT" | grep -q "state UP"; do
    echo "[INFO] $LIDAR_PORT is not ready"
    sleep 1s;
done
echo "[INFO] $LIDAR_PORT started successfully";

#MediaMTX
gnome-terminal -- bash -c '
cd mediamtx/; 
./mediamtx; 
exec bash'
sleep 0.5

#FFmpeg
gnome-terminal -- bash -c '
ffmpeg -i "rtsp://admin:@192.168.1.36:554/stream?user=admin&password=&channel=1&stream=0.sdp&real_stream" \
    -c copy -f rtsp "rtsp://localhost:8554/mystream"; 
exec bash'
    
