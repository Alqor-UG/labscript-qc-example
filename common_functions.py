"""
In this module, we define functions that are used by multiple MOT scripts.

To make it simpler to call them we put them into a common class called 
Experiment.
"""


class MotExperiment:
    """
    A class that contains functions that are used by multiple MOT scripts.
    """

    def load(self, wires: list[int], params: list[float]):
        """
        Load atoms into the MOT.
        """
