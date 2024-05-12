import random
import numpy as np


class CustomDistributionModel:
    """
    This is an inverse logarimthic number generator which will give you a 
    random number based on a hardcoded probability range.
    1-20 is 50%, 21-40 is 30%, 41-60 is 15%, 61-80 is 4% and 81-100 is 1%.

    At the moment this uses numpy as without it the code is incredibly laggy.
    """
    def __init__(self):
        # Define the intervals and their corresponding percentages
        self.intervals = [(1, 20), (21, 40), (41, 60), (61, 80), (81, 100)]
        self.percentages = [0.50, 0.3, 0.15, 0.04, 0.01]
        # Calculate the cumulative percentages
        self.cumulative_percentages = np.cumsum(self.percentages)

    def generate_sample(self):
        # Generate a random number to determine which interval to sample from
        random_value = random.uniform(0, 1)
        for i, cumulative_percentage in enumerate(self.cumulative_percentages):
            if random_value <= cumulative_percentage:
                # Sample from the corresponding interval
                lower_bound, upper_bound = self.intervals[i]
                chance = 1 / np.log(random.uniform(1, np.e))
                # Ensure the generated number falls within the specified range
                while not (lower_bound <= chance <= upper_bound):
                    chance = 1 / np.log(random.uniform(1, np.e))
                if chance >= 81:
                    return("LEGENDARY")
                elif chance >= 61:
                    return("MYSTICAL")
                elif chance >= 41:
                    return("RARE")
                elif chance >= 21:
                    return("UNCOMMON")
                else:
                    return("COMMON")
                

# Example usage 
#model = CustomDistributionModel()
#sample = model.generate_sample()