"""
In this module we define all the configuration parameters for the mot device. 

No runs are started here. The entire logic is implemented in the `spooler.py` module.
"""

from typing import Literal, List, Optional
from pydantic import Field, BaseModel
from typing_extensions import Annotated

from sqooler.schemes import LabscriptSpooler

from spooler import (  # pylint: disable=import-error
    gen_script_and_globals,
    remoteClient,
)

N_MAX_SHOTS = 100
N_MAX_ATOMS = 500
MAX_EXPERIMENTS = 1000


class LoadInstruction(BaseModel):
    """
    The load instruction. As each instruction it requires the

    Attributes:
        name: The string to identify the instruction
        wires: The wire on which the instruction should be applied
            so the indices should be between 0 and N_MAX_WIRES-1
        params: has to be empty
    """

    name: Literal["load"]
    wires: Annotated[
        List[Annotated[int, Field(ge=0, le=0)]], Field(min_length=0, max_length=1)
    ]
    params: Annotated[
        List[Annotated[int, Field(ge=1, le=N_MAX_ATOMS)]],
        Field(min_length=1, max_length=1),
    ]


class MeasureBarrierInstruction(BaseModel):
    """
    The measure and barrier instruction. As each instruction it requires the

    Attributes:
        name: The string to identify the instruction
        wires: The wire on which the instruction should be applied
            so the indices should be between 0 and N_MAX_WIRES-1
        params: has to be empty
    """

    name: Literal["measure", "barrier"]
    wires: Annotated[
        List[Annotated[int, Field(ge=0, le=0)]], Field(min_length=0, max_length=1)
    ]
    params: Annotated[List[float], Field(min_length=0, max_length=0)]


class MotExperiment(BaseModel):
    """
    The class that defines the mot experiments
    """

    wire_order: Literal["interleaved", "sequential"] = "sequential"
    shots: Annotated[int, Field(gt=0, le=N_MAX_SHOTS)]
    num_wires: Literal[1]
    instructions: List[list]
    seed: Optional[int] = None


# This is the spooler object that is used by the main function.
spooler_object = LabscriptSpooler(
    ins_schema_dict={
        "barrier": MeasureBarrierInstruction,
        "measure": MeasureBarrierInstruction,
        "load": LoadInstruction,
    },
    remote_client=remoteClient,
    device_config=MotExperiment,
    n_wires=1,
    version="0.1",
    description="Setup of an atomic mot.",
    n_max_experiments=MAX_EXPERIMENTS,
    n_max_shots=N_MAX_SHOTS,
    operational=True,
)

# Now also add the function that generates the circuit
spooler_object.gen_circuit = gen_script_and_globals
