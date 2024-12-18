"""environ.py -- define configuration options for MFDn scripting

Patrick Fasano
University of Notre Dame

- 3/22/17 (pjf): Created, split from __init__.py.
- 4/7/17 (pjf): Rename Configuration -> Environment.
- 6/3/17 (pjf): Remove dependence of filenames on natural orbital iteration.
- 6/5/17 (pjf): Clean up formatting.
- 8/11/17 (pjf): Split TruncationMode into SingleParticleTruncationMode and
    ManyBodyTruncationMode.
- 08/26/17 (pjf): Add parity flag for WeightMax many-body truncation mode.
- 9/12/17 (mac): Put mfdn executable filename under common mcscript install directory.
- 09/12/17 (pjf): Split config.py -> mode.py + environ.py.
- 09/20/17 (pjf): Add configuration for pn-overlap filenames
- 10/15/17 (pjf): Add em-gen and obscalc-ob filenames.
- 12/20/17 (pjf): Remove singleton layer of indirection and make methods module
    globals.
- 12/21/17 (pjf): Allow absolute paths for MFDn and interaction filenames.
- 02/21/19 (mac): Support search for "interaction" file with no hw.
- 04/04/19 (pjf): Add operator_dir_list for operator TBME input file search support.
- 05/29/19 (mac): Add mfdn_postprocessor_filename.
- 08/23/19 (pjf): Add obme_filename.
- 09/20/19 (pjf): Remove observable_me_filename().
- 06/30/22 (pjf):
    + Rename interaction_filename() -> find_interaction_file().
    + Use multi-file mode of mcscript.utils.search_in_subdirectories().
    + Add filename functions for rel and tbme files.
- 06/16/23 (mac): Change default location of mfdn and mfdn-transitions executables to bin subdirectory.
- 08/17/24 (mac):
    + Allow truncation argument of None in find_interaction_file().
    + Add find_operator_file().
    + Rename tmbe_filename() to tbme_filename().

"""

from __future__ import annotations
import os
from typing import Optional

import mcscript.parameters
import mcscript.utils
import mcscript.exception


################################################################
# environment configuration
################################################################

data_dir_h2_list = os.environ.get("NCCI_DATA_DIR_H2", "").split(":")
# Base directories for interaction tbme files ("NCCI_DATA_DIR_H2")
# Environment variable is interpreted as a PATH-style colon-delimited list.

interaction_run_list = []
# subdirectories for interaction tbme files (to be set by calling run script) --
# DEPRECATED in favor of interaction_dir_list

interaction_dir_list = []
# subdirectories for interaction tbme files (to be set by calling run script)

operator_dir_list = []
# subdirectories for operator tbme files (to be set by calling run script)

data_dir_rel_list = os.environ.get("NCCI_DATA_DIR_REL", "").split(":")
# Base directories for interaction tbme files ("NCCI_DATA_DIR_H2")
# Environment variable is interpreted as a PATH-style colon-delimited list.

rel_dir_list = []
# subdirectories for rel and relcm files (to be set by calling run script)

data_dir_decomposition_list = os.environ.get("NCCI_DATA_DIR_DECOMPOSITION", "").split(":")
# Base directories for decomposition coefficient files ("NCCI_DATA_DIR_DECOMPOSITION")
# Environment variable is interpreted as a PATH-style colon-delimited list.

decomposition_dir_list = []
# subdirectories for decomposition coefficient files (to be set by calling run script)

def shell_filename(name):
    """Construct filename for shell package executable."""
    return os.path.join(mcscript.parameters.run.install_dir, "shell", "bin", name)


def mfdn_filename(name):
    """Construct filename for MFDn executable."""
    # check for absolute path to file (which takes priority)
    if os.path.isfile(mcscript.utils.expand_path(name)):
        return mcscript.utils.expand_path(name)
    # check for legacy installation location for executable (not in "bin" subdirectory)
    if os.path.isfile(os.path.join(mcscript.parameters.run.install_dir, "mfdn", name)):
        return os.path.join(mcscript.parameters.run.install_dir, "mfdn", name)
    # standard path
    return os.path.join(mcscript.parameters.run.install_dir, "mfdn", "bin", name)

def mfdn_postprocessor_filename(name):
    """Construct filename for MFDn postprocessor executable."""
    # check for absolute path to file (which takes priority)
    if os.path.isfile(mcscript.utils.expand_path(name)):
        return mcscript.utils.expand_path(name)
    # check for legacy installation location for executable (not in "bin" subdirectory)
    if os.path.isfile(os.path.join(mcscript.parameters.run.install_dir, "mfdn-transitions", name)):
        return os.path.join(mcscript.parameters.run.install_dir, "mfdn-transitions", name)
    # standard path
    return os.path.join(mcscript.parameters.run.install_dir, "mfdn-transitions", "bin", name)

def find_interaction_file(
    interaction:str, truncation:Optional[tuple[str,int]], hw:Optional[float]
):
    """Construct filename for interaction h2 file.

    Arguments:
        interaction (str): interaction name
        truncation (tuple): truncation tuple, e.g. ("tb", 10) (or None)
        hw (float): hw of interaction (or None)

    Returns:
        (str): fully qualified path of interaction file

    Raises:
        mcscript.exception.ScriptError: if no suitable match is found
    """
    if truncation is None:
        # for shell model interaction files
        interaction_filename_candidates = [
            f"{interaction}.bin",
            f"{interaction}.dat",
        ]
    else:
        truncation_str = mcscript.utils.dashify(truncation)
        if hw is None:
            # for special operator files
            interaction_filename_candidates = [
                f"{interaction}_{truncation_str}.bin",
                f"{interaction}-{truncation_str}.bin",  # DEPRECATED
                f"{interaction}_{truncation_str}.dat",
                f"{interaction}-{truncation_str}.dat",  # DEPRECATED
            ]
        else:
            interaction_filename_candidates = [
                f"{interaction}_{truncation_str}_{hw:04.1f}.bin",
                f"{interaction}-{truncation_str}-{hw:04.1f}.bin",  # DEPRECATED
                f"{interaction}-{truncation_str}-{hw:g}.bin",  # DEPRECATED
                f"{interaction}_{truncation_str}_{hw:04.1f}.dat",
                f"{interaction}-{truncation_str}-{hw:04.1f}.dat",  # DEPRECATED
                f"{interaction}-{truncation_str}-{hw:g}.dat",  # DEPRECATED
            ]
    full_interaction_dir_list = interaction_run_list + interaction_dir_list  # interaction_run_list is DEPRECATED
    return mcscript.utils.search_in_subdirectories(
        data_dir_h2_list, full_interaction_dir_list, interaction_filename_candidates,
        fail_on_not_found=True
    )

def find_operator_file(
    operator:str,
):
    """Construct filename for operator h2 file.

    Arguments:
        operator (str): operator name

    Returns:
        (str): fully qualified path of opertor file

    Raises:
        mcscript.exception.ScriptError: if no suitable match is found
    """
    operator_filename_candidates = [
        f"{operator}.bin",
        f"{operator}.dat",
        f"{operator}",  # DEPRECATED -- explicit filename with extension
    ]
    return mcscript.utils.search_in_subdirectories(
        data_dir_h2_list, operator_dir_list, operator_filename_candidates,
        fail_on_not_found=True
    )

def find_rel_file(name:str, Nmax:int, hw:Optional[float]) -> str:
    """Construct filename for relative file.

    Arguments:
        operator (str): operator name
        Nmax (tuple): Nmax
        hw (float): hw of interaction (or None)

    Returns:
        (str): fully qualified path of relative file

    Raises:
        mcscript.exception.ScriptError: if no suitable match is found
    """
    if (hw is None):
        # for special operator files
        filename_candidates = [
            f"{name:s}_Nmax{Nmax:02d}_rel.dat"
        ]
    else:
        filename_candidates = [
            f"{name:s}_Nmax{Nmax:02d}_hw{hw:04.1f}_rel.dat",
            f"{name:s}_Nmax{Nmax:02d}_hw{hw:g}_rel.dat",  # DEPRECATED
        ]
    return mcscript.utils.search_in_subdirectories(
        data_dir_rel_list, rel_dir_list, filename_candidates,
        fail_on_not_found=True
    )

def find_relcm_file(name:str, Nmax:int, hw:Optional[float]) -> str:
    """Construct filename for relative-cm file.

    Arguments:
        operator (str): operator name
        Nmax (tuple): Nmax
        hw (float): hw of interaction (or None)

    Returns:
        (str): fully qualified path of relative-cm file

    Raises:
        mcscript.exception.ScriptError: if no suitable match is found
    """
    if (hw is None):
        # for special operator files
        filename_candidates = [
            f"{name:s}_Nmax{Nmax:02d}_relcm.bin"
            f"{name:s}_Nmax{Nmax:02d}_relcm.dat"
        ]
    else:
        filename_candidates = [
            f"{name:s}_Nmax{Nmax:02d}_hw{hw:04.1f}_relcm.bin",
            f"{name:s}_Nmax{Nmax:02d}_hw{hw:g}_relcm.bin",  # DEPRECATED
            f"{name:s}_Nmax{Nmax:02d}_hw{hw:04.1f}_relcm.dat",
            f"{name:s}_Nmax{Nmax:02d}_hw{hw:g}_relcm.dat",  # DEPRECATED
        ]
    return mcscript.utils.search_in_subdirectories(
        data_dir_rel_list, rel_dir_list, filename_candidates,
        fail_on_not_found=True
    )


################################################################
# filename configuration
################################################################

# filename templates for tbme files
_tbme_filename_template = "{:s}_{:s}-{:d}_{:04.1f}.{:s}"
_tbme_filename_template_nohw = "{:s}_{:s}-{:d}.{:s}"
# filename templates for relative files
_rel_filename_template = "{:s}_Nmax{:02d}_hw{:04.1f}_rel.dat"
_rel_filename_template_nohw = "{:s}_Nmax{:02d}_rel.dat"
# filename templates for relative-cm files
_relcm_filename_template = "{:s}_Nmax{:02d}_hw{:04.1f}_relcm.{:s}"
_relcm_filename_template_nohw = "{:s}_Nmax{:02d}_relcm.{:s}"
# filename template for interaction tbme basis orbitals
_orbitals_int_filename_template = "orbitals-int{:s}.dat"
# filename template for Coulomb tbme basis orbitals
_orbitals_coul_filename_template = "orbitals-coul{:s}.dat"
# filename template for target basis orbitals
_orbitals_filename_template = "orbitals{:s}.dat"
# filename template for change of basis xform
_radial_xform_filename_template = "radial-xform{:s}.dat"
# filename template for radial matrix elements
_radial_me_filename_template = "radial-me-{}{}{:s}.dat"  # "{}{}" will be replaced by {"r1","r2","k1","k2"}
# filename template for one-body matrix elements
_obme_filename_template = "obme-{}{:s}.dat"  # "{}" will be replaced with an operator name
# filename for pn overlap matrix elements
_radial_pn_olap_filename_template = "radial-pn-olap{:s}.dat"
# filename template for overlaps from interaction tbme basis
_radial_olap_int_filename_template = "radial-olap-int{:s}.dat"
# filename template for overlaps from Coulomb tbme basis
_radial_olap_coul_filename_template = "radial-olap-coul{:s}.dat"
# filename template for h2mixer input
_h2mixer_filename_template = "h2mixer{:s}.in"
# filename template for obscalc-ob input
_obscalc_ob_filename_template = "obscalc-ob{:s}.in"
# filename template for obscalc-ob results
_obscalc_ob_res_filename_template = "obscalc-ob{:s}.res"
# filename template for em-gen input
_emgen_filename_template = "em-gen{:s}.in"
# filename template for OBDME info for building natural orbitals
_natorb_info_filename_template = "natorb-obdme{:s}.info"
# filename template for static OBDME file for building natural orbitals
_natorb_obdme_filename_template = "natorb-obdme{:s}.dat"
# filename template for natural orbital xform from previous basis
_natorb_xform_filename_template = "natorb-xform{:s}.dat"

def tbme_filename(name:str, truncation:tuple[str,int], hw:Optional[float], ext:str="bin") -> str:
    """Construct filename for tbme file.

    Arguments:
        name (str): operator/interaction name
        truncation (tuple[str,int]): truncation tuple, e.g. ("ob",10)
        hw (float or None): oscillator hw (in MeV) for operator; None if hw-independent
        ext (str, optional): file extension; defaults to "bin"

    Returns:
        (str): filename
    """
    if hw is None:
        return _tbme_filename_template_nohw.format(name, *truncation, ext)
    return _tbme_filename_template.format(name, *truncation, hw, ext)

def rel_filename(name:str, Nmax:int, hw:Optional[float]) -> str:
    """Construct filename for relative file.

    Arguments:
        name (str): operator/interaction name
        Nmax (int): Nmax truncation for operator
        hw (float or None): oscillator hw (in MeV) for operator; None if hw-independent

    Returns:
        (str): filename
    """
    if hw is None:
        return _rel_filename_template_nohw.format(name, Nmax)
    return _rel_filename_template.format(name, Nmax, hw)

def relcm_filename(name:str, Nmax:int, hw:Optional[float], ext:str="bin") -> str:
    """Construct filename for relative-cm file.

    Arguments:
        name (str): operator/interaction name
        Nmax (int): Nmax truncation for operator
        hw (float or None): oscillator hw (in MeV) for operator; None if hw-independent
        ext (str, optional): file extension; defaults to "bin"

    Returns:
        (str): filename
    """
    if hw is None:
        return _relcm_filename_template_nohw.format(name, Nmax, ext)
    return _relcm_filename_template.format(name, Nmax, hw, ext)

def orbitals_int_filename(postfix):
    """Construct filename for interaction tbme basis orbitals.

    Arguments:
        postfix (str): ignored
    Returns: (str) filename
    """
    # don't make the interaction orbital filename dependent on postfix
    return _orbitals_int_filename_template.format("")

def orbitals_coul_filename(postfix):
    """Construct filename for Coulomb tbme basis orbitals.

    Arguments:
        postfix (str): ignored
    Returns: (str) filename
    """
    # don't make the Coulomb orbital filename dependent on postfix
    return _orbitals_coul_filename_template.format("")

def orbitals_filename(postfix):
    """Construct filename for target basis orbitals.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _orbitals_filename_template.format(postfix)

def radial_xform_filename(postfix):
    """Construct filename for change of basis xform.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _radial_xform_filename_template.format(postfix)

def radial_me_filename(postfix, operator_type, power):
    """Construct filename for radial matrix elements.

    Arguments:
        postfix (str): string to append to end of filename
        operator_type (str): operator code
        power (int): radial operator power
    Returns: (str) filename
    """
    return _radial_me_filename_template.format(operator_type, power, postfix)

def obme_filename(postfix, id):
    """Construct filename for one-body matrix elements.

    Arguments:
        postfix (str): string to append to end of filename
        id (str): operator id
        power (int): radial operator power
    Returns: (str) filename
    """
    return _obme_filename_template.format(id, postfix)

def radial_pn_olap_filename(postfix):
    """Construct filename for overlaps between p and n orbitals.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _radial_pn_olap_filename_template.format(postfix)

def radial_olap_int_filename(postfix):
    """Construct filename for overlaps from interaction tbme basis.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _radial_olap_int_filename_template.format(postfix)

def radial_olap_coul_filename(postfix):
    """Construct filename for overlaps from Coulomb tbme basis.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _radial_olap_coul_filename_template.format(postfix)

def h2mixer_filename(postfix):
    """Construct filename for h2mixer input.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _h2mixer_filename_template.format(postfix)

def obscalc_ob_filename(postfix):
    """Construct filename for obscalc-ob input.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _obscalc_ob_filename_template.format(postfix)

def obscalc_ob_res_filename(postfix):
    """Construct filename for obscalc-ob output.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _obscalc_ob_res_filename_template.format(postfix)

def emgen_filename(postfix):
    """Construct filename for em-gen input.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _emgen_filename_template.format(postfix)

def natorb_info_filename(postfix):
    """Construct filename for MFDn OBDME info output for natural orbitals.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _natorb_info_filename_template.format(postfix)

def natorb_obdme_filename(postfix):
    """Construct filename for MFDn OBDME output for natural orbitals.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _natorb_obdme_filename_template.format(postfix)

def natorb_xform_filename(postfix):
    """Construct filename for natural orbital xform.

    Arguments:
        postfix (str): string to append to end of filename
    Returns: (str) filename
    """
    return _natorb_xform_filename_template.format(postfix)
