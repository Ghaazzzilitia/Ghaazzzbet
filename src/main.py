import logging

import os
from re import MULTILINE
from pymongo import message
import telegram
from telegram import user
from telegram import chat
from telegram.chat import Chat

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

import datetime
import time

from database import Database

from classes import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

token = os.getenv("token")

db_url = os.getenv("db_url")
db = Database(db_url=db_url)

updater = Updater(token, use_context=True)


st = {}
last_message = {}
user_bet = {}
add_teams = {}
mulvec = {}

def add_user(user):
    user_id = user.id
    db.register_user(user)
    try:
        st[user_id]
        return 0
    except:
        st[user_id] = "main"
        return 1
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    if add_user(user):
        last_message[user_id] = update.message.reply_text("سلام به بات پیش بینی غاززز خوش اومدید.")
    else:
        last_message[user_id] = update.message.reply_text("سلامی دوباره")
    st[user_id] = "main"
def settings(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    add_user(user)
    if st[user_id] != "main":
        last_message[user_id] = update.message.reply_text("شما در استیت درست قرار ندارید.")
        return
    keys = []
    keys.append([InlineKeyboardButton(text = "Notification",
                                            callback_data = "settings_notif")])
    markup = InlineKeyboardMarkup(keys)
    msg = "تنظیمات"
    last_message[user_id] = update.message.reply_text(msg, reply_markup = markup, parse_mode='HTML')
def matches(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    add_user(user)
    if st[user_id] != "main":
        last_message[user_id] = update.message.reply_text("شما در استیت درست قرار ندارید.")
        return
    if db.count_active_games() == 0:
        last_message[user_id] = update.message.reply_text("در حال حاضر بازی ای برای پیش بینی وجود ندارد.")
        return
    games = db.get_active_games()
    msg = ""
    for game in games:
        msg += game["first_team"]["name"] + ' - ' + game["second_team"]["name"] + '\n' + "شروع بازی: " + game["time_msg"] + "\n" + "تورنومنت: " + game["tr_name"] + "\n"
        if (game["is_over"]):
            msg += "نتیحه نهایی: " + str(game["first_score"]) + ' - ' + str(game["second_score"]) + "\n"
        msg += "\n"
    last_message[user_id] = update.message.reply_text(msg, parse_mode = "HTML")
    return

def bet(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    add_user(user)
    if st[user_id] != "main":
        last_message[user_id] = update.message.reply_text("شما در استیت درست قرار ندارید.")
        return
    if db.count_active_games() == 0:
        last_message[user_id] = update.message.reply_text("در حال حاضر بازی ای برای پیش بینی وجود ندارد.")
        return

    keys = []
    i = 0
    games = db.get_active_games()
    for game in games:
        keys.append([InlineKeyboardButton(text = game["first_team"]["name"] + ' - ' + game["second_team"]["name"],
                                            callback_data = "choose_game bet " + str(game["game_id"]))])
    markup = InlineKeyboardMarkup(keys)
    msg = "کدوم بازی"
    last_message[user_id] = update.message.reply_text(msg, reply_markup = markup, parse_mode='HTML')
    st[user_id] = "bet0"
def mulbet(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    add_user(user)
    if st[user_id] != "main":
        last_message[user_id] = update.message.reply_text("شما در استیت درست قرار ندارید.")
        return
    if db.count_active_mulents() == 0:
        last_message[user_id] = update.message.reply_text("در حال حاضر سوالی برای پیش بینی وجود ندارد.")
        return

    keys = []
    i = 0
    mulents = db.get_active_mulents()
    for mulent in mulents:
        keys.append([InlineKeyboardButton(text = mulent["title"],
                                            callback_data = "mulbet " + str(mulent["mulent_id"]))])
    markup = InlineKeyboardMarkup(keys)
    msg = "کدوم بت"
    last_message[user_id] = update.message.reply_text(msg, reply_markup = markup, parse_mode='HTML')
    st[user_id] = "mulbet0"
def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    add_user(user)

    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}):
        add_teams[user_id] = []

    last_message[user_id] = update.message.reply_text("شما در استیت مین قرار دارید.")
    st[user_id] = "main"

def user_game_score(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    add_user(user)
    if st[user_id] != "main":
        last_message[user_id] = update.message.reply_text("شما در استیت درست قرار ندارید.")
        return

    last_message[user_id] = update.message.reply_text("امتیاز شما: " + str(db.get_user_game_score(user_id)))
    return
def handle(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    add_user(user)


    if st[user_id] == "main":
        return
    if st[user_id] == "bet1":
        msg = update.message.text
        try:
            x = int(msg)
        except:
            return
        user_bet[user_id].first_score = x
        st[user_id] = "bet2"
        last_message[user_id] = update.message.reply_text("تعداد گل " + user_bet[user_id].second_team + " : ")
        return
    if st[user_id] == "bet2":
        msg = update.message.text
        try:
            x = int(msg)
        except:
            return
        user_bet[user_id].second_score = x
        st[user_id] = "bet3"
        last_message[user_id] = update.message.reply_text("فکت : ", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = "Skip", callback_data = "skip_fact")]]))
        return
    if st[user_id] == "bet3":
        msg = update.message.text
        user_bet[user_id].facts = msg
        user_bet[user_id].time = update.message.date
        if user_bet[user_id].time > datetime.datetime.strptime(user_bet[user_id].game_time, '%Y-%m-%d %H:%M:%S%z'):
            last_message[user_id] = update.message.reply_text("بعد شروع بازي حق پيش بيني نداريد.")
            st[user_id] = "main"
            return
        db.add_bet(user_bet[user_id])
        last_message[user_id] = update.message.reply_text("پیش بینی شما ذخیره شد.")
        st[user_id] = "main"
        return
    if st[user_id] == "add0":
        team_name = update.message.text
        team_id = db.next_team_id()
        db.add_team(Team(team_id, team_name))
        add_teams[user_id].append(Team(team_id, team_name))
        last_message[user_id] = update.message.reply_text("نام تیم دوم:")
        st[user_id] = "add1"
        return
    if st[user_id] == "add1":
        team_name = update.message.text
        team_id = db.next_team_id()
        db.add_team(Team(team_id, team_name))
        add_teams[user_id].append(Team(team_id, team_name))
        last_message[user_id] = update.message.reply_text("Time\nYYYY-MM-DD HH:MM:SS", parse_mode="HTML")
        st[user_id] = "add2"
        return
    if st[user_id] == "add2":
        time = update.message.text + "+04:30"
        try:
            datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S%z')
            add_teams[user_id].append(time)
            last_message[user_id] = update.message.reply_text("متن الکی تایم")
            st[user_id] = "add3"
        except:
            last_message[user_id] = update.message.reply_text("Time\nYYYY-MM-DD HH:MM:SS", parse_mode="HTML")
            st[user_id] = "add2"
        return
    if st[user_id] == "add3":
        time = update.message.text
        add_teams[user_id].append(time)
        last_message[user_id] = update.message.reply_text("tournoment :")
        st[user_id] = "add4"
        return
    if st[user_id] == "add4":
        tr_name = update.message.text
        game_id = db.next_game_id()
        db.add_game(Game(game_id, add_teams[user_id][0], add_teams[user_id][1], add_teams[user_id][2], add_teams[user_id][3], tr_name))
        last_message[user_id] = update.message.reply_text("بازی افزوده شد.")
        add_teams[user_id].clear()
        st[user_id] = "main"
        return
    if st[user_id] == "announce_all":
        msg = update.message.text
        cnt_mellat = 0
        for mellat in db.users.find({}):
            try:
                chat_id = mellat["tg_user"]["id"]
                last_message[chat_id] = context.bot.send_message(
                    chat_id = chat_id,
                    text = msg
                )
                cnt_mellat += 1
            except:
                cnt_mellat += 0
        for mellat in db.users.find({"is_admin": 1}):
            chat_id = mellat["tg_user"]["id"]
            last_message[chat_id] = context.bot.send_message(
                chat_id = chat_id,
                text = "به " + str(cnt_mellat) + " نفر فرستادم"
            )
        st[user_id] = "main"
        return
    if st[user_id] == "announce_1":
        msg = update.message.text
        for mellat in db.users.find({"notif.1": 1}):
            try:
                chat_id = mellat["tg_user"]["id"]
                last_message[chat_id] = context.bot.send_message(
                    chat_id = chat_id,
                    text = msg
                )
                cnt_mellat += 1
            except:
                cnt_mellat += 0
        for mellat in db.users.find({"is_admin": 1}):
            chat_id = mellat["tg_user"]["id"]
            last_message[chat_id] = context.bot.send_message(
                chat_id = chat_id,
                text = "به " + str(cnt_mellat) + " نفر فرستادم"
            )
        st[user_id] = "main"
        return
    if st[user_id] == "mulent_0":
        msg = update.message.text
        mulvec[user_id].append(msg)
        last_message[user_id] = update.message.reply_text("سوال:")
        st[user_id] = "mulent_1"
        return
    if st[user_id] == "mulent_1":
        msg = update.message.text
        mulvec[user_id].append(msg)
        last_message[user_id] = update.message.reply_text("Time:")
        st[user_id] = "mulent_2"
        return
    if st[user_id] == "mulent_2":
        msg = update.message.text
        if msg == "end_mul":
            db.add_mul(mulvec[user_id])
            mulvec[user_id].clear()
            last_message[user_id] = update.message.reply_text("موفقیت")
            st[user_id] = "main"
            return
        mulvec[user_id].append(msg)
        last_message[user_id] = update.message.reply_text("گزینه " + str(len(mulvec[user_id]) - 2))
        return
    

def handle_choose_game_key(update: Update, context: CallbackContext):
    
    user = update.callback_query.from_user
    user_id = user.id
    add_user(user)
    query = update.callback_query
    try:
        if(query.message.message_id != last_message[user_id].message_id):
            return
    except:
        return
    stt = query.data.split()[1]
    game_id = int(query.data.split()[2])
    game = db.games.find_one({"game_id": game_id})
    bot = context.bot
    if stt == "bet":
        if st[user_id] != "bet0":
            return
        last_message[user_id] = bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text = game["first_team"]["name"] + ' - ' + game["second_team"]["name"] + '\n' + "شروع بازی: " + game["time_msg"] + '\n' + "تورنومنت: " + game["tr_name"]
        )
        user_bet[user_id] = Bet(user, game["game_id"], game["first_team"]["name"], game["second_team"]["name"], game["time"])
        st[user_id] = "bet1"
        if game["is_over"]:
            last_message[user_id] = last_message[user_id].reply_text("بازی به پایان رسیده.")
            last_message[user_id] = last_message[user_id].reply_text(game["first_team"]["name"] + " " + str(game["first_score"]) +
            " - " + str(game["second_score"]) + " " + game["second_team"]["name"])
            st[user_id] = "main"
            return
        if db.bets.count_documents({"game_id": game["game_id"], "user.id": user_id}):
            last_message[user_id] = last_message[user_id].reply_text("شما قبلا پیش بینی کرده اید.")
            bet = db.bets.find_one({"game_id": game["game_id"], "user.id": user_id})
            last_message[user_id] = last_message[user_id].reply_text(game["first_team"]["name"] + " " + str(bet["first_score"]) +
            " - " + str(bet["second_score"]) + " " + game["second_team"]["name"])
            st[user_id] = "main"
            return
        last_message[user_id] = last_message[user_id].reply_text("تعداد گل " + user_bet[user_id].first_team + " : ")
        return
    if stt == "remove":
        if st[user_id] != "remove_game":
            return
        last_message[user_id] = bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text = game["first_team"]["name"] + ' - ' + game["second_team"]["name"] + '\n' + "شروع بازی: " + game["time_msg"] + '\n' + "تورنومنت: " + game["tr_name"]
        )
        db.deactivate_game(game_id)
        last_message[user_id] = bot.send_message(chat_id=query.message.chat_id, text="با موفقیت حذف شد.")
        return

def handle_mulbet_key(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    user_id = user.id
    add_user(user)
    query = update.callback_query
    try:
        if(query.message.message_id != last_message[user_id].message_id):
            return
    except:
        return
    if st[user_id] != "mulbet0":
        return
    x = int(query.data[len("mulbet "):])
    mulent = db.mulents.find_one({"mulent_id": x})
    bot = context.bot
    last_message[user_id] = bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = mulent["title"]
    )
    if db.mulbets.count_documents({"mulent_id": mulent["mulent_id"], "user.id": user_id}):
        last_message[user_id] = last_message[user_id].reply_text("شما قبلا پیش بینی کرده اید.")
        mulbet = db.mulbets.find_one({"mulent_id": mulent["mulent_id"], "user.id": user_id})
        last_message[user_id] = last_message[user_id].reply_text(mulent["question"] + "\n\n" + mulent["choices"][str(mulbet["choice"])])
        st[user_id] = "main"
        return
    if mulent["is_over"]:
        last_message[user_id] = last_message[user_id].reply_text("مهلت بت به پایان رسیده.")
        st[user_id] = "main"
        return
    keys = []
    i = 0
    for i in range(mulent["choice_cnt"]):
        keys.append([InlineKeyboardButton(text = mulent["choices"][str(i)],
                                            callback_data = "mulent " + str(mulent["mulent_id"]) + "-" + str(str(i)))])
    markup = InlineKeyboardMarkup(keys)
    msg = mulent["question"]
    last_message[user_id] = last_message[user_id].reply_text(msg, reply_markup = markup, parse_mode='HTML')
    st[user_id] = "mulbet1"

def handle_mulent_key(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    user_id = user.id
    add_user(user)
    query = update.callback_query
    try:
        if(query.message.message_id != last_message[user_id].message_id):
            return
    except:
        return
    if st[user_id] != "mulbet1":
        return
    mulent_id = int(query.data[query.data.find(' ') + 1 : query.data.find('-')])
    x = int(query.data[query.data.find('-') + 1:])
    mulent = db.mulents.find_one({"mulent_id": mulent_id})
    bot = context.bot
    last_message[user_id] = bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = mulent["question"] + "\n\n" + mulent["choices"][str(x)]
    )
    if mulent["is_over"]:
        last_message[user_id] = last_message[user_id].reply_text("مهلت بت به پایان رسیده.")
        st[user_id] = "main"
        return
    db.add_mulbet(Mulbet(user, mulent_id, query.message.date, x))
    last_message[user_id] = last_message[user_id].reply_text('پیش بینی شما با موفقیت ثبت شد.')
    st[user_id] = "main"

def handle_skip_key(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    user_id = user.id
    add_user(user)
    query = update.callback_query
    try:
        if(query.message.message_id != last_message[user_id].message_id):
            return
    except:
        return
    bot = context.bot
    if query.data == "skip_fact":
        if(st[user_id] != "bet3"):
            return
        msg = ""
        user_bet[user_id].facts = msg
        user_bet[user_id].time = query.message.date
        if user_bet[user_id].time > datetime.datetime.strptime(user_bet[user_id].game_time, '%Y-%m-%d %H:%M:%S%z'):
            last_message[user_id] = bot.send_message(
                chat_id = query.message.chat_id,
                text = "بعد شروع بازي حق پيش بيني نداريد."
            )
            last_message[user_id] = bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text = "فکت: "
            )
            st[user_id] = "main"
            return
        db.add_bet(user_bet[user_id])
        last_message[user_id] = bot.send_message(
            chat_id = query.message.chat_id,
            text = "پیش بینی شما ذخیره شد."
        )
        last_message[user_id] = bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text = "فکت: "
        )
        st[user_id] = "main"
        return

def handle_settings_key(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    user_id = user.id
    add_user(user)
    query = update.callback_query
    try:
        if(query.message.message_id != last_message[user_id].message_id):
            return
    except:
        return
    bot = context.bot
    if query.data == "settings_notif":
        keys = []
        user_notif = db.users.find_one({"tg_user.id": user_id})["notif"]
        notif_emojis = ["❌", "✅"]
        keys.append([
                    InlineKeyboardButton(text = "اطلاعیه اضافه شدن بازی", callback_data = "ignore"),
                    InlineKeyboardButton(text = notif_emojis[user_notif["1"]], callback_data = "notif_1")
                    ])
        keys.append([
                    InlineKeyboardButton(text = "اطلاعیه بلند قبل بازی", callback_data = "ignore"),
                    InlineKeyboardButton(text = notif_emojis[user_notif["2"]], callback_data = "notif_2")
                    ])
        keys.append([
                    InlineKeyboardButton(text = "اطلاعیه کوتاه قبل بازی", callback_data = "ignore"),
                    InlineKeyboardButton(text = notif_emojis[user_notif["3"]], callback_data = "notif_3")
                    ])
        keys.append([
                    InlineKeyboardButton(text = "اطلاعیه شروع شدن بازی", callback_data = "ignore"),
                    InlineKeyboardButton(text = notif_emojis[user_notif["4"]], callback_data = "notif_4")
                    ])
        markup = InlineKeyboardMarkup(keys)
        last_message[user_id] = bot.edit_message_text(
            chat_id = query.message.chat_id,
            message_id = query.message.message_id,
            text = "تنظیمات نوتیفیکیشن", 
            reply_markup = markup, parse_mode='HTML'
        )

def handle_notif_key(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    user_id = user.id
    add_user(user)
    query = update.callback_query
    try:
        if(query.message.message_id != last_message[user_id].message_id):
            return
    except:
        return
    bot = context.bot
    notif_index = query.data[6:]
    user_notif = db.users.find_one({"tg_user.id": user_id})["notif"]
    db.users.update_one(
        filter = {"tg_user.id": user_id},
        update = {"$set": {"notif." + notif_index: 1 - user_notif[notif_index]}}
    )
    keys = []
    user_notif = db.users.find_one({"tg_user.id": user_id})["notif"]
    notif_emojis = ["❌", "✅"]
    keys.append([
                InlineKeyboardButton(text = "اطلاعیه اضافه شدن بازی", callback_data = "ignore"),
                InlineKeyboardButton(text = notif_emojis[user_notif["1"]], callback_data = "notif_1")
                ])
    keys.append([
                InlineKeyboardButton(text = "اطلاعیه بلند قبل بازی", callback_data = "ignore"),
                InlineKeyboardButton(text = notif_emojis[user_notif["2"]], callback_data = "notif_2")
                ])
    keys.append([
                InlineKeyboardButton(text = "اطلاعیه کوتاه قبل بازی", callback_data = "ignore"),
                InlineKeyboardButton(text = notif_emojis[user_notif["3"]], callback_data = "notif_3")
                ])
    keys.append([
                InlineKeyboardButton(text = "اطلاعیه شروع شدن بازی", callback_data = "ignore"),
                InlineKeyboardButton(text = notif_emojis[user_notif["4"]], callback_data = "notif_4")
                ])
    markup = InlineKeyboardMarkup(keys)
    last_message[user_id] = bot.edit_message_text(
        chat_id = query.message.chat_id,
        message_id = query.message.message_id,
        text = "تنظیمات نوتیفیکیشن", 
        reply_markup = markup, parse_mode='HTML'
    )

def add_admin(update: Update, context: CallbackContext):
    user_id = update.message.chat.id

    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return
    
    db.users.update_one(
        filter = {"tg_user.id": int(context.args[0])},
        update = {"$set": {"is_admin": 1}}
    )
    return

def add_game(update: Update, context: CallbackContext):
    user_id = update.message.chat.id

    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return
    
    add_teams[user_id] = []
    last_message[user_id] = update.message.reply_text("نام تیم اول:")
    st[user_id] = "add0"
def remove_game(update: Update, context: CallbackContext):
    user_id = update.message.chat.id

    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return
    if st[user_id] != "main":
        last_message[user_id] = update.message.reply_text("شما در استیت درست قرار ندارید.")
        return
    if db.count_active_games() == 0:
        last_message[user_id] = update.message.reply_text("در حال حاضر بازی ای برای پیش بینی وجود ندارد.")
        return

    keys = []
    i = 0
    games = db.get_active_games()
    for game in games:
        keys.append([InlineKeyboardButton(text = game["first_team"]["name"] + ' - ' + game["second_team"]["name"],
                                            callback_data = "choose_game remove " + str(game["game_id"]))])
    markup = InlineKeyboardMarkup(keys)
    msg = "کدوم بازی"
    last_message[user_id] = update.message.reply_text(msg, reply_markup = markup, parse_mode='HTML')
    st[user_id] = "remove_game"
def remove_mulent(update: Update, context: CallbackContext):
    user_id = update.message.chat.id

    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return
    
    if len(context.args) < 1:
        last_message[user_id] = update.message.reply_text('اندیس ندادی')
        return
    try:
        shomare_mulent = int(context.args[0])
    except:
        return
    if not(0 <= shomare_mulent < db.count_active_mulents()):
        last_message[user_id] = update.message.reply_text('اندیس خراب')
        return
    mulents = db.get_active_mulents()
    db.deactivate_mulent(mulents[shomare_mulent]["mulent_id"])
    last_message[user_id] = update.message.reply_text("موفقیت")
def end_game(update: Update, context: CallbackContext):
    user_id = update.message.chat.id
    
    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return
    
    if len(context.args) < 3:
        return
    games = db.get_active_games()
    try:
        game = games[int(context.args[0])]
        first_score = int(context.args[1])
        second_score = int(context.args[2])
    except:
        return
    game_id = game["game_id"]
    msg = game["first_team"]["name"] + " - " + game["second_team"]["name"] + " winners : " + "\n"
    for bt in db.get_game_bets(game_id):
        if int(bt["first_score"]) != first_score or int(bt["second_score"]) != second_score:
            continue
        db.users.update_one(
            filter = {"tg_user.id": bt["user"]["id"]},
            update = { "$inc": {
                "score" : 1
            }},
            upsert = True
        )
        last_message[user_id] = context.bot.send_message(
            chat_id = bt["user"]["id"],
            text = "!تبریک" + "\n" + "شما نتیجه بازی " + game["first_team"]["name"] + " - " + game["second_team"]["name"] + " را درست حدس زدید." + "\n\n" +
                    "امتیاز شما: " + str(db.get_user_game_score(bt["user"]["id"]))
        )
        msg += "<a href=\"tg://user?id=" + str(bt["user"]["id"]) + "\">" + bt["user"]["first_name"] + "</a>  \n"
    msg += "\n"
    last_message[user_id] = update.message.reply_text(msg, parse_mode="HTML")
    db.games.update_one(
        filter={"game_id": game_id},
        update={"$set": {
            "is_over": 1,
            "first_score": first_score, "second_score": second_score
        }},
        upsert=True
    )

def end_mulent(update: Update, context: CallbackContext):
    user_id = update.message.chat.id
    
    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return
    
    if len(context.args) != 2:
        return
    mulents = db.get_active_mulents()
    try:
        mulent = mulents[int(context.args[0])]
        correct_choice = int(context.args[1])
    except:
        return
    mulent_id = mulent["mulent_id"]
    msg = mulent["title"] + " winners : " + "\n"
    for bt in db.get_mulent_bets(mulent_id):
        if int(bt["choice"]) != correct_choice:
            continue
        db.users.update_one(
            filter = {"tg_user.id": bt["user"]["id"]},
            update = { "$inc": {
                "mulent_score" : 1
            }},
            upsert = True
        )
        last_message[user_id] = context.bot.send_message(
            chat_id = bt["user"]["id"],
            text = "!تبریک" + "\n" + "جواب سوال " + mulent["title"] + "را درست حدس زدید" + "\n\n" +
                    "امتیاز شما در بخش سوال های چند گزینه ای: " + str(db.get_user_mulent_score(bt["user"]["id"]))
        )
        msg += "<a href=\"tg://user?id=" + str(bt["user"]["id"]) + "\">" + bt["user"]["first_name"] + "</a>  \n"
    msg += "\n"
    last_message[user_id] = update.message.reply_text(msg, parse_mode="HTML")
    db.mulents.update_one(
        filter={"game_id": mulent_id},
        update={"$set": {
            "is_over": 1,
            "correct_choice": correct_choice
        }},
        upsert=True
    )

def user_ranking(update: Update, context: CallbackContext):

    user = update.message.from_user
    user_id = user.id
    add_user(user)

    cnt = 10
    try:
        cnt = int(context.args[0])
    except:
        pass
    a = []
    for user in db.users.find({}):
        a.append([user["score"], user["tg_user"]["id"], user["tg_user"]["first_name"]])
    a.sort(); a.reverse()
    cnt = min(cnt, len(a))
    msg = "Top " + str(cnt) + ": " + "\n"
    for i in range(cnt):
        msg += "  <a href=\"tg://user?id=" + str(a[i][1]) + "\">" + str(a[i][2]) + "</a>  " + str(a[i][0]) + "\n"
    last_message[user_id] = update.message.reply_text(msg, parse_mode = "HTML")

def prnt(update: Update, context: CallbackContext):
    user_id = update.message.chat.id

    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return
    
    games = db.get_active_games()
    if len(context.args) > 0:
        game = games[int(context.args[0])]
        for ii in context.args[1:]:
            i = int(ii)
            bt = db.get_game_bets(game["game_id"])[i]
            msg = " <a href=\"tg://user?id=" + str(bt["user"]["id"]) + "\">" + bt["user"]["first_name"] + "</a>  " + str(bt["first_score"]) + " - " + str(bt["second_score"]) + "\n"
            msg += str(bt["facts"]) + "\n"
            msg += str(bt["time"]) + "\n"
            last_message[user_id] = update.message.reply_text(msg, parse_mode="HTML")
        return
    msg = "Bets\n"
    i = 0
    for game in games:
        msg += str(i) + ": " + game["first_team"]["name"] + " - " + game["second_team"]["name"] + "\n"
        j = 0
        for bt in db.get_game_bets(game["game_id"]):
            msg += "   " + str(j) + ": <a href=\"tg://user?id=" + str(bt["user"]["id"]) + "\">" + bt["user"]["first_name"] + "</a>  " + str(bt["first_score"]) + " - " + str(bt["second_score"]) + "\n"
            j += 1
        msg += "\n"
        i += 1
    last_message[user_id] = update.message.reply_text(msg, parse_mode="HTML")
def announce(update: Update, context: CallbackContext):
    user_id = update.message.chat.id

    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return
    
    if "all" in context.args:
        st[user_id] = "announce_all"
    else:
        st[user_id] = "announce_1"
    last_message[user_id] = update.message.reply_text(":متن اطلاعیه")
    return
def remind_game(update: Update, context: CallbackContext):
    user_id = update.message.chat.id

    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return

    try:
        x = int(context.args[0])
    except:
        return
    
    game = db.get_active_games()[x]
    db.games.update_one(
        filter={"game_id": game["game_id"]},
        update={"$set": {
            "remind": 1
        }}
    )
    bot = context.bot

    last_message[user_id] = bot.send_message(chat_id=user_id, text='Remind ' + game["first_team"]["name"] + ' - ' + game["second_team"]["name"])
    
    first_rem = 6 * 60 * 60
    second_rem = 15 * 60
    timestamp = datetime.datetime.strptime('1970-01-01 00:00:00+00:00', '%Y-%m-%d %H:%M:%S%z')
    y = (datetime.datetime.strptime(game['time'], '%Y-%m-%d %H:%M:%S%z') - timestamp).total_seconds()
    now = int(time.time())
    if y - now - first_rem > 0:
        time.sleep(y - now - first_rem)
        cnt_mellat = 0
        for mellat in db.users.find({"notif.2" : 1}):
            try:
                chat_id = mellat["tg_user"]["id"]
                last_message[chat_id] = bot.send_message(
                    chat_id = chat_id,
                    text = game["first_team"]["name"] + ' - ' + game["second_team"]["name"] + '\n' + "تنها ۶ ساعت تا شروع بازی" + "\n\n" + "برای اطلاعات بیشتر از دستور" + " /matches " + "و برای غیر فعال کردن اطلاعیه ها از دستور" + " /settings " + "استفاده کنید."
                )
                cnt_mellat += 1
            except:
                pass
        for mellat in db.users.find({"is_admin": 1}):
            chat_id = mellat["tg_user"]["id"]
            last_message[chat_id] = bot.send_message(
                chat_id = chat_id,
                text = "به " + str(cnt_mellat) + " نفر فرستادم"
            )
    now = int(time.time())
    if y - now - second_rem > 0:
        time.sleep(y - now - second_rem)
        cnt_mellat = 0
        for mellat in db.users.find({"notif.3" : 1}):
            try:
                chat_id = mellat["tg_user"]["id"]
                last_message[chat_id] = bot.send_message(
                    chat_id = chat_id,
                    text = game["first_team"]["name"] + ' - ' + game["second_team"]["name"] + '\n' + "تنها یک ربع تا شروع بازی" + "\n\n" + "برای اطلاعات بیشتر از دستور" + " /matches " + "و برای غیر فعال کردن اطلاعیه ها از دستور" + " /settings " + "استفاده کنید."
                )
                cnt_mellat += 1
            except:
                pass
        for mellat in db.users.find({"is_admin": 1}):
            chat_id = mellat["tg_user"]["id"]
            last_message[chat_id] = bot.send_message(
                chat_id = chat_id,
                text = "به " + str(cnt_mellat) + " نفر فرستادم"
            )
    now = int(time.time())
    if y - now > 0:
        time.sleep(y - now)
        cnt_mellat = 0
        for mellat in db.users.find({"notif.4" : 1}):
            try:
                chat_id = mellat["tg_user"]["id"]
                last_message[chat_id] = bot.send_message(
                    chat_id = chat_id,
                    text = game["first_team"]["name"] + ' - ' + game["second_team"]["name"] + '\n' + "بازی شروع شد!" + "\n\n" + "برای اطلاعات بیشتر از دستور" + " /matches " + "و برای غیر فعال کردن اطلاعیه ها از دستور" + " /settings " + "استفاده کنید."
                )
                cnt_mellat += 1
            except:
                pass
        for mellat in db.users.find({"is_admin": 1}):
            chat_id = mellat["tg_user"]["id"]
            last_message[chat_id] = bot.send_message(
                chat_id = chat_id,
                text = "به " + str(cnt_mellat) + " نفر فرستادم"
            )
def add_mulent(update: Update, context: CallbackContext):
    user_id = update.message.chat.id

    if db.users.count_documents({"tg_user.id": user_id, "is_admin": 1}) == 0:
        return
    
    if st[user_id] != "main":
        last_message[user_id] = update.message.reply_text("شما در استیت درست قرار ندارید.")
        return
    
    mulvec[user_id] = []

    st[user_id] = "mulent_0"
    last_message[user_id] = update.message.reply_text("Title:")

    return
    

dp = updater.dispatcher

for mellat in db.users.find({"is_admin": 1}):
    chat_id = mellat["tg_user"]["id"]
    last_message[chat_id] = dp.bot.send_message(
        chat_id = chat_id,
        text = "روشن شدم"
    )

gi = -1
for game in db.get_active_games():
    gi += 1
    try:
        if game["remind"] != 1:
            continue
    except:
        continue
    cbc = CallbackContext(dp)
    cbc.args = [str(gi)]
    update = Update(message=telegram.Message(chat=Chat(id=1203400559, type="private"), message_id=1, date=datetime.datetime(2021, 9, 3, 0, 0, 0)), update_id=67974905)
    dp.run_async(remind_game, update, cbc, update=update)


dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("matches", matches))
dp.add_handler(CommandHandler("bet", bet))
dp.add_handler(CommandHandler("other_bets", mulbet))
dp.add_handler(CommandHandler("cancel", cancel))
dp.add_handler(CommandHandler("add_admin", add_admin))
dp.add_handler(CommandHandler("add_game", add_game))
dp.add_handler(CommandHandler("remove_game", remove_game))
dp.add_handler(CommandHandler("remove_mulent", remove_mulent))
dp.add_handler(CommandHandler("end_game", end_game))
dp.add_handler(CommandHandler("end_mulent", end_mulent))
dp.add_handler(CommandHandler("my_score", user_game_score))
dp.add_handler(CommandHandler("ranking", user_ranking))
dp.add_handler(CommandHandler("settings", settings))
dp.add_handler(CommandHandler("print", prnt))
dp.add_handler(CommandHandler("announce", announce))
dp.add_handler(CommandHandler("add_mulent", add_mulent))
dp.add_handler(CommandHandler("remind_game", remind_game, run_async = True))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command & ~Filters.update.edited_message, handle))
dp.add_handler(CallbackQueryHandler(handle_choose_game_key, pattern = "^choose_game"))
dp.add_handler(CallbackQueryHandler(handle_mulbet_key, pattern = "^mulbet"))
dp.add_handler(CallbackQueryHandler(handle_mulent_key, pattern = "^mulent"))
dp.add_handler(CallbackQueryHandler(handle_skip_key, pattern = "^skip"))
dp.add_handler(CallbackQueryHandler(handle_settings_key, pattern = "^settings"))
dp.add_handler(CallbackQueryHandler(handle_notif_key, pattern = "^notif"))



updater.start_polling()

updater.idle()
