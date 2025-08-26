import os
import json 
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
user_order_data = {}


# --- Bot Settings ---
TOKEN = "8134869323:AAHI2Hhqx-roNtTYHj6xCi5TqBJPm3Bf7VE"
ADMIN_CHAT_ID = 1921230090
ALLOWED_USERS_FILE = 'allowed_users.json'
PENDING_REQUESTS_FILE = 'pending_requests.json'

# --- Helper Functions ---
def load_allowed_users():
    if not os.path.exists(ALLOWED_USERS_FILE):
        return []
    with open(ALLOWED_USERS_FILE, 'r', encoding="utf-8") as f:
        return json.load(f)

def save_allowed_users(users):
    with open(ALLOWED_USERS_FILE, 'w', encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def load_pending_requests():
    if not os.path.exists(PENDING_REQUESTS_FILE):
        return {}
    with open(PENDING_REQUESTS_FILE, 'r', encoding="utf-8") as f:
        return json.load(f)

def save_pending_requests(requests):
    with open(PENDING_REQUESTS_FILE, 'w', encoding="utf-8") as f:
        json.dump(requests, f, ensure_ascii=False, indent=4)


# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    allowed_users = load_allowed_users()

    if user.id not in allowed_users:
        text = (
            f"🚫 Bot အသုံးပြုခွင့် မရှိပါ!\n\n"
            f"👋 မင်္ဂလာပါ {user.first_name}\n"
            f"🆔 Telegram ID: {user.id}\n\n"
            f"🙇 'အသုံးပြုခွင့်ရရန်' ကိုနှိပ်ပြီး Owner ထံမေးပါ။"
        )
        keyboard = [[InlineKeyboardButton("အသုံးပြုခွင့်ရရန်", callback_data='request_access')]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    text = (
        f"🙋🏻 မင်္ဂလာပါ {user.first_name}!\n"
        f"𝗡𝗦𝗔 𝗕𝗼𝘁 မှ ကြိုဆိုပါတယ်ရှင့်\n\n"
        f"Admin ရဲ့ Channel ကိုလည်း Join ထားပေးပါဦး။ 🙆🏻"
    )

    keyboard = [
        [InlineKeyboardButton("📢 NSA Channel", url="https://t.me/nsavenom")],
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    await update.message.reply_text(f"🎉 မင်္ဂလာပါ {user.first_name}!\nBot ကို အသုံးပြုနိုင်ပါပြီ။ /help ကိုနှိမ့်ပြီး အသုံးပြုနည်းလေ့လာပေးပါ")

# --- Main Button Handler ---
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'request_access':
        # Handle access request
        user = update.effective_user
        
        # Save pending request
        pending_requests = load_pending_requests()
        pending_requests[str(user.id)] = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "id": user.id
        }
        save_pending_requests(pending_requests)
        
        # Send request to admin with approve/reject buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ အတည်ပြု", callback_data=f'approve_{user.id}'),
                InlineKeyboardButton("❌ ငြင်းပါယ်", callback_data=f'reject_{user.id}'),
            ]
        ]
        
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🔔 အသုံးပြုခွင့်တောင်းခံမှု\n\n"
                 f"👤 အမည်: {user.first_name} {user.last_name or ''}\n"
                 f"🆔 ID: {user.id}\n"
                 f"👤 Username: @{user.username or 'မရှိ'}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.edit_message_text("✅ အသုံးပြုခွင့်တောင်းခံမှုကို Admin ထံပေးပို့ပြီးပါပြီ။")

    # Handle help command buttons
    elif query.data.startswith('cmd_'):
        await handled_help_buttons(update, context)

        
    # Handle admin approve/reject actions
    elif query.data.startswith('approve_'):
        user_id = int(query.data.split('_')[1])
        
        # Add user to allowed users
        allowed_users = load_allowed_users()
        if user_id not in allowed_users:
            allowed_users.append(user_id)
            save_allowed_users(allowed_users)
        
        # Remove from pending requests
        pending_requests = load_pending_requests()
        user_data = pending_requests.pop(str(user_id), {})
        save_pending_requests(pending_requests)
        
        # Notify admin
        await query.edit_message_text(f"✅ အသုံးပြုခွင့်အတည်ပြုပြီးပါပြီ။\n\n👤 အမည်: {user_data.get('first_name', 'Unknown')}\n🆔 ID: {user_id}")
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 ခွင့်ပြုချက်ရရှိပြီးပါပြီ!\n\n"
                     "✅ သင့်အားBotအသုံးပြုခွင့်ပေးလိုက်ပြီးပါပြီ။\n"
                     "🚀 /start ကိုနှိပ်ပြီး စတင်အသုံးပြုနိုင်ပါပြီ။"
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"⚠️ User {user_id} ကို notification မပို့နိုင်ပါ။ ({str(e)})"
            )
    
    elif query.data.startswith('reject_'):
        user_id = int(query.data.split('_')[1])
        
        # Get user data and remove from pending requests
        pending_requests = load_pending_requests()
        user_data = pending_requests.pop(str(user_id), {})
        save_pending_requests(pending_requests)
        
        # Notify admin
        await query.edit_message_text(f"❌ အသုံးပြုခွင့်ငြင်းပါယ်ပြီးပါပြီ။\n\n👤 အမည်: {user_data.get('first_name', 'Unknown')}\n🆔 ID: {user_id}")
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🚫 အသုံးပြုခွင့်ငြင်းပါယ်ခြင်း\n\n"
                     "❌ သင့်အား Bot အသုံးပြုခွင့်မပေးနိုင်ပါ။\n"
                     "📞 အကြောင်းရင်းသိလိုပါက Admin ကိုဆက်သွယ်ပါ။"
            )
        except Exception as e:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"⚠️ User {user_id} ကို rejection notification မပို့နိုင်ပါ။ ({str(e)})"
            )



async def handled_help_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    commands = {
        "cmd_start": "/start ကိုနှိပ်ပါ။ Bot ကိုစတင်နိုင်ပါတယ်။",
        "cmd_open": "/open ကိုနှိပ်ပါပြီး အကောင့်သစ်ဖွင့်ပေးပါရန်",
        "cmd_price": "/price ကိုနှိပ်ပါ။ Categories နှင့် Price များကြည့်နိုင်ပါတယ်။",
        "cmd_buy": "/buy ကိုနှိပ်ပြီး order တင်နိုင်ပါတယ်",
        "cmd_withdraw": "/withdraw ကိုနှိပ်ပြီး ငွေထုတ်နိုင်ပါသည်",
        "cmd_help": "အသုံးပြုနိုင်သော Command များကို ပြထားပါတယ်။",
        "cmd_msg": "/msg နောက်မှာရေးချင်တဲ့စာကိုရေးပို့ပေးပါ",
        "cmd_my_order_history": "/my_order_history ဖြင့် သင့်အော်ဒါများကြည့်နိုင်ပါတယ်။",
        "cmd_contact_owner": "/contact_owner ဖြင့် owner ကိုမက်ဆေ့ချ် ပေးပို့နိုင်ပါတယ်။"
    }
    await query.edit_message_text(text=commands.get(query.data, "❌ မသိသော Command ဖြစ်ပါတယ်။"))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 စတင်ရန်", callback_data="cmd_start")],
        [InlineKeyboardButton("🎮 အကောင့်သစ်ဖွင့်ရန်", callback_data="cmd_open")],
        [InlineKeyboardButton("📋 Price ကြည့်ရန်", callback_data="cmd_price")],
        [InlineKeyboardButton("🛒 အော်ဒါ တင်ရန်", callback_data="cmd_buy")],
        [InlineKeyboardButton("📋 ငွေထုတ်ရန်", callback_data="cmd_withdraw")],
        [InlineKeyboardButton("📖 အသုံးပြုနည်း", callback_data="cmd_help")],
        [InlineKeyboardButton("🎯 စကားပြောရန်", callback_data="cmd_msg")],
        [InlineKeyboardButton("📜 My Order History", callback_data="cmd_my_order_history")],
        [InlineKeyboardButton("📩 Contact Owner", callback_data="cmd_contact_owner")],
    ]
    await update.message.reply_text(
        "📌 အသုံးပြုနိုင်သော Command များကို Button အဖြစ်ရွေးနိုင်ပါသည်။",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    
async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎮 ကစားရန်လိုသော Category တစ်ခုရွေးပါ။\n\n"
        "📝 Telegram Premium ဝယ်ယူချင်ရင် /msg ကို သုံးပါ။\n"
        "🔍 /price ကို အသုံးပြုပြီး ပစ္စည်းစျေးနှုန်းများ အလိုလိုကြည့်နိုင်ပါတယ်။"
    )

    keyboard = [
        [InlineKeyboardButton("1xbet", callback_data="buy_1xbet")],
        [InlineKeyboardButton("Batman688", callback_data="buy_batman688")],
        [InlineKeyboardButton("555Mix", callback_data="buy_555mix")],
        [InlineKeyboardButton("ကျွဲဂိမ်း", callback_data="buy_konmin")],
        [InlineKeyboardButton("Mobile legends", callback_data="buy_mobile_legends")],
        [InlineKeyboardButton("Magic chess gogo", callback_data="buy_magic_chess")],
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Handle Category Selection ---
async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_1xbet":
        # Prompt user to input 1xBet ID
        user_id = update.effective_user.id
        user_order_data[user_id] = {"category": "1xbet", "step": "enter_id"}

        text = (
            "🛒 1xBet Unit ထည့်ရန်:\n"
            "➤ 1xBet ID ကို ပေးပိုပါ။\n\n"
            "💰 အနည်းဆုံး 500 MMK မှ စ၍ ထည့်ပေးပါရန်။"
        )

        await query.edit_message_text(text)
        return


# --- Handle User Input for 1xBet ID ---
async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text

    if user_id in user_order_data and user_order_data[user_id]["step"] == "enter_id":
        # Store the 1xBet ID
        user_order_data[user_id]["1xbet_id"] = user_input
        user_order_data[user_id]["step"] = "payment_details"

        # Send payment instructions
        text = (
            "💳 Kpay Pay နံပါတ်: 09671495396 ကို copy လုပ်ပါ။\n"
            "• Name - Hsu Zin Zin Aung\n\n"
            "💳 Wave Pay နံပါတ်: 09942600822 ကို copy လုပ်ပါ။\n"
            "• Name - Ngwe Soe Aung\n\n"
            "📝 Note မှာ shop လို ရေးပေးပါရန်!\n"
            "📸 ငွေလွှဲပြီးရင် Screenshot ကို တင်ပေးပါ။"
        )

        await update.message.reply_text(text)

    elif user_id in user_order_data and user_order_data[user_id]["step"] == "payment_details":
        # If it's a screenshot, send it to admin
        if update.message.photo:
            # Save screenshot
            screenshot = update.message.photo[-1].file_id

            # Send the order to admin
            admin_message = (
                f"🛒 New order received!\n"
                f"Category: {user_order_data[user_id]['category']}\n"
                f"1xBet ID: {user_order_data[user_id]['1xbet_id']}\n"
                f"Screenshot: [Click to view]({screenshot})"
            )

            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message, parse_mode=ParseMode.MARKDOWN)

            # Notify user
            await update.message.reply_text("✅ Order received! Admin will review it soon.")

            # Clear user order data after the process
            del user_order_data[user_id]


# --- Ban User Command ---
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Admin check
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 သင့်မှာ အာဏာမရှိပါ။")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❗ သုံးပုံ: /ban_user <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ User ID မှားနေပါတယ်။")
        return

    allowed_users = load_allowed_users()

    if target_id not in allowed_users:
        await update.message.reply_text("ℹ️ အဲ့ယောက်သမားသည် အခုတလော Allow မပေးထားပါ။")
        return

    # Remove from allowed users
    allowed_users.remove(target_id)
    save_allowed_users(allowed_users)

    # Notify admin
    await update.message.reply_text(f"✅ User {target_id} ကို Ban လိုက်ပြီ။")

    # Try notifying banned user
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text="🚫 သင်ကို Bot အသုံးပြုခွင့်မှ ဖယ်ရှားလိုက်ပါပြီ။"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ User ကို မက်ဆေ့ပို့မရပါ။ ({str(e)})")



# --- Application Setup ---
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("buy", buy_command))
    application.add_handler(CommandHandler("ban_user", ban_user))
    application.add_handler(CallbackQueryHandler(handle_category_selection, pattern="^buy_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
    application.add_handler(MessageHandler(filters.PHOTO, handle_user_input))



    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
