"""
The start of the labscript experimental sequence.
"""
from labscript import start, stop, add_time_marker, AnalogOut, DigitalOut
from labscript_devices.DummyPseudoclock.labscript_devices import DummyPseudoclock
from labscript_devices.DummyIntermediateDevice import DummyIntermediateDevice
from labscript_devices.FunctionRunner.labscript_devices import FunctionRunner


from time import sleep
import csv

# Use a virtual, or 'dummy', device for the psuedoclock
DummyPseudoclock(name="pseudoclock")

# An output of this DummyPseudoclock is its 'clockline' attribute, which we use
# to trigger children devices
DummyIntermediateDevice(name="intermediate_device", parent_device=pseudoclock.clockline)

# Create an AnalogOut child of the DummyIntermediateDevice
AnalogOut(name="analog_out", parent_device=intermediate_device, connection="ao0")

# Create a DigitalOut child of the DummyIntermediateDevice
DigitalOut(
    name="digital_out", parent_device=intermediate_device, connection="port0/line0"
)

# create a FunctionRunner child of the DummyIntermediateDevice
FunctionRunner(name="function_runner")


def func(shot_context: dict, t: str) -> None:
    """
    The function that is added to the function runner.
    """

    # pylint: disable=C0415
    import csv
    from lyse import Run

    # we have to write it at the right position
    # csv_file_path = "/Users/fredjendrzejewski/output.csv"
    csv_file_path = "C:/Users/BASOARO/Documents/output_test.csv"
    # aaaaand save it to the hdf5

    # Open the CSV file in read mode
    with open(csv_file_path, mode="r") as csv_file:
        # Create a CSV reader object
        csv_reader = csv.reader(csv_file)

        # Read the number from the CSV file (assuming it's in the first row)
        for row in csv_reader:
            if len(row) > 0:
                number_from_csv = int(row[0])  # Assuming the number is an integer
    run = Run(shot_context.h5_file)
    run.save_result("nat", number_from_csv, group="/measure")


class ExperimentClass:
    """
    This class will contain all the functions that are necessary to run the experiment.
    """

    def __init__(self):
        self.t = 0
        self.n_at = 0

    def load(self, wires: list[int], params: list[float]):
        """
        Load atoms into the MOT.
        """
        print("Loading atoms into the MOT.")
        print(wires)
        sleep(params[0] / 10)
        # Wait for 0.5 seconds
        self.t += params[0] / 10
        # simulate the loading of atoms.
        self.n_at = params[0]

    def measure(self, wires: list[int], params: list[float]):
        """
        Measure the number of atoms in the MOT.
        """
        print("Measure atoms in the the MOT.")
        # we have to write it at the right position
        # csv_file_path = "/Users/fredjendrzejewski/output.csv"
        csv_file_path = "C:/Users/BASOARO/Documents/output_test.csv"

        # Open the CSV file in write mode
        with open(csv_file_path, mode="w", newline="") as csv_file:
            # Create a CSV writer object
            csv_writer = csv.writer(csv_file)

            # Write the number to the CSV file
            csv_writer.writerow([self.n_at])
        print("Adding the cool function.")
        function_runner.add_function(t="stop", function=func)

    def final_action(self):
        """
        Clean up at the end of the sequence.
        """
        print("Cleaning up.")


Experiment = ExperimentClass()
# Begin issuing labscript primitives
# A timing variable t is used for convenience
# start() elicits the commencement of the shot
t = 0
add_time_marker(t, "Start", verbose=True)
start()
