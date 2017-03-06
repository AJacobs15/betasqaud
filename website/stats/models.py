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
                if results[player]['team'] == key:
                    temp.append((player,results[player]))
            return temp

        from data import dict
        results = dict

        roster = find_stats(results)
        
        return roster

    
