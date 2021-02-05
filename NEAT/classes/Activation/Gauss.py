import math

from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Gauss(ActivationFunction):
    def compute(self, z):
        z = max(-3.4, min(3.4, z))
        return math.exp(-5.0 * z ** 2)