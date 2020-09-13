"""ob.py -- one-body operator definitions and functions

This file defines one-body operator functions and documents the syntax
for one-body matrix element sources.

A one-body source is defined by the dictionary mapping:
    id: parameter_dict
where parameters_dict can contain:
    "qn": tuple of (j0,g0,tz0)
    "builtin": "kinematic"|"am"|"isospin"|"solid-harmonic"
    "tensor-product": [factor_a_id, factor_b_id]
    "linear-combination": CoefficientDict({"a": c_a, "b": c_b, ...})
    "filename": input filename str
    "orbital_filename": orbital filename str (for generation in a larger space)

A one-body operator (a.k.a target) is defined by the tuple:
    (name, qn, operator_id)
where operator_id is the id of an obme source.

Patrick J. Fasano
University of Notre Dame

- 09/09/20 (pjf): Created, with some content from operators.py
- 09/12/20 (pjf): Overhaul logic for generating one-body targets and sources.
"""
import collections
import math
import re

import mcscript.utils

from .. import (
    environ,
    utils,
    modes,
)
from . import tb

################################################################
# kinematic operators
################################################################

k_kinematic_operators = {
    "identity": {"builtin": "kinematic", "qn": (0,0,0)},
    "r":        {"builtin": "kinematic", "qn": (1,1,0)},
    "r.r":      {"builtin": "kinematic", "qn": (0,0,0)},
    "ik":       {"builtin": "kinematic", "qn": (1,1,0)},
    "ik.ik":    {"builtin": "kinematic", "qn": (0,0,0)},
}

################################################################
# angular momentum operators
################################################################

k_am_operators = {
    "j":  {"builtin": "am", "qn": (1,0,0)},
    "j2": {"builtin": "am", "qn": (1,0,0)},
    "l":  {"builtin": "am", "qn": (1,0,0)},
    "l2": {"builtin": "am", "qn": (1,0,0)},
    "s":  {"builtin": "am", "qn": (1,0,0)},
    "s2": {"builtin": "am", "qn": (1,0,0)},
    "sp": {"tensor-product": ["delta_p", "s"], "qn": (1,0,0)},
    "sn": {"tensor-product": ["delta_n", "s"], "qn": (1,0,0)},
    "sp2": {"tensor-product": ["delta_p", "s2"], "qn": (0,0,0)},
    "sn2": {"tensor-product": ["delta_n", "s2"], "qn": (0,0,0)},
}

################################################################
# isospin operators
################################################################
k_isospin_operators = {
    "tz": {"builtin": "isospin", "qn": (0,0,0)},
    "t+": {"builtin": "isospin", "qn": (0,0,+1)},
    "t-": {"builtin": "isospin", "qn": (0,0,-1)},
    "delta_p": {"linear-combination": mcscript.utils.CoefficientDict({"identity": 0.5, "tz": +1.0}), "qn": (0,0,0)},
    "delta_n": {"linear-combination": mcscript.utils.CoefficientDict({"identity": 0.5, "tz": -1.0}), "qn": (0,0,0)},
}

################################################################
# ladder operators
################################################################
k_ladder_operators_native = {
    "c+": {"builtin": "ladder", "qn": (1,1,0)},
    "c-": {"builtin": "ladder", "qn": (1,1,0)},
}

def ladder_operators_generic(hw):
    """Generate ladder operator source info for generic basis.

    Arguments:
        hw (float): hw of basis

    Returns:
        (dict): operator sources
    """

    qn = (1,1,0)
    b = utils.oscillator_length(hw)
    sources = {}
    sources["c+"] = {
        "linear-combination": mcscript.utils.CoefficientDict({
            "r": 1/b, "ik": -b
        }),
        "qn": qn
    }
    sources["c"] = {
        "linear-combination": mcscript.utils.CoefficientDict({
            "r": 1/b, "ik": b
        }),
        "qn": qn
    }

    return sources

################################################################
# solid harmonic operators
################################################################
def solid_harmonic_source(coordinate, order, j0=None):
    """Generate solid harmonic source info.

    Arguments:
        coordinate (str): "r" or "ik"
        order (int): power of coordinate (i.e. r^n)
        j0 (int, optional): rank of spherical harmonic (defaults to order)

    Returns:
        (id (str), source (dict)): id and source dictionary
    """
    if j0 is None:
        j0 = order
    if coordinate not in {"r", "ik"}:
        raise mcscript.exception.ScriptError("unknown coordinate {}".format(coordinate))

    qn = (j0,j0%2,0)  # (j0,g0,tz0)
    identifier = "{:s}{:d}Y{:d}".format(coordinate, order, j0)
    source_dict = {
        "builtin": "solid-harmonic", "coordinate": "r", "order": order, "qn": qn
    }
    return (identifier, source_dict)

################################################################
# predefined sets
################################################################

k_h2mixer_builtin = {
    "identity",
    "j",  # this is safe, as our orbitals are always eigenstates of j
    "l2", "s2", "j2",
    "tz",
}

################################################################
# obme sources
################################################################
def generate_ob_observable_sets(task):
    """
    """
    ob_observables = []
    obme_sources = {}
    ob_observable_sets = task.get("ob_observable_sets", [])
    for name in ob_observable_sets:
        # special case for E0
        if name == "E0":
            qn = (0,0,0)
            coefficient = utils.oscillator_length(task["hw"])**2
            ob_observables += [
                ("E0p", qn, "E0p"),
                ("E0n", qn, "E0p"),
            ]
            obme_sources["r.r"] = k_kinematic_operators["r.r"]
            obme_sources["E0p"] = {
                "tensor-product": ["delta_p", "r.r"],
                "coefficient": coefficient,
                "qn": qn
            }
            obme_sources["E0n"] = {
                "tensor-product": ["delta_n", "r.r"],
                "coefficient": coefficient,
                "qn": qn
            }
            continue

        # electric transitions (general)
        match = re.fullmatch(r"E([0-9]+)", name)
        if match:
            order = int(match.group(1))
            qn = (order,order%2,0)
            (j0, _, _) = qn
            coefficient = utils.oscillator_length(task["hw"])**order
            ob_observables += [
                ("E{}p".format(order), qn, "E{}p".format(order)),
                ("E{}n".format(order), qn, "E{}n".format(order)),
            ]
            (solid_harmonic_id, solid_harmonic_def) = solid_harmonic_source("r", order, j0)
            obme_sources[solid_harmonic_id] = solid_harmonic_def
            obme_sources["E{}p".format(order)] = {
                "tensor-product": ["delta_p", solid_harmonic_id],
                "coefficient": coefficient,
                "qn": qn
            }
            obme_sources["E{}n".format(order)] = {
                "tensor-product": ["delta_n", solid_harmonic_id],
                "coefficient": coefficient,
                "qn": qn
            }
            continue

        # special case for M1
        if name == "M1":
            qn = (1,0,0)
            coefficient = math.sqrt(3/(4*math.pi))
            ob_observables += [
                ("Dlp", qn, "Dlp"),
                ("Dln", qn, "Dln"),
                ("Dsp", qn, "Dsp"),
                ("Dsn", qn, "Dsn"),
                ("M1", qn, "M1"),
            ]
            obme_sources["l"] = k_am_operators["l"]
            obme_sources["s"] = k_am_operators["s"]
            obme_sources["Dlp"] = {
                "tensor-product": ["delta_p", "l"], "coefficient": coefficient, "qn": qn
            }
            obme_sources["Dln"] = {
                "tensor-product": ["delta_n", "l"], "coefficient": coefficient, "qn": qn
            }
            obme_sources["Dsp"] = {
                "tensor-product": ["delta_p", "s"], "coefficient": coefficient, "qn": qn
            }
            obme_sources["Dsn"] = {
                "tensor-product": ["delta_n", "s"], "coefficient": coefficient, "qn": qn
            }
            obme_sources["M1"] = {
                "linear-combination": {
                    "Dlp": 1.0,
                    # "Dln": 0.0,
                    "Dsp": 5.5856946893,  # NIST CODATA 2018
                    "Dsn": -3.82608545,   # NIST CODATA 2018
                },
                "qn": qn,
            }
            continue

        # magnetic transitions (general)
        match = re.fullmatch(r"M([0-9]+)", name)
        if match:
            order = int(match.group(1))
            if order == 0:
                raise mcscript.exception.ScriptError("you must construct additional magnetic monopoles")
            qn = (order,(order-1)%2,0)
            l_coefficient = math.sqrt((2*order+1)*order) * 2/(order+1)
            s_coefficient = math.sqrt((2*order+1)*order)
            ob_observables += [
                ("M{}lp".format(order), qn, "M{}lp".format(order)),
                ("M{}ln".format(order), qn, "M{}ln".format(order)),
                ("M{}sp".format(order), qn, "M{}sp".format(order)),
                ("M{}sn".format(order), qn, "M{}sn".format(order)),
                ("M{}".format(order), qn, "M{}".format(order)),
            ]
            obme_sources["l"] = k_am_operators["l"]
            obme_sources["s"] = k_am_operators["s"]
            (solid_harmonic_id, solid_harmonic_def) = solid_harmonic_source("r", order-1, j0-1)
            obme_sources[solid_harmonic_id] = solid_harmonic_def
            obme_sources["l"+solid_harmonic_id] = {
                "tensor-product": ["l", solid_harmonic_id], "qn": qn
            }
            obme_sources["s"+solid_harmonic_id] = {
                "tensor-product": ["s", solid_harmonic_id], "qn": qn
            }
            obme_sources["M{}lp".format(order)] = {
                "tensor-product": ["delta_p", "l"+solid_harmonic_id],
                "coefficient": l_coefficient,
                "qn": qn
            }
            obme_sources["M{}ln".format(order)] = {
                "tensor-product": ["delta_n", "l"+solid_harmonic_id],
                "coefficient": l_coefficient,
                "qn": qn
            }
            obme_sources["M{}sp".format(order)] = {
                "tensor-product": ["delta_p", "s"+solid_harmonic_id],
                "coefficient": s_coefficient,
                "qn": qn
            }
            obme_sources["M{}sn".format(order)] = {
                "tensor-product": ["delta_n", "s"+solid_harmonic_id],
                "coefficient": s_coefficient,
                "qn": qn
            }
            obme_sources["M1"] = {
                "linear-combination": {
                    "M{}lp".format(order): 1.0,
                    # "M{}ln".format(order): 0.0,
                    "M{}sp".format(order): 5.5856946893,  # NIST CODATA 2018
                    "M{}sn".format(order): -3.82608545,   # NIST CODATA 2018
                },
                "qn": qn,
            }

            continue

        if name in {"F", "beta"}:
            qn = (0,0,1)
            ob_observables += [("F", qn, "t+")]
            obme_sources["t+"] = k_isospin_operators["t+"]

        if name in {"GT", "beta"}:
            qn = (1,0,1)
            ob_observables += [("GT", qn, "GT")]
            obme_sources["t+"] = k_isospin_operators["t+"]
            obme_sources["s"] = k_am_operators["s"]
            obme_sources["GT"] = {"tensor-product": ["s", "t+"], "qn": qn}

    return (ob_observables, obme_sources)

def get_obme_targets_h2mixer(task, tbme_targets):
    """Get OBME target list for h2mixer for a given set of TBME targets.

    These are the sources required internally by h2mixer, for upgrading to
    two-body via U or V.

    Arguments:
        task (dict): as described in module docstring
        tbme_targets (list of target dicts): list of TBME target dictionaries

    Returns:
        (set of str): set of OBME targets for h2mixer
    """
    # accumulate obme targets
    obme_targets = set()

    # extract dependencies from tbme targets
    #   postfix is irrelevant for this purpose
    tbme_sources = tb.get_tbme_sources(task, tbme_targets, postfix="")
    for tbme_source in tbme_sources.values():
        if "operatorU" in tbme_source:
            obme_targets.add(tbme_source["operatorU"])
        if "operatorV" in tbme_source:
            obme_targets.update(tbme_source["operatorV"])

    return obme_targets

def get_obme_targets_observables(task):
    """Get OBME target set for observables.

    These are the sources required for one-body observables, i.e. for input to
    obscalc-ob.

    Arguments:
        task (dict): as described in module docstring

    Returns:
        (set of str): set of observable OBME targets
    """
    # accumulate obme targets
    obme_targets = set()

    for (basename, qn, operator) in generate_ob_observable_sets(task)[0]:
        obme_targets.add(operator)
    for (basename, qn, operator) in task.get("ob_observables", []):
        obme_targets.add(operator)

    return obme_targets

def get_obme_targets_obmixer(task):
    """Get OBME target set for output by obmixer.

    These are the sources for observables plus the sources which cannot be
    generated within h2mixer.

    Arguments:
        task (dict): as described in module docstring

    Returns:
        (set of str): set of OBME targets for obmixer
    """
    # accumulate obme targets
    obme_targets = set()

    # get h2mixer targets and connected sources
    tbme_targets_by_qn = tb.get_tbme_targets(task, builtin_scalar_targets=True)
    obme_targets_h2mixer = set()
    for tbme_targets in tbme_targets_by_qn.values():
        obme_targets_h2mixer.update(
            get_obme_targets_h2mixer(task, tbme_targets)  # postfix doesn't matter
        )
    obme_sources_h2mixer = get_obme_sources(task, obme_targets_h2mixer)

    # iterate over sources and accumulate those which cannot
    # be generated by h2mixer as targets for obmixer
    for (identifier, source) in obme_sources_h2mixer.items():
        if ("builtin" in source) and (identifier not in k_h2mixer_builtin):
            obme_targets.add(identifier)

    # add observable targets
    obme_targets.update(get_obme_targets_observables(task))

    return obme_targets

def get_obme_sources(task, targets):
    """Get OBME sources for task.

    Arguments:
        task (dict): as described in module docstring
        targets (set): set of targets to generate

    Returns:
        (OrderedDict of dict): id to source mapping, sorted in reverse
            topological order
    """
    # accumulate sources
    obme_sources = {}

    # gather pre-defined sources first
    obme_sources.update(**k_kinematic_operators, **k_am_operators, **k_isospin_operators)
    if task.get("basis_mode") in {modes.BasisMode.kDirect, modes.BasisMode.kDilated}:
        obme_sources.update(**k_ladder_operators_native)
    else:
        obme_sources.update(**ladder_operators_generic(task["hw"]))


    # add sources from observable sets
    obme_sources.update(**generate_ob_observable_sets(task)[1])

    # override with user-defined sources
    user_obme_sources = task.get("obme_sources", [])
    for (source_id, source) in user_obme_sources:
        obme_sources[source_id] = source

    # construct dependency graph
    obme_dependency_graph = {}
    for (source_id, source) in obme_sources.items():
        if source.get("linear-combination"):
            obme_dependency_graph[source_id] = source["linear-combination"].keys()
        elif source.get("tensor-product"):
            obme_dependency_graph[source_id] = source["tensor-product"]
        else:
            obme_dependency_graph[source_id] = []

    # construct minimal set of sources (in reverse topological order)
    sorted_obme_sources = collections.OrderedDict()
    for id_ in reversed(mcscript.utils.topological_sort(obme_dependency_graph, targets)):
        sorted_obme_sources[id_] = obme_sources[id_]

    return sorted_obme_sources

def get_obme_sources_h2mixer(task, targets, postfix):
    """Get OBME sources for task (for use by h2mixer).

    This modifies the list of OBME sources generated by get_obme_sources()
    by determining which sources are written to file by obmixer, and reading
    them from file instead of regenerating them.

    Arguments:
        task (dict): as described in module docstring
        targets (set): set of targets to generate

    Returns:
        (OrderedDict of dict): id to source mapping, sorted in reverse
            topological order
    """
    # input normalization
    if not isinstance(targets, set):
        targets = set(targets)

    # get obme sources
    obme_sources = get_obme_sources(task, targets)

    # sources which were previously a target for obmixer should now be file inputs
    #   this is achieved by erasing their dependency information; this
    #   turns them into leaf nodes
    for identifier in (get_obme_targets_obmixer(task) & targets):
        obme_sources[identifier] = {
            "filename": environ.obme_filename(postfix, identifier),
            "qn": obme_sources[identifier]["qn"]
        }

    # re-construct dependency graph
    obme_dependency_graph = {}
    for (source_id, source) in obme_sources.items():
        if source.get("linear-combination"):
            obme_dependency_graph[source_id] = source["linear-combination"].keys()
        elif source.get("tensor-product"):
            obme_dependency_graph[source_id] = source["tensor-product"]
        else:
            obme_dependency_graph[source_id] = []

    # re-construct minimal set of sources (in reverse topological order)
    sorted_obme_sources = collections.OrderedDict()
    for id_ in reversed(mcscript.utils.topological_sort(obme_dependency_graph, targets)):
        sorted_obme_sources[id_] = obme_sources[id_]

    return sorted_obme_sources
