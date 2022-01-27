import logging
import telegram
import requests
import json
from flask import Flask
from bs4 import BeautifulSoup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters, ConversationHandler)
import os
from telegram import Update,KeyboardButton,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, Updater, CallbackQueryHandler



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

Genre, Minr, Maxr, Country, Search = range(5)


def write_json(data, filename="film.json"):
    data1 = read_json()
    data1.update(data)
    with open(filename, 'w') as target:
        json.dump(data1, target, indent=4, ensure_ascii=False)


def read_json(filename="film.json"):
    with open(filename, 'r') as target:
        data = json.load(target)
    return data


with open('film.json', 'w') as target:
    json.dump({}, target, indent=4, ensure_ascii=False)



reply_keyboard1 = [['درام', 'اکشن', 'رمانتیک',
                    'جنایی', 'ترسناک', 'تاریخی', 'اجتماعی']]
reply_keyboard2 = [['USA', 'France', 'Germany',
                    'India', 'Iran', 'Italy', 'Japan', 'Spain']]

markup1 = ReplyKeyboardMarkup(
    reply_keyboard1, resize_keyboard=True, one_time_keyboard=True)
markup2 = ReplyKeyboardMarkup(
    reply_keyboard2, resize_keyboard=True, one_time_keyboard=True)




# def facts_to_str(user_data):
#     facts = list()
#
#     for key, value in user_data.items():
#         facts.append('{} - {}'.format(key, value))
#
#     return "\n".join(facts).join(['\n', '\n'])


def start(update, callback):
    buttons = [[KeyboardButton("/start")], [KeyboardButton("/find")], [KeyboardButton("/favorites")]]
    callback.bot.send_message(chat_id=update.effective_chat.id, text="Hi🖐.Welcome to moviefinder bot.\nChoose one to continue.👇",
                              reply_markup=ReplyKeyboardMarkup(buttons))

    # buttonss = [[InlineKeyboardButton("favorites", callback_data="list")]]


def find(update, callback):

    reply_keyboard1 = [['درام', 'اکشن', 'رمانتیک',
                        'جنایی', 'ترسناک', 'تاریخی', 'اجتماعی']]
    callback.bot.send_message(chat_id=update.effective_chat.id,
                              text="please choose the genre 🎬",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard1))

    return Genre

def genre(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Genre'
    text = update.message.text
    user_data[category] = text
    update.message.reply_text(
        "please enter Min release year 📅")
    return Minr


def minr(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Minr'
    text = update.message.text
    user_data[category] = text
    update.message.reply_text('please enter Max release year 📅')
    return Maxr


def maxr(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Maxr'
    text = update.message.text
    user_data[category] = text
    update.message.reply_text('please choose The country 🏳',
                              reply_markup=markup2)

    return Country


def country(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'country'
    text = update.message.text
    user_data[category] = text
    update.message.reply_text('tap on /search for searching 🔎')
    # print('------------')
    # print(user_data)
    # return Search


def search(update: Update, callback: CallbackContext):
    buttons = [[KeyboardButton("/start")], [KeyboardButton("/find")], [KeyboardButton("/favorites")]]
    callback.bot.send_message(chat_id=update.effective_chat.id,
                              text="please wait...",
                              reply_markup=ReplyKeyboardMarkup(buttons))
    user = update.message.from_user
    user_data = callback.user_data
    user_name = update.message.chat.id
    url = f"https://hmvz.xyz/?s=&post_type=&genreOne={user_data['Genre']}&country={user_data['country']}&minRelease={user_data['Minr']}&maxRelease={user_data['Maxr']}"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    a = soup.find_all("h2")
    b = str(a)
    b = b.replace("</h2>", "")
    b = b.replace("<h2>", "")
    b = b.replace("[", "")
    b = b.replace("]", "")
    b = b.split(",")
    q = 0
    for movie in b:
        if q < 5:
            q += 1
            try:
                infbutton = [[InlineKeyboardButton("🤩 add to favorites", callback_data=f"inf{movie}")]]
                callback.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(infbutton), text=f"{movie}")
            except:
                update.message.reply_text(f"noting found. try again😔. /find")

    return ConversationHandler.END





def queryHandler(update: Update, callback: CallbackContext):
    query = update.callback_query.data
    update.callback_query.answer()

    if "searcher" in query:
        callback.bot.send_message(chat_id=update.effective_chat.id, text=f"/find")


    elif "list" in query:
        username = update.effective_user.username
        films = read_json()
        if username in films.keys():
            favorites = ""
            for index in films[username]:
                favorites += f"🍿{index}\n"
            callback.bot.send_message(chat_id=update.effective_chat.id, text=f"{favorites}")
        else:
            callback.bot.send_message(chat_id=update.effective_chat.id, text="List is empty!")



    if 'inf' in query:
        film = read_json()
        username = update.effective_user.username
        query = query.replace("inf", "")
        if username not in film.keys():
            film[username] = []
        if query not in film[username]:
            film[username].append(query)
            write_json(film)




def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the coneversation", user.first_name)

    update.message.reply_text(
        "👋🏻 goodbye", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def getlist(update, context):
    # user = update.message.from_user
    # user_data = context.user_data
    username = update.effective_user.username
    films = read_json()
    if username in films.keys():
        favorites = ""
        for index in films[username]:
            favorites += f"🍿{index}\n"
        update.message.reply_text(favorites)
    else:
        update.message.reply_text('list is empty.')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)



# bot = telegram.Bot(token=TOKEN)
def main():
    PORT = int(os.environ.get('PORT', '8443'))
    TOKEN = "5196209735:AAEpivbVU4KjXHqr178naRjcGsD4rJV62T4"
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('search', search))
    dp.add_handler(CommandHandler('favorites', getlist))
    dp.add_handler(CallbackQueryHandler(queryHandler))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('find', find)],

        states={
            Genre: [CommandHandler('find', find), MessageHandler(Filters.text, genre)],
            Minr: [CommandHandler('find', find), MessageHandler(Filters.text, minr)],
            Maxr: [CommandHandler('find', find), MessageHandler(Filters.text, maxr)],
            Country: [CommandHandler('find', find), MessageHandler(Filters.text, country)],
            Search: [CommandHandler('find', find), MessageHandler(Filters.text, search)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url="https://telegrambotsample.herokuapp.com/" + TOKEN)

    updater.idle()


if __name__ == '__main__':
    read_json()
    main()
