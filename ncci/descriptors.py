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
- 04/23/19 (pjf): Make task_descriptor_c1 use two-digit Z and N fields.
- 12/26/19 (mac): Add task_descriptor_7_trans.
- 08/13/20 (pjf): Fix passing M to task_descriptor_7_trans
- 12/02/20 (pjf): Add natural orbital base state info to task_descriptor_7.
- 01/13/21 (pjf): Add task_descriptor_decomposition_1.
- 05/27/21 (pjf): Fix mixed parity indicator in task_descriptor_7.
- 07/08/21 (pjf): Add natural_orbital_indicator to task_descriptor_7_trans.
- 12/30/22 (zz): Add isoscalar_coulomb_indicator to task_descriptor_7.
"""
import mcscript.exception
import mcscript.utils

from . import modes


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
        - Provide default Nstep=2 for convenience when used in transitions run.
    """
    if (
        task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kNmax
        and
        task["basis_mode"] in (modes.BasisMode.kDirect, modes.BasisMode.kDilated)
    ):
        # traditional oscillator run
        template_string = (
            "Z{nuclide[0]}-N{nuclide[1]}-{interaction}-coul{coulomb_flag:d}{isoscalar_coulomb_indicator}"
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
    if (truncation_parameters.get("Nstep") == 1) or (truncation_parameters.get("parity") == 0):
        mixed_parity_indicator = "x"
    else:
        mixed_parity_indicator = ""
    coulomb_flag = int(task["use_coulomb"])
    if task.get("natural_orbitals"):
        natural_orbital_indicator = "-natorb-J{:04.1f}-g{:1d}-n{:02d}".format(*task["natorb_base_state"])
    else:
        natural_orbital_indicator = ""
    if task.get("use_isoscalar_coulomb") is True:
        isoscalar_coulomb_indicator = "is"
    else:
        isoscalar_coulomb_indicator = ""

    descriptor = template_string.format(
        coulomb_flag=coulomb_flag,
        isoscalar_coulomb_indicator=isoscalar_coulomb_indicator,
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
    truncation_int = mcscript.utils.ifelse(task.get("xform_truncation_int"), task["xform_truncation_int"], task["truncation_int"])
    Ncut = "{:s}{:02d}".format(*truncation_int)
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

def task_descriptor_7_trans(task):
    """Task descriptor format 7_trans

        Set up for use with transitions:
        - Remove dependence on basis modes (assumed Nmax mode).
        - Remove max_iterations, and tolerance dependence.
        - Make M dependence optional.
        - Strip mixed parity and fci indicators.
        - Remove a_cm field (may need to restore later).
        - Provide subsetting index.
    """
    truncation_parameters = task["truncation_parameters"]
    template_string = (
        "Z{nuclide[0]}-N{nuclide[1]}-{interaction}-coul{coulomb_flag:d}"
        "-hw{hw:06.3f}"
        ##"-a_cm{a_cm:g}"
        "-Nmax{Nmax:02d}"
        "{M_field}"
        "{subset_field}"
        "{natural_orbital_indicator}"
    )

    coulomb_flag = int(task["use_coulomb"])
    ##natural_orbital_indicator = mcscript.utils.ifelse(task.get("natural_orbitals"), "-natorb", "")
    M_field = "-Mj{M:03.1f}".format(**truncation_parameters) if (truncation_parameters.get("M") is not None) else ""
    subset_field = "-subset{subset[0]:03d}".format(**task) if (task.get("subset") is not None) else ""
    if task.get("natural_orbitals"):
        natural_orbital_indicator = "-natorb-J{:04.1f}-g{:1d}-n{:02d}".format(*task["natorb_base_state"])
    else:
        natural_orbital_indicator = ""
    descriptor = template_string.format(
        coulomb_flag=coulomb_flag,
        M_field=M_field,
        subset_field=subset_field,
        natural_orbital_indicator=natural_orbital_indicator,
        **mcscript.utils.dict_union(task, truncation_parameters)
    )

    return descriptor

def task_descriptor_8(task):
    """Task descriptor format 8

        General (triangular) truncation run descriptor.
    """
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


def task_descriptor_decomposition_1(task):
    """Task descriptor for decomposition.

    Requires task to have "wf_source_info" with "descriptor" function.
    """

    template_string = (
        "{source_wf_descriptor:s}"
        "-J{source_wf_qn[0]:04.1f}-g{source_wf_qn[1]:1d}-n{source_wf_qn[2]:02d}"
        "-op{decomposition_operator_name:s}-dlan{max_iterations:d}"
        # 01/19/21 (mac): However, we propose moving away from calling this an "operator",
        # but rather a decomposition type.  See runmac0566.py.  "-{decomposition_name:s}".
        # How does this interact with the "decomposition" flag in the format 7 mfdnres parser?
    )

    descriptor = template_string.format(
        source_wf_descriptor=task["wf_source_info"]["descriptor"](task["wf_source_info"]),
        **task
    )

    return descriptor


def task_descriptor_c1(task):
    """Task descriptor format c1

        Task descriptor for counting-only runs:
            - Currently support Nmax and triangular s.p. truncations.
            - Currently support FCI, Nmax, and WTmax m.b. truncations.
    """

    template_string = (
        "Z{nuclide[0]:02d}-N{nuclide[1]:02d}"
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
        **mcscript.utils.dict_union(task, truncation_parameters)
        )

    return descriptor
