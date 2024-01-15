"""
This is the file that creates the labscript file and sends it to the BLACS. It is unlikely
that we will need to change this file. It is a bit messy but it works.
"""
import os
from time import sleep
from decouple import config
import numpy as np

import runmanager.remote  # pylint: disable=import-error
from lyse import Run  # pylint: disable=import-error

from sqooler.schemes import ExperimentDict
from sqooler.utils import create_memory_data

remoteClient = runmanager.remote.Client()


# in the labscript ini file this is equivalent to the the path `labscriptlib`

EXP_SCRIPT_FOLDER = config("EXP_SCRIPT_FOLDER")

# local files
HEADER_PATH = f"{EXP_SCRIPT_FOLDER}/header.py"
REMOTE_EXPERIMENTS_PATH = f"{EXP_SCRIPT_FOLDER}/remote_experiments"

# how long should we wait for runs until we have a look again ?
T_WAIT = 2


def get_file_queue(dir_path: str) -> list:
    """
    A function that returns the list of files in the directory.
    """
    files = list(fn for fn in next(os.walk(dir_path))[2])
    return files


def modify_shot_output_folder(new_dir: str) -> None:
    """
    I am not sure what this function does.

    Args:
        new_dir: The new directory under which we save the shots.
    """
    defaut_shot_folder = str(remoteClient.get_shot_output_folder())
    print(f"Default shot folder: {defaut_shot_folder}")
    modified_shot_folder = (defaut_shot_folder.rsplit("\\", 1)[0]) + "/" + new_dir
    print(f"Modified shot folder: {modified_shot_folder}")
    remoteClient.set_shot_output_folder(modified_shot_folder)


def gen_script_and_globals(json_dict: dict, job_id: str) -> ExperimentDict:
    """
    This is the main script that generates the labscript file.

    Args:
        json_dict: The dictionary that contains the instructions for the circuit.
        job_id: The user id of the user that is running the experiment.

    Returns:
        The path to the labscript file.
    """
    exp_name = next(iter(json_dict))
    ins_list = json_dict[next(iter(json_dict))]["instructions"]
    n_shots = json_dict[next(iter(json_dict))]["shots"]

    globals_dict = {
        "job_id": "guest",
        "shots": 4,
    }
    globals_dict["shots"] = np.arange(n_shots)
    globals_dict["job_id"] = job_id

    remoteClient.set_globals(globals_dict)
    script_name = f"experiment_{globals_dict['job_id']}.py"
    exp_script = os.path.join(REMOTE_EXPERIMENTS_PATH, script_name)
    ins_list = json_dict[next(iter(json_dict))]["instructions"]
    print(f"File path: {exp_script}")
    code = ""
    # this is the top part of the script it allows us to import the
    # typical functions that we require for each single sequence
    with open(HEADER_PATH, "r", encoding="UTF-8") as header_file:
        code = header_file.read()

    # add a line break to the code
    code += "\n"
    # pylint: disable=bare-except
    try:
        with open(exp_script, "w", encoding="UTF-8") as script_file:
            script_file.write(code)
    except:
        print("Something wrong. Does file path exists?")

    for inst in ins_list:
        # we can directly use the function name as we have already verified
        # that the function exists in the `add_job` function
        func_name = inst[0]
        params = "(" + str(inst[1:])[1:-1] + ")"
        code = "Experiment." + func_name + params + "\n"

        # we should add proper error handling here
        # pylint: disable=bare-except
        try:
            with open(exp_script, "a", encoding="UTF-8") as script_file:
                script_file.write(code)
        except:
            print("Something wrong. Does file path exists?")

    code = "Experiment.final_action()" + "\n" + "stop(Experiment.t+0.1)"
    # pylint: disable=bare-except
    try:
        with open(exp_script, "a", encoding="UTF-8") as script_file:
            script_file.write(code)
    except:
        print("Something wrong. Does file path exists?")
    remoteClient.set_labscript_file(
        exp_script
    )  # CAUTION !! This command only selects the file. It does not generate it!

    # be careful. This is not a blocking command
    remoteClient.engage()

    # now that we have engaged the calculation we need to wait for the
    # calculation to be done

    # we need to get the current shot output folder
    current_shot_folder = remoteClient.get_shot_output_folder()

    # we need to get the list of files in the folder
    hdf5_files = get_file_queue(current_shot_folder)

    # we need to wait until we have the right number of files
    while len(hdf5_files) < n_shots:
        sleep(T_WAIT)
        hdf5_files = get_file_queue(current_shot_folder)

    shots_array = []
    # once the files are there we can read them
    for file in hdf5_files:
        run = Run(current_shot_folder + "/" + file)
        got_nat = False
        n_tries = 0
        # sometimes the file is not ready yet. We need to wait a bit
        while not got_nat and n_tries < 15:
            # the exception is raised if the file is not ready yet
            # it is broadly defined within labscript so we cannot do anything about
            # it here.
            # pylint: disable=W0718
            try:
                print(run.get_results("/measure", "nat"))
                # append the result to the array
                shots_array.append(run.get_results("/measure", "nat"))
                got_nat = True
            except Exception as exc:
                print(exc)
                sleep(T_WAIT)
                n_tries += 1
    print(f"Shots array: {shots_array}")

    exp_sub_dict = create_memory_data(shots_array, exp_name, n_shots)
    return exp_sub_dict
