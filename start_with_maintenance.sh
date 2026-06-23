#!/bin/bash
# 服务启动脚本 - 默认显示公告页面

echo "🔧 正在启动服务..."

# 1. 停止现有服务
pkill -f "http.server 8080" 2>/dev/null
pkill -f "app.py" 2>/dev/null
sleep 1

# 2. 切换到公告页面
cp index.html index.html.game_backup 2>/dev/null || true
cp maintenance.html index.html
echo "✅ 公告页面已挂"

# 3. 启动前端服务（显示公告）
nohup python3 -m http.server 8080 > /dev/null 2>&1 &
echo "✅ 前端服务已启动（公告页面）"

# 4. 启动后端服务
cd backend
source venv/bin/activate
nohup python3 app.py > /dev/null 2>&1 &
echo "✅ 后端服务已启动"

cd ..

# 5. 等待用户确认更新完成
echo ""
echo "📢 服务已启动，当前显示公告页面"
echo "   用户看到的是维护公告，无法进入游戏"
echo ""
echo "   更新完成后，运行以下命令切换到游戏页面："
echo "   ./switch_to_game.sh"
echo ""
