import math


class XORFitnessEvaluator:
    # This class evaluates and keeps track of network fitnesses

    def __init__(self):
        self.networks = {}

    def calculate(self, network, outs, ins):
        ans = outs[network]

        ctr = 0
        my_sum = 0.0

        for i in range(int(len(ins) / 2)):
            my_ans = ins[ctr] ^ ins[ctr + 1]
            my_sum += abs(my_ans - ans[i])
            ctr += 2

        fitness = math.pow(4 - my_sum, 2)

        network.fitness = fitness
        self.networks[network] = network.fitness

    def evaluate(self, network):
        return self.networks[network]
