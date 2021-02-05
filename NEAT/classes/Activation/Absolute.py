from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Absolute(ActivationFunction):
    def compute(self, z):
        return abs(z)