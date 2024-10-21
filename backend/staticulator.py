from backend.staticulatorSettings import StaticulatorSettings


class Staticulator(StaticulatorSettings):

    # TODO: database integration?
    # TODO: pass stats to website instead of printing
    def __init__(self):
        super().__init__()

    def calculate_statistics(self, detector):
        self.possession_stats(detector.possessions)

    def possession_stats(self, possessions):
        max_index = possessions.index(max(possessions))
        print(f'The rod with the most ball possession was the {self.zone_names[max_index]}, '
              f'with a total time of {round(possessions[max_index], 2)} seconds')

        blue_total = 0.0
        for i in [0, 1, 3, 5]:
            blue_total += possessions[i]
        red_total = 0.0
        for i in [2, 4, 6, 7]:
            red_total += possessions[i]
        if blue_total > red_total:
            percentage = round(blue_total / (blue_total + red_total) * 100, 2)
            print(f'Blue possessed the ball the most this game, with a percentage of {percentage}%')
        else:
            percentage = round(red_total / (blue_total + red_total) * 100, 2)
            print(f'Red possessed the ball the most this game, with a percentage of {percentage}%')
