import logging

import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import datetime

from database import Database

from classes import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

token = os.getenv("token")

db_url = os.getenv("db_url")
db = Database(db_url=db_url)

updater = Updater(token, use_context=True)


st = {}
bet_message = {}
#games = [] #to database
user_bet = {}
add_teams = []

admins = list(map(int, os.getenv("admins").split(":")))

def add_user(user):
    user_id = user.id
    db.register_user(user)
    try:
        st[user_id]
        return 0
    except:
        st[user_id] = "main"
        return 1

def start(update, context):
    user = update.message.from_user
    user_id = user.id
    if add_user(user):
        update.message.reply_text("سلام به بات شرط بندی غاززز خوش اومدید.")
    else:
        update.message.reply_text("سلامی دوباره")
    st[user_id] = "main"

def matches(update, context):
    user = update.message.from_user
    user_id = user.id
    add_user(user)
    if st[user_id] != "main":
        update.message.reply_text("شما در استیت درست قرار ندارید.")
        return
    if db.count_active_games() == 0:
        update.message.reply_text("در حال حاضر بازی ای برای شرط بندی وجود ندارد.")
        return
    games = db.get_active_games()
    msg = ""
    for game in games:
        msg += game["first_team"]["name"] + ' - ' + game["second_team"]["name"] + '\n' + "شروع بازی: " + game["time_msg"] + "\n" + "تورنومنت: " + game["tr_name"] + "\n"
        if (game["is_over"]):
            msg += "نتیحه نهایی: " + str(game["first_score"]) + ' - ' + str(game["second_score"]) + "\n"
        msg += "\n"
    update.message.reply_text(msg, parse_mode = "HTML")
    return

def bet(update, context):
    user = update.message.from_user
    user_id = user.id
    add_user(user)
    if st[user_id] != "main":
        update.message.reply_text("شما در استیت درست قرار ندارید.")
        return
    if db.count_active_games() == 0:
        update.message.reply_text("در حال حاضر بازی ای برای شرط بندی وجود ندارد.")
        return

    keys = []
    i = 0
    games = db.get_active_games()
    for game in games:
        keys.append([InlineKeyboardButton(text = game["first_team"]["name"] + ' - ' + game["second_team"]["name"],
                                            callback_data = "bet " + str(game["game_id"]))])
    markup = InlineKeyboardMarkup(keys)
    msg = "کدوم بت"
    bet_message[user_id] = update.message.reply_text(msg, reply_markup = markup, parse_mode='HTML')
    st[user_id] = "bet0"
def cancel(update, context):
    user = update.message.from_user
    user_id = user.id
    add_user(user)

    update.message.reply_text("شما در استیت مین قرار دارید.")
    st[user_id] = "main"
def handle(update, context):
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
        update.message.reply_text("تعداد گل " + user_bet[user_id].second_team + " : ")
        return
    if st[user_id] == "bet2":
        msg = update.message.text
        try:
            x = int(msg)
        except:
            return
        user_bet[user_id].second_score = x
        st[user_id] = "bet3"
        update.message.reply_text("فکت : ", reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = "Skip", callback_data = "skip_fact")]]))
        return
    if st[user_id] == "bet3":
        msg = update.message.text
        user_bet[user_id].facts = msg
        user_bet[user_id].time = update.message.date
        if user_bet[user_id].time > datetime.datetime.strptime(user_bet[user_id].game_time, '%Y-%m-%d %H:%M:%S%z'):
            update.message.reply_text("بعد شروع بازي حق پيش بيني نداريد.")
            st[user_id] = "main"
            return
        db.add_bet(user_bet[user_id])
        #user_bet[user_id].game.bets[user_id] = user_bet[user_id]
        update.message.reply_text("پیش بینی شما ذخیره شد.")
        st[user_id] = "main"
        return
    if st[user_id] == "add0":
        team_name = update.message.text
        team_id = db.next_team_id()
        db.add_team(Team(team_id, team_name))
        add_teams.append(Team(team_id, team_name))
        update.message.reply_text("نام تیم دوم:")
        st[user_id] = "add1"
        return
    if st[user_id] == "add1":
        team_name = update.message.text
        team_id = db.next_team_id()
        db.add_team(Team(team_id, team_name))
        add_teams.append(Team(team_id, team_name))
        update.message.reply_text("Time\nYYYY-MM-DD HH:MM:SS+04:30", parse_mode="HTML")
        st[user_id] = "add2"
        return
    if st[user_id] == "add2":
        time = update.message.text
        add_teams.append(time)
        update.message.reply_text("متن الکی تایم")
        st[user_id] = "add3"
        return
    if st[user_id] == "add3":
        time = update.message.text
        add_teams.append(time)
        update.message.reply_text("tournoment :")
        st[user_id] = "add4"
        return
    if st[user_id] == "add4":
        tr_name = update.message.text
        game_id = db.next_game_id()
        db.add_game(Game(game_id, add_teams[0], add_teams[1], add_teams[2], add_teams[3], tr_name))
        update.message.reply_text("بازی افزوده شد.")
        add_teams.clear()
        st[user_id] = "main"
        return

def handle_bet_key(update, context):
    user = update.callback_query.from_user
    user_id = user.id
    add_user(user)
    query = update.callback_query
    try:
        if(query.message.message_id != bet_message[user_id].message_id):
            return
    except:
        return
    if st[user_id] != "bet0":
        return
    x = int(query.data[4:])
    game = db.games.find_one({"game_id": x})
    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = game["first_team"]["name"] + ' - ' + game["second_team"]["name"] + '\n' + "شروع بازی: " + game["time_msg"] + '\n' + "تورنومنت: " + game["tr_name"]
    )
    user_bet[user_id] = Bet(user, game["game_id"], game["first_team"]["name"], game["second_team"]["name"], game["time"])
    st[user_id] = "bet1"
    if game["is_over"]:
        bet_message[user_id].reply_text("بازی به پایان رسیده.")
        bet_message[user_id].reply_text(game["first_team"]["name"] + " " + str(game["first_score"]) +
        " - " + str(game["second_score"]) + " " + game["second_team"]["name"])
        st[user_id] = "main"
        return
    if db.bets.count({"game_id": game["game_id"], "user_id": user_id}):
        bet_message[user_id].reply_text("شما قبلا پیش بینی کرده اید.")
        bet = db.bets.find_one({"game_id": game["game_id"], "user_id": user_id})
        bet_message[user_id].reply_text(game["first_team"]["name"] + " " + str(bet["first_score"]) +
        " - " + str(bet["second_score"]) + " " + game["second_team"]["name"])
        st[user_id] = "main"
        return
    bet_message[user_id].reply_text("تعداد گل " + user_bet[user_id].first_team + " : ")

def handle_skip_key(update, context):
    user = update.callback_query.from_user
    user_id = user.id
    add_user(user)
    query = update.callback_query
    bot = context.bot
    if query.data == "skip_fact":
        if(st[user_id] != "bet3"):
            return
        msg = ""
        user_bet[user_id].facts = msg
        user_bet[user_id].time = query.message.date
        if user_bet[user_id].time > datetime.datetime.strptime(user_bet[user_id].game_time, '%Y-%m-%d %H:%M:%S%z'):
            bot.send_message(
                chat_id = query.message.chat_id,
                text = "بعد شروع بازي حق پيش بيني نداريد."
            )
            bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text = "فکت: "
            )
            st[user_id] = "main"
            return
        db.add_bet(user_bet[user_id])
        #user_bet[user_id].game.bets[user_id] = user_bet[user_id]
        bot.send_message(
            chat_id = query.message.chat_id,
            text = "پیش بینی شما ذخیره شد."
        )
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text = "فکت: "
        )
        st[user_id] = "main"
        return

def add_admin(update, context):
    user_id = update.message.chat.id
    global admins

    if not user_id in admins:
        return
    admins += [context.args[0]]
def add_game(update, context):
    user_id = update.message.chat.id
    global admins

    if not user_id in admins:
        return
    update.message.reply_text("نام تیم اول:")
    st[user_id] = "add0"
def remove_game(update, context):
    user_id = update.message.chat.id
    global admins

    if not user_id in admins:
        return
    if len(context.args) < 1:
        return
    try:
        shomare_bazi = int(context.args[0])
    except:
        return
    # arze dick
    # dicke arz
    games = db.get_active_games()
    db.deactivate_game(games[shomare_bazi]["game_id"])
def end_game(update, context):
    user_id = update.message.chat.id
    global admins

    if not user_id in admins:
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
        msg += "<a href=\"tg://user?id=" + str(bt["user"]["id"]) + "\">" + bt["user"]["first_name"] + "</a>  \n"
    msg += "\n"
    update.message.reply_text(msg, parse_mode="HTML")
    db.games.update_one(
        filter={"game_id": game_id},
        update={"$set": {
            "is_over": 1,
            "first_score": first_score, "second_score": second_score
        }},
        upsert=True
    )
def user_ranking(update, context):
    cnt = 10
    if 0 < len(context.args) and type(context.args[0]) == int:
        cnt = int(context.args[0])
    a = []
    for user in db.users.find({}):
        a.append([user["score"], user["tg_user"]["id"], user["tg_user"]["first_name"]])
    a.sort(); a.reverse()
    cnt = min(cnt, len(a))
    msg = "Top " + str(cnt) + ": " + "\n"
    for i in range(cnt):
        msg += "  <a href=\"tg://user?id=" + str(a[i][1]) + "\">" + str(a[i][2]) + "</a>  " + str(a[i][0]) + "\n"
    update.message.reply_text(msg, parse_mode = "HTML")
def prnt(update, context):
    user_id = update.message.chat.id
    global admins

    if not user_id in admins:
        return
    games = db.get_active_games()
    if len(context.args) > 0:
        game = games[int(context.args[0])]
        for ii in context.args[1:]:
            i = int(ii)
            bt = db.get_game_bets(game["game_id"])[i]
            msg = " <a href=\"tg://user?id=" + str(bt["user"]["id"]) + "\">" + bt["user"]["first_name"] + "</a>  " + str(bt["first_score"]) + " - " + str(bt["second_score"]) + "\n"
            msg += bt["facts"] + "\n"
            msg += str(bt["time"]) + "\n"
            update.message.reply_text(msg, parse_mode="HTML")
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
    update.message.reply_text(msg, parse_mode="HTML")




dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("matches", matches))
dp.add_handler(CommandHandler("bet", bet))
dp.add_handler(CommandHandler("cancel", cancel))
dp.add_handler(CommandHandler("add_admin", add_admin))
dp.add_handler(CommandHandler("add_game", add_game))
dp.add_handler(CommandHandler("remove_game", remove_game))
dp.add_handler(CommandHandler("end_game", end_game))
dp.add_handler(CommandHandler("ranking", user_ranking))
dp.add_handler(CommandHandler("print", prnt))
dp.add_handler(MessageHandler(Filters.all & ~Filters.command, handle))
dp.add_handler(CallbackQueryHandler(handle_bet_key, pattern = "^bet"))
dp.add_handler(CallbackQueryHandler(handle_skip_key, pattern = "^skip"))


updater.start_polling()

updater.idle()
