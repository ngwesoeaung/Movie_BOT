import telebot
from telebot import types
import json

API_TOKEN = '7621703689:AAHLi1TH9CCC0WTRLt5OUhaqHRv_j0NRwbQ'

bot = telebot.TeleBot(API_TOKEN)

# Only allow admin user to control the system
ADMIN_ID = 1921230090  # Replace with your Telegram ID

diamonds_options = [
    {"value": "86", "price": 5200},
    {"value": "172", "price": 10400},
    {"value": "257", "price": 15500},
    {"value": "514", "price": 31000},
    {"value": "706", "price": 41000}
]

weekly_pass_price = 6500

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("View Prices", "Update Diamonds")
        markup.row("Update Weekly Pass Price")
        bot.send_message(message.chat.id, "Welcome Admin! Choose an option:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "You are not authorized to control this bot.")

@bot.message_handler(func=lambda m: m.text == "View Prices")
def view_prices(message):
    if message.from_user.id == ADMIN_ID:
        diamond_list = "\n".join([f"{d['value']} Diamonds - {d['price']} MMK" for d in diamonds_options])
        bot.send_message(message.chat.id, f"Current Diamond Options:\n{diamond_list}\n\nWeekly Pass: {weekly_pass_price} MMK")

@bot.message_handler(func=lambda m: m.text == "Update Diamonds")
def ask_diamond_update(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Send new diamond options in JSON format (e.g. \n[{\"value\":\"100\",\"price\":8000}])")

@bot.message_handler(func=lambda m: m.text == "Update Weekly Pass Price")
def ask_weekly_pass_price(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Send new Weekly Pass price in MMK (e.g. 7000)")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    global diamonds_options, weekly_pass_price
    if message.from_user.id != ADMIN_ID:
        return

    try:
        # Try to parse JSON as diamond options
        new_diamonds = json.loads(message.text)
        if isinstance(new_diamonds, list):
            diamonds_options = new_diamonds
            # Send to frontend via localStorage or file for integration
            with open('diamondsOptions.json', 'w') as f:
                json.dump(diamonds_options, f)
            bot.send_message(message.chat.id, "Diamond options updated successfully!")
            return
    except Exception as e:
        pass  # Not JSON

    if message.text.isdigit():
        weekly_pass_price = int(message.text)
        with open('weeklyPassPrice.txt', 'w') as f:
            f.write(str(weekly_pass_price))
        bot.send_message(message.chat.id, f"Weekly Pass price updated to {weekly_pass_price} MMK")

bot.polling()

from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DIAMONDS_FILE = 'diamondsOptions.json'
WEEKLY_FILE = 'weeklyPassPrice.txt'

@app.route('/api/diamonds', methods=['GET'])
def get_diamonds():
    if os.path.exists(DIAMONDS_FILE):
        with open(DIAMONDS_FILE, 'r') as f:
            diamonds = json.load(f)
        return jsonify(diamonds)
    return jsonify([])

@app.route('/api/weekly-price', methods=['GET'])
def get_weekly_price():
    if os.path.exists(WEEKLY_FILE):
        with open(WEEKLY_FILE, 'r') as f:
            return jsonify({"price": int(f.read().strip())})
    return jsonify({"price": 6500})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# ✅ Start bot
print("🤖 Bot is running...")
bot.infinity_polling()