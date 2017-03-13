from django.db import models

class Team(models.Model):

    team_name = models.CharField(max_length=200)

    def __str__(self):
        return self.team_name

    def make_player_table(self):
        
        key = self.team_name
        results = []

        def find_stats(results):
            key = self.team_name
            temp = []
            for player in results:
                if results[player]['TEAM'] == key:
                    temp.append((player, results[player]['STATS']))
            return temp

        import json

        with open('data_dump.json') as data_file:    
            data = json.load(data_file)

        roster = find_stats(data)
        
        return roster

class Player:
    
    def __init__(self, player, cat):
        self.name = player
        self.type = cat
        self.stats = self.find_stats(player)

    def __str__(self):
        return self.name

    def find_stats(self,athlete):

        import json

        with open('data_dump.json') as data_file:    
            data = json.load(data_file)

        for player in data:
            if player == athlete:
                return data[player]['STATS']

