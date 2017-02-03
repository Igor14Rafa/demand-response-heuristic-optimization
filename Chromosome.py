from random import *


class Chromosome():
    def __init__(self, chromosome_size, crossover_tax, mutation_chance):
        self.chromosome_size = chromosome_size
        self.crossover_tax = crossover_tax
        self.mutation_chance = mutation_chance
        self.relative_fitness = 0
        self.absolute_fitness = 0
	    self.value = []
        for i in range(self.chromosome_size):
	        self.value.append(randrange(0,2))         #initialize the chromossome with the bits representing the devices

    """ Implementation of the default crossover operator.
         This crossover calculates a cutpoint
         and split the two fathers at this point,
         joining different parts of each one to make a new son.
    """
    def crossover(self, chromosome_2):
        sons = []
        cutpoint = int(random() * self.chromosome_size)
        son_1 = Chromosome(self.chromosome_size, self.crossover_tax, self.mutation_chance)
	    if random() < self.crossover_tax:
        	son_1.value = self.value[0: cutpoint] + chromosome_2.value[cutpoint: (len(self.value))]
	    else:
		    son_1.value = self.value
            sons.append(son_1)
            son_2 = Chromosome(self.chromosome_size, self.crossover_tax, self.mutation_chance)
	    if random() < self.crossover_tax:
        	   son_2.value = chromosome_2.value[0: cutpoint] + self.value[cutpoint: (len(self.value))]
	    else:
		    son_2.value = self.value
            sons.append(son_2)
        return sons

    """Implementation of the default mutation operator.
        This operator calculates if the "mutation" will occur
        in any of the "genes"(devices) in chromosome,
        based on the mutation chance.
    """
    def mutation(self):
        for i in range(self.chromosome_size):
            if random() < self.mutation_chance:
                self.value[i] = abs(self.value[i] - 1)
   """
      Read the devices's consumption data from the file.
   """

    def __str__(self):
        return "Value=>{0} : Absolute Fitness=>{1}; Relative Fitness=>{2}\n".format(self.value, self.absolute_fitness, self.relative_fitness)

if __name__ == "__main__":
    test = Chromosome(240, 0.6, 0.1)
    print test.value
