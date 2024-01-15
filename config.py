"""
In this module we define all the configuration parameters for the mot device. 

No runs are started here. The entire logic is implemented in the `spooler.py` module.
"""

from typing import Literal, List, Optional
from pydantic import Field, BaseModel
from typing_extensions import Annotated

from sqooler.schemes import Spooler, ResultDict, StatusMsgDict

from spooler import (  # pylint: disable=import-error
    gen_script_and_globals,
    modify_shot_output_folder,
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


class MotSpooler(Spooler):
    """
    The spooler class that handles all the circuit logic.
    """

    def add_job(
        self, json_dict: dict, status_msg_dict: StatusMsgDict
    ) -> tuple[ResultDict, StatusMsgDict]:
        """
        The function that translates the json with the instructions into some circuit
        and executes it. It performs several checks for the job to see if it is properly
        working. If things are fine the job gets added the list of things that should be
        executed.

        Args:
            json_dict: The job dictonary of all the instructions.
            status_msg_dict: the status dictionary of the job we are treating.
        """
        job_id = status_msg_dict.job_id

        result_draft: dict = {
            "display_name": self.display_name,
            "backend_version": self.version,
            "job_id": job_id,
            "qobj_id": None,
            "success": True,
            "status": "finished",
            "header": {},
            "results": [],
        }
        err_msg, json_is_fine = self.check_json_dict(json_dict)
        if json_is_fine:
            # check_hilbert_space_dimension
            dim_err_msg, dim_ok = self.check_dimension(json_dict)
            if dim_ok:
                for exp in json_dict:
                    exp_dict = {exp: json_dict[exp]}
                    # prepare the shots folder
                    remoteClient.reset_shot_output_folder()
                    modify_shot_output_folder(job_id + "/" + str(exp))

                    # Here we generate the ciruit
                    result_draft["results"].append(self.gen_circuit(exp_dict, job_id))

                status_msg_dict.detail += "; Passed json sanity check; Compilation done. \
                    Shots sent to solver."
                status_msg_dict.status = "DONE"
                result_dict = ResultDict(**result_draft)
                return result_dict, status_msg_dict

            status_msg_dict.detail += (
                ";Failed dimensionality test. Too many atoms. File will be deleted. Error message: "
                + dim_err_msg
            )
            status_msg_dict.error_message += (
                ";Failed dimensionality test. Too many atoms. File will be deleted. Error message: "
                + dim_err_msg
            )
            status_msg_dict.status = "ERROR"

            result_dict = ResultDict(**result_draft)
            return result_dict, status_msg_dict

        status_msg_dict.detail += (
            "; Failed json sanity check. File will be deleted. Error message : "
            + err_msg
        )
        status_msg_dict.error_message += (
            "; Failed json sanity check. File will be deleted. Error message : "
            + err_msg
        )
        status_msg_dict.status = "ERROR"

        result_dict = ResultDict(**result_draft)
        return result_dict, status_msg_dict


# This is the spooler object that is used by the main function.
spooler_object = MotSpooler(
    ins_schema_dict={
        "barrier": MeasureBarrierInstruction,
        "measure": MeasureBarrierInstruction,
        "load": LoadInstruction,
    },
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
