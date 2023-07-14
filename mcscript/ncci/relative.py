"""relative.py -- generation and manipulation of relative matrix elements

Patrick J. Fasano
University of Notre Dame

- 03/20/22 (pjf): Created.
- 06/29/22 (pjf): Initial implementation completed.
- 07/06/22 (pjf): Add save_rel() and save_moshinsky().
"""
from __future__ import annotations
import glob
import os
from typing import Callable

import mcscript.control
import mcscript.utils
import mcscript.exception
import mcscript.task

from . import (
    utils,
    modes,
    environ,
    operators,
)


_k_rel_target_handlers:dict[str,Callable] = {}

def relative_filename_for_source(source_id:str, source:dict) -> str:
    """Generate relative filename for given source defintion.

    Arguments:
        source (dict): relative/relative-cm source as defined in operators.rel

    Returns:
        (str): filename for relative/relative-cm source
    """
    # if the source is a file, find it on the filesystem
    if source["source_type"] == "file":
        filename = source.get("parameters", {}).get("filename")
        if filename is not None:
            rel_filename = mcscript.utils.expand_path(filename)
            if not os.path.isfile(rel_filename):
                rel_filename = mcscript.utils.search_in_subdirectories(
                    environ.data_dir_rel_list, environ.rel_dir_list,
                    filename, fail_on_not_found=True
                )
        else:
            rel_filename = environ.find_rel_file(
                source_id, source["Nmax"], source["hw"]
            )
    # otherwise, find the filename we will use for output
    else:
        if source["type"] == operators.rel.RelativeOperatorType.kRelative:
            rel_filename = environ.rel_filename(source_id, source['Nmax'], source['hw'])
        elif source["type"] == operators.rel.RelativeOperatorType.kRelativeCM:
            rel_filename = environ.relcm_filename(source_id, source['Nmax'], source['hw'])
        else:
            raise ValueError("invalid operator type: {}".format(source["type"]))

    return rel_filename

_k_rel_target_handlers["file"] = (
    lambda source_id, sources: relative_filename_for_source(source_id, sources[source_id])
)

def _jpv2rel_handler(source_id:str, rel_sources:dict):
    source = rel_sources[source_id]
    parameters = source["parameters"]
    qn = source["qn"]
    (J0, g0, T0_min, T0_max) = qn
    if (J0 != 0) or (g0 != 0) or (T0_min != 0):
        raise mcscript.exception.ScriptError(f"invalid quantum numbers for jpv2rel: {qn}")
    rel_filename = relative_filename_for_source(source_id, source)

    lines = []
    lines.append(f"{source['Nmax']} {parameters['Jmax']} {T0_max:d}")
    if T0_max == 0:
        lines.append(parameters["source_filename"])
    else:
        lines.append('{source_filename_pp:s} {source_filename_nn:s} {source_filename_pn:s}'.format(**parameters))
    lines.append(rel_filename)
    lines += [""]

    mcscript.control.call(
        [
            environ.shell_filename("jpv2rel")
        ],
        input_lines=lines,
        mode=mcscript.control.CallMode.kSerial,
        check_return=True
    )

    return rel_filename

_k_rel_target_handlers["jpv"] = _jpv2rel_handler

_k_relativegen_operator_patterns = {
    "coordinate-sqr": " {coordinate_type:s} {T0:d}",
    "dipole": " {coordinate_type:s} {T0:d}",
    "quadrupole": " {coordinate_type:s} {T0:d}",
    "orbital-am": " {T0:d}",
    "spin-am": " {T0:d}",
    "coulomb": " {species:s} {steps:d}",
    "symmunit": " {T0:d} {Np:d} {Lp:d} {Sp:d} {Jp:d} {Tp:d} {N:d} {L:d} {S:d} {J:d} {T:d}",
    "interaction": " {interaction:s} {parameters:s}",
    "LENPIC-N2LOGT": " {regulator:g} {oscillator_length:15.8e} {steps:d}",
    "LENPIC-NLOM1": " {regulator:g} {oscillator_length:15.8e} {steps:d}",
}
def _relativegen_handler(source_id:str, rel_sources:dict):
    source = rel_sources[source_id]
    parameters = source["parameters"]
    qn = source["qn"]
    (J0, g0, T0_min, T0_max) = qn
    operator_name = parameters["operator_name"]
    rel_filename = relative_filename_for_source(source_id, source)

    lines = []
    lines += [f"{J0:d} {g0:d} {T0_min:d} {T0_max:d}"]
    lines += [f"{source['Nmax']:d}"]
    lines += [operator_name + _k_relativegen_operator_patterns.get(operator_name, "").format(**parameters)]
    lines += [rel_filename]
    lines += [""]

    mcscript.control.call(
        [
            environ.shell_filename(source["source_type"])
        ],
        input_lines=lines,
        mode=mcscript.control.CallMode.kSerial,
        check_return=True
    )

    return rel_filename

_k_rel_target_handlers["relative-gen"] = _relativegen_handler
_k_rel_target_handlers["relcm-gen"] = _relativegen_handler


def _relativexform_handler(source_id:str, rel_sources:dict):
    source = rel_sources[source_id]
    parameters = source["parameters"]
    input_source_id = source["inputs"][0]
    input_source = rel_sources[input_source_id]
    if source["qn"] != input_source["qn"]:
        raise mcscript.exception.ScriptError(
            "incompatible quantum numbers: {} {}".format(source["qn"],input_source["qn"])
        )
    rel_filename = relative_filename_for_source(source_id, source)

    # TODO: update once relative-xform is generalized
    if source["type"] != operators.rel.RelativeOperatorType.kRelative:
        raise ValueError("invalid operator type: {}".format(source["type"]))

    input_filename = relative_filename_for_source(input_source_id, input_source)

    b_ratio = utils.oscillator_length(source["hw"])/utils.oscillator_length(input_source["hw"])

    lines = []
    lines += [input_filename]
    lines += [f"{source['Nmax']:d} {b_ratio:.17e} {parameters['steps']:d}"]
    lines += [rel_filename]
    lines += [""]

    mcscript.control.call(
        [
            environ.shell_filename("relative-xform")
        ],
        input_lines=lines,
        mode=mcscript.control.CallMode.kSerial,
        check_return=True
    )

    return rel_filename

_k_rel_target_handlers["relative-xform"] = _relativexform_handler


def generate_rel_targets(task):
    """Generate relative and relative-cm matrix elements for task.

    Arguments:
        task (dict): as described in module docstring
    """
    # get targets
    targets = operators.rel.get_rel_targets(task)

    # get rel sources
    rel_sources = operators.rel.get_rel_sources(task, targets)

    # dispatch to handlers
    for source_id,source in rel_sources.items():
        _k_rel_target_handlers[source["source_type"]](source_id, rel_sources)

def generate_moshinsky_targets(task):
    """Perform Talmi-Moshinsky transformation for task.

    Arguments:
        task (dict): as described in module docstring
    """
    targets = task.get("moshinsky_targets", [])

    # get rel sources
    rel_sources = operators.rel.get_rel_sources(task, {target[2]["id"] for target in targets})

    for (name, qn, parameters) in targets:
        (J0, g0, Tz0) = qn
        relative_id = parameters["id"]
        relative_source = rel_sources[relative_id]
        truncation = parameters["truncation"]
        rel_filename = relative_filename_for_source(relative_id, relative_source)
        tbme_filename = environ.tmbe_filename(
            name, truncation, relative_source['hw'], ext=task["h2_extension"]
        )

        if ((J0 != relative_source["qn"][0])
            or (g0 != relative_source["qn"][1])
            or (Tz0 > relative_source["qn"][3])
        ):
            raise mcscript.exception.ScriptError(
                f"incompatible quantum numbers: {relative_source['qn']} {qn}"
            )

        lines = []
        lines += ["{:s} {:d}".format(*truncation)]
        lines += [f"{rel_filename:s} {relative_source['type'].value:s}"]
        lines += [f"{tbme_filename:s} jjjpn {task['h2_format']} {Tz0:d}"]
        lines += [""]

        mcscript.control.call(
            [
                environ.shell_filename("moshinsky")
            ],
            input_lines=lines,
            mode=mcscript.control.CallMode.kSerial,
            check_return=True
        )

def save_rel(task):
    """Save relative targets to results.

    Arguments:
        task (dict): as described in module docstring
    """
    # get targets
    targets = operators.rel.get_rel_targets(task)

    # get rel sources
    rel_sources = operators.rel.get_rel_sources(task, targets)

    for (basename, _, source_id) in task.get("relative_targets", []):
        source = rel_sources[source_id]
        source_filename = relative_filename_for_source(source_id, source)
        if source["type"] == operators.rel.RelativeOperatorType.kRelative:
            target_filename = environ.rel_filename(basename, source['Nmax'], source['hw'])
        elif source["type"] == operators.rel.RelativeOperatorType.kRelativeCM:
            target_filename = environ.relcm_filename(basename, source['Nmax'], source['hw'])
        else:
            raise ValueError("invalid operator type: {}".format(source["type"]))
        mcscript.task.save_results_single(
            task, source_filename, target_filename, subdirectory="rel"
        )

def save_moshinsky(task):
    """Save moshinsky targets to results.

    Arguments:
        task (dict): as described in module docstring
    """
    # get targets
    targets = operators.rel.get_rel_targets(task)

    # get rel sources
    rel_sources = operators.rel.get_rel_sources(task, targets)

    for (basename, _, parameters) in task.get("moshinsky_targets", []):
        source_id = parameters["id"]
        source = rel_sources[source_id]
        filename = environ.tmbe_filename(
            basename, parameters["truncation"], source['hw'], task.get("h2_extension", "bin")
        )
        mcscript.task.save_results_single(
            task, filename, subdirectory="tbme"
        )
