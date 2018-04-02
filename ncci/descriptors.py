"""descriptors.py -- task descriptors for MFDn runs.

Patrick Fasano
University of Notre Dame

- 03/22/17 (pjf): Created, split from __init__.py.
- 04/07/17 (pjf): Reference new config submodule.
- 06/03/17 (pjf): Switch natorb_iteration -> natural_orbitals.
- 06/13/17 (pjf): Add task_descriptor_7b (includes Ncut).
- 08/11/17 (pjf): Use new TruncationModes.
- 08/26/17 (pjf): Add task_descriptor_8 for general truncation.
- 09/12/17 (pjf): Update for config -> modes + environ split.
- 10/04/17 (pjf): Add counting-only descriptor.
- 01/04/18 (pjf): Add task_descriptor_9 for manual orbitals.
"""
import mcscript.exception
import mcscript.utils

from . import (
    input,
    modes,
    )


_parity_map = {+1: "g0", -1: "g1", 0: "gx"}

################################################################
# task descriptor for h2mixer + mfdn run
################################################################

def task_descriptor_7(task):
    """Task descriptor format 7

        Overhaul for new h2utils scripting:
        - Strip back down to basic form for oscillator-like runs only.
        - Adjust some field labels.
        - Add tolerance.
    """
    # preprocess task dictionary
    input.fill_default_values(task)

    if (
        task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kNmax
        and
        task["basis_mode"] in (modes.BasisMode.kDirect, modes.BasisMode.kDilated)
    ):
        # traditional oscillator run
        template_string = (
            "Z{nuclide[0]}-N{nuclide[1]}-{interaction}-coul{coulomb_flag:d}"
            "-hw{hw:06.3f}"
            "-a_cm{a_cm:g}"
            "-Nmax{Nmax:02d}{mixed_parity_indicator}{fci_indicator}-Mj{M:03.1f}"
            "-lan{max_iterations:d}-tol{tolerance:.1e}"
            "{natural_orbital_indicator}"
            )
    else:
        raise mcscript.exception.ScriptError("mode not supported by task descriptor")

    truncation_parameters = task["truncation_parameters"]
    if task["mb_truncation_mode"] == modes.ManyBodyTruncationMode.kFCI:
        fci_indicator = "-fci"
    else:
        fci_indicator = ""
    mixed_parity_indicator = mcscript.utils.ifelse(truncation_parameters["Nstep"] == 1, "x", "")
    coulomb_flag = int(task["use_coulomb"])
    natural_orbital_indicator = mcscript.utils.ifelse(task["natural_orbitals"], "-natorb", "")

    descriptor = template_string.format(
        coulomb_flag=coulomb_flag,
        mixed_parity_indicator=mixed_parity_indicator,
        fci_indicator=fci_indicator,
        natural_orbital_indicator=natural_orbital_indicator,
        **mcscript.utils.dict_union(task, truncation_parameters)
        )

    return descriptor


def task_descriptor_7b(task):
    """Task descriptor format 7b

        - Add Ncut field
    """
    # preprocess task dictionary
    input.fill_default_values(task)

    if (
        task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kNmax
        and
        task["basis_mode"] in (modes.BasisMode.kDirect, modes.BasisMode.kDilated)
    ):
        # traditional oscillator run
        template_string = (
            "Z{nuclide[0]}-N{nuclide[1]}-{interaction}-coul{coulomb_flag:d}"
            "-hw{hw:06.3f}"
            "-a_cm{a_cm:g}"
            "-Nmax{Nmax:02d}-Ncut{Ncut:s}"
            "{mixed_parity_indicator}{fci_indicator}-Mj{M:03.1f}"
            "-lan{max_iterations:d}-tol{tolerance:.1e}"
            "{natural_orbital_indicator}"
            )
    else:
        raise mcscript.exception.ScriptError("mode not supported by task descriptor")

    truncation_parameters = task["truncation_parameters"]
    Ncut = "{:s}{:02d}".format(*task["xform_truncation_int"])
    if task["mb_truncation_mode"] == modes.ManyBodyTruncationMode.kFCI:
        fci_indicator = "-fci"
    else:
        fci_indicator = ""
    mixed_parity_indicator = mcscript.utils.ifelse(truncation_parameters["Nstep"] == 1, "x", "")
    coulomb_flag = int(task["use_coulomb"])
    natural_orbital_indicator = mcscript.utils.ifelse(task.get("natural_orbitals"), "-natorb", "")

    descriptor = template_string.format(
        coulomb_flag=coulomb_flag,
        Ncut=Ncut,
        mixed_parity_indicator=mixed_parity_indicator,
        fci_indicator=fci_indicator,
        natural_orbital_indicator=natural_orbital_indicator,
        **mcscript.utils.dict_union(task, truncation_parameters)
        )

    return descriptor


def task_descriptor_8(task):
    """Task descriptor format 8

        General (triangular) truncation run descriptor.
    """
    # preprocess task dictionary
    input.fill_default_values(task)

    if (
            task["basis_mode"] in (modes.BasisMode.kDirect, modes.BasisMode.kDilated)
            and
            task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kTriangular
            and
            task["mb_truncation_mode"] in (modes.ManyBodyTruncationMode.kWeightMax, modes.ManyBodyTruncationMode.kFCI)
    ):
        # oscillator basis
        template_string = (
            "Z{nuclide[0]}-N{nuclide[1]}-{interaction}-coul{coulomb_flag:d}"
            "-hw{hw:06.3f}"
            "-a_cm{a_cm:g}"
            "-an{n_coeff:06.3f}-bl{l_coeff:06.3f}-spWTmax{sp_weight_max:06.3f}"
            "{mb_truncation}-{parity_indicator}-Mj{M:03.1f}"
            "-its{max_iterations:d}-tol{tolerance:.1e}"
            "{natural_orbital_indicator}"
            )
    else:
        raise mcscript.exception.ScriptError("mode not supported by task descriptor")

    truncation_parameters = task["truncation_parameters"]
    if task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kFCI:
        mb_truncation = "-FCI"
    elif task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kWeightMax:
        mb_truncation = "-WTmax{mb_weight_max:06.3f}".format(**truncation_parameters)
    parity_indicator = _parity_map[truncation_parameters["parity"]]
    coulomb_flag = int(task["use_coulomb"])
    natural_orbital_indicator = mcscript.utils.ifelse(task.get("natural_orbitals"), "-natorb", "")

    descriptor = template_string.format(
        coulomb_flag=coulomb_flag,
        mb_truncation=mb_truncation,
        parity_indicator=parity_indicator,
        natural_orbital_indicator=natural_orbital_indicator,
        **mcscript.utils.dict_union(task, truncation_parameters)
        )

    return descriptor


def task_descriptor_9(task):
    """Task descriptor format 9

        General truncation run descriptor for manual orbitals.
    """
    # preprocess task dictionary
    input.fill_default_values(task)

    if (
            task["basis_mode"] in (modes.BasisMode.kDirect, modes.BasisMode.kDilated)
            and
            task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kManual
            and
            task["mb_truncation_mode"] in (modes.ManyBodyTruncationMode.kWeightMax, modes.ManyBodyTruncationMode.kFCI)
    ):
        # oscillator basis
        template_string = (
            "Z{nuclide[0]}-N{nuclide[1]}-{interaction}-coul{coulomb_flag:d}"
            "-hw{hw:06.3f}"
            "-a_cm{a_cm:g}"
            "-spWTmax{sp_weight_max:06.3f}"
            "{mb_truncation}{parity_indicator}-Mj{M:03.1f}"
            "-its{max_iterations:d}-tol{tolerance:.1e}"
            "{natural_orbital_indicator}"
            )
    else:
        raise mcscript.exception.ScriptError("mode not supported by task descriptor")

    truncation_parameters = task["truncation_parameters"]
    if task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kFCI:
        mb_truncation = "-FCI"
    elif task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kWeightMax:
        mb_truncation = "-WTmax{mb_weight_max:06.3f}".format(**truncation_parameters)
    parity_indicator = _parity_map[truncation_parameters["parity"]]
    coulomb_flag = int(task["use_coulomb"])
    natural_orbital_indicator = mcscript.utils.ifelse(task.get("natural_orbitals"), "-natorb", "")

    descriptor = template_string.format(
        coulomb_flag=coulomb_flag,
        mb_truncation=mb_truncation,
        parity_indicator=parity_indicator,
        natural_orbital_indicator=natural_orbital_indicator,
        **mcscript.utils.dict_union(task, truncation_parameters)
        )

    return descriptor


def task_descriptor_c1(task):
    """Task descriptor format c1

        Task descriptor for counting-only runs:
            - Currently support Nmax and triangular s.p. truncations.
            - Currently support FCI, Nmax, and WTmax m.b. truncations.
    """
    # preprocess task dictionary
    input.fill_default_values(task)

    template_string = (
        "Z{nuclide[0]}-N{nuclide[1]}"
        "{sp_truncation:s}{mb_truncation:s}{mixed_parity_indicator}-Mj{M:03.1f}"
    )
    if task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kNmax:
        sp_truncation = "-Nmax{Nmax:02d}".format(**task["truncation_parameters"])
    elif task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kTriangular:
        sp_truncation = "-an{n_coeff:06.3f}-bl{l_coeff:06.3f}-spWTmax{sp_weight_max:06.3f}".format(**task["truncation_parameters"])
    else:
        raise mcscript.exception.ScriptError("mode not supported by task descriptor")

    truncation_parameters = task["truncation_parameters"]
    if task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kFCI:
        mb_truncation = "-FCI"
    elif task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kNmax:
        mb_truncation = ""
    elif task["mb_truncation_mode"] is modes.ManyBodyTruncationMode.kWeightMax:
        mb_truncation = "-WTmax{mb_weight_max:06.3f}".format(**truncation_parameters)
    mixed_parity_indicator = mcscript.utils.ifelse(truncation_parameters.get("parity") == 0, "x", "")

    descriptor = template_string.format(
        sp_truncation=sp_truncation,
        mb_truncation=mb_truncation,
        mixed_parity_indicator=mixed_parity_indicator,
        **task
        )

    return descriptor
