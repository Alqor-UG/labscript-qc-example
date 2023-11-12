from labscript import start, stop, add_time_marker, AnalogOut, DigitalOut
from labscript_devices.DummyPseudoclock.labscript_devices import DummyPseudoclock
from labscript_devices.DummyIntermediateDevice import DummyIntermediateDevice
from labscript_devices.FunctionRunner.labscript_devices import FunctionRunner


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


def func(shot_context, t):
    """
    The function that is added to the function runner.
    """
    import csv
    from lyse import Run

    print("Here I am")
    print("I added the cool function from the function runner.")
    # we have to write it at the right position
    csv_file_path = "/Users/fredjendrzejewski/output_test.csv"

    # Open the CSV file in write mode
    with open(csv_file_path, mode="w", newline="") as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)

        # Write the number to the CSV file
        csv_writer.writerow([27])

    with open(csv_file_path, mode="w", newline="") as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)

        # Write the number to the CSV file
        csv_writer.writerow([27])
    # aaaaand save it to the hdf5

    # Open the CSV file in read mode
    with open(csv_file_path, mode="r") as csv_file:
        # Create a CSV reader object
        csv_reader = csv.reader(csv_file)

        # Read the number from the CSV file (assuming it's in the first row)
        for row in csv_reader:
            if len(row) > 0:
                number_from_csv = int(row[0])  # Assuming the number is an integer
        shots_array = [number_from_csv]

    run = Run(shot_context.h5_file)
    run.save_result("n_at", shots_array)


print("Here I am")
function_runner.add_function(t="start", function=func)
print("Done.")
# Begin issuing labscript primitives
# A timing variable t is used for convenience
# start() elicits the commencement of the shot
t = 0
add_time_marker(t, "Start", verbose=True)
start()

# Wait for 1 second with all devices in their default state
t += 1

# Change the state of digital_out, and denote this using a time marker
add_time_marker(t, "Toggle digital_out (high)", verbose=True)
digital_out.go_high(t)

# Wait for 0.5 seconds
t += 0.5

# Ramp analog_out from 0.0 V to 1.0 V over 0.25 s with a 1 kS/s sample rate
t += analog_out.ramp(t=t, initial=0.0, final=1.0, duration=0.25, samplerate=1e3)

# Change the state of digital_out, and denote this using a time marker
add_time_marker(t, "Toggle digital_out (low)", verbose=True)
digital_out.go_low(t)

# Wait for 0.5 seconds
t += 0.5

# Stop the experiment shot with stop()
stop(t)
