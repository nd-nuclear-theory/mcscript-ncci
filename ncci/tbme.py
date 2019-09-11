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
"""
import collections
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

k_h2mixer_builtin_obo = {
    "identity": (0,0,0),
    "j": (1,0,0),  # this is safe, as our orbitals are always eigenstates of j
    "l2": (0,0,0), "s2": (0,0,0), "j2": (0,0,0),
    "tz": (0,0,0),
}

k_h2mixer_builtin_tbo = {
    "identity",
}

def generate_h2mixer_obme_source_lines(identifier, parameters):
    """
    """
    filename = parameters.get("filename")
    (j0, g0, tz0) = parameters["qn"]
    lines = []
    if filename is not None:
        if identifier in k_h2mixer_builtin_obo:
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
    elif identifier in k_h2mixer_builtin_obo:
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
        lines += ["define-ob-source tensor-product {id:s} {factor_a:s} {factor_b:s} {j0:d}".format(
            id=identifier, factor_a=factor_a, factor_b=factor_b, j0=j0
        )]
    else:
        raise mcscript.exception.ScriptError(
            "unknown one-body operator {id}".format(id=identifier)
            )

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

        if identifier in k_h2mixer_builtin_tbo:
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
        line = ("define-tb-source operatorV {id:s} {source_id_a:s} {source_id_b:s}".format(
            id=identifier, source_id_a=source_id_a, source_id_b=source_id_b
        ))
    elif identifier in k_h2mixer_builtin_tbo:
        line = ("define-tb-source builtin {id}".format(id=identifier))
    else:
        raise mcscript.exception.ScriptError(
            "unknown two-body operator {id}".format(id=identifier)
            )
    return [line]


def generate_tbme(task, postfix=""):
    """Generate TBMEs for MFDn run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier added to input filenames
    """
    # extract parameters for convenience
    A = sum(task["nuclide"])
    a_cm = task["a_cm"]
    hw = task["hw"]
    hw_cm = task.get("hw_cm")
    if (hw_cm is None):
        hw_cm = hw
    hw_int = task["hw_int"]
    hw_coul = task["hw_coul"]
    hw_coul_rescaled = task.get("hw_coul_rescaled")
    if (hw_coul_rescaled is None):
        hw_coul_rescaled = hw
    xform_truncation_int = task.get("xform_truncation_int")
    if (xform_truncation_int is None):
        xform_truncation_int = task["truncation_int"]
    xform_truncation_coul = task.get("xform_truncation_coul")
    if (xform_truncation_coul is None):
        xform_truncation_coul = task["truncation_coul"]

    # sanity check on hw
    if (task["basis_mode"] is modes.BasisMode.kDirect) and (hw != hw_int):
        raise mcscript.exception.ScriptError(
            "Using basis mode {} but hw = {} and hw_int = {}".format(
                task["basis_mode"], hw, hw_int
            ))

    # accumulate h2mixer targets
    targets = collections.OrderedDict()

    # target: Hamiltonian
    if (task.get("hamiltonian")):
        targets["tbme-H"] = task["hamiltonian"]
    else:
        targets["tbme-H"] = operators.Hamiltonian(
            A=A, hw=hw, a_cm=a_cm, hw_cm=hw_cm,
            use_coulomb=task["use_coulomb"], hw_coul=hw_coul,
            hw_coul_rescaled=hw_coul_rescaled
        )

    # accumulate observables
    if task.get("tb_observables"):
        for (basename, operator) in task["tb_observables"]:
            targets["tbme-{}".format(basename)] = mcscript.utils.CoefficientDict(operator)

    # target: radius squared
    if "tbme-rrel2" not in targets:
        targets["tbme-rrel2"] = operators.rrel2(A=A, hw=hw)

    # target: Ncm
    if "tbme-Ncm" not in targets:
        targets["tbme-Ncm"] = operators.Ncm(A=A, hw=hw, hw_cm=hw_cm)

    # optional observable sets
    # Hamiltonian components
    if "H-components" in task["observable_sets"]:
        # target: Trel (diagnostic)
        targets["tbme-Tintr"] = operators.Tintr(A=A, hw=hw)
        # target: Tcm (diagnostic)
        targets["tbme-Tcm"] = operators.Tcm(A=A, hw=hw)
        # target: VNN (diagnostic)
        targets["tbme-VNN"] = operators.VNN()
        # target: VC (diagnostic)
        if (task["use_coulomb"]):
            targets["tbme-VC"] = operators.VC(hw=hw_coul_rescaled, hw_coul=hw_coul)
    # squared angular momenta
    if ("am-sqr" in task["observable_sets"]):
        targets["tbme-L2"] = operators.L2()
        targets["tbme-Sp2"] = operators.Sp2()
        targets["tbme-Sn2"] = operators.Sn2()
        targets["tbme-S2"] = operators.S2()
        targets["tbme-J2"] = operators.J2()
    if ("isospin" in task["observable_sets"]):
        targets["tbme-T2"] = operators.T2(A=A)

    # get set of required sources
    required_obme_sources = set()
    required_tbme_sources = set()
    required_tbme_sources.update(*[op.keys() for op in targets.values()])

    # obme and tbme sources: accumulate definitions
    obme_sources = collections.OrderedDict()
    tbme_sources = collections.OrderedDict()

    # tbme sources: h2mixer built-ins
    builtin_tbme_sources = k_h2mixer_builtin_tbo
    for source in sorted(builtin_tbme_sources):
        tbme_sources[source] = dict()

    # tbme sources: upgraded one-body and separable operators
    for source in sorted(required_tbme_sources):
        # parse upgraded one-body operator
        match = re.fullmatch(r"U\[(.+)\]", source)
        if match:
            tbme_sources[source] = {"operatorU": match.group(1)}
            required_obme_sources |= {match.group(1)}
            continue

        # parse separable operator
        match = re.fullmatch(r"V\[(.+),(.+)\]", source)
        if match:
            tbme_sources[source] = {"operatorV": (match.group(1), match.group(2))}
            required_obme_sources |= {match.group(1), match.group(2)}
            continue

    # tbme sources: VNN
    if "VNN" in required_tbme_sources:
        VNN_filename = task.get("interaction_file")
        if VNN_filename is None:
            VNN_filename = environ.interaction_filename(
                task["interaction"],
                task["truncation_int"],
                task["hw_int"]
            )

        if task["basis_mode"] is modes.BasisMode.kDirect:
            tbme_sources["VNN"] = dict(filename=VNN_filename)
        else:
            tbme_sources["VNN"] = dict(
                filename=VNN_filename,
                xform_filename=environ.radial_olap_int_filename(postfix),
                xform_truncation=xform_truncation_int
            )

    # tbme sources: Coulomb
    #
    # Note: This is the "unscaled" Coulomb, still awaiting the scaling
    # factor from dilation.
    if "VC_unscaled" in required_tbme_sources:
        VC_filename = task.get("coulomb_file")
        if VC_filename is None:
            VC_filename = environ.interaction_filename(
                "VC",
                task["truncation_coul"],
                task["hw_coul"]
            )
        if task["basis_mode"] in (modes.BasisMode.kDirect, modes.BasisMode.kDilated):
            tbme_sources["VC_unscaled"] = dict(filename=VC_filename)
        else:
            tbme_sources["VC_unscaled"] = dict(
                filename=VC_filename,
                xform_filename=environ.radial_olap_coul_filename(postfix),
                xform_truncation=xform_truncation_coul
            )

    # tbme sources: override with user-provided
    user_tbme_sources = task.get("tbme_sources")
    if (user_tbme_sources is not None):
        for (source_id, source) in user_tbme_sources:
            tbme_sources[source_id] = source

    # obme sources: h2mixer built-ins
    builtin_obme_sources = k_h2mixer_builtin_obo
    for source_id, qn in builtin_obme_sources.items():
        obme_sources[source_id] = {"qn": qn}

    # obme sources: radial-gen builtins
    radialgen_obme_sources = radial.k_radialgen_operators
    for source_id, qn in radialgen_obme_sources.items():
        obme_sources[source_id] = {
            "filename": environ.obme_filename(postfix, source_id),
            "qn": qn
        }

    # obme sources: special linear combinations
    obme_sources["delta_p"] = {"linear-combination": mcscript.utils.CoefficientDict({"identity": 0.5, "tz": +1.0}), "qn": (0,0,0)}
    obme_sources["delta_n"] = {"linear-combination": mcscript.utils.CoefficientDict({"identity": 0.5, "tz": -1.0}), "qn": (0,0,0)}
    obme_sources["sp"] = {"tensor-product": ["delta_p", "s"], "qn": (1,0,0)}
    obme_sources["sn"] = {"tensor-product": ["delta_n", "s"], "qn": (1,0,0)}
    obme_sources["sp2"] = {"tensor-product": ["delta_p", "s2"], "qn": (0,0,0)}
    obme_sources["sn2"] = {"tensor-product": ["delta_n", "s2"], "qn": (0,0,0)}

    # obme sources: override with user-provided
    user_obme_sources = task.get("obme_sources")
    if (user_obme_sources is not None):
        for (source_id, source) in user_obme_sources:
            obme_sources[source_id] = source

    # obme sources: construct dependency graph
    obme_dependency_graph = {}
    for (source_id, source) in obme_sources.items():
        if source.get("linear-combination"):
            obme_dependency_graph[source_id] = source["linear-combination"].keys()
        elif source.get("tensor-product"):
            obme_dependency_graph[source_id] = source["tensor-product"]
        else:
            obme_dependency_graph[source_id] = []

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
    lines.append("set-target-multipolarity 0 0 0")  # TODO(pjf): generalize for nonscalar operators
    lines.append("set-output-format {h2_format}".format(**task))
    lines.append("set-mass {A}".format(A=A, **task))
    lines.append("")

    # xform sources: collect unique filenames
    xform_filename_set = set()
    for source_id in required_tbme_sources:
        xform_filename = tbme_sources[source_id].get("xform_filename")
        xform_truncation = tbme_sources[source_id].get("xform_truncation")
        if (xform_filename is not None) and (xform_truncation is not None):
            xform_filename_set.add(xform_filename)

    # xform sources: generate h2mixer input
    for xform_filename in sorted(xform_filename_set):
        lines.append("define-xform {filename:s} {filename:s}".format(filename=xform_filename))

    # obme sources: generate h2mixer input (in reverse topological order)
    for id_ in reversed(mcscript.utils.topological_sort(obme_dependency_graph, required_obme_sources)):
        lines.extend(generate_h2mixer_obme_source_lines(id_, obme_sources[id_]))

    lines.append("")

    # sources: generate h2mixer input
    for id_ in sorted(required_tbme_sources):
        lines.extend(generate_h2mixer_tbme_source_lines(id_, tbme_sources[id_]))

    lines.append("")

    # targets: generate h2mixer input
    for (basename, operator) in targets.items():
        lines.append("define-target work{:s}/{:s}.bin".format(postfix, basename))
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
