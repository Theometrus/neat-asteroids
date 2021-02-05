from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Clamped(ActivationFunction):
    def compute(self, z):
        return max(-1.0, min(1.0, z))
