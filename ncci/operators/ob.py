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
"""
import collections
import math
import re

import mcscript.utils

from .. import (
    environ,
    utils,
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
    "t+": {"builtin": "isospin", "qn": (0,0,1)},
    "t-": {"builtin": "isospin", "qn": (0,0,1)},
    "delta_p": {"linear-combination": mcscript.utils.CoefficientDict({"identity": 0.5, "tz": +1.0}), "qn": (0,0,0)},
    "delta_n": {"linear-combination": mcscript.utils.CoefficientDict({"identity": 0.5, "tz": -1.0}), "qn": (0,0,0)},
}

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
            obme_sources["E0p"] = {"tensor-product": ["delta_p", "r.r"], "coefficient": coefficient, "qn": qn}
            obme_sources["E0n"] = {"tensor-product": ["delta_n", "r.r"], "coefficient": coefficient, "qn": qn}
            obme_sources["r.r"] = k_kinematic_operators["r.r"]
            continue

        # electric transitions (general)
        match = re.fullmatch(r"E([0-9]+)", name)
        if match:
            order = int(match.group(1))
            qn = (order,order%2,0)
            coefficient = utils.oscillator_length(task["hw"])**order
            ob_observables += [
                ("E{}p".format(order), qn, "E{}p".format(order)),
                ("E{}n".format(order), qn, "E{}n".format(order)),
            ]
            obme_sources["rY{:d}".format(order)] = {
                "builtin": "solid-harmonic",
                "coordinate": "r", "order": order,
                "qn": qn
            }
            obme_sources["E{}p".format(order)] = {
                "tensor-product": ["delta_p", "rY{:d}".format(order)],
                "coefficient": coefficient,
                "qn": qn
            }
            obme_sources["E{}n".format(order)] = {
                "tensor-product": ["delta_n", "rY{:d}".format(order)],
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
            ]
            obme_sources["l"] = k_am_operators["l"]
            obme_sources["s"] = k_am_operators["s"]
            obme_sources["Dlp"] = {"tensor-product": ["delta_p", "l"], "coefficient": coefficient, "qn": qn}
            obme_sources["Dln"] = {"tensor-product": ["delta_n", "l"], "coefficient": coefficient, "qn": qn}
            obme_sources["Dsp"] = {"tensor-product": ["delta_p", "s"], "coefficient": coefficient, "qn": qn}
            obme_sources["Dsn"] = {"tensor-product": ["delta_n", "s"], "coefficient": coefficient, "qn": qn}
            continue

        # magnetic transitions (general)
        match = re.fullmatch(r"M([0-9]+)", name)
        if match:
            order = int(match.group(1))
            if order == 0:
                raise mcscript.exception.ScriptError("you must construct additional magnetic monopoles")
            qn = (order,(order-1)%2,0)
            coefficient = utils.oscillator_length(task["hw"])**(order-1) * math.sqrt((2*order+1)*order)
            ob_observables += [
                ("M{}lp".format(order), qn, "M{}lp".format(order)),
                ("M{}ln".format(order), qn, "M{}ln".format(order)),
                ("M{}sp".format(order), qn, "M{}sp".format(order)),
                ("M{}sn".format(order), qn, "M{}sn".format(order)),
            ]
            obme_sources["l"] = k_am_operators["l"]
            obme_sources["s"] = k_am_operators["s"]
            obme_sources["rY{:d}".format(order-1)] = {
                "builtin": "solid-harmonic",
                "coordinate": "r", "order": order-1,
                "qn": (order-1,(order-1)%2,0)
            }
            obme_sources["lrY{:d}".format(order-1)] = {
                "tensor-product": ["l", "rY{:d}".format(order-1)], "qn": qn
            }
            obme_sources["srY{:d}".format(order-1)] = {
                "tensor-product": ["s", "rY{:d}".format(order-1)], "qn": qn
            }
            obme_sources["M{}lp".format(order)] = {
                "tensor-product": ["delta_p", "lrY{:d}".format(order-1)],
                "coefficient": coefficient * (2/(order+1)),
                "qn": qn
            }
            obme_sources["M{}ln".format(order)] = {
                "tensor-product": ["delta_n", "lrY{:d}".format(order-1)],
                "coefficient": coefficient * (2/(order+1)),
                "qn": qn
            }
            obme_sources["M{}sp".format(order)] = {
                "tensor-product": ["delta_p", "srY{:d}".format(order-1)],
                "coefficient": coefficient,
                "qn": qn
            }
            obme_sources["M{}sn".format(order)] = {
                "tensor-product": ["delta_n", "srY{:d}".format(order-1)],
                "coefficient": coefficient,
                "qn": qn
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

def get_obme_targets(task, tbme_targets=None, tbme_targets_only=False):
    """
    """
    if tbme_targets is None:
        tbme_targets = {}

    # accumulate obme targets
    obme_targets = collections.OrderedDict()

    # extract dependencies from tbme targets
    tbme_sources = tb.get_tbme_sources(task, tbme_targets)
    for tbme_source in tbme_sources.values():
        if "operatorU" in tbme_source:
            obme_targets[tbme_source["operatorU"]] = tbme_source["operatorU"]
        if "operatorV" in tbme_source:
            factor_a, factor_b = tbme_source["operatorV"]
            obme_targets[factor_a] = factor_a
            obme_targets[factor_b] = factor_b

    # remove tbme dependencies which can be satisfied within h2mixer
    ##obme_targets -= k_h2mixer_builtin

    # add one-body observables
    if not tbme_targets_only:
        for (basename, qn, operator) in generate_ob_observable_sets(task)[0]:
            obme_targets[basename] = operator
        for (basename, qn, operator) in task.get("ob_observables", []):
            obme_targets[basename] = operator

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

def get_obme_sources_h2mixer(task, targets):
    """Get OBME sources for task (for use by h2mixer).

    """
    # get tbme sources and flatten for all quantum numbers
    tbme_targets_by_qn = tb.get_tbme_targets(task, builtin_scalar_targets=True)
    tbme_targets = {k: d[k] for d in tbme_targets_by_qn.values() for k in d}

    # get obme sources
    obme_targets = get_obme_targets(task, tbme_targets)
    obme_sources = get_obme_sources(task, obme_targets.values())

    # sources which were previously a target should now be file inputs
    #   this is achieved by erasing their dependency information; this
    #   turns them into leaf nodes
    for (identifier, operator) in obme_targets.items():
        obme_sources[identifier] = {"qn": obme_sources[operator]["qn"]}

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
