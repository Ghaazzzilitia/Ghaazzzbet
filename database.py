import logging
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from telegram import User
from classes import Team, Game, Bet

logger = logging.getLogger('database')



class Database:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.users: Collection = self.client.ghaazzzbot.users
        self.teams: Collection = self.client.ghaazzzbot.teams
        self.games: Collection = self.client.ghaazzzbot.games
        self.bets:  Collection = self.client.ghaazzzbot.bets
        self.vars: Collection = self.client.ghaazzzbot.variables

    def register_user(self, tg_user: User) -> None:
        self.users.update_one(
            filter={"tg_user.id": tg_user.id},
            update={"$set": {
                "tg_user": {"id": tg_user.id, "first_name": tg_user.first_name, "last_name": tg_user.last_name},
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
        x = self.vars.find_one({"var_name": "next_team_id"})["next_team_id"]
        self.vars.update_one(
            filter = {"var_name": "next_team_id"},
            update={"$set": {
                "var_name": "next_team_id", "next_team_id": x + 1,
            }},
            upsert=True
        )
        return x
    def next_game_id(self):
        x = self.vars.find_one({"var_name": "next_game_id"})["next_game_id"]
        self.vars.update_one(
            filter = {"var_name": "next_game_id"},
            update={"$set": {
                "var_name": "next_game_id", "next_game_id": x + 1,
            }},
            upsert=True
        )
        return x
    def next_bet_id(self):
        x = self.vars.find_one({"var_name": "next_bet_id"})["next_bet_id"]
        self.vars.update_one(
            filter = {"var_name": "next_bet_id"},
            update={"$set": {
                "var_name": "next_bet_id", "next_bet_id": x + 1,
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
                "time": game.time, "tr_name": game.tr_name, "is_active": game.is_active
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
    def get_game_bets(self, game_id):
        return self.bets.find({"game_id": game_id})
    def get_active_games(self):
        return self.games.find({"is_active": 1})
    def count_active_games(self):
        return self.games.count({"is_active": 1})
    def close(self):
        self.client.close()
        logger.info('client closed')
