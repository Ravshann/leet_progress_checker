import telegram
from telegram import ParseMode
from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, MessageHandler
from code import *
from secrets import telegram_bot_token

updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    chat_id = update.effective_chat.id
    text = """
    Welcome to LeetProgressChecker
    All possible commands:
    /start
    /updatedb 
    /adduser
    /deleteuser
    /getprogresslist
    """
    context.bot.send_message(chat_id=chat_id, text=text)


def update_db(update, context):
    status = update_database()
    if status is None:
        message = "Finished update"
    else:
        message = "Wrong leetcode user: " + status

    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=message)


def add_user(update, context):
    text = """Write username like below: \nAdd LeetUser: LeetCodeUser"""
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=text)


def delete_user(update, context):
    text = """Write username like below: \nDelete LeetUser: LeetCodeUser"""
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=text)


def get_input(update, context):
    txt = update.message.text
    user_set = get_all_users()
    # add user
    if(not txt.startswith('/') and txt.startswith('Add LeetUser:')):
        username = txt.split("Add LeetUser:")
        username = username[1].strip()
        answer = f'New user is added: {username}'
        add_new_user(username, user_set)
        update.message.reply_text(answer)
    # delete user
    if(not txt.startswith('/') and txt.startswith('Delete LeetUser:')):
        username = txt.split("Delete LeetUser:")
        username = username[1].strip()
        answer = f'User is deleted: {username}'
        delete_user_by_name(username, user_set)
        update.message.reply_text(answer)


def get_progress(update, context):
    data = get_all_user_progress()
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text=f'```\n{data}```', parse_mode=ParseMode.MARKDOWN_V2)


dispatcher.add_handler(CommandHandler("getprogresslist", get_progress))
dispatcher.add_handler(CommandHandler("updatedb", update_db))
dispatcher.add_handler(CommandHandler("adduser", add_user))
dispatcher.add_handler(CommandHandler("deleteuser", delete_user))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text, get_input))
print("bot started")
updater.start_polling()
