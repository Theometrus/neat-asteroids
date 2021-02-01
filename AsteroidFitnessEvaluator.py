class AsteroidFitnessEvaluator:
    def __init__(self):
        self.networks = {}

    def calculate(self, player):
        self.networks[player.brain] = player.score \
                                      + player.time_alive * 0.005\
                                      + player.moved * 0.03\
                                      + player.turned * 0.01

    def evaluate(self, network):
        return self.networks[network]