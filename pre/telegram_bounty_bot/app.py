from flask import request, jsonify
import telegram
from manage import manager, app
from bounty_bot.bot import BOT, webhook
from db import Bounter

@app.route('/')
def home():
    print(request.remote_addr)
    print(request.headers['X-Forwarded-For'])
    return "hello", 200

@app.route('/tele', methods=['POST', 'GET'])
def telegram_bot():
    """Listens to update from telegram"""
    if request.method == 'GET':
        return 'ok', 200

    if request.method == 'POST':
        update = telegram.Update.de_json(request.get_json(force=True), BOT)
        webhook(update)
        return 'ok', 200

def main(host='0.0.0.0', port='80'):
    @manager.command
    def run():
        app.run(
            host=host,
            port=port
        )
    manager.run() #python3 app.py run [will use the above config] else use runserver --port 5001

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    