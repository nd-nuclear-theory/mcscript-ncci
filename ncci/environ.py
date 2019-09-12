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
"""

import os

import mcscript.parameters
import mcscript.utils


################################################################
# environment configuration
################################################################

data_dir_h2_list = os.environ.get("NCCI_DATA_DIR_H2").split(":")
# Base directories for interaction tbme files ("NCCI_DATA_DIR_H2")
# Environment variable is interpreted as a PATH-style colon-delimited list.

interaction_run_list = []
# subdirectories for interaction tbme files (to be set by calling run script)

operator_dir_list = []
# subdirectories for operator tbme files (to be set by calling run script)


def shell_filename(name):
    """Construct filename for shell package executable."""
    return os.path.join(mcscript.parameters.run.install_dir, "shell", "bin", name)


def mfdn_filename(name):
    """Construct filename for MFDn executable."""
    if os.path.isfile(mcscript.utils.expand_path(name)):
        return mcscript.utils.expand_path(name)
    return os.path.join(mcscript.parameters.run.install_dir, "mfdn", name)

def mfdn_postprocessor_filename(name):
    """Construct filename for MFDn postprocessor executable."""
    if os.path.isfile(mcscript.utils.expand_path(name)):
        return mcscript.utils.expand_path(name)
    return os.path.join(mcscript.parameters.run.install_dir, "mfdn-transitions", name)

def interaction_filename(interaction, truncation, hw):
    """Construct filename for interaction h2 file.

    Arguments:
        interaction (str): interaction name
        truncation (tuple): truncation tuple, e.g. ("tb", 10)
        hw (float): hw of interaction (or None)

    Returns:
        (str): fully qualified path of interaction file

    Raises:
        mcscript.exception.ScriptError: if no suitable match is found
    """
    if (hw is None):
        # for special operator files
        interaction_filename_patterns = [
            "{}-{}.bin",
            "{}-{}.dat"
        ]
    else:
        interaction_filename_patterns = [
            "{}-{}-{:04.1f}.bin",
            "{}-{}-{:g}.bin",
            "{}-{}-{:04.1f}.dat",
            "{}-{}-{:g}.dat",
        ]
    for filename_pattern in interaction_filename_patterns:
        filename = filename_pattern.format(
            interaction, mcscript.utils.dashify(truncation), hw
        )
        path = mcscript.utils.search_in_subdirectories(
            data_dir_h2_list, interaction_run_list, filename,
            fail_on_not_found=False
            )
        if path is not None:
            return path

    # no valid file found
    raise mcscript.exception.ScriptError("no match on interaction filename")



################################################################
# filename configuration
################################################################

### orbital filename templates ###
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
# filename template for observable matrix elements
_observable_me_filename_template = "observable-me-{}{}{}{:s}.dat"  # "{}{}{}" will be replaced by {"E2p","M1n",etc.}
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

def observable_me_filename(postfix, operator_type, power, species):
    """Construct filename for observable matrix elements.

    Arguments:
        postfix (str): string to append to end of filename
        operator_type (str): operator code
        power (int): radial operator power
        species (str): species operator applies to
    Returns: (str) filename
    """
    return _observable_me_filename_template.format(operator_type, power, species, postfix)

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
