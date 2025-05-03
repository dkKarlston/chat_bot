# telegram.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters
from flask import Flask
from flask_socketio import SocketIO, emit
import asyncio

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

TELEGRAM_TOKEN = "7892773235:AAHIKq0LAJ9gRUbmxuMleW0JAw9uUjFt46o"
BOT_USERNAME = "karlstonBot"

async def handle_message(update: Update, context):
    message = update.message.text
    chat_id = update.message.chat_id

    socketio.emit('user_uttered', {
        'message': message,
        'session_id': chat_id
    })

telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@socketio.on('bot_uttered')
def handle_bot_response(data):
    message = data.get('message')
    chat_id = data.get('session_id')
    buttons = data.get('buttons', [])  # Получаем кнопки из данных

    # Создаем клавиатуру
    if buttons:
        keyboard = [buttons]  # Кнопки в один ряд
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    else:
        reply_markup = None

    telegram_app.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    from threading import Thread

    def run_flask():
        socketio.run(app, port=5000, allow_unsafe_werkzeug=True)

    def run_telegram():
        telegram_app.run_polling()

    Thread(target=run_flask).start()
    Thread(target=run_telegram).start()