"""
Test module for the mot file.
"""

import pytest
from pydantic import ValidationError

from sqooler.spoolers import gate_dict_from_list
from sqooler.utils import run_json_circuit
from config import (
    spooler_object as spooler,
    MotExperiment,
    MeasureBarrierInstruction,
    LoadInstruction,
)


def test_pydantic_exp_validation() -> None:
    """
    Test that the validation of the experiment is working
    """
    experiment = {
        "instructions": [
            ["load", [7], []],
            ["load", [2], []],
            ["measure", [2], []],
            ["measure", [6], []],
            ["measure", [7], []],
        ],
        "num_wires": 1,
        "shots": 4,
        "wire_order": "interleaved",
    }
    MotExperiment(**experiment)

    with pytest.raises(ValidationError):
        poor_experiment = {
            "instructions": [
                ["load", [7], []],
                ["load", [2], []],
                ["measure", [2], []],
                ["measure", [6], []],
                ["measure", [7], []],
            ],
            "num_wires": 8,
            "shots": 4,
            "wire_order": "sequential",
        }
        MotExperiment(**poor_experiment)


def test_barrier_instruction() -> None:
    """
    Test that the barrier instruction is properly constrained.
    """
    inst_list = ["barrier", [0], []]
    gate_dict = gate_dict_from_list(inst_list)
    MeasureBarrierInstruction(**gate_dict.model_dump())
    # test that the name is nicely fixed
    with pytest.raises(ValidationError):
        poor_inst_list = ["barriers", [7], []]
        gate_dict = gate_dict_from_list(poor_inst_list)
        MeasureBarrierInstruction(**gate_dict.model_dump())

    # test that we cannot give too many wires
    with pytest.raises(ValidationError):
        poor_inst_list = ["barrier", [0, 1, 2, 3, 4, 5, 6, 7, 8], []]
        gate_dict = gate_dict_from_list(poor_inst_list)
        MeasureBarrierInstruction(**gate_dict.model_dump())

    # make sure that the wires cannot be above the limit
    with pytest.raises(ValidationError):
        poor_inst_list = ["barrier", [8], []]
        gate_dict = gate_dict_from_list(poor_inst_list)
        MeasureBarrierInstruction(**gate_dict.model_dump())

    # make sure that the parameters are enforced to be empty
    with pytest.raises(ValidationError):
        poor_inst_list = ["barrier", [7], [2.3]]
        gate_dict = gate_dict_from_list(poor_inst_list)
        MeasureBarrierInstruction(**gate_dict.model_dump())


def test_load_measure_instruction() -> None:
    """
    Test that the barrier instruction is properly constrained.
    """
    inst_list = ["load", [0], [2]]
    gate_dict = gate_dict_from_list(inst_list)
    LoadInstruction(**gate_dict.model_dump())

    inst_list = ["measure", [0], []]
    gate_dict = gate_dict_from_list(inst_list)
    MeasureBarrierInstruction(**gate_dict.model_dump())

    # test that the name is nicely fixed
    with pytest.raises(ValidationError):
        poor_inst_list = ["loads", [0], []]
        gate_dict = gate_dict_from_list(poor_inst_list)
        LoadInstruction(**gate_dict.model_dump())

    # test that we cannot give too many wires
    with pytest.raises(ValidationError):
        poor_inst_list = ["load", [0, 1], [2]]
        gate_dict = gate_dict_from_list(poor_inst_list)
        LoadInstruction(**gate_dict.model_dump())

    # make sure that the wires cannot be above the limit
    with pytest.raises(ValidationError):
        poor_inst_list = ["load", [2], [3]]
        gate_dict = gate_dict_from_list(poor_inst_list)
        LoadInstruction(**gate_dict.model_dump())

    # make sure that the parameters are enforced to be empty
    with pytest.raises(ValidationError):
        poor_inst_list = ["measure", [0], [2.3]]
        gate_dict = gate_dict_from_list(poor_inst_list)
        LoadInstruction(**gate_dict.model_dump())


def test_load_gate() -> None:
    """
    Test that the loading is properly working.
    """

    # first submit the job
    job_payload = {
        "experiment_0": {
            "instructions": [
                ["load", [0], [20]],
                ["measure", [0], []],
            ],
            "num_wires": 1,
            "shots": 2,
            "wire_order": "interleaved",
        },
    }

    job_id = "81"
    data = run_json_circuit(job_payload, job_id, spooler)

    shots_array = data["results"][0]["data"][  # pylint: disable=unsubscriptable-object
        "memory"
    ]
    print(shots_array)
    assert data["job_id"] == job_id, "job_id got messed up"
    assert len(shots_array) == 2, "shots_array got messed up"
    assert shots_array[0] == "20", "shots_array got messed up"


def test_number_experiments() -> None:
    """
    Make sure that we cannot submit too many experiments.
    """

    # first test the system that is fine.
    job_payload = {
        "experiment_0": {
            "instructions": [
                ["load", [0], [30]],
                ["measure", [0], []],
            ],
            "num_wires": 1,
            "shots": 4,
            "wire_order": "interleaved",
        },
    }
    job_id = "21"
    data = run_json_circuit(job_payload, job_id, spooler)

    shots_array = data["results"][0]["data"]["memory"]
    assert data["job_id"] == job_id, "job_id got messed up"
    assert len(shots_array) == 4, "shots_array got messed up"
    assert shots_array[0] == "30", "shots_array got messed up"

    inst_dict = {
        "instructions": [
            ["load", [0], [50]],
            ["measure", [0], []],
        ],
        "num_wires": 1,
        "shots": 4,
        "wire_order": "interleaved",
    }

    # and now run too many experiments
    n_exp = 2000
    job_payload = {}
    for ii in range(n_exp):
        job_payload[f"experiment_{ii}"] = inst_dict
    job_id = "1"
    with pytest.raises(AssertionError):
        data = run_json_circuit(job_payload, job_id, spooler)


def test_spooler_config() -> None:
    """
    Test that the back-end is properly configured and we can indeed provide those parameters
     as we would like.
    """
    config_dict = {
        "description": ("Setup of an atomic mot."),
        "version": "0.1",
        "display_name": "",
        "cold_atom_type": "spin",
        "gates": [],
        "max_experiments": 1000,
        "max_shots": 100,
        "simulator": True,
        "supported_instructions": [
            "barrier",
            "measure",
            "load",
        ],
        "num_wires": 1,
        "wire_order": "interleaved",
        "num_species": 1,
        "operational": True,
        "pending_jobs": None,
        "status_msg": None,
        "last_queue_check": None,
        "sign": False,
    }
    spooler_config = spooler.get_configuration()
    assert spooler_config.model_dump() == config_dict


def test_add_job() -> None:
    """
    Test if we can simply add jobs as we should be able too.
    """

    # first test the system that is fine.
    job_payload = {
        "experiment_0": {
            "instructions": [
                ["load", [0], [31]],
                ["measure", [0], []],
            ],
            "num_wires": 1,
            "shots": 2,
            "wire_order": "interleaved",
        },
    }

    job_id = "41"

    result_dict = run_json_circuit(job_payload, job_id, spooler)
    # assert that all the elements in the result dict memory are of string '1 0'
    expected_value = "31"
    for element in result_dict["results"][0][  # pylint: disable=unsubscriptable-object
        "data"
    ]["memory"]:
        assert (
            element == expected_value
        ), f"Element {element} is not equal to {expected_value}"
