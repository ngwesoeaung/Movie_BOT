import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext import CallbackContext

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Season data
SEASON_DATA = {
    "season1": [
        "https://t.me/piece_piece1/3",
        "https://t.me/piece_piece1/4",
        "https://t.me/piece_piece1/5",
        "https://t.me/piece_piece1/6",
        "https://t.me/piece_piece1/7",
        "https://t.me/piece_piece1/8",
        "https://t.me/piece_piece1/9",
        "https://t.me/piece_piece1/10",
        "https://t.me/piece_piece1/11",
        "https://t.me/piece_piece1/12",
        "https://t.me/piece_piece1/13",
        "https://t.me/piece_piece1/14",
        "https://t.me/piece_piece1/15",
        "https://t.me/piece_piece1/16",
        "https://t.me/piece_piece1/17",
        "https://t.me/piece_piece1/18",
        "https://t.me/piece_piece1/19",
        "https://t.me/piece_piece1/20",
        "https://t.me/piece_piece1/21",
        "https://t.me/piece_piece1/22",
        "https://t.me/piece_piece1/23",
        "https://t.me/piece_piece1/24",
        "https://t.me/piece_piece1/25",
        "https://t.me/piece_piece1/26",
        "https://t.me/piece_piece1/27",
        "https://t.me/piece_piece1/28",
        "https://t.me/piece_piece1/29",
        "https://t.me/piece_piece1/30",
        "https://t.me/piece_piece1/31",
        "https://t.me/piece_piece1/32",
        "https://t.me/piece_piece1/33",
        "https://t.me/piece_piece1/34",
        "https://t.me/piece_piece1/35",
        "https://t.me/piece_piece1/36",
        "https://t.me/piece_piece1/37",
        "https://t.me/piece_piece1/38",
        "https://t.me/piece_piece1/39",
        "https://t.me/piece_piece1/40",
        
        
    ],
    "season2": [
        "VIDEO FIle ID 4",
        "VIDEO File ID 5",
        "VIDEO File ID 6",
    ],
    "season3": [
        "VIDEO FIle ID 7",
        "VIDEO File ID 8",
        "VIDEO File ID 9",
    ],
    "season4": [
        "VIDEO FIle ID 7",
        "VIDEO File ID 8",
        "VIDEO File ID 9",
    ],
}

# Store chat IDs of users who interact with the bot
user_chat_ids = set()

# Owner's user ID (replace with the owner's Telegram ID)
OWNER_USER_ID = 1921230090  # Replace with your Telegram User ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start command that welcomes the user """
    user_chat_ids.add(update.message.chat.id)  # Add user to the chat ID list

    await update.message.reply_text(
        """
        🎉 မင်္ဂလာပါ!
        ကျေးဇူးပြု၍ ဇာတ်လမ်းတွဲများကို အောက်ပါ Menu မှ ရွေးချယ်ပါ။
        """
    )

    menu_keyboard = ReplyKeyboardMarkup(
        [["Season 1", "Season 2", "Season 3", "Season 4"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        " အောက်က Button Keyboard မှာ ရွေးချယ်ပါ။",
        reply_markup=menu_keyboard
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Help command to show instructions """
    await update.message.reply_text(
        """
        📖 အကူအညီ:
        - /start: Bot ကိုစတင်ပါ
        - /help: အကူအညီစာသားကိုကြည့်ပါ
        - /broadcast <message>: Owner သုံးသပ်ထားသော message ကို user အားလုံးကိုပို့ပါ
        """
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to broadcast message to all users"""
    if update.message.chat.id != OWNER_USER_ID:
        await update.message.reply_text("❌ သင့်မှာ broadcast ခြင်းခွင့်မရှိပါ။")
        return

    # Get the broadcast message from the command
    broadcast_message = ' '.join(context.args)
    if not broadcast_message:
        await update.message.reply_text("❌ broadcast message များကို မှတ်ချက်ထည့်ပါ။")
        return

    # Send the message to all users
    for chat_id in user_chat_ids:
        try:
            await context.bot.send_message(chat_id, broadcast_message)
        except Exception as e:
            logger.error(f"Failed to send broadcast message to {chat_id}: {e}")

    await update.message.reply_text(f"✅ broadcast message ကို အားလုံးကိုပို့ပြီးပါပြီ။")


async def send_season_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE, season: str):
    """ Send all videos for the selected season """
    episodes = SEASON_DATA.get(season, [])

    if not episodes:
        await update.message.reply_text(f"❌ {season} တွင် Video များမရှိသေးပါ။")
        return

    for index, video_id in enumerate(episodes, start=1):
        try:
            sent_message = await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video_id,
                caption=f"🎥 One Piece - Episode {index}"
            )
            
            # Schedule the deletion of this message after 24 hours
            asyncio.create_task(delete_message_after_delay(context, update.effective_chat.id, sent_message.message_id, 86400))
        
        except Exception as e:
            logger.error(f"Video ပို့ရာတွင် အမှားဖြစ်နေပါသည်: {e}")

    await update.message.reply_text(f"✅ {season} ဇာတ်လမ်းတွဲအားလုံးကို ပို့ပြီးပါပြီ။")


async def delete_message_after_delay(context: CallbackContext, chat_id: int, message_id: int, delay: int):
    """ Function to delete a message after a given delay (in seconds) """
    await asyncio.sleep(delay)  # Wait for the specified delay
    try:
        await context.bot.delete_message(chat_id, message_id)
        logger.info(f"Message {message_id} deleted after {delay} seconds.")
    except Exception as e:
        logger.error(f"Error deleting message {message_id}: {e}")


async def handle_season_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Handle season selection and send videos """
    selected_text = update.message.text
    season_key = selected_text.lower().replace(" ", "")

    if season_key not in SEASON_DATA:
        await update.message.reply_text("❌ မရှိသော Season ဖြစ်နေပါသည်။")
        return

    episodes = SEASON_DATA[season_key]
    for index, video_id in enumerate(episodes, start=1):
        try:
            sent_message = await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video_id,
                caption=f"🎥 One Piece - Episode {index}"
            )
            
            # Schedule the deletion of this message after 24 hours
            asyncio.create_task(delete_message_after_delay(context, update.effective_chat.id, sent_message.message_id, 86400))
        
        except Exception as e:
            logger.error(f"Video ပို့ချက်အမှား: {e}")

    await update.message.reply_text(f""
                                    "Copyright ပြဿနာတွေ ကြောင့် Video များ\n"
                                    "24hoursအတွင်းပျက်ပါမည်\n"
                                    "--------/start--------\n" 
                                    "ကိုနှိမ့်ပြီး ပြန်ကြည့်ပေးပါရန်\n"
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Handle received video and return the file ID """
    video_id = update.message.video.file_id
    await update.message.reply_text(f"📁 File ID: {video_id}")


def main():
    # Initialize the application with the bot token
    application = Application.builder().token("8134869323:AAHI2Hhqx-roNtTYHj6xCi5TqBJPm3Bf7VE").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Handle video and season selection messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_season_selection))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

    # Add handlers for each season
    for season in SEASON_DATA.keys():
        application.add_handler(
            CommandHandler(
                season,
                lambda update, context, s=season: send_season_episodes(update, context, s)
            )
        )

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()

from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello Railway Web App!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
