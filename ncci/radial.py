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
- 09/04/19 (pjf):
  + Update for new radial-gen input on stdin.
  + Update for new orbital-gen flags.
  + Rewrite for new em-gen workflow.
- 09/07/19 (pjf): Remove Nv from truncation_parameters.
- 06/03/20 (pjf):
  + Make natural orbital base state selected by quantum numbers.
  + Pass input to natorb-gen on stdin.
- 09/02/20 (pjf): Fix set_up_observable_radial_analytic for operators other than
  E and M.
- 09/09/20 (pjf): Use obmixer inside set_up_radial_analytic().
- 09/13/20 (pjf):
  + Improve source/target handling in set_up_radial_analytic().
  + Use obmixer inside set_up_radial_natorb().
  + Pass oscillator length to obmixer.
- 09/19/20 (pjf): Break out xform generation into set_up_xforms_analytic().
- 07/08/21 (pjf): Only generate interaction and Coulomb xforms if needed for
    tbme sources.
"""
import math
import os

import mcscript
import mcscript.exception

from . import (
    utils,
    modes,
    environ,
    operators
)


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
            "--Nmax",
            "{truncation_int[1]:d}".format(**task),
            "{:s}".format(environ.orbitals_int_filename(postfix))
        ],
        mode=mcscript.CallMode.kSerial
    )
    if task["use_coulomb"]:
        mcscript.call(
            [
                environ.shell_filename("orbital-gen"),
                "--Nmax",
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
        Nmax_orb = truncation_parameters["Nmax"] + utils.Nv_for_nuclide(task["nuclide"])
    elif task["mb_truncation_mode"] == modes.ManyBodyTruncationMode.kFCI:
        Nmax_orb = truncation_parameters["Nmax"]
    mcscript.call(
        [
            environ.shell_filename("orbital-gen"),
            "--Nmax",
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

    Limitation: Currently uses initial orbital weights and truncation as natural
    orbital weights and truncation.
    """

    # validate natural orbitals enabled
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals are not enabled")

    (J, g, n) = task["natorb_base_state"]

    lines = []
    lines += ["set-indexing {:s}".format(environ.orbitals_filename(source_postfix))]
    lines += ["define-densities {J:3.1f} {g:d} {n:d} {obdme_filename:s} {info_filename:s}".format(
            J=J, g=g, n=n,
            obdme_filename=environ.natorb_obdme_filename(source_postfix),
            info_filename=environ.natorb_info_filename(source_postfix)
        )]
    lines += ["set-output-xform {orbital_filename:s} {xform_filename:s}".format(
            orbital_filename=environ.orbitals_filename(target_postfix),
            xform_filename=environ.natorb_xform_filename(target_postfix)
        )]

    mcscript.call(
        [environ.shell_filename("natorb-gen")],
        mode=mcscript.CallMode.kSerial,
        input_lines=lines
    )


def set_up_obme_analytic(task, postfix=""):
    """Generate one-body matrix elements by analytic formulae or integration in
    analytic basis.

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

    ################################################################
    # obmixer input
    ################################################################
    basis_command = "set-basis {basis_type:s} {orbital_filename:s}"
    length_command = "set-length-parameter {length_parameter:.17e}"
    xform_command = "define-xform {id:s} {xform_filename:s}"

    # get obme sources
    obme_targets = operators.ob.get_obme_targets_obmixer(task)
    obme_sources = operators.ob.get_obme_sources(task, obme_targets)

    # collect input lines
    lines = []
    lines.append(basis_command.format(
        basis_type=basis_radial_code,
        orbital_filename=environ.orbitals_filename(postfix)
    ))
    lines.append(length_command.format(
        length_parameter=utils.oscillator_length(task["hw"])
    ))

    # generate one-body RMEs
    for (identifier, parameters) in obme_sources.items():
        filename = parameters.get("filename")
        (j0, g0, tz0) = parameters["qn"]
        if filename is not None:
            lines += ["define-source input {id:s} {filename:s} {j0:d} {g0:d} {tz0:d}".format(
                id=identifier,
                filename=filename,
                j0=j0, g0=g0, tz0=tz0
            )]
        elif "builtin" in parameters:
            line = "define-source {mode:s} {id:}".format(
                id=identifier, mode=parameters["builtin"]
            )
            if parameters["builtin"] == "solid-harmonic":
                line += " {coordinate:s} {order:d} {j0:d}".format(j0=j0, **parameters)
            if "orbital_filename" in parameters:
                line += " {orbital_filename:s}".format(**parameters)
            lines.append(line)
        elif "linear-combination" in parameters:
            lines += ["define-source linear-combination {id:s}".format(id=identifier)]
            for (source_id, coefficient) in parameters["linear-combination"].items():
                lines.append("  add-source {id:s} {coefficient:.17e}".format(
                    id=source_id, coefficient=coefficient
                ))
        elif "tensor-product" in parameters:
            (factor_a, factor_b) = parameters["tensor-product"]
            coefficient = parameters.get("coefficient", 1.0)
            lines += ["define-source tensor-product {id:s} {factor_a:s} {factor_b:s} {j0:d} {coefficient:.17e}".format(
                id=identifier, factor_a=factor_a, factor_b=factor_b, j0=j0, coefficient=coefficient
            )]
        else:
            raise mcscript.exception.ScriptError("unknown one-body operator {}".format(identifier))

    for identifier in sorted(obme_targets):
        lines += ["define-target {id:s} {filename:s}".format(
            id=identifier, filename=environ.obme_filename(postfix, identifier)
        )]

    # # set up radial matrix elements for observables
    # lines += set_up_observable_radial_analytic(task, postfix)

    # call obmixer
    mcscript.call(
        [
            environ.shell_filename("obmixer")
        ],
        mode=mcscript.CallMode.kSerial,
        input_lines=lines
    )


def set_up_xforms_analytic(task, postfix=""):
    """Generate analytic transformation matrix elements (e.g. dilation or Laguerre
    basis transformation).

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    # validate basis mode
    if (task["basis_mode"] not in {modes.BasisMode.kDirect, modes.BasisMode.kDilated}):  # no modes.BasisMode.kGeneric yet
        raise ValueError("invalid basis mode {basis_mode}".format(**task))

    # basis radial code -- expected by radial_utils codes
    basis_radial_code = "oscillator"  # TODO GENERALIZE: if not oscillator basis

    # get tbme sources
    targets_by_qn = operators.tb.get_tbme_targets(task)
    tbme_sources = {}
    for targets in targets_by_qn.values():
        tbme_sources.update(operators.tb.get_tbme_sources(task, targets, postfix))

    ################################################################
    # radial-gen input
    ################################################################
    # define commands
    ket_basis_command = "set-ket-basis {basis_type:s} {orbital_filename:s}"
    operator_target_command = (
        "define-operator-target {mode:s} {operator_type:s} {output_filename:s}"
    )
    xform_target_command = (
        "define-xform-target {scale_factor:.17e} {bra_basis_type:s} {bra_orbital_file:s} {output_filename:s}"
    )

    # collect input lines
    lines = []
    lines.append(ket_basis_command.format(
        basis_type=basis_radial_code,
        orbital_filename=environ.orbitals_filename(postfix)
    ))

    # generate radial overlaps -- generate trivial identities if applicable
    #
    # dummy radial xform
    lines.append(xform_target_command.format(
        scale_factor=1.0, bra_basis_type=basis_radial_code,
        bra_orbital_file=environ.orbitals_filename(postfix),
        output_filename=environ.radial_xform_filename(postfix)
        )
    )

    if "VNN" in tbme_sources:
        # interaction xform
        b_ratio = math.sqrt(task.get("hw_int", task["hw"])/task["hw"])
        lines.append(xform_target_command.format(
            scale_factor=b_ratio, bra_basis_type="oscillator",
            bra_orbital_file=environ.orbitals_int_filename(postfix),
            output_filename=environ.radial_olap_int_filename(postfix)
        ))
    if task.get("use_coulomb", False) and ("VC_unscaled" in tbme_sources):
        if task.get("hw_coul_rescaled") is None:
            b_ratio = 1
        else:
            b_ratio = math.sqrt(task["hw_coul_rescaled"]/task["hw"])
        lines.append(xform_target_command.format(
            scale_factor=b_ratio, bra_basis_type="oscillator",
            bra_orbital_file=environ.orbitals_coul_filename(postfix),
            output_filename=environ.radial_olap_coul_filename(postfix)
        ))

    # call radial-gen
    mcscript.call(
        [
            environ.shell_filename("radial-gen")
        ],
        mode=mcscript.CallMode.kSerial,
        input_lines=lines
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

    # get tbme sources
    targets_by_qn = operators.tb.get_tbme_targets(task)
    tbme_sources = {}
    for targets in targets_by_qn.values():
        tbme_sources.update(operators.tb.get_tbme_sources(task, targets, target_postfix))

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

    if "VNN" in tbme_sources:
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
    if task.get("use_coulomb", False) and ("VC_unscaled" in tbme_sources):
        mcscript.call(
            [
                environ.shell_filename("radial-compose"),
                environ.radial_olap_coul_filename(source_postfix),
                environ.natorb_xform_filename(target_postfix),
                environ.radial_olap_coul_filename(target_postfix)
            ],
            mode=mcscript.CallMode.kSerial
        )

    ################################################################
    # obmixer input
    ################################################################
    basis_command = "set-basis {basis_type:s} {orbital_filename:s}"
    length_command = "set-length-parameter {length_parameter:.17e}"
    xform_command = "define-xform natorb {xform_filename:s}"
    input_source_command = "define-source input {id:s}{source_postfix:s} {filename:s} {j0:d} {g0:d} {tz0:d}"
    xform_source_command = "define-source xform {id:s}{target_postfix:s} {id:s}{source_postfix:s} natorb"
    target_command = "define-target {id:s}{target_postfix:s} {filename:s}"

    # get obme sources
    obme_targets = operators.ob.get_obme_targets_obmixer(task)
    obme_sources = operators.ob.get_obme_sources(task, obme_targets)

    # collect input lines
    lines = []
    lines.append(basis_command.format(
        basis_type="oscillator",  # dummy -- not used for xforms
        orbital_filename=environ.orbitals_filename(target_postfix)
    ))

    lines.append(xform_command.format(
        xform_filename=environ.natorb_xform_filename(target_postfix)
    ))

    for identifier in sorted(obme_targets):
        (j0, g0, tz0) = obme_sources[identifier]["qn"]
        lines += [input_source_command.format(
            id=identifier, source_postfix=source_postfix, target_postfix=target_postfix,
            filename=environ.obme_filename(source_postfix, identifier),
            j0=j0, g0=g0, tz0=tz0
        )]
        lines += [xform_source_command.format(
            id=identifier, source_postfix=source_postfix, target_postfix=target_postfix,
        )]
        lines += [target_command.format(
            id=identifier, source_postfix=source_postfix, target_postfix=target_postfix,
            filename=environ.obme_filename(target_postfix, identifier)
        )]

    # call obmixer
    mcscript.call(
        [
            environ.shell_filename("obmixer")
        ],
        mode=mcscript.CallMode.kSerial,
        input_lines=lines
    )
