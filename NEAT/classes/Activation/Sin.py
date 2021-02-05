import math

from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Sin(ActivationFunction):
    def compute(self, z):
        z = max(-60.0, min(60.0, 5.0 * z))
        return math.sin(z)