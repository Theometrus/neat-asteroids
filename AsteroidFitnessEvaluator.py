class AsteroidFitnessEvaluator:
    def __init__(self):
        self.networks = {}

    def calculate(self, player):
        self.networks[player.brain] = ((player.score + 1) * 2) * (player.time_alive * 0.01) * (
                (player.shots_hit + 1) / (player.shots_fired + 1) ** 2) * (
                                                  (player.moved + 1) * 0.01)

        if player.shots_fired == 0:
            self.networks[player.brain] /= 2

    def evaluate(self, network):
        return self.networks[network]
