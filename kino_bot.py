
import telebot
import json
from telebot import types
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

MOVIES_FILE = 'movies.json'
bot = telebot.TeleBot(BOT_TOKEN)

def load_movies():
    try:
        with open(MOVIES_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_movies(data):
    with open(MOVIES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def check_subscription(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_subscription(user_id):
        bot.send_message(user_id, "🎬 Kino raqamini kiriting yoki fayl yuboring (faqat adminlar).")
    else:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🔗 Kanalga a’zo bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")
        markup.add(btn)
        bot.send_message(user_id, "📛 Avval kanalga a’zo bo‘ling:
" + CHANNEL_USERNAME, reply_markup=markup)

@bot.message_handler(content_types=['video', 'document'])
def add_movie(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        bot.send_message(user_id, "❌ Siz admin emassiz.")
        return

    movies = load_movies()
    new_id = str(max([int(k) for k in movies.keys()] + [0]) + 1)

    file_id = message.video.file_id if message.content_type == 'video' else message.document.file_id
    movies[new_id] = {'file_id': file_id, 'views': 0}
    save_movies(movies)

    bot.send_message(user_id, f"✅ Kino qo‘shildi. Kino raqami: {new_id}")

@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def send_movie_by_number(message):
    user_id = message.from_user.id
    movie_number = message.text.strip()

    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🔗 Kanalga a’zo bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")
        markup.add(btn)
        bot.send_message(user_id, "❗ Avval kanalga a’zo bo‘ling", reply_markup=markup)
        return

    movies = load_movies()
    if movie_number in movies:
        file_id = movies[movie_number]['file_id']
        movies[movie_number]['views'] += 1
        save_movies(movies)
        bot.send_video(user_id, file_id)
    else:
        bot.send_message(user_id, "❌ Bunday kino topilmadi.")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return bot.send_message(user_id, "❌ Siz admin emassiz.")

    movies = load_movies()
    msg = "📊 Kino statistikasi:

"
    for k, v in movies.items():
        msg += f"🎬 Kino {k}: {v['views']} marta ko‘rilgan
"
    bot.send_message(user_id, msg)

print("Bot ishga tushdi...")
bot.infinity_polling()
