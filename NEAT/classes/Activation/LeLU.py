from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class LeLU(ActivationFunction):
    def compute(self, z):
        leaky = 0.005
        return z if z > 0.0 else leaky * z