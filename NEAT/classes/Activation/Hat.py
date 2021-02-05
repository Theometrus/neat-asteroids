from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Hat(ActivationFunction):
    def compute(self, z):
        return max(0.0, 1 - abs(z))
