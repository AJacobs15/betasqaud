from django.db import models



INDEX_MAP = {'0' : 'GP', '1' : 'MPG', '2' : 'FGM', '3' : 'FGA', '4' : 'FG%', '5' : '3PM', '6' : '3PA', '7' : '3P%', 
                '8' : 'FTM', '9' : 'FTA', '10' : 'FT%', '11' : 'TOV', '12' : 'PF', '13' : 'ORB', '14': 'DRB', '15' : 'RPG',
                '16': 'APG', '17' : 'SPG', '18' : 'BPG', '19' : 'PPG'}


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
    
    def __init__(self, player, data, image, awards, cat, tokens):
        self.name = player
        self.data = data
        self.image_links = image
        self.awards = awards
        self.type = cat
        self.tokens = tokens
        self.stats = self.find_stats(player)
        self.graph = self.find_graph(player)


    def __str__(self):
        return self.name

    def find_stats(self,athlete):

        import json

        with open('data_dump.json') as data_file:    
            data = json.load(data_file)

        for player in data:
            if player == athlete:
                stats = data[player]['STATS']

                nl = []
                for i in range(len(stats)):
                    stat = stats[i]
                    stat = str(stat)
                    info = INDEX_MAP[str(i)] + ' : ' + stat
                    nl.append(info)
                rv = ', '.join(nl)
                return rv

    def find_graph(self, player):
        temp = player.split()
        string = "/media/" + temp[0] + "_" + temp[1] + ".png"
        return string
