#!/usr/bin/env python3
"""加密货币冒险 - 后端服务器 v1.0"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'game.db')

# ========== 数据库初始化 ==========
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        token TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )''')
    
    # 存档表
    c.execute('''CREATE TABLE IF NOT EXISTS saves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        slot_name TEXT NOT NULL,
        game_data TEXT NOT NULL,
        total_asset REAL,
        day INTEGER,
        difficulty TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, slot_name)
    )''')
    
    # 成就表
    c.execute('''CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        achievement_id TEXT NOT NULL,
        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, achievement_id)
    )''')
    
    # 排行榜表
    c.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        total_asset REAL NOT NULL,
        pnl_percent REAL NOT NULL,
        days INTEGER,
        difficulty TEXT,
        ending TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ========== 工具函数 ==========
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return secrets.token_hex(32)

def get_user_from_token(token):
    if not token:
        return None
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE token = ?', (token,)).fetchone()
    conn.close()
    return user

# ========== API 路由 ==========

# --- 用户注册 ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    if len(username) < 2 or len(username) > 20:
        return jsonify({'error': '用户名长度2-20个字符'}), 400
    
    if len(password) < 4:
        return jsonify({'error': '密码至少4个字符'}), 400
    
    conn = get_db()
    
    existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'error': '用户名已存在'}), 400
    
    password_hash = hash_password(password)
    token = generate_token()
    
    cursor = conn.execute(
        'INSERT INTO users (username, password_hash, token) VALUES (?, ?, ?)',
        (username, password_hash, token)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '注册成功',
        'user_id': user_id,
        'username': username,
        'token': token
    })

# --- 用户登录 ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password_hash = ?',
        (username, hash_password(password))
    ).fetchone()
    
    if not user:
        conn.close()
        return jsonify({'error': '用户名或密码错误'}), 401
    
    token = generate_token()
    conn.execute(
        'UPDATE users SET token = ?, last_login = ? WHERE id = ?',
        (token, datetime.now().isoformat(), user['id'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '登录成功',
        'user_id': user['id'],
        'username': user['username'],
        'token': token
    })

# --- 保存存档 ---
@app.route('/api/save', methods=['POST'])
def save_game():
    data = request.json
    token = data.get('token')
    slot_name = data.get('slot_name', 'auto_save')
    game_data = data.get('game_data')
    
    if not token or not game_data:
        return jsonify({'error': '参数不完整'}), 400
    
    user = get_user_from_token(token)
    if not user:
        return jsonify({'error': '未登录或token过期'}), 401
    
    conn = get_db()
    
    # 检查存档数量限制（最多5个）
    existing_saves = conn.execute('SELECT COUNT(*) FROM saves WHERE user_id = ?', (user['id'],)).fetchone()[0]
    existing_slot = conn.execute('SELECT 1 FROM saves WHERE user_id = ? AND slot_name = ?', (user['id'], slot_name)).fetchone()
    
    if not existing_slot and existing_saves >= 5:
        conn.close()
        return jsonify({'error': '存档已满（最多5个），请删除旧存档后再保存'}), 400
    
    # 检查玩家名是否重复（同一账号下）
    player_name = game_data.get('player', '')
    if player_name:
        # 查询同一账号下是否有同名玩家的存档（排除当前存档）
        duplicate = conn.execute('''
            SELECT 1 FROM saves 
            WHERE user_id = ? AND slot_name != ? AND json_extract(game_data, '$.player') = ?
        ''', (user['id'], slot_name, player_name)).fetchone()
        
        if duplicate:
            conn.close()
            return jsonify({'error': '存档名已存在，请修改昵称'}), 400
    
    total_asset = game_data.get('totalAsset', 0)
    day = game_data.get('day', 1)
    difficulty = game_data.get('difficulty', 'normal')
    
    conn.execute('''
        INSERT INTO saves (user_id, slot_name, game_data, total_asset, day, difficulty, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, slot_name) DO UPDATE SET
            game_data = excluded.game_data,
            total_asset = excluded.total_asset,
            day = excluded.day,
            difficulty = excluded.difficulty,
            updated_at = excluded.updated_at
    ''', (user['id'], slot_name, json.dumps(game_data), total_asset, day, difficulty, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': '存档成功'})

# --- 加载存档 ---
@app.route('/api/load', methods=['POST'])
def load_game():
    data = request.json
    token = data.get('token')
    slot_name = data.get('slot_name', 'auto_save')
    
    if not token:
        return jsonify({'error': '未登录'}), 400
    
    user = get_user_from_token(token)
    if not user:
        return jsonify({'error': '未登录或token过期'}), 401
    
    conn = get_db()
    save = conn.execute(
        'SELECT * FROM saves WHERE user_id = ? AND slot_name = ?',
        (user['id'], slot_name)
    ).fetchone()
    conn.close()
    
    if not save:
        return jsonify({'error': '存档不存在'}), 404
    
    return jsonify({
        'game_data': json.loads(save['game_data']),
        'slot_name': save['slot_name'],
        'total_asset': save['total_asset'],
        'day': save['day'],
        'difficulty': save['difficulty'],
        'updated_at': save['updated_at']
    })

# --- 获取所有存档列表 ---
@app.route('/api/saves', methods=['POST'])
def list_saves():
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 400
    
    user = get_user_from_token(token)
    if not user:
        return jsonify({'error': '未登录或token过期'}), 401
    
    conn = get_db()
    saves = conn.execute(
        '''SELECT slot_name, total_asset, day, difficulty, created_at, updated_at 
           FROM saves WHERE user_id = ? ORDER BY updated_at DESC''',
        (user['id'],)
    ).fetchall()
    conn.close()
    
    return jsonify({
        'saves': [{
            'slot_name': s['slot_name'],
            'total_asset': s['total_asset'],
            'day': s['day'],
            'difficulty': s['difficulty'],
            'created_at': s['created_at'],
            'updated_at': s['updated_at']
        } for s in saves]
    })

# --- 删除存档 ---
@app.route('/api/save/delete', methods=['POST'])
def delete_save():
    data = request.json
    token = data.get('token')
    slot_name = data.get('slot_name')
    
    if not token or not slot_name:
        return jsonify({'error': '参数不完整'}), 400
    
    user = get_user_from_token(token)
    if not user:
        return jsonify({'error': '未登录或token过期'}), 401
    
    conn = get_db()
    conn.execute(
        'DELETE FROM saves WHERE user_id = ? AND slot_name = ?',
        (user['id'], slot_name)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': '删除成功'})

# --- 解锁成就 ---
@app.route('/api/achievement', methods=['POST'])
def unlock_achievement():
    data = request.json
    token = data.get('token')
    achievement_id = data.get('achievement_id')
    
    if not token or not achievement_id:
        return jsonify({'error': '参数不完整'}), 400
    
    user = get_user_from_token(token)
    if not user:
        return jsonify({'error': '未登录或token过期'}), 401
    
    conn = get_db()
    try:
        conn.execute(
            'INSERT OR IGNORE INTO achievements (user_id, achievement_id) VALUES (?, ?)',
            (user['id'], achievement_id)
        )
        conn.commit()
    except:
        pass
    conn.close()
    
    return jsonify({'message': '成就已解锁'})

# --- 获取成就列表 ---
@app.route('/api/achievements', methods=['POST'])
def get_achievements():
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 400
    
    user = get_user_from_token(token)
    if not user:
        return jsonify({'error': '未登录或token过期'}), 401
    
    conn = get_db()
    achievements = conn.execute(
        'SELECT achievement_id, unlocked_at FROM achievements WHERE user_id = ?',
        (user['id'],)
    ).fetchall()
    conn.close()
    
    return jsonify({
        'achievements': [{
            'id': a['achievement_id'],
            'unlocked_at': a['unlocked_at']
        } for a in achievements]
    })

# --- 提交排行榜成绩 ---
@app.route('/api/leaderboard', methods=['POST'])
def submit_score():
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 400
    
    user = get_user_from_token(token)
    if not user:
        return jsonify({'error': '未登录或token过期'}), 401
    
    conn = get_db()
    conn.execute(
        '''INSERT INTO leaderboard (user_id, username, total_asset, pnl_percent, days, difficulty, ending)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (user['id'], user['username'], data.get('total_asset', 0), 
         data.get('pnl_percent', 0), data.get('days', 0),
         data.get('difficulty', 'normal'), data.get('ending', ''))
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': '成绩已提交'})

# --- 获取排行榜 ---
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    conn = get_db()
    scores = conn.execute(
        '''SELECT username, total_asset, pnl_percent, days, difficulty, ending, created_at
           FROM leaderboard ORDER BY pnl_percent DESC LIMIT 50'''
    ).fetchall()
    conn.close()
    
    return jsonify({
        'leaderboard': [{
            'username': s['username'],
            'total_asset': s['total_asset'],
            'pnl_percent': s['pnl_percent'],
            'days': s['days'],
            'difficulty': s['difficulty'],
            'ending': s['ending'],
            'date': s['created_at']
        } for s in scores]
    })

# --- 健康检查 ---
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': '1.0'})

# ========== 启动 ==========
if __name__ == '__main__':
    init_db()
    print('🎮 加密货币冒险后端启动中...')
    print('📡 API地址: http://0.0.0.0:5000')
    print('📦 版本: 1.0 - 杠杆·手续费·新闻·K线·山寨币·庄家AI·NPC')
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("DEBUG", "false").lower() == "true")
