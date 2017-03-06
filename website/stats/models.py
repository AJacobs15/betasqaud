from django.db import models
import csv

class Team(models.Model):

    team_name = models.CharField(max_length=200)

    def __str__(self):
        return self.team_name


class Player(models.Model):
    
    team_name = models.CharField(max_length=200)

    def make_player_table(self):
        
        results = []

        def find_stats(table):
            key = self.team_name
            temp = {}
            for player in table:
                print(player)
                for player_name in player:
                    print(player_name)
                    if player[player_name]['team'] == key:
                        temp[player] = player[player_name]
            return temp

        dicts_from_file = []
        with open('data.txt','r') as inf:
            for line in inf:
                dicts_from_file.append(eval(line))  

        roster = find_stats(dict_from_file)
        
        return roster

    
