import telebot

TOKEN = "7621703689:AAHLi1TH9CCC0WTRLt5OUhaqHRv_j0NRwbQ"
bot = telebot.TeleBot(TOKEN)

# Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("One Piece (1 - 100)")
    btn2 = telebot.types.KeyboardButton("One Piece (101 - 200)")
    btn3 = telebot.types.KeyboardButton("One Piece (201 - 300)")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "မင်္ဂလာပါ 🤗 One Piece Episodes ကိုရွေးချယ်ပါ။", reply_markup=markup)

# Handle Text
@bot.message_handler(func=lambda m: True)
def send_links(message):
    if message.text == "One Piece (1 - 100)":
        bot.send_message(message.chat.id, "👉 Link: https://example.com/onepiece-1-100")
    elif message.text == "One Piece (101 - 200)":
        bot.send_message(message.chat.id, "👉 Link: https://example.com/onepiece-101-200")
    elif message.text == "One Piece (201 - 300)":
        bot.send_message(message.chat.id, "👉 Link: https://example.com/onepiece-201-300")

print("Bot is running...")
bot.polling()