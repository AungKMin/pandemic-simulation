import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy as np 
from math import gcd

# RGB tuples
GRAY = (0.86, 0.86, 0.86) # uninfected
RED = (0.86, 0.08, 0.23) # infected
GREEN = (0, 0.86, 0.01) # recovered
BLACK = (0, 0, 0) # dead

# COVID19 specific information
COVID19_PARAMS = { 
    "r0": 2.28, # expected number of cases generated by one infection
    "incubation": 5, # days it takes for virus to incubate
    "percent_mild": 0.8, # percent of infections that are mild
    "mild_recovery_fast": 7, # range of time between incubation to recovery for mild cases
    "mild_recovery_slow": 14,
    "severe_recovery_fast": 21, # range of time between incubation to recovery for severe cases
    "severe_recovery_slow": 42,
    "severe_death_fast": 14, # range of time between incubation to death for severe cases
    "severe_death_slow": 56,
    "fatality_rate": 0.034, # percent of cases that result in death
}

class Virus():
    def __init__(self, params):
        # create polar plot
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111, projection="polar")
        self.axes.grid(False)
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])
        self.axes.set_ylim(0, 1)

        # create annotations
        self.day_text = self.axes.annotate(
            "Day 0", xy=[np.pi / 2, 1], ha="center", va="bottom"
        )
        self.infected_text = self.axes.annotate(
            "Infected: 0", xy=[3 * np.pi / 2, 1], ha="center", va="top", color=RED
        )
        self.deaths_text = self.axes.annotate(
            "\nDeaths: 0", xy=[3 * np.pi / 2, 1], ha="center", va="top", color=BLACK
        )
        self.recovered_text = self.axes.annotate(
            "\n\nRecovered: 0", xy=[3 * np.pi / 2, 1], ha="center", va="top", color=GREEN
        )

        # create virus variables
        self.day = 0
        self.total_infected = 0
        self.currently_infected = 90
        self.recovered = 0
        self.deaths = 0
        self.r0 = params["r0"]
        self.percent_mild = params["percent_mild"]
        self.percent_severe = 1 - params["percent_mild"]
        self.fatality_rate = params["fatality_rate"]
        # calculate interval when simulation should update
        self.serial_interval = gcd(params["mild_recovery_fast"], params["mild_recovery_slow"], params["severe_recovery_fast"], params["severe_recovery_slow"], params["severe_death_fast"], params["severe_death_slow"])

        # times it takes from infection to outcome
        self.mild_recovery_fast = params["incubation"] + params["mild_recovery_fast"]
        self.mild_recovery_slow = params["incubation"] + params["mild_recovery_slow"]
        self.severe_recovery_fast = params["incubation"] + params["severe_recovery_fast"]
        self.severe_recovery_slow = params["incubation"] + params["severe_recovery_slow"]
        self.severe_death_fast = params["incubation"] + params["severe_death_fast"]
        self.severe_death_slow = params["incubation"] + params["severe_death_slow"]

        # locations of recovered mild cases for specific days
        self.mild = {day : {"thetas": [], "rs": []} for day in range(self.mild_recovery_fast, 365)}
        # locations of recovered and dead severe cases for specific days day
        self.severe = {
            "recovery": {day: {"thetas": [], "rs": []} for day in range(self.severe_recovery_fast, 365)},
            "death": {day: {"thetas": [], "rs": []} for day in range(self.severe_death_fast, 365)}
        }

        self.exposed_before = 0 # number of people exposed to virus
        self.exposed_after = 1 # number of people who will be exposed to virus by end of current wave

        self.set_initial_population()

    def set_initial_population(self):
        population = 4500
        self.currently_infected = 1
        self.total_infected = 1

        # define the locations of points on the polar plot using golden spiral method
        indices = np.arange(0, population) + 0.5
        self.thetas = np.pi * (1 + 5**0.5) * indices
        self.rs = np.sqrt(indices / population)
        self.plot = self.axes.scatter(self.thetas, self.rs, s=5, color=GRAY)

        #set patient zero to mild recovery fast
        self.axes.scatter(self.thetas[0], self.rs[0], s=5, color=RED)
        self.mild[self.mild_recovery_fast]["thetas"].append(self.thetas[0])
        self.mild[self.mild_recovery_fast]["rs"].append(self.rs[0])


    def spread_virus(self, i):
        self.exposed_before = self.exposed_after
        if self.day % self.serial_interval == 0 and self.exposed_before < 4500: 
            self.new_infected = round(self.r0 * self.total_infected)
            self.exposed_after += round(self.new_infected * 1.1) # there are more people exposed than there are people infected
            # if exposed is more than the population 
            if self.exposed_after > 4500: 
                self.new_infected = round((4500 - self.exposed_before) / 1.1) # set number of new infections to 90% of the remaining population instead
                self.exposed_after = 4500 # then the entire population has been exposed

            # update infected numbers
            self.currently_infected += self.new_infected
            self.total_infected += self.new_infected

            # get locations of new infected cases
            self.new_infected_indices = list(
                np.random.choice(
                    range(self.exposed_before, self.exposed_after),
                    self.new_infected,
                    replace=False
                )
            )
            thetas = [self.thetas[i] for i in self.new_infected_indices]
            rs = [self.rs[i] for i in self.new_infected_indices]

            # stop the main animation loop
            self.anim.event_source.stop()

            # start the subanimation for infection cases
            if self.new_infected > 24: 
                list_size = round(self.new_infected / 24)
                theta_chunk = list(self.chunks(thetas, list_size))
                r_chunk = list(self.chunks(rs, list_size))
                self.anim2 = ani.FuncAnimation(
                    self.fig, 
                    self.one_by_one, 
                    interval=5,
                    frames=len(theta_chunk),
                    fargs=(theta_chunk, r_chunk, RED)
                )
            else: 
                self.anim2 = ani.FuncAnimation(
                    self.fig,
                    self.one_by_one,
                    interval=5,
                    frames=len(thetas),
                    fargs=(thetas, rs, RED)
                )

            self.assign_symtoms()

        self.day += 1

        self.update()

    # function for animation
    def one_by_one(self, i, thetas, rs, color):
        self.axes.scatter(thetas[i], rs[i], s=5, color=color)
        # if this wave is done plotting, stop anim2 animation and start the main anim animation
        if i == (len(thetas) - 1):
            self.anim2.event_source.stop()
            self.anim.event_source.start()
        
    # return chunks
    def chunks(self, a_list, n):
        for i in range(0, len(a_list), n):
            yield a_list[i:(i + n)]

    # calculate number of mild and severe cases for new wave
    def assign_symtoms(self):
        num_mild= round(self.percent_mild * self.new_infected)
        num_severe = round(self.percent_severe * self.new_infected)
        # get indices of the newly infected cases with mild symptoms
        self.mild_indices = np.random.choice(
            self.new_infected_indices, num_mild, replace=False
        )
        # get locations of newly infected cases with severe symptoms
        severe_indices = [
            i for i in self.new_infected_indices if i not in self.mild_indices
        ]
        percent_severe_recovery = 1 - (self.fatality_rate / self.percent_severe) # percentage of severe cases that recover
        num_severe_recovery = round(percent_severe_recovery * num_severe) # number of severe cases that recover in the new wave
        self.severe_recovery_indices = []
        self.severe_death_indices = []
        # get locations of newly infected severe cases resulting in death and those resulting in recovery
        if severe_indices: 
            self.severe_recovery_indices = np.random.choice(
                severe_indices, num_severe_recovery, replace=False
            )
            self.severe_death_indices = [
                i for i in severe_indices if i not in self.severe_recovery_indices
            ]

        #  set recovery times for newly infected mild cases
        mild_recovery_day_low = self.day + self.mild_recovery_fast
        mild_recovery_day_high = self.day + self.mild_recovery_slow
        for index in self.mild_indices: 
            recovery_day = np.random.randint(mild_recovery_day_low, mild_recovery_day_high)
            theta = self.thetas[index]
            r = self.rs[index]
            self.mild[recovery_day]["thetas"].append(theta)
            self.mild[recovery_day]["rs"].append(r)

        # set recovery times for newly infected severe cases
        severe_recovery_day_low = self.day + self.severe_recovery_fast
        severe_recovery_day_high = self.day + self.severe_recovery_slow
        for index in self.severe_recovery_indices:
            recovery_day = np.random.randint(severe_recovery_day_low, severe_recovery_day_high)
            theta = self.thetas[index]
            r = self.rs[index]
            self.severe["recovery"][recovery_day]["thetas"].append(theta)
            self.severe["recovery"][recovery_day]["rs"].append(r)
        
        # set death times for newly infected severe cases
        severe_death_day_low = self.day + self.severe_death_fast
        severe_death_day_high = self.day + self.severe_death_slow
        for index in self.severe_death_indices:
            death_day = np.random.randint(severe_death_day_low, severe_death_day_high)
            theta = self.thetas[index]
            r = self.rs[index]
            self.severe["death"][death_day]["thetas"].append(theta)
            self.severe["death"][death_day]["rs"].append(r)


    # update plots and annotations
    def update(self):
        # update plots for recovered mild cases
        if self.day >= self.mild_recovery_fast:
            mild_thetas = self.mild[self.day]["thetas"]
            mild_rs = self.mild[self.day]["rs"]
            self.axes.scatter(mild_thetas, mild_rs, s=5, color=GREEN)
            self.recovered += len(mild_thetas)
            self.currently_infected -= len(mild_thetas)
        
        # update plots for recovered severe cases
        if self.day >= self.severe_recovery_fast:
            severe_thetas = self.severe["recovery"][self.day]["thetas"]
            severe_rs = self.severe["recovery"][self.day]["rs"]
            self.axes.scatter(severe_thetas, severe_rs, s=5, color=GREEN)
            self.recovered += len(severe_thetas)
            self.currently_infected -= len(severe_thetas)

        # update plots for dead severe cases
        if self.day >= self.severe_death_fast:
            severe_thetas = self.severe["death"][self.day]["thetas"] 
            severe_rs = self.severe["death"][self.day]["rs"]
            self.axes.scatter(severe_thetas, severe_rs, s=5, color=BLACK)
            self.deaths += len(severe_thetas)
            self.currently_infected -= len(severe_thetas)

        # Update annotations
        self.day_text.set_text("Day {}".format(self.day))
        self.infected_text.set_text("Infected: {}".format(self.currently_infected))
        self.deaths_text.set_text("\nDeaths: {}".format(self.deaths))
        self.recovered_text.set_text("\n\nRecovered: {}".format(self.recovered))

    # generator for animation 
    def generate(self):
        while self.deaths + self.recovered < self.total_infected: 
            yield

    # animate graph
    def animate(self):
        self.anim = ani.FuncAnimation(
            self.fig,
            self.spread_virus,
            frames=self.generate,
            repeat=True
        )
        return [self.fig, self.anim]

    def pause(self, event):
        self.anim.event_source.stop()
        self.anim2.event_source.stop()

    def unpause(self, event):
        self.anim.event_source.start()
        self.anim2.event_source.start()

if __name__ == '__main__':
    user_input = input("Use Custom params? (if not, will default to Covid-19 params)\n")
    user_params = {}
    if (user_input.lower() == 'yes' or user_input.lower() == 'y'):
        keys = list(COVID19_PARAMS.keys())
        values = list(COVID19_PARAMS.values())
        index = 0
        while index < len(keys):
            try: 
                if type(values[index]) is float:
                    user_params[keys[index]] = float(input('{} (COVID-19 value: {}): '.format(keys[index], values[index])))
                else: 
                    user_params[keys[index]] = int(input('{} (COVID-19 value: {}): '.format(keys[index], values[index])))                    
            except ValueError: 
                print("Invalid Input - please try again")
                continue
            index += 1
    else :
        user_params = COVID19_PARAMS
    coronavirus = Virus(user_params)
    fig, anim = coronavirus.animate()

    index = 0
    keys = list(user_params.keys())
    values = list(user_params.values())
    while index < len(keys): 
        fig.text(0.2, 0.9 - 0.05*index, '{}: {}'.format(keys[index], values[index]))
        index += 1
    plt.show()


