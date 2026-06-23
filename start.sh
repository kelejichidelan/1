#!/bin/bash
# 加密货币冒险游戏 - 启动脚本 (含 Cloudflare 隧道)

CLOUDFLARED=~/.local/bin/cloudflared

# 启动前端静态服务器 (后台)
cd /home/kelejichi/.openclaw/workspace/crypto-adventure
python3 -m http.server 8080 &
HTTP_PID=$!
echo "📡 前端服务器: http://localhost:8080 (PID: $HTTP_PID)"

# 启动后端 API (前台 - 主进程)
cd /home/kelejichi/.openclaw/workspace/crypto-adventure/backend
source venv/bin/activate
echo "⚙️  后端 API: http://localhost:5000"

# 启动 Cloudflare 隧道 (后台)
if [ -f "$CLOUDFLARED" ]; then
    cd /home/kelejichi/.openclaw/workspace/crypto-adventure
    $CLOUDFLARED tunnel --url http://localhost:8080 --no-autoupdate > cloudflare-tunnel.log 2>&1 &
    CF_PID=$!
    echo "🌐 正在建立外网隧道..."
    sleep 5
    TUNNEL_URL=$(grep -oP 'https://[a-z-]+\.trycloudflare\.com' cloudflare-tunnel.log | head -1)
    echo "📱 手机访问: $TUNNEL_URL"
    echo "🌐 Tunnel PID: $CF_PID"
else
    echo "⚠️  cloudflared 未安装，手机无法外网访问"
fi

cd /home/kelejichi/.openclaw/workspace/crypto-adventure
exec python3 -c "
import time, subprocess, sys, os
# Keep the http.server alive as main process
os.chdir('/home/kelejichi/.openclaw/workspace/crypto-adventure')
import http.server
import socketserver
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(('0.0.0.0', 8080), Handler) as httpd:
    httpd.serve_forever()
" 2>/dev/null || exec tail -f /dev/null
