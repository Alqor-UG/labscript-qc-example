"""
This module creates a connection table for the example experiment in the labscript documentation. 
It should be run in a first within runmanager, before the experiment is run, to create the 
connection table. For more information, see https://docs.labscriptsuite.org/
"""


from labscript import start, stop, AnalogOut, DigitalOut
from labscript_devices.DummyPseudoclock.labscript_devices import DummyPseudoclock
from labscript_devices.DummyIntermediateDevice import DummyIntermediateDevice
from labscript_devices.FunctionRunner.labscript_devices import FunctionRunner

# Use a virtual, or 'dummy', device for the psuedoclock
DummyPseudoclock(name="pseudoclock")

# An output of this DummyPseudoclock is its 'clockline' attribute, which we use
# to trigger children devices

DummyIntermediateDevice(
    name="intermediate_device",
    parent_device=pseudoclock.clockline,  # pylint: disable=undefined-variable
)

# Create an AnalogOut child of the DummyIntermediateDevice
AnalogOut(
    name="analog_out",
    parent_device=intermediate_device,  # pylint: disable=undefined-variable
    connection="ao0",
)

# Create a DigitalOut child of the DummyIntermediateDevice
DigitalOut(
    name="digital_out",
    parent_device=intermediate_device,  # pylint: disable=undefined-variable
    connection="port0/line0",
)

# create a FunctionRunner child of the DummyIntermediateDevice
FunctionRunner(name="function_runner")

if __name__ == "__main__":
    # Begin issuing labscript primitives
    # start() elicits the commencement of the shot
    start()

    # Stop the experiment shot with stop()
    stop(1.0)
