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
"""
import collections
import os

import mcscript.utils

from . import (
    utils,
    modes,
    environ,
    operators,
    input,
)


def generate_tbme(task, postfix=""):
    """Generate TBMEs for MFDn run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier added to input filenames
    """
    # preprocess task dictionary
    input.fill_default_values(task)

    # extract parameters for convenience
    A = sum(task["nuclide"])
    a_cm = task["a_cm"]
    hw = task["hw"]
    hw_cm = task["hw_cm"]
    hw_coul = task["hw_coul"]
    hw_coul_rescaled = task["hw_coul_rescaled"]
    xform_truncation_int = task["xform_truncation_int"]
    xform_truncation_coul = task["xform_truncation_coul"]

    # accumulate h2mixer targets
    targets = collections.OrderedDict()

    # target: Hamiltonian
    if task["hamiltonian"]:
        targets["tbme-H"] = task["hamiltonian"]
    else:
        targets["tbme-H"] = operators.Hamiltonian(
            A=A, hw=hw, a_cm=a_cm, bsqr_intr=hw/hw_cm,
            use_coulomb=task["use_coulomb"], bsqr_coul=hw_coul_rescaled/hw_coul
        )

    # accumulate observables
    targets.update(task["tb_observables"])

    # target: radius squared
    if "tbme-rrel2" not in targets.keys():
        targets["tbme-rrel2"] = operators.rrel2(A, hw)

    # optional observable sets
    # Hamiltonian components
    if ("H-components" in task["observable_sets"]):
        # target: Ncm
        if ("tbme-Ncm" not in targets.keys()):
            targets["tbme-Ncm"] = operators.Ncm(A, hw/hw_cm)
        # target: Trel (diagnostic)
        targets["tbme-Trel"] = operators.Trel(A, hw)
        # target: VNN (diagnostic)
        targets["tbme-VNN"] = operators.VNN()
        # target: VC (diagnostic)
        if (task["use_coulomb"]):
            targets["tbme-VC"] = operators.VC(hw_coul_rescaled/hw_coul)
    # squared angular momenta
    if ("am-sqr" in task["observable_sets"]):
        targets["tbme-L"] = operators.L()
        targets["tbme-Sp"] = operators.Sp()
        targets["tbme-Sn"] = operators.Sn()
        targets["tbme-S"] = operators.S()
        targets["tbme-J"] = operators.J()
    if ("isospin" in task["observable_sets"]):
        targets["tbme-T"] = operators.T()

    # get set of required sources
    required_sources = set()
    required_sources.update(*[op.keys() for op in targets.values()])

    # accumulate h2mixer input lines
    lines = []

    # initial comment
    lines.append("# task: {}".format(task))
    lines.append("")

    # global mode definitions
    target_truncation = task["target_truncation"]
    if target_truncation is None:
        # automatic derivation
        truncation_parameters = task["truncation_parameters"]
        if task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kNmax:
            if task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kNmax:
                # important: truncation of orbitals file, one-body
                # truncation of interaction file, and MFDn
                # single-particle shells (beware 1-based) must agree
                N1_max = truncation_parameters["Nv"]+truncation_parameters["Nmax"]
                N2_max = 2*truncation_parameters["Nv"]+truncation_parameters["Nmax"]
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
    lines.append("set-target-multipolarity 0 0 0")
    lines.append("set-output-format {h2_format}".format(**task))
    lines.append("set-mass {A}".format(A=A, **task))
    lines.append("")

    # radial operator inputs
    for operator_type in ["r", "k"]:
        for power in [1, 2]:
            radial_me_filename = environ.radial_me_filename(postfix, operator_type, power)
            lines.append("define-radial-operator {} {} {}".format(operator_type, power, radial_me_filename))
    lines.append("")

    # pn overlap input
    pn_olap_me_filename = environ.radial_pn_olap_filename(postfix)
    lines.append("define-pn-overlaps {}".format(pn_olap_me_filename))
    lines.append("")

    # sources: h2mixer built-ins
    builtin_sources = (operators.kinematic_operator_set | operators.angular_momentum_operator_set | operators.isospin_operator_set)
    for source in sorted(builtin_sources & required_sources):
        lines.append("define-source operator " + source)
    lines.append("")

    # sources: VNN
    if ("VNN" in required_sources):
        if os.path.isfile(task["interaction"]):
            VNN_filename = task["interaction"]
        else:
            VNN_filename = environ.interaction_filename(
                "{}-{}-{:g}.bin".format(
                    task["interaction"],
                    mcscript.utils.dashify(task["truncation_int"]),
                    task["hw_int"]
                )
            )
        if task["basis_mode"] is modes.BasisMode.kDirect:
            lines.append("define-source input VNN {VNN_filename}".format(VNN_filename=VNN_filename, **task))
        else:
            xform_weight_max_int = utils.weight_max_string(xform_truncation_int)
            lines.append("define-source xform VNN {VNN_filename} {xform_weight_max_int} {radial_olap_int_filename}".format(
                VNN_filename=VNN_filename,
                xform_weight_max_int=xform_weight_max_int,
                radial_olap_int_filename=environ.radial_olap_int_filename(postfix),
                **task
            ))

    # sources: Coulomb
    #
    # Note: This is the "unscaled" Coulomb, still awaiting the scaling
    # factor from dilation.
    if ("VC_unscaled" in required_sources):
        VC_filename = environ.interaction_filename(
            "{}-{}-{:g}.bin".format(
                "VC",
                mcscript.utils.dashify(task["truncation_coul"]),
                task["hw_coul"]
            )
        )
        if task["basis_mode"] in (modes.BasisMode.kDirect, modes.BasisMode.kDilated):
            lines.append("define-source input VC_unscaled {VC_filename}".format(VC_filename=VC_filename, **task))
        else:
            xform_weight_max_coul = utils.weight_max_string(xform_truncation_coul)
            lines.append("define-source xform VC_unscaled {VC_filename} {xform_weight_max_coul} {radial_olap_coul_filename}".format(
                VC_filename=VC_filename,
                xform_weight_max_coul=xform_weight_max_coul,
                radial_olap_coul_filename=environ.radial_olap_coul_filename(postfix),
                **task
            ))

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
