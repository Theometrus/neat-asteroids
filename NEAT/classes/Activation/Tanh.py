import math

from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Tanh(ActivationFunction):
    def compute(self, z):
        z = max(-60.0, min(60.0, 2.5 * z))
        return math.tanh(z)
