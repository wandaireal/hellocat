from flask import Flask, request, render_template_string
import requests
import os
import json

app = Flask(__name__)

# 访问计数文件
COUNTER_FILE = 'visitor_count.json'

# 初始化计数器
def init_counter():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'w') as f:
            json.dump({'count': 0}, f)
    with open(COUNTER_FILE, 'r') as f:
        return json.load(f)['count']

# 更新并获取最新计数
def update_counter():
    data = init_counter()
    count = data + 1
    with open(COUNTER_FILE, 'w') as f:
        json.dump({'count': count}, f)
    return count

# 获取用户真实IP
def get_real_ip():
    # 检查代理头信息，适用于Render.com等平台
    headers = request.headers
    if 'X-Forwarded-For' in headers:
        return headers['X-Forwarded-For'].split(',')[0].strip()
    elif 'X-Real-IP' in headers:
        return headers['X-Real-IP']
    else:
        return request.remote_addr

# 根据IP获取地理位置
def get_location(ip):
    try:
        # 使用免费的IP地理位置API
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        if response.status_code == 200:
            data = response.json()
            # 返回城市和国家
            if 'city' in data and 'country' in data:
                return f"{data['city']}, {data['country']}"
            elif 'country' in data:
                return data['country']
    except:
        pass
    # 默认返回
    return "未知地区"

@app.route('/')
def index():
    # 获取IP
    ip = get_real_ip()
    # 获取地理位置
    location = get_location(ip)
    # 更新并获取访问计数
    visitor_count = update_counter()
    
    # HTML模板
    html = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>欢迎访问</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f8ff;
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="2" fill="%23ffb6c1" opacity="0.5"/><circle cx="10" cy="10" r="1.5" fill="%23ffb6c1" opacity="0.3"/><circle cx="30" cy="30" r="1.5" fill="%23ffb6c1" opacity="0.3"/><circle cx="30" cy="10" r="1.5" fill="%23ffb6c1" opacity="0.3"/><circle cx="10" cy="30" r="1.5" fill="%23ffb6c1" opacity="0.3"/></svg>');
            }
            .container {
                text-align: center;
                background-color: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                max-width: 500px;
                width: 90%;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
                font-size: 28px;
            }
            p {
                color: #666;
                font-size: 18px;
                line-height: 1.6;
            }
            .highlight {
                color: #ff6b81;
                font-weight: bold;
            }
            .cat-emoji {
                font-size: 48px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="cat-emoji">🐱</div>
            <h1>欢迎来到小猫网站！</h1>
            <p>欢迎IP为<span class="highlight">{{ ip }}</span>，来自<span class="highlight">{{ location }}</span>的小猫</p>
            <p>你是本网站的第<span class="highlight">{{ visitor_count }}</span>个访问者</p>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, ip=ip, location=location, visitor_count=visitor_count)

if __name__ == '__main__':
    # 初始化计数器
    init_counter()
    # 从环境变量获取端口，默认为5000
    port = int(os.environ.get('PORT', 5000))
    # 启动应用
    app.run(host='0.0.0.0', port=port, debug=True)
