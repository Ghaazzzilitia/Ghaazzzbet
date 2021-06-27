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
class Game:
    def __init__(self, game_id, first_team, second_team, time, tr_name):
        self.game_id = game_id
        self.first_team = first_team
        self.second_team = second_team
        self.time = time
        self.tr_name = tr_name
        self.is_active = 1