from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    # สั่งให้ Flask เปิดพอร์ต 8080 เพื่อให้ Render ตรวจสอบผ่าน
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()