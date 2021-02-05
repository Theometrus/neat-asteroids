import math

from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class SeLU(ActivationFunction):
    def compute(self, z):
        lam = 1.0507009873554804934193349852946
        alpha = 1.6732632423543772848170429916717
        return lam * z if z > 0.0 else lam * alpha * (math.exp(z) - 1)