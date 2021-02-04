class AsteroidFitnessEvaluator:
    def __init__(self):
        self.networks = {}

    def calculate(self, player):
        self.networks[player.brain] = ((player.score + 1) * 2) * (player.time_alive) \
         * (player.shots_hit/player.shots_fired * player.shots_hit/player.shots_fired)

    def evaluate(self, network):
        return self.networks[network]
