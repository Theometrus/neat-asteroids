import math

from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Exp(ActivationFunction):
    def compute(self, z):
        z = max(-60.0, min(60.0, z))
        return math.exp(z)
