from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Cube(ActivationFunction):
    def compute(self, z):
        return z ** 3
