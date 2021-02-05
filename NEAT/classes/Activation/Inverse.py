from NEAT.classes.Activation.ActivationFunction import ActivationFunction


class Inverse(ActivationFunction):
    def compute(self, z):
        try:
            z = 1.0 / z
        except ArithmeticError:  # handle overflows
            return 0.0
        else:
            return z