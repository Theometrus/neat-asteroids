class AsteroidFitnessEvaluator:
    def __init__(self):
        self.networks = {}

    def calculate(self, player):
        self.networks[player.brain] = player.score + player.time_alive * 0.01

    def evaluate(self, network):
        return self.networks[network]