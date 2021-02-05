import math

from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Softplus(ActivationFunction):
    def compute(self, z):
        z = max(-60.0, min(60.0, 5.0 * z))
        return 0.2 * math.log(1 + math.exp(z))