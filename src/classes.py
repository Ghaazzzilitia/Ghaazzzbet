from pymongo.read_preferences import _ALL_READ_PREFERENCES


class Team:
    def __init__(self, team_id, name):
        self.team_id = team_id
        self.name = name
class Bet:
    def __init__(self, user, game_id, first_team, second_team, game_time):
        self.user = user
        self.game_id = game_id
        self.first_team = first_team
        self.second_team = second_team
        self.game_time = game_time
class Mulent:
    def __init__(self, mulent_id, title, question, choices, time):
        self.mulent_id = mulent_id
        self.title = title
        self.question = question
        self.choices = choices
        self.time = time
class Mulbet:
    def __init__(self, user, mulent_id, time, choice):
        self.user = user
        self.mulent_id = mulent_id
        self.time = time
        self.choice = choice
class Game:
    def __init__(self, game_id, first_team, second_team, time, time_msg, tr_name):
        self.game_id = game_id
        self.first_team = first_team
        self.second_team = second_team
        self.time = time
        self.time_msg = time_msg
        self.tr_name = tr_name
        self.is_active = 1
