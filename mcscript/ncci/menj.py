""" menj.py -- collection of functions needed to run MFDn in MENJ mode

Shwetha Vittal
University of Notre Dame

- 11/05/23 (slv): 
    + Create function to copy interaction files to working directory.
    + Move generate_menj_par() from mfdn_v15.py.

- 01/13/23 (zz): 
    + Skip copying 3b files for 2b runs.
    + Fix file names to use the correct truncations.


"""
import os

import mcscript
from . import environ

def set_up_menj_files(task, postfix=""):
    """Copy interaction files to work directory

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    work_dir = "work{:s}".format(postfix)
    mcscript.utils.mkdir(work_dir, exist_ok=True, parents=True) 

    energy_truncation_2b = "eMax{:d}_EMax{:d}".format(task["EMax"],task["EMax"])
    energy_truncation_3b = "eMax{:d}_EMax{:d}".format(task["E3Max"],task["E3Max"])
    bin_extension_2b = "me2j.bin"
    bin_extension_3b = "me3j.bin"
    
    # construct the matrix element file names
    # me2j_filename = "{:>}_eMax{:d}_EMax{:d}_hwHO{:03d}.me2j.bin".format(task["me2j_file_id"],task["EMax"],task["E3Max"],task["hw"])
    # trel_filename = "trel_eMax{:d}_EMax{:d}.me2j.bin".format(task["EMax"],task["E3Max"])
    # rsq_filename =  "rsq_eMax{:d}_EMax{:d}.me2j.bin".format(task["EMax"],task["E3Max"])
    # me3j_filename = "{:>}_eMax{:d}_EMax{:d}_hwHO{:03d}.me3j.bin".format(task["me3j_file_id"],task["EMax"],task["E3Max"],task["hw"])

    # find and copy matrix element files to the working directory
    # source_filenames = [me2j_filename, trel_filename, rsq_filename, me3j_filename]

    source_filenames = [
        "{:>}_{:>}_hwHO{:03d}.{:>}".format(task["me2j_file_id"], energy_truncation_2b, task["hw"], bin_extension_2b),
        "trel_{:>}.{:>}".format(energy_truncation_2b, bin_extension_2b),
        "rsq_{:>}.{:>}".format(energy_truncation_2b, bin_extension_2b),
    ]
    if task["use_3b"]:
        source_filenames.append("{:>}_{:>}_hwHO{:03d}.{:>}".format(task["me3j_file_id"],energy_truncation_3b, task["hw"], bin_extension_3b))
    for source in source_filenames:
        mcscript.control.call(
            [
                "cp",
                "--verbose",
                mcscript.utils.search_in_subdirectories(os.environ.get("NCCI_DATA_DIR_H2","").split(":"), environ.interaction_dir_list, source),
                os.path.join(work_dir)
            ],
            shell=True
        )

def generate_menj_par(task, postfix=""):

    """
    Generate the menj.par input file for the MFDn version 15 with menj extension.

    Arguments:
        task (dict): as described in docs/task.md
        run_mode (modes.MFDnRunMode): run mode for MFDn
        postfix (string, optional): identifier to add to generated files

    Raises:
        mcscript.exception.ScriptError: if MFDn output not found
    
    """
    # create work directory if it doesn't exist yet
    work_dir = "work{:s}".format(postfix)
    mcscript.utils.mkdir(work_dir, exist_ok=True, parents=True)
    
    # create list of lines for menj.par file
    lines = []
    
    # nucleus
    # A       : total nucleon number
    #           (needs to be the same as (Z+N) in mfdn.input)
    Z, N = task["nuclide"]
    lines.append("A={:d}".format(Z+N))

    # hwHO    : HO basis parameter
    lines.append("hwHO={:d}".format(task["hw"]))
    
    # lamHcm  : scaling factor for Hcm Hamiltonian (dimensionless)
    lines.append("lamHcm={:.1f}".format(task["a_cm"]/task["hw"]))
    
    # NN      : compute 2-body matrix elements (0=no, 1=yes)
    # Hardcoded to be 1, since there is no point in using the menj
    # variant without two body interaction  
    lines.append("NN={:d}".format(1))
    
    # EMax    : maximum 2-body HO quantum number of the TBME file
    lines.append("EMax={:d}".format(task["EMax"]))
            
    # MEID    : string containing path/ID of the 2B interaction
    lines.append("MEID={:>1}".format(task["me2j_file_id"]))
            
    # TrelID  : string containing path/ID of the 2B kinetic energy
    #           matrix element file that is read in
    #
    # Hardcoding "trel" as file ID
    lines.append("TrelID={:>1}".format("trel"))
            
    # RsqID   : string containing path/ID of the 2B squared radius
    #           matrix element file that is read in
    #
    # Hardcoding "rsq" as file ID
    lines.append("RsqID={:>1}".format("rsq"))
    
    # NNN     : compute 3-body matrix elements (0=no, 1=yes)
    lines.append("NNN={:d}".format(task["use_3b"]))
    
    # E3Max   : maximum 3-body HO quantum number
    lines.append("E3Max={:d}".format(task["E3Max"]))
    
    # ME3ID   : string containing path/ID of the 3B interaction
    #           matrix element file that is read in
    lines.append("ME3ID={:>1}".format(task["me3j_file_id"]))

    # generate menj.par file
    mcscript.utils.write_input(
        os.path.join(work_dir, "menj.par"), lines
    )
