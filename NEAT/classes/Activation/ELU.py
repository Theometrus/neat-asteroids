import math

from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class ELU(ActivationFunction):
    def compute(self, z):
        return z if z > 0.0 else math.exp(z) - 1
