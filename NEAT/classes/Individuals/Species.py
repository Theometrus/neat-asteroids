class Species:
    def __init__(self, representative):
        self.members = []
        self.total_fitness = 0.0
        self.average_fitness = 0.0
        self.max_fitness = 0.0
        self.improved = False
        self.new_size = 0
        self.representative = representative  # Compared with other networks to determine speciation distance
        self.champion = None
        self.current_best = 0.0
        # If a species has not improved its max fitness before this timer reaches zero, it
        # is forced to go extinct
        self.stagnation_timer = 15

    def calculate_fitnesses(self, fitness_evaluator):
        for i in self.members:
            try:
                i.fitness = fitness_evaluator.evaluate(i)
            except:
                print("fuuuck me luya")

    def adjust_fitnesses(self):
        self.total_fitness = 0.0
        self.average_fitness = 0.0
        self.improved = False
        self.current_best = 0.0
        self.champion = None

        if len(self.members) == 0:
            self.total_fitness = 0.0
            return

        for i in self.members:
            i.fitness /= len(self.members)
            self.total_fitness += i.fitness

            if i.fitness > self.max_fitness:
                self.improved = True
                self.stagnation_timer = 15
                self.max_fitness = i.fitness

            if i.fitness > self.current_best:
                self.current_best = i.fitness
                self.champion = i

        self.average_fitness = self.total_fitness / len(self.members)

        if not self.improved:
            self.stagnation_timer -= 1
