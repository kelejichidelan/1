#!/bin/bash
# 切换到游戏页面

echo "🔄 正在切换到游戏页面..."

# 1. 恢复游戏页面
cp index.html.game_backup index.html 2>/dev/null || cp index.html.bak index.html

# 2. 重启前端服务
pkill -f "http.server 8080" 2>/dev/null
sleep 1
nohup python3 -m http.server 8080 > /dev/null 2>&1 &

echo "✅ 已切换到游戏页面，用户刷新即可进入游戏"
