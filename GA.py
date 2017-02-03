from Chromosome import *
from copy import *
from math import *



class GA():
    def __init__(self, num_gen=100, pop_size=50, cross_tax=0.6,
                 mut_chance=0.1, chrom_size=240, tourn_size=3, selection=1, n_dev=10):
        self.num_generation = num_gen
        self.pop_size = pop_size
        self.crossover_tax = cross_tax
        self.mutation_chance = mut_chance
        self.chromosome_size = chrom_size
        self.tournament_size = tourn_size
	    self.num_devices = n_dev
        self.prices = []
        self.devices_consumption = []
        self.population = []
        self.selection = selection
        self.error = 0.01

    """ Reads a set of float values from a given file and stores it in a list.
    """
    def read_float_file(self, filename, values):
        f = open(filename, 'r')
        for line in f:
            values.append(float(line))
        f.close()

    """ Initialize the population."""
    def init_pop(self):
        for i in range(self.pop_size):
            chromosome = Chromosome(self.chromosome_size, self.crossover_tax, self.mutation_chance)
#            self.verify_valid_son(chromosome)
            self.population.append(chromosome)

    """Calculates the actual consumption for all the chromossomes in population.
    """
    def calculates_load(self):
        for chromosome in population:
            chromosome.absolute_fitness = 0 #Total consumption of the configuration represented by the chromosome
            chromosome.relative_fitness = 0 #Value used for minimize the problem (Inverse of the absolute_fitness)
	        for h in range(24): #Along all day
                for i in range(num_devices): #For all devices available
                    chromosome.absolute_fitness += chromossome[(self.num_devices*h) + i] * self.prices[h]

    """ Calculate the fitness for each chromosome in "population",
        based on the route represented in the chromosome.
    """
    def fitness(self, population):
        for chromosome in population:
            chromosome.relative_fitness = pow(chromosome.absolute_fitness - objective_value, 2) #Calculates the difference between the actual load and the objectiv load.
            #The line above must iterate over each hour.

    """ Verify if the "chromosome" is a valid solution for the Traveller Salesman Problem."""
    def verify_valid_son(self, chromosome):
        generate_new_son = False
        for i in range(len(chromosome.value) - 1):
            if (self.prices[int(chromosome.value[i])][int(chromosome.value[i + 1]) - 1] == -1): #Verify if each route in chromosome really exist.
                generate_new_son = True
        if(chromosome.value[0] != chromosome.value[-1]): #Verify if the route in chromosome returns to its origin.
            generate_new_son = True
        for i in range(0, self.chromosome_size - 1):
            for j in range(i + 1, self.chromosome_size):
                if chromosome.value[i] == chromosome.value[j]: #Verify if each city (except origin) is visited only once.
                    generate_new_son = True
        if generate_new_son == True:
            chromosome.value = sample(xrange(1, self.chromosome_size + 1),  self.chromosome_size)
            chromosome.value.append(chromosome.value[0])
            self.verify_valid_son(chromosome)

    """ Implementation of the tournament selection operator."""
    def tournament(self):
        fathers = []
        best_index = 0
        best_fitness = 0
        for i in range(self.tournament_size):
            fathers.append(self.population[int(random() * self.pop_size)])
            if fathers[i].relative_fitness > best_fitness:
                best_index = i
                best_fitness = fathers[i].relative_fitness
        return fathers[best_index]

    """ Implementation of the roulette selection ooperator. """
    def roulette(self):
        index = 0
        aux_sum = 0
        upper_boundary = random()*self.sum_all_fitness()
        i = 0
        while(aux_sum < upper_boundary) and (i < self.pop_size):
            aux_sum += self.population[i].relative_fitness
            i += 1
        index = i - 1
        return self.population[index]

    """ Returns the sum of all fitness in population."""
    def sum_all_fitness(self):
        sum_fitness = 0
        for chromosome in self.population:
            sum_fitness += chromosome.relative_fitness
        return sum_fitness

    """ Gets the best chromosome in population, according to its relative fitness."""
    def get_best(self, population):
        index_best = 0
        fitness_best = 0
        for i in range(len(population)):
            if population[i].relative_fitness > fitness_best:
                index_best = i
                fitness_best = population[i].relative_fitness
        return index_best

    """ Updates the population, creating sons by crossover of two fathers (chromosomes),
        and adding the sons to the new population.
    """
    def generation(self):
        new_population = []
        index_fathers = 1
        index_sons = 1
        if self.selection == 0:
            print "Selection Mode: Roulette"
        else:
            print "Selection Mode: Tournament"
        while(len(new_population) < self.pop_size):
            if self.selection == 0:
                father1 = self.roulette()
                father2 = self.roulette()
                print "Selected Fathers:\n\n#{0}: {1}\n#{2}: {3}\n".format(index_fathers, father1, index_fathers + 1, father2)
                sons = father1.crossover(father2)
                index_fathers += 2
            else:
                father1 = self.tournament()
                father2 = self.tournament()
                print "Selected Fathers:\n\n#{0}: {1}\n#{2}: {3}\n".format(index_fathers, father1, index_fathers + 1, father2)
                sons = father1.crossover(father2)
                index_fathers += 2
            for son in sons:
                son.mutation()
                self.verify_valid_son(son)
                print "Adding son #{0}:{1} to the population.\n".format(index_sons, son)
                index_sons += 1
                new_population.append(son)
        self.population = deepcopy(new_population)
        self.fitness(self.population)

    """Calculates the media of the fitness in population."""
    def calc_media(self, population):
        media = 0.0
        for chromosome in population:
            media += chromosome.relative_fitness
        media = media / len(population)
        return media

    """ Verify if the population is converging,
        calculating the difference between the media and the best chromosome in population.
    """
    def verify_convergence(self):
        convergence = False
        index_best = self.get_best(self.population)
        if (self.population[index_best].relative_fitness - self.calc_media(self.population)) < self.error:
            convergence = True
        return convergence

    """ The main process of the genetic algorithm."""
    def process(self):
        self.read_float_file("prices_per_hour.txt", self.prices) #Initializes prices data
        self.read_float_file("devices_consumption.txt", self.devices_consumption) #Initializes consumption data
        self.init_pop()
        self.fitness(self.population)
        generation_index = 1
        while(generation_index < self.num_generation):
            print "\n\n\t\t\tGENERATION {0}\n".format(generation_index)
            generation_index += 1
            self.generation()
        print "\n\n\t\tBEST SOLUTION FOUND AT GENERATION {0}.\nBest is : {1}".format(generation_index, self.population[self.get_best(self.population)])
        print "Number of Generations: {0}.\n".format(generation_index)
        print "Population Converged.\n"
        return self.population[self.get_best(self.population)]

if __name__ == "__main__":
    test = GA(10, 5, 0.5, 0.1, 7, 3, 1)
    test.process()
