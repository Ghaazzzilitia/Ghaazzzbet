import logging 
from typing import Optional


from pymongo import MongoClient
from pymongo.collection import Collection
from telegram import User
from classes import *

logger = logging.getLogger('database')

import datetime

class Database:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.users: Collection = self.client.ghaazzzbot.users
        self.teams: Collection = self.client.ghaazzzbot.teams
        self.games: Collection = self.client.ghaazzzbot.games
        self.bets:  Collection = self.client.ghaazzzbot.bets
        self.mulbets:  Collection = self.client.ghaazzzbot.mulbets
        self.vars: Collection = self.client.ghaazzzbot.variables
        self.mulents: Collection = self.client.ghaazzzbot.mulent

    def register_user(self, tg_user: User) -> None:
        if self.users.count_documents({"tg_user.id": tg_user.id}):
            self.users.update_one(
                filter={"tg_user.id": tg_user.id},
                update={"$set": {
                    "tg_user": {"id": tg_user.id, "first_name": tg_user.first_name, "last_name": tg_user.last_name},
                }},
                upsert=True
            )
            return
        self.users.update_one(
            filter={"tg_user.id": tg_user.id},
            update={"$set": {
                "tg_user": {"id": tg_user.id, "first_name": tg_user.first_name, "last_name": tg_user.last_name},
                "score": 0, "mulent_score": 0,
                "notif": {"1": 1, "2": 1, "3": 1, "4": 1}
            }},
            upsert=True
        )
    def add_team(self, team: Team):
        self.teams.update_one(
            filter={"team_id": team.team_id},
            update={"$set": {
                "team_id": team.team_id, "name": team.name,
            }},
            upsert=True
        )
    def next_team_id(self):
        x = self.vars.find_one({})["next_team_id"]
        self.vars.update_one(
            filter = {},
            update={"$set": {
                "var_name": "next_team_id", "next_team_id": x + 1,
            }},
            upsert=True
        )
        return x
    def next_game_id(self):
        x = self.vars.find_one({})["next_game_id"]
        self.vars.update_one(
            filter = {},
            update={"$set": {
                "var_name": "next_game_id", "next_game_id": x + 1,
            }},
            upsert=True
        )
        return x
    def next_bet_id(self):
        x = self.vars.find_one({})["next_bet_id"]
        self.vars.update_one(
            filter = {},
            update={"$set": {
                "var_name": "next_bet_id", "next_bet_id": x + 1,
            }},
            upsert=True
        )
        return x
    def next_mulent_id(self):
        x = self.vars.find_one({})["next_mulent_id"]
        self.vars.update_one(
            filter = {},
            update={"$set": {
                "var_name": "next_mulent_id", "next_mulent_id": x + 1,
            }},
            upsert=True
        )
        return x
    def add_game(self, game: Game):
        self.games.update_one(
            filter={"game_id": game.game_id},
            update={"$set": {
                "game_id": game.game_id,
                "first_team": {"team_id": game.first_team.team_id, "name": game.first_team.name},
                "second_team": {"team_id": game.second_team.team_id, "name": game.second_team.name},
                "time_msg": game.time_msg, "time": game.time, "tr_name": game.tr_name,
                 "is_active": game.is_active, "is_over": 0
            }},
            upsert=True
        )
    def deactivate_game(self, game_id):
        self.games.update_one(
            filter={"game_id": game_id},
            update={"$set": {
                "is_active": 0
            }},
            upsert=True
        )
    def deactivate_mulent(self, mulent_id):
        self.mulents.update_one(
            filter={"mulent_id": mulent_id},
            update={"$set": {
                "is_active": 0
            }},
            upsert=True
        )
    def add_bet(self, bet: Bet):
        x = self.next_bet_id()
        self.bets.insert_one({
            "bet_id": x,
            "game_id": bet.game_id,
            "user": {"id": bet.user.id, "first_name": bet.user.first_name, "last_name": bet.user.last_name},
            "first_score": bet.first_score,
            "second_score": bet.second_score,
            "time": str(bet.time),
            "facts": bet.facts
        })
    def add_mulbet(self, mulbet: Mulbet):
        x = self.next_mulent_id()
        self.mulbets.insert_one({
            "mulent_id": mulbet.mulent_id,
            "mulbet_id": x,
            "user": {"id": mulbet.user.id, "first_name": mulbet.user.first_name, "last_name": mulbet.user.last_name},
            "time": str(mulbet.time),
            "choice": mulbet.choice,
        })
    def get_user_game_score(self, user_id: int):
        return self.users.find_one({"tg_user.id": user_id})["score"]
    def get_user_mulent_score(self, user_id: int):
        return self.users.find_one({"tg_user.id": user_id})["mulent_score"]
    def get_game_bets(self, game_id):
        return self.bets.find({"game_id": game_id})
    def get_mulent_bets(self, mulent_id):
        return self.mulbets.find({"mulent_id": mulent_id})
    def count_active_games(self):
        return self.games.count({"is_active": 1})
    def get_active_games(self):
        a = []
        i = 0
        games = self.games.find({"is_active": 1})
        for game in games:
            a.append([datetime.datetime.strptime(game["time"], '%Y-%m-%d %H:%M:%S%z'), i, game])
            i += 1
        a.sort()
        games = []
        for j in range(len(a)):
            games.append(a[j][2])
        return games
    def count_active_mulents(self):
        return self.mulents.count({"is_active": 1})
    def get_active_mulents(self):
        a = []
        i = 0
        mulents = self.mulents.find({"is_active": 1})
        for mulent in mulents:
            a.append([datetime.datetime.strptime(mulent["time"], '%Y-%m-%d %H:%M:%S%z'), i, mulent])
            i += 1
        a.sort()
        mulents = []
        for j in range(len(a)):
            mulents.append(a[j][2])
        return mulents
    def add_mul(self, mul_vec):
        mul_id = self.next_mulent_id()
        choices = {}
        i = 0
        for s in mul_vec[3:]:
            choices[str(i)] = s
            i += 1
        mul_doc = {
            "mulent_id": mul_id, "title": mul_vec[0], "question": mul_vec[1],
            "time": mul_vec[2], "choices": choices, "choice_cnt": len(choices),
            "is_active": 1, "is_over": 0
        }
        self.mulents.insert_one(mul_doc)
    def close(self):
        self.client.close()
        logger.info('client closed')
