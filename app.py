from flask import Flask, request, render_template_string, render_template
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
    
    # 使用外部HTML模板
    return render_template('index.html', ip=ip, location=location, visitor_count=visitor_count)

if __name__ == '__main__':
    # 初始化计数器
    init_counter()
    # 从环境变量获取端口，默认为5000
    port = int(os.environ.get('PORT', 5000))
    # 启动应用
    app.run(host='0.0.0.0', port=port, debug=True)
