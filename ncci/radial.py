"""radial.py -- radial matrix element generation for NCCI runs.

Patrick Fasano
University of Notre Dame

- 03/22/17 (pjf): Created, split from __init__.py.
- 04/06/17 (pjf): Correctly reference config submodule (mfdn.config).
- 04/07/17 (pjf): Update for mcscript namespace changes.
- 04/11/17 (pjf): Fix broken imports.
- 06/03/17 (pjf): Remove explicit references to natural orbitals from bulk of
    scripting.
- 06/07/17 (pjf): Clean up style.
- 08/11/17 (pjf): Use new TruncationModes.
- 08/26/17 (pjf): Add general truncation support:
  + Split out set_up_interaction_orbitals().
  + Rename set_up_orbitals_ho() -> set_up_orbitals_Nmax().
  + Rename set_up_orbitals_natorb() -> set_up_natural_orbitals().
  + Add set_up_orbitals_triangular().
  + Add set_up_orbitals() dispatch function.
- 09/12/17 (pjf): Update for config -> modes + environ split.
- 09/20/17 (pjf):
  + Generate pn overlaps.
  + Update for new --xform option of radial-gen.
- 10/25/17 (pjf): Add radial generation for electromagnetic observables.
- 01/04/18 (pjf): Add support for manual orbital files.
- 04/23/19 (pjf): Allow override for Nmax_orb.
"""
import errno
import math
import os

import mcscript
import mcscript.exception

from . import modes, environ


def set_up_interaction_orbitals(task, postfix=""):
    """Set up interaction orbitals for MFDn run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    # generate orbitals -- interaction bases
    mcscript.call(
        [
            environ.shell_filename("orbital-gen"),
            "--oscillator",
            "{truncation_int[1]:d}".format(**task),
            "{:s}".format(environ.orbitals_int_filename(postfix))
        ],
        mode=mcscript.CallMode.kSerial
    )
    if task["use_coulomb"]:
        mcscript.call(
            [
                environ.shell_filename("orbital-gen"),
                "--oscillator",
                "{truncation_coul[1]:d}".format(**task),
                "{:s}".format(environ.orbitals_coul_filename(postfix))
            ],
            mode=mcscript.CallMode.kSerial
        )


def set_up_orbitals_manual(task, postfix=""):
    """Copy in manually-provided orbitals.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    if task["sp_truncation_mode"] is not modes.SingleParticleTruncationMode.kManual:
        raise ValueError("expecting truncation_mode to be {} but found {truncation_mode}".format(modes.SingleParticleTruncationMode.kManual, **task))

    truncation_parameters = task["truncation_parameters"]
    sp_filename = truncation_parameters.get("sp_filename")
    if sp_filename is None:
        raise mcscript.exception.ScriptError("sp_orbitals file must be provided")
    else:
        sp_filename = mcscript.utils.expand_path(sp_filename)
        if not os.path.exists(sp_filename):
            raise FileNotFoundError(sp_filename)
    mcscript.call([
        "cp", "--verbose",
        sp_filename,
        environ.orbitals_filename(postfix)
        ])


def set_up_orbitals_Nmax(task, postfix=""):
    """Set up Nmax-truncated target orbitals for MFDn run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    # validate truncation mode
    if task["sp_truncation_mode"] is not modes.SingleParticleTruncationMode.kNmax:
        raise ValueError("expecting truncation_mode to be {} but found {truncation_mode}".format(modes.SingleParticleTruncationMode.kNmax, **task))

    # generate orbitals -- target basis
    truncation_parameters = task["truncation_parameters"]
    if truncation_parameters.get("Nmax_orb") is not None:
        Nmax_orb = truncation_parameters["Nmax_orb"]
    elif task["mb_truncation_mode"] == modes.ManyBodyTruncationMode.kNmax:
        Nmax_orb = truncation_parameters["Nmax"] + truncation_parameters["Nv"]
    elif task["mb_truncation_mode"] == modes.ManyBodyTruncationMode.kFCI:
        Nmax_orb = truncation_parameters["Nmax"]
    mcscript.call(
        [
            environ.shell_filename("orbital-gen"),
            "--oscillator",
            "{Nmax_orb:d}".format(Nmax_orb=Nmax_orb),
            "{:s}".format(environ.orbitals_filename(postfix))
        ],
        mode=mcscript.CallMode.kSerial
    )


def set_up_orbitals_triangular(task, postfix=""):
    """Set up triangular-truncated (an+bl) target orbitals for MFDn run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    # validate truncation mode
    if task["sp_truncation_mode"] is not modes.SingleParticleTruncationMode.kTriangular:
        raise ValueError("expecting truncation_mode to be {} but found {truncation_mode}".format(modes.SingleParticleTruncationMode.kTriangular, **task))

    # generate orbitals -- target basis
    truncation_parameters = task["truncation_parameters"]
    mcscript.call(
        [
            environ.shell_filename("orbital-gen"),
            "--triangular",
            "{sp_weight_max:f}".format(**truncation_parameters),
            "{n_coeff:f}".format(**truncation_parameters),
            "{l_coeff:f}".format(**truncation_parameters),
            "{:s}".format(environ.orbitals_filename(postfix))
        ],
        mode=mcscript.CallMode.kSerial
    )


def set_up_orbitals(task, postfix=""):
    """Set up target orbitals for MFDn run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    target_orbital_set_up_functions = {
        modes.SingleParticleTruncationMode.kManual: set_up_orbitals_manual,
        modes.SingleParticleTruncationMode.kNmax: set_up_orbitals_Nmax,
        modes.SingleParticleTruncationMode.kTriangular: set_up_orbitals_triangular,
    }

    # validate truncation mode
    if task["sp_truncation_mode"] not in target_orbital_set_up_functions.keys():
        raise ValueError("truncation mode {truncation_mode} not supported".format(**task))

    return target_orbital_set_up_functions[task["sp_truncation_mode"]](task, postfix)


def set_up_natural_orbitals(task, source_postfix, target_postfix):
    """Set up natural orbitals for MFDn run.

    Arguments:
        task (dict): as described in module docstring
        source_postfix (string): identifier for source of natural orbital information
        target_postfix (string): identifier to add to generated files

    Limitation: Currently only supports harmonic oscillator style
    truncation.
    """

    # validate natural orbitals enabled
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals are not enabled")

    mcscript.call(
        [
            environ.shell_filename("natorb-gen"),
            environ.orbitals_filename(source_postfix),
            environ.natorb_info_filename(source_postfix),
            environ.natorb_obdme_filename(source_postfix),
            environ.natorb_xform_filename(target_postfix),
            environ.orbitals_filename(target_postfix)
        ],
        mode=mcscript.CallMode.kSerial
    )


def set_up_radial_analytic(task, postfix=""):
    """Generate radial integrals and overlaps by integration for MFDn run
    in analytic basis.

    Operation mode may in general be direct oscillator, dilated
    oscillator, or generic (TODO).

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    # validate basis mode
    if (task["basis_mode"] not in {modes.BasisMode.kDirect, modes.BasisMode.kDilated}):  # no modes.BasisMode.kGeneric yet
        raise ValueError("invalid basis mode {basis_mode}".format(**task))

    # basis radial code -- expected by radial_utils codes
    basis_radial_code = "oscillator"  # TODO GENERALIZE: if not oscillator basis

    # generate radial integrals
    for operator_type in ["r", "k"]:
        for power in [1, 2]:
            mcscript.call(
                [
                    environ.shell_filename("radial-gen"),
                    "--kinematic",
                    "{:s}".format(operator_type),
                    "{:d}".format(power),
                    basis_radial_code,
                    environ.orbitals_filename(postfix),
                    environ.radial_me_filename(postfix, operator_type, power)
                ],
                mode=mcscript.CallMode.kSerial
            )

    # generate pn overlaps -- currently only trivial identity
    mcscript.call(
        [
            environ.shell_filename("radial-gen"),
            "--pn-overlaps",
            environ.orbitals_filename(postfix),
            environ.radial_pn_olap_filename(postfix)
        ],
        mode=mcscript.CallMode.kSerial
    )

    # set up radial matrix elements for observables
    set_up_observable_radial_analytic(task, postfix)

    # generate radial overlaps -- generate trivial identities if applicable
    mcscript.call(
        [
            environ.shell_filename("radial-gen"),
            "--identity",
            environ.orbitals_filename(postfix),
            environ.radial_xform_filename(postfix)
        ],
        mode=mcscript.CallMode.kSerial
    )
    if (task["basis_mode"] in {modes.BasisMode.kDirect}):
        mcscript.call(
            [
                environ.shell_filename("radial-gen"),
                "--identity",
                environ.orbitals_int_filename(postfix),
                environ.orbitals_filename(postfix),
                environ.radial_olap_int_filename(postfix)
            ],
            mode=mcscript.CallMode.kSerial
        )
    else:
        b_ratio = math.sqrt(task["hw_int"]/task["hw"])
        mcscript.call(
            [
                environ.shell_filename("radial-gen"),
                "--xform",
                "{:g}".format(b_ratio),
                basis_radial_code,
                environ.orbitals_int_filename(postfix),
                environ.orbitals_filename(postfix),
                environ.radial_olap_int_filename(postfix)
            ],
            mode=mcscript.CallMode.kSerial
        )
    if (task["use_coulomb"]):
        if (task["basis_mode"] in {modes.BasisMode.kDirect, modes.BasisMode.kDilated}):
            mcscript.call(
                [
                    environ.shell_filename("radial-gen"),
                    "--identity",
                    environ.orbitals_coul_filename(postfix),
                    environ.orbitals_filename(postfix),
                    environ.radial_olap_coul_filename(postfix)
                ],
                mode=mcscript.CallMode.kSerial
            )
        else:
            if task.get("hw_coul_rescaled") is None:
                b_ratio = 1
            else:
                b_ratio = math.sqrt(task["hw_coul_rescaled"]/task["hw"])
            mcscript.call(
                [
                    environ.shell_filename("radial-gen"),
                    "--xform",
                    "{:g}".format(b_ratio),
                    basis_radial_code,
                    environ.orbitals_coul_filename(postfix),
                    environ.orbitals_filename(postfix),
                    environ.radial_olap_coul_filename(postfix)
                ],
                mode=mcscript.CallMode.kSerial
            )


def set_up_radial_natorb(task, source_postfix, target_postfix):
    """Generate radial integrals and overlaps by transformation for MFDn run in natural orbital basis.

    Operation mode must be generic.

    Arguments:
        task (dict): as described in module docstring
        source_postfix (str): postfix for old basis
        target_postfix (str): postfix for new basis
    """
    # validate natural orbitals enabled
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals are not enabled")

    # compose radial transform
    mcscript.call(
        [
            environ.shell_filename("radial-compose"),
            environ.radial_xform_filename(source_postfix),
            environ.natorb_xform_filename(target_postfix),
            environ.radial_xform_filename(target_postfix)
        ],
        mode=mcscript.CallMode.kSerial
    )

    # compose interaction transform
    mcscript.call(
        [
            environ.shell_filename("radial-compose"),
            environ.radial_olap_int_filename(source_postfix),
            environ.natorb_xform_filename(target_postfix),
            environ.radial_olap_int_filename(target_postfix)
        ],
        mode=mcscript.CallMode.kSerial
    )

    # compose Coulomb transform
    if (task["use_coulomb"]):
        mcscript.call(
            [
                environ.shell_filename("radial-compose"),
                environ.radial_olap_coul_filename(source_postfix),
                environ.natorb_xform_filename(target_postfix),
                environ.radial_olap_coul_filename(target_postfix)
            ],
            mode=mcscript.CallMode.kSerial
        )

    # transform radial integrals
    for operator_type in ["r", "k"]:
        for power in [1, 2]:
            mcscript.call(
                [
                    environ.shell_filename("radial-xform"),
                    environ.orbitals_filename(target_postfix),
                    environ.natorb_xform_filename(target_postfix),
                    environ.radial_me_filename(source_postfix, operator_type, power),
                    environ.radial_me_filename(target_postfix, operator_type, power)
                ],
                mode=mcscript.CallMode.kSerial
            )

    # transform pn overlaps
    mcscript.call(
        [
            environ.shell_filename("radial-xform"),
            environ.orbitals_filename(target_postfix),
            environ.natorb_xform_filename(target_postfix),
            environ.radial_pn_olap_filename(source_postfix),
            environ.radial_pn_olap_filename(target_postfix)
        ],
        mode=mcscript.CallMode.kSerial
    )

    # set up radial matrix elements for natural orbitals
    set_up_observable_radial_natorb(task, source_postfix, target_postfix)


def set_up_observable_radial_analytic(task, postfix=""):
    """Generate radial integrals and overlaps by integration for one-body observables.

    Operation mode may in general be direct oscillator, dilated
    oscillator, or generic (TODO).

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    # validate basis mode
    if (task["basis_mode"] not in {modes.BasisMode.kDirect, modes.BasisMode.kDilated}):  # no modes.BasisMode.kGeneric yet
        raise ValueError("invalid basis mode {basis_mode}".format(**task))

    # basis radial code -- expected by radial_utils codes
    basis_radial_code = "oscillator"  # TODO GENERALIZE: if not oscillator basis

    for (operator_type, order) in task.get("ob_observables", []):
        if operator_type == 'E':
            radial_power = order
        elif operator_type == 'M':
            radial_power = order-1
        else:
            raise mcscript.exception.ScriptError("only E or M transitions currently supported")
        g0 = radial_power % 2
        Tz0 = 0  # TODO(pjf): generalize to isospin-changing operators
        mcscript.call(
            [
                environ.shell_filename("radial-gen"),
                "--radial",
                "{:d}".format(radial_power),
                "{:d}".format(order),
                "{:d}".format(g0),
                "{:d}".format(Tz0),
                basis_radial_code,
                environ.orbitals_filename(postfix),
                environ.radial_me_filename(postfix, operator_type, order)
            ],
            mode=mcscript.CallMode.kSerial
        )


def set_up_observable_radial_natorb(task, source_postfix, target_postfix):
    """Generate radial integrals and overlaps by transformation for MFDn run in natural orbital basis.

    Operation mode must be generic.

    Arguments:
        task (dict): as described in module docstring
        source_postfix (str): postfix for old basis
        target_postfix (str): postfix for new basis
    """
    # validate natural orbitals enabled
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals are not enabled")

    for (operator_type, order) in task.get("ob_observables", []):
        mcscript.call(
            [
                environ.shell_filename("radial-xform"),
                environ.orbitals_filename(target_postfix),
                environ.natorb_xform_filename(target_postfix),
                environ.radial_me_filename(source_postfix, operator_type, order),
                environ.radial_me_filename(target_postfix, operator_type, order)
            ],
            mode=mcscript.CallMode.kSerial
        )
