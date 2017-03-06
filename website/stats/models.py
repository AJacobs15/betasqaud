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

        def find_stats(results):
            key = self.team_name
            temp = {}
            for player in results:
                print(player)
                if results[player]['team'] == key:
                    temp[player] = results[player]
            return temp

        from data import dict
        results = dict

        roster = find_stats(results)
        
        return roster

    
