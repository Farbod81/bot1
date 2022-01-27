import logging
import telegram
import requests
import json
from bs4 import BeautifulSoup
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters, ConversationHandler)
import os

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




def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    user_data = context.user_data
    update.message.reply_text('''\t\tHello🖐\n
                              if you would watch your playlist📃 tap > /list <\n
                              if you want to search🔎 for movie👇🏿 \n
                              select your favorite genre🎬 from buttons blow''',
                              reply_markup=markup1)
    return Genre


def genre(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Genre'
    text = update.message.text
    user_data[category] = text
    update.message.reply_text(
        "please Enter Min release year📡")
    return Minr


def minr(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Minr'
    text = update.message.text
    user_data[category] = text
    update.message.reply_text('please Enter Max release year🎞')
    return Maxr


def maxr(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'Maxr'
    text = update.message.text
    user_data[category] = text
    update.message.reply_text('Please Choose The Country🏜',
                              reply_markup=markup2)

    return Country


def country(update, context):
    user = update.message.from_user
    user_data = context.user_data
    category = 'country'
    text = update.message.text
    user_data[category] = text
    update.message.reply_text('tap on /search for searching🔎')
    # print('------------')
    # print(user_data)
    # return Search


def search(update, context):
    update.message.reply_text('please Wait.')
    user = update.message.from_user
    user_data = context.user_data
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

    write_json({user_name: b})
    # user_data['favorite films'] = b
    q = 0
    for index in b:
        if q < 5:
            update.message.reply_text(index)
            q += 1
    update.message.reply_text('all movies🎞 added to your favorite list📃 \nyou can see by /list')
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the coneversation", user.first_name)

    update.message.reply_text(
        "بدرود امیدوارم بازم شما رو ببینم", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def getlist(update, context):
    user = update.message.from_user
    user_data = context.user_data
    user_name = update.message.chat.id
    # films = user_data['favorite films']
    # for i in films:
    #     update.message.reply_text(i)
    Films = read_json()
    if str(user_name) in Films.keys():
        b = Films[str(user_name)]
        for index in b:
            update.message.reply_text(index)
    else:
        update.message.reply_text('You DO NOT have any playlist🤦🏻‍♂️.')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)



# bot = telegram.Bot(token=TOKEN)
def main():
    PORT = int(os.environ.get('PORT', '8443'))
    TOKEN = "5045797845:AAESN8MluCR2jbLQz0-qayvAf1olNwFyRAI"
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('search', search))
    dp.add_handler(CommandHandler('list', getlist))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            Genre: [CommandHandler('start', start), MessageHandler(Filters.text, genre)],
            Minr: [CommandHandler('start', start), MessageHandler(Filters.text, minr)],
            Maxr: [CommandHandler('start', start), MessageHandler(Filters.text, maxr)],
            Country: [CommandHandler('start', start), MessageHandler(Filters.text, country)],
            Search: [CommandHandler('start', start), MessageHandler(Filters.text, search)]
        },

        fallbacks=[CommandHandler('cancle', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url="https://moviefinderproject2.herokuapp.com/" + TOKEN)


    updater.idle()



# app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
if __name__ == '__main__':
    read_json()
    main()