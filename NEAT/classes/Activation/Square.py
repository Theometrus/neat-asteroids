from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Square(ActivationFunction):
    def compute(self, z):
        return z ** 2
