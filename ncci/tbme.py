"""tbme.py -- task handlers for MFDn runs.

Patrick Fasano
University of Notre Dame

- 03/22/17 (pjf): Created, split from __init__.py.
- 04/06/17 (pjf): Correctly reference config submodule (mfdn.config).
- 04/11/17 (pjf): Fix broken imports.
- 06/03/17 (pjf):
  + Remove explicit references to natural orbitals from bulk of scripting.
  + Fix VC scaling.
- 06/07/17 (pjf): Clean up style.
- 08/11/17 (pjf): Use new TruncationModes.
- 08/26/17 (pjf): Add support for general truncation schemes.
- 09/12/17 (pjf): Update for config -> modes + environ split.
- 09/20/17 (pjf): Add isospin operators.
- 09/22/17 (pjf): Take "observables" as list of tuples instead of dict.
- 10/18/17 (pjf): Use separate work directory for each postfix.
- 10/25/17 (pjf): Rename "observables" to "tb_observables".
- 03/15/19 (pjf): Rough in support for arbitrary two-body operators.
- 04/04/19 (pjf): Polish arbitrary two-body operator support.
- 09/04/19 (pjf):
    + Rewrite generate_tbme for new h2mixer:
        * Collect and manipulate both one- and two-body sources and channels.
        + Provide generic interface ("U[x]" and "V[x,y]") for upgraded one-body
          operators and separable operators.
- 09/07/19 (pjf): Remove Nv from truncation_parameters.
- 09/11/19 (pjf): Pass parameters as kwargs to operators.
- 10/10/19 (pjf): Generalize TBME generation:
    + Make generate_tbme() generic for all operator quantum numbers.
    + Add generate_diagonalization_tbme() for TBMEs needed at diagonalization time.
    + Add generate_observable_tbme() for two-body observables.
- 10/26/19 (pjf): Make "observable_sets" an optional task dictionary key.
- 12/22/19 (pjf): Add save_tbme() handler.
- 08/14/20 (pjf):
    + Allow passing A instead of nuclide (important for Tz-changing operators).
    + Fix bug with mutable defaults passed to generate_tbme().
    + Add flag for controlling whether to construct "built-in" scalar operators.
- 08/24/20 (pjf): Add "h2_extension" option for debugging with text-mode.
- 09/09/20 (pjf): Major rewrite to use operators.ob and operators.tb.
"""
import collections
import glob
import os
import re

import mcscript.utils

from . import (
    utils,
    modes,
    environ,
    operators,
    radial
)

def generate_h2mixer_obme_source_lines(identifier, parameters, postfix=""):
    """
    """
    filename = parameters.get("filename")
    (j0, g0, tz0) = parameters["qn"]
    lines = []
    if filename is not None:
        if identifier in operators.ob.k_h2mixer_builtin:
            raise Warning(
                "overriding builtin operator {id} with {filename}".format(
                    id=identifier, filename=filename
                )
            )
        lines += ["define-ob-source input {id:s} {filename:s} {j0:d} {g0:d} {tz0:d}".format(
            id=identifier,
            filename=filename,
            j0=j0, g0=g0, tz0=tz0
        )]
    elif identifier in operators.ob.k_h2mixer_builtin:
        orbital_filename = parameters.get("orbital_filename", "")
        lines += ["define-ob-source builtin {id:s} {orbital_filename:s}".format(
            id=identifier, orbital_filename=orbital_filename
        ).rstrip()]
    elif "linear-combination" in parameters:
        lines += ["define-ob-source linear-combination {id:s}".format(id=identifier)]
        for (source_id, coefficient) in parameters["linear-combination"].items():
            lines.append("  add-ob-source {id:s} {coefficient:e}".format(
                id=source_id, coefficient=coefficient
            ))
    elif "tensor-product" in parameters:
        (factor_a, factor_b) = parameters["tensor-product"]
        coefficient = parameters.get("coefficient", 1.0)
        lines += ["define-ob-source tensor-product {id:s} {factor_a:s} {factor_b:s} {j0:d} {coefficient:e}".format(
            id=identifier, factor_a=factor_a, factor_b=factor_b, j0=j0, coefficient=coefficient
        )]
    else:
        lines += ["define-ob-source input {id:s} {filename:s} {j0:d} {g0:d} {tz0:d}".format(
            id=identifier,
            filename=environ.obme_filename(postfix, identifier),
            j0=j0, g0=g0, tz0=tz0
        )]

    return lines


def generate_h2mixer_tbme_source_lines(identifier, parameters):
    """Generate input line for h2mixer source channel.

    Arguments:
        identifier (str): parameters for input line (id, parameters)
        parameters (dict): specification for input file
            {"filename": (str), "xform_filename": (str), "xform_truncation": (str)}

    Returns:
        (list of str) h2mixer input lines
    """
    filename = parameters.get("filename")
    xform_filename = parameters.get("xform_filename")
    xform_truncation = parameters.get("xform_truncation")
    if filename is not None:
        tbme_filename = mcscript.utils.expand_path(filename)
        if not os.path.isfile(tbme_filename):
            tbme_filename = mcscript.utils.search_in_subdirectories(
                environ.data_dir_h2_list, environ.operator_dir_list,
                filename, fail_on_not_found=True
                )

        if identifier in operators.tb.k_h2mixer_builtin:
            raise Warning(
                "overriding builtin operator {id} with {tbme_filename}".format(
                    id=identifier,
                    tbme_filename=tbme_filename
                    )
                )
        if (xform_filename is not None) and (xform_truncation is not None):
            xform_weight_max = utils.weight_max_string(xform_truncation)
            line = ("define-tb-source xform {id} {tbme_filename} {xform_weight_max} {xform_filename}".format(
                id=identifier,
                tbme_filename=tbme_filename,
                xform_weight_max=xform_weight_max,
                xform_filename=xform_filename
                ))
        else:
            line = ("define-tb-source input {id} {tbme_filename}".format(
                id=identifier, tbme_filename=tbme_filename
                ))
    elif "operatorU" in parameters:
        source_id = parameters["operatorU"]
        line = ("define-tb-source operatorU {id:s} {source_id:s}".format(
            id=identifier, source_id=source_id
        ))
    elif "operatorV" in parameters:
        source_id_a, source_id_b = parameters["operatorV"]
        coefficient = parameters.get("coefficient", 1.0)
        line = ("define-tb-source operatorV {id:s} {source_id_a:s} {source_id_b:s} {coefficient:e}".format(
            id=identifier, source_id_a=source_id_a, source_id_b=source_id_b, coefficient=coefficient
        ))
    elif identifier in operators.tb.k_h2mixer_builtin:
        line = ("define-tb-source builtin {id}".format(id=identifier))
    else:
        raise mcscript.exception.ScriptError(
            "unknown two-body operator {id}".format(id=identifier)
            )
    return [line]


def generate_diagonalization_tbme(task, postfix=""):
    """Generate TBMEs for diagonalization.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier added to input filenames
    """
    # extract parameters for convenience
    hw = task["hw"]
    hw_int = task["hw_int"]

    # sanity check on hw
    if (task["basis_mode"] is modes.BasisMode.kDirect) and (hw != hw_int):
        raise mcscript.exception.ScriptError(
            "Using basis mode {basis_mode} but hw = {hw} and hw_int = {hw_int}".format(**task)
            )

    # get targets
    targets = operators.tb.get_tbme_targets(task, builtin_scalar_targets=True).get((0,0,0), {})

    # generate MFDn TBMEs
    generate_tbme(
        task,
        targets=targets, target_qn=(0,0,0),
        postfix=postfix
    )


def generate_observable_tbme(task, postfix="", generate_scalar=False):
    """Generate observable TBMEs.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier added to input filenames
        generate_scalar (bool, default False): whether to generate scalar TBMEs;
            this is generally false, since they will be generated during setup
            for diagonalization
    """
    targets_by_qn = operators.tb.get_tbme_targets(task, builtin_scalar_targets=False)

    if not generate_scalar and ((0,0,0) in targets_by_qn.keys()):
        del targets_by_qn[(0,0,0)]

    for target_qn,targets in targets_by_qn.items():
        generate_tbme(task, targets=targets, target_qn=target_qn, postfix=postfix)


def generate_tbme(task, targets, target_qn=(0,0,0), postfix=""):
    """Generate TBMEs with h2mixer.

    Arguments:
        task (dict): as described in module docstring
        targets
    """
    # extract parameters for convenience
    nuclide = task.get("nuclide")
    if nuclide is None:
        A = task["A"]
    else:
        A = sum(nuclide)

    # get set of required sources
    required_tbme_sources = set()
    required_tbme_sources.update(*[op.keys() for op in targets.values()])

    # get tbme sources
    tbme_sources = operators.tb.get_tbme_sources(task, targets)

    # get obme sources
    obme_targets = operators.ob.get_obme_targets(task, targets, tbme_targets_only=True)
    obme_sources = operators.ob.get_obme_sources_h2mixer(task, obme_targets.keys())

    # accumulate h2mixer input lines
    lines = []

    # initial comment
    lines.append("# task: {}".format(task))
    lines.append("")

    # global mode definitions
    target_truncation = task.get("target_truncation")
    if target_truncation is None:
        # automatic derivation
        truncation_parameters = task["truncation_parameters"]
        if task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kNmax:
            if task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kNmax:
                # important: truncation of orbitals file, one-body
                # truncation of interaction file, and MFDn
                # single-particle shells (beware 1-based) must agree
                N1_max = utils.Nv_for_nuclide(task["nuclide"])+truncation_parameters["Nmax"]
                N2_max = 2*utils.Nv_for_nuclide(task["nuclide"])+truncation_parameters["Nmax"]
                target_weight_max = utils.weight_max_string((N1_max, N2_max))
            elif task["mb_truncation_mode"] == modes.ManyBodyTruncationMode.kFCI:
                N1_max = truncation_parameters["Nmax"]
                target_weight_max = utils.weight_max_string(("ob", N1_max))
            else:
                raise mcscript.exception.ScriptError(
                    "invalid mb_truncation_mode {}".format(task["mb_truncation_mode"])
                )
        else:
            if task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kFCI:
                w1_max = truncation_parameters["sp_weight_max"]
                target_weight_max = utils.weight_max_string(("ob", w1_max))
            else:
                w1_max = truncation_parameters["sp_weight_max"]
                w2_max = min(truncation_parameters["mb_weight_max"], 2*truncation_parameters["sp_weight_max"])  # TODO this is probably too large
                target_weight_max = utils.weight_max_string((w1_max, w2_max))
    else:
        # given value
        target_weight_max = utils.weight_max_string(target_truncation)

    lines.append("set-target-indexing {orbitals_filename} {target_weight_max}".format(
        orbitals_filename=environ.orbitals_filename(postfix),
        target_weight_max=target_weight_max,
        **task
    ))
    lines.append("set-target-multipolarity {:d} {:d} {:d}".format(*target_qn))
    lines.append("set-output-format {h2_format}".format(**task))
    lines.append("set-mass {A}".format(A=A, **task))
    lines.append("")

    # xform sources: collect unique filenames
    xform_filename_set = set()
    for source_id in sorted(required_tbme_sources & set(tbme_sources.keys())):
        xform_filename = tbme_sources[source_id].get("xform_filename")
        xform_truncation = tbme_sources[source_id].get("xform_truncation")
        if (xform_filename is not None) and (xform_truncation is not None):
            xform_filename_set.add(xform_filename)

    # xform sources: generate h2mixer input
    for xform_filename in sorted(xform_filename_set):
        lines.append("define-xform {filename:s} {filename:s}".format(filename=xform_filename))

    # obme sources: generate h2mixer input (in reverse topological order)
    for obme_id,obme_source in obme_sources.items():
        lines.extend(generate_h2mixer_obme_source_lines(obme_id, obme_source, postfix))

    lines.append("")

    # sources: generate h2mixer input
    for id_ in sorted(required_tbme_sources):
        lines.extend(generate_h2mixer_tbme_source_lines(id_, tbme_sources[id_]))

    lines.append("")

    # targets: generate h2mixer input
    h2_extension = task.get("h2_extension", "bin")
    for (basename, operator) in targets.items():
        lines.append("define-target work{:s}/{:s}.{:s}".format(postfix, basename, h2_extension))
        for (source, coefficient) in operator.items():
            lines.append("  add-source {:s} {:e}".format(source, coefficient))
        lines.append("")

    # ensure terminal line
    lines.append("")

    # diagnostic: log input lines to file
    #
    # This is purely for easy diagnostic purposes, since lines will be
    # fed directly to h2mixer as stdin below.
    mcscript.utils.write_input(environ.h2mixer_filename(postfix), input_lines=lines, verbose=False)

    # create work directory if it doesn't exist yet (-p)
    mcscript.call(["mkdir", "-p", "work{:s}".format(postfix)])

    # invoke h2mixer
    mcscript.call(
        [
            environ.shell_filename("h2mixer")
        ],
        input_lines=lines,
        mode=mcscript.CallMode.kSerial
    )


def save_tbme(task, postfix=""):
    """Save h2 TBME files to results directory.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier added to input filenames
    """
    # convenience definitions
    descriptor = task["metadata"]["descriptor"]
    target_directory_name = descriptor + postfix
    work_dir = "work{:s}".format(postfix)

    # glob for list of tbme files
    archive_file_list = glob.glob(os.path.join(work_dir, "tbme-*"))

    mcscript.task.save_results_multi(
        task, archive_file_list, target_directory_name, "tbme"
    )
