from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Identity(ActivationFunction):
    def compute(self, z):
        return z
