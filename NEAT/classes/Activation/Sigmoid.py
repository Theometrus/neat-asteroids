import math

from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Sigmoid(ActivationFunction):
    def compute(self, z):
        z = max(-60.0, min(60.0, 4.9 * z))  # Steeper than regular sigmoid for optimization purposes
        return 1.0 / (1 + math.exp(-z))
