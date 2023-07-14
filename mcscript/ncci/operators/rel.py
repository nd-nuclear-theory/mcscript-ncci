"""rel.py -- define relative and relative-cm operators for moshinsky input

This file defines relative and relative-cm operator functions and documents the
syntax for rel/relcm matrix element sources.

A relative or relative-cm source is defined by the mapping:
    id: parameters
where `parameters` is a dict containing the following keys:
    "type" (RelativeOperatorType): relative or relative-cm operator
    "qn" (tuple of int): tuple of (J0,g0,T0_min,T0_max)
    "hw" (float or None): hw of operator or None for hw-independent operators
    "Nmax" (int): Nmax for source
    "source_type" (str):
        ("file"|"jpv"|"relative-gen"|"relcm-gen"|"relative-xform") type of
        source, used to select generator
    "parameters" (dict): additional parameters to be passed to generator
    "inputs" (list of str): dependencies of the current source

Depending on the "source_type", the "parameters" may contain:
    "file":
        "filename" (optional): explicit path to input relative or relative-cm
            matrix elements; deduced/searched for if not provided

A relative target/operator is the tuple
    (name, qn, id)

A moshinsky target/operator is the tuple
    (name, qn, parameters)
where parameters` is a dict containing the following keys:
    "id": relative or relative-cm source
    "truncation": output (rank, cutoff) truncation, e.g., ("tb", 10)


Patrick J. Fasano
University of Notre Dame

- 04/13/22 (pjf): Created, based on ob.py.
- 06/29/22 (pjf): Initial implementation completed.
"""
from __future__ import annotations
import collections
import enum
import math
from typing import Optional, OrderedDict

import mcscript.utils
import mcscript.exception

from .. import (
    constants,
    environ,
    utils,
    modes,
)

@enum.unique
class RelativeOperatorType(enum.Enum):
    kRelative = 'rel'
    kRelativeCM = 'relcm'

################################################################
# relative-gen operators
################################################################

def relative_zero(Nmax:int):
    """Generate source definition for zero operator in relative coordinates.

    Arguments:
        Nmax (int): truncation for operator

    Returns:
        (dict): zero operator source
    """
    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (0,0,0,0),
        "hw": None,
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {"operator_name": "zero"},
    }

def relative_identity(Nmax:int):
    """Generate source definition for identity operator in relative coordinates.

    Arguments:
        Nmax (int): truncation for operator

    Returns:
        (dict): identity operator source
    """
    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (0,0,0,0),
        "hw": None,
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {"operator_name": "identity"},
    }

def relative_coordinate_sqr(Nmax:int, coordinate:str, T0:int):
    """Generate source definition for relative coordinate-squared (r^2 or k^2) operator.

    Arguments:
        Nmax (int): truncation for operator
        coordinate (str): type of operator (r or k)
        T0 (int): isospin tensor character of operator

    Returns:
        (dict): relative coordinate-sqr operator source
    """
    if coordinate not in {"r", "k"}:
        raise mcscript.exception.ScriptError(f"unknown coordinate {coordinate}")

    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (0,0,T0,T0),
        "hw": utils.hw_from_oscillator_length(1.),
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {
            "operator_name": "coordinate-sqr",
            "coordinate_type": coordinate,
            "T0": f"{T0:d}",
        },
    }

def relative_dipole(Nmax:int, coordinate:str, T0:int):
    """Generate source definition for relative dipole operator (r or k) operator.

    Arguments:
        Nmax (int): truncation for operator
        coordinate (str): type of operator (r or k)
        T0 (int): isospin tensor character of operator

    Returns:
        (dict): relative dipole operator dictionary
    """
    if coordinate not in {"r", "k"}:
        raise mcscript.exception.ScriptError(f"unknown coordinate {coordinate}")

    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (1,1,T0,T0),
        "hw": utils.hw_from_oscillator_length(1.),
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {
            "operator_name": "dipole",
            "coordinate_type": coordinate,
            "T0": f"{T0:d}",
        },
    }

def relative_quadrupole(Nmax:int, coordinate:str, T0:int):
    """Generate source definition for relative quadrupole operator (r or k) operator.

    Arguments:
        Nmax (int): truncation for operator
        coordinate (str): type of operator (r or k)
        T0 (int): isospin tensor character of operator

    Returns:
        (dict): relative quadrupole operator source
    """
    if coordinate not in {"r", "k"}:
        raise mcscript.exception.ScriptError(f"unknown coordinate {coordinate}")

    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (2,0,T0,T0),
        "hw": utils.hw_from_oscillator_length(1.),
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {
            "operator_name": "quadrupole",
            "coordinate_type": coordinate,
            "T0": f"{T0:d}",
        },
    }

def relative_angular_momentum(Nmax:int, am_type:str, T0:int):
    """Generate source definition for two-body angular momentum (L or S) operator.

    Arguments:
        Nmax (int): truncation for operator
        am_type (str): type of operator (L or S)
        T0 (int): isospin tensor character of operator

    Returns:
        (dict): relative angular momentum operator source
    """
    if am_type not in {"L", "S"}:
        raise mcscript.exception.ScriptError(f"unknown angular momentum type {am_type}")

    am_type_dict = {"L": "orbital-am", "S": "spin-am"}

    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (1,0,T0,T0),
        "hw": None,
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {
            "operator_name": am_type_dict[am_type],
            "T0": f"{T0:d}",
        },
    }

def coulomb(Nmax:int, species:str, steps:int):
    """Generate source definition for two-body angular momentum (L or S) operator.

    Arguments:
        Nmax (int): truncation for operator
        species (str): type of operator ("p"|"n"|"total")
        steps (int): number of steps for integration

    Returns:
        (dict): coulomb operator dictionary
    """
    if species not in {"p", "n", "total"}:
        raise mcscript.exception.ScriptError(f"unknown species {species}")

    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (0,0,0,0 if species == "total" else 2),
        "hw": utils.hw_from_oscillator_length(1.),
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {
            "operator_name": "coulomb",
            "species": species,
            "steps": f"{steps:d}",
        },
    }

def symmetrized_relative_unit_tensor(
    Nmax:int, J0:int, T0:int,
    Np:int, Lp:int, Sp:int, Jp:int, Tp:int,
    N:int, L:int, S:int, J:int, T:int
):
    """Generate source definition for two-body symmetrized unit tensor operator.

    Arguments:
        Nmax (int): truncation for operator
        T0 (int): isospin tensor character of operator
        Np, Lp, Sp, Jp, Tp, N, L, S, J, T (int): quantum numbers

    Returns:
        (dict): symmetrized unit tensor operator dictionary
    """
    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (J0,(Lp+L)%2,T0,T0),
        "hw": None,
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {
            "operator_name": "symmunit",
            "T0": f"{T0:d}",
            "Np": f"{Np:d}",
            "Lp": f"{Lp:d}",
            "Sp": f"{Sp:d}",
            "Jp": f"{Jp:d}",
            "Tp": f"{Tp:d}",
            "N": f"{N:d}",
            "L": f"{L:d}",
            "S": f"{S:d}",
            "J": f"{J:d}",
            "T": f"{T:d}",
        },
    }

k_interaction_hw_dict = {"Daejeon16": 25}

def relative_interaction(Nmax:int, name:str, params:Optional[list]):
    """Generate source definition for two-body interaction.

    Arguments:
        Nmax (int): truncation for operator
        name (str): name of interaction
        params (list of str): additional (positional) parameters

    Returns:
        (dict): interaction operator dictionary
    """

    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (0,0,0,2),
        "hw": k_interaction_hw_dict.get(name),
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {
            "operator_name": "interaction",
            "interaction": name,
            "parameters": " ".join(params) if params else "",
        },
    }

def LENPIC_regulator_code(regulator_param:float) -> str:
    """Convert regulator paramater to LENPIC regulator code.

    Args:
        regulator_param (float): regulator parameter R in fm

    Raises:
        (ValueError): unrecognized regulator_param value

    Returns:
        (str): LENPIC regulator code
    """
    if math.isclose(regulator_param, 0.8):
        regulator_code = "A"
    if math.isclose(regulator_param, 0.9):
        regulator_code = "B"
    elif math.isclose(regulator_param, 1.0):
        regulator_code = "C"
    elif math.isclose(regulator_param, 1.1):
        regulator_code = "D"
    elif math.isclose(regulator_param, 1.2):
        regulator_code = "E"
    else:
        raise ValueError("LENPIC regulator codes only defined for R=0.8,0.9,1.0,1.1,1.2fm")

    return regulator_code

def LENPIC_SCS_N2LO_gamow_teller(Nmax:int, hw:float, regulator_param:float, steps:int):
    """Generate source definition for LENPIC SCS N2LO Gamow-Teller operator.

    Arguments:
        Nmax (int): truncation for operator
        hw (float): oscillator frequency for basis
        regulator_param (float): regulator length parameter
        steps (int): number of steps for integrations

    Returns:
        (dict): Gamow-Teller operator dictionary
    """
    if LENPIC_regulator_code(regulator_param) not in {"B","C"}:
        raise ValueError("LENPIC SCS Gamow-Teller operator only defined for R=0.9 and 1.0")

    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (1,0,1,1),
        "hw": hw,
        "Nmax": Nmax,
        "source_type": "relative-gen",
        "parameters": {
            "operator_name": "LENPIC-N2LOGT",
            "regulator": regulator_param,
            "oscillator_length": utils.oscillator_length(hw),
            "steps": steps,
        },
    }

def LENPIC_SCS_NLO_M1(Nmax:int, hw:float, regulator_param:float, steps:int):
    """Generate source definition for LENPIC SCS N2LO M1 operator.

    Arguments:
        Nmax (int): truncation for operator
        hw (float): oscillator frequency for basis
        regulator_param (float): regulator length parameter
        steps (int): number of steps for integrations

    Returns:
        (dict): Gamow-Teller operator dictionary
    """
    return {
        "type": RelativeOperatorType.kRelativeCM,
        "qn": (1,0,1,1),
        "hw": hw,
        "Nmax": Nmax,
        "source_type": "relcm-gen",
        "parameters": {
            "operator_name": "LENPIC-NLOM1",
            "regulator": regulator_param,
            "oscillator_length": utils.oscillator_length(hw),
            "steps": steps,
        },
    }

def dilated_operator(source_operator_id:str, source_operator:dict, target_Nmax:int, target_hw:float, steps:int=3000):
    """Generate source definition for numerically-dilated operator.

    Arguments:
        source_operator (dict): dict defining source (original hw) operator
        target_Nmax (int): new truncation after transform
        target_hw (float): new oscillator parameter hw after transform
        steps (int, optional): number of steps for overlap integrals

    Returns:
        (dict): operator dict for dilated operator
    """

    return {
        "type": source_operator["type"],
        "qn": source_operator["qn"],
        "hw": target_hw,
        "Nmax": target_Nmax,
        "source_type": "relative-xform",
        "parameters": {
            "steps": steps,
        },
        "inputs": [source_operator_id]
    }

def relative_operator_from_jpv(
    Nmax:int, hw:float, Jmax:int, *,
    source_filename:Optional[str]=None,
    source_filename_pp:Optional[str]=None,
    source_filename_nn:Optional[str]=None,
    source_filename_pn:Optional[str]=None,
) -> dict:
    """Generate source definition for operators converted from JPV relative format.

    Arguments:
        name (str): name of operator
        Nmax (int): input/output truncation
        hw (float): oscillator parameter of operator
        Jmax (int): maximum J included in files
        source_filename (str, optional): isoscalar operator file name. Defaults to None.
        source_filename_pp, source_filename_nn, source_filename_pn (str, optional): non-isoscalar filenames. Defaults to None.

    Returns:
        (dict): operator dict for converted operator
    """
    if source_filename:
        if (source_filename_pp or source_filename_nn or source_filename_pn):
            raise ValueError("source_filename_{pp,nn,pn} must not be given when source_filename is specified")
        T0_max = 0
        parameters = {"Jmax": Jmax, "source_filename": source_filename}
    elif (source_filename_pp and source_filename_nn and source_filename_pn):
        T0_max = 2
        parameters = {
            "Jmax": Jmax,
            "source_filename_pp": mcscript.utils.expand_path(source_filename_pp),
            "source_filename_nn": mcscript.utils.expand_path(source_filename_nn),
            "source_filename_pn": mcscript.utils.expand_path(source_filename_pn),
        }
    else:
        raise ValueError("must specify source_filename or all of source_filename_{pp,nn,pn}")

    return {
        "type": RelativeOperatorType.kRelative,
        "qn": (0,0,0,T0_max),
        "hw": hw,
        "Nmax": Nmax,
        "source_type": "jpv",
        "parameters": parameters
    }


def get_rel_targets(task) -> set[str]:
    """Extract list of relative targets from task.

    Arguments:
        task (dict): as described in module docstring

    Returns:
        (set of str): relative targets
    """
    # accumulate relative targets
    rel_targets = set()

    for (basename, qn, operator) in task.get("relative_targets", []):
        rel_targets.add(operator)
    for (basename, qn, parameters) in task.get("moshinsky_targets", []):
        rel_targets.add(parameters["id"])

    return rel_targets

def get_rel_sources(task:dict, targets:set[str]) -> collections.OrderedDict[str, dict]:
    """Get OBME sources for task.

    Arguments:
        task (dict): as described in module docstring
        targets (set): set of targets to generate

    Returns:
        (OrderedDict of dict): id to source mapping, sorted in reverse
            topological order
    """
    # accumulate sources
    rel_sources = {}

    # add user-defined sources
    user_rel_sources = task.get("relative_sources", [])
    for (source_id, source) in user_rel_sources:
        if source_id in rel_sources:
            print(f"WARN: overriding rel source '{source_id:s}' with {source}")
        rel_sources[source_id] = source

    # construct dependency graph
    rel_dependency_graph = {}
    for (source_id, source) in rel_sources.items():
        rel_dependency_graph[source_id] = []
        rel_dependency_graph[source_id] += source.get("inputs", [])

    # construct minimal set of sources (in reverse topological order)
    sorted_rel_sources = collections.OrderedDict()
    for id_ in reversed(mcscript.utils.topological_sort(rel_dependency_graph, targets)):
        sorted_rel_sources[id_] = rel_sources[id_]

    return sorted_rel_sources
