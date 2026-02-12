from telebot import TeleBot, types
from config import API_TOKEN, ADMIN_GROUP_ID

bot = TeleBot(API_TOKEN)

# Maps forwarded_admin_message_id -> (user_id, original_content_text)
user_message_map = {}


# ===== /start =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome to HU Bible Study Section Question and Answer Bot!" \
        "\n እንኳን ወደ HU Bible Study Section የጥያቄ እና መልስ bot በደህና መጡ! "
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(
        "ከገላትያ ", callback_data="btn1"
    )
    btn2 = types.InlineKeyboardButton(
        "ከየትኛውም ቦታ ይጠይቁ", callback_data="btn2"
    )
    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "ከየት መጠየቅ ይፈልጋሉ?:\nChoose an option:",
        reply_markup=markup
    )


# ===== Inline button =====
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.send_message(
        call.message.chat.id,
        "ጥያቄዎን ይላኩ...\n"
        "Send your Question..."
    )


# ===== Forward ANY user message to admin group =====
@bot.message_handler(
    func=lambda m: m.chat.id != ADMIN_GROUP_ID,
    content_types=['text', 'photo',"document", "voice"]
)
def forward_to_admin(message):

    # == Photo with caption ==
    if message.content_type == "photo":
        if message.photo:
            file_id = message.photo[-1].file_id
            caption = message.caption or ""
            sent = bot.send_photo(
                ADMIN_GROUP_ID,
                file_id,
                caption=f"📸 From @{message.from_user.username} ({message.from_user.id}):\n{caption}"
            )
            user_message_map[sent.message_id] = (message.from_user.id, caption)

            bot.send_message(
                message.chat.id,
                "✅ ጥያቄዎ  ተልኳል። \n Your question has been sent! \nWait for the Answer...."
            )
            return
        # == Photo with caption ==
    if message.content_type == "voice":
        if message.voice:
            file_id = message.voice.file_id
            caption = f"🎤 Voice from @{message.from_user.username} ({message.from_user.id})"
            sent = bot.send_voice(
                ADMIN_GROUP_ID,
                file_id,
                caption=caption
            )
            user_message_map[sent.message_id] = (message.from_user.id, caption)

            bot.send_message(
                message.chat.id,
                "✅ ጥያቄዎ  ተልኳል። \n Your voice has been sent! \nWait for the Answer...."
            )
            return
        
     # == Photo with caption ==
    if message.content_type == "document":
        if message.document:
            file_id = message.document.file_id
            caption = message.caption or ""
            sent = bot.send_document(
                ADMIN_GROUP_ID,
                file_id,
                caption=f"📸 From @{message.from_user.username} ({message.from_user.id}):\n{caption}"
            )
            user_message_map[sent.message_id] = (message.from_user.id, caption)

            bot.send_message(
                message.chat.id,
                "✅ ጥያቄዎ  ተልኳል። \n Your question has been sent! \nWait for the Answer...."
            )
            return    
       
    # == Text only ==
    if message.content_type == "text":
        text = message.text
        sent = bot.send_message(
            ADMIN_GROUP_ID,
            f"📩 From @{message.from_user.username} ({message.from_user.id}):\n{text}"
        )
        user_message_map[sent.message_id] = (message.from_user.id, text)

        bot.send_message(
            message.chat.id,
            "✅ መልዕክትዎ ተልኳል።\nYour text has been sent!\nWait for the Answer....."
        )
        return


# ===== Handle admin reply =====
@bot.message_handler(
    func=lambda m: m.chat.id == ADMIN_GROUP_ID and m.reply_to_message is not None,
    content_types=['text', 'photo', "voice", "document"]
)
def handle_admin_reply(message):

    replied_id = message.reply_to_message.message_id
    data = user_message_map.get(replied_id)

    if not data:
        return  # this reply wasn’t mapped

    user_id, orig_text = data

    # --- Admin replied with photo + caption ---
    if message.content_type == "photo":
        if message.photo:
            file_id = message.photo[-1].file_id
            caption = message.caption or ""
            bot.send_photo(
                user_id,
                file_id,
                caption=f"💬 Admin Reply:\n{caption}"
            )
            bot.send_message(ADMIN_GROUP_ID, "✔ Photo reply sent to user!")
            

    # --- Admin replied with text ---
    if message.content_type == "text":
        bot.send_message(
            user_id,
            f"❓ *Original:* {orig_text}\n\n💬 *Admin Reply:* {message.text}",
            parse_mode="Markdown"
        )
        bot.send_message(ADMIN_GROUP_ID, "✔ Text reply sent to user!")
        return

    # --- Admin replied with photo + caption ---
    if message.content_type == "voice":
        if message.voice:
            file_id = message.voice.file_id
            caption = f"🎤 Voice from @{message.from_user.username} ({message.from_user.id})"
            bot.send_voice(
                user_id,
                file_id,
                caption=f"💬 Admin Reply:\n{caption}"
            )
            bot.send_message(ADMIN_GROUP_ID, "✔ Voice reply sent to user!")
    # --- Admin replied with photo + caption ---
    if message.content_type == "document":
        if message.document:
            file_id = message.document.file_id
            caption = message.caption or ""
            bot.send_document(
                user_id,
                file_id,
                caption=f"💬 Admin Reply:\n{caption}"
            )
            bot.send_message(ADMIN_GROUP_ID, "✔ Document reply sent to user!")
                    
# ===== Start bot =====
bot.infinity_polling()
