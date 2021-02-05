import math

from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Log(ActivationFunction):
    def compute(self, z):
        z = max(1e-7, z)
        return math.log(z)