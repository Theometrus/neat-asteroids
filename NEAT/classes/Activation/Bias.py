from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Bias(ActivationFunction):
    def compute(self, z):
        return 1.0
