from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class ReLU(ActivationFunction):
    def compute(self, z):
        return max(0.0, z)
