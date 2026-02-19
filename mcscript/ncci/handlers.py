"""handlers.py -- task handlers for MFDn runs.

Patrick Fasano
University of Notre Dame

- 03/22/17 (pjf): Created, split from __init__.py.
- 04/07/17 (pjf): Update for mcscript namespace changes.
- 06/05/17 (pjf): Added basic handlers for oscillator and natural orbital runs.
- 06/07/17 (pjf): Clean up style.
- 06/22/17 (pjf): Update references to mcscript.exception.ScriptError.
- 07/31/17 (pjf): Move mfdn driver from handler argument to task dictionary.
- 09/12/17 (pjf): Update for config -> modes + environ split.
- 09/24/17 (pjf): Fix call to cleanup_mfdn_workdir() in task_handler_natorb().
- 09/25/17 (pjf): Add archive_handler_mfdn() and archive_handler_mfdn_hsi().
- 10/11/17 (pjf): Break task handlers into serial/hybrid phases.
- 10/18/17 (pjf): Call extract_natural_orbitals().
- 04/23/18 (mac): Provide handler for MFDn phase of oscillator run.
- 10/17/18 (mac): Remove deprecated results-only archive handler.
- 04/30/19 (mac): Add separate archive for task data archive directory.
- 05/03/19 (mac): Add task_handler_post_run_no_cleanup().
- 05/29/19 (mac): Remove task_handler_post_run_no_cleanup().
- 05/30/19 (pjf):
    + Call save_wavefunctions() in task_handler_post_run().
    + Make archive_handler_mfdn() and archive_handler_mfdn_hsi() simple
      wrappers for underlying mcscript generic handlers.
    + Remove references to save_mfdn_output_out_only().
- 06/02/19 (mac): Rename save_mfdn_output to save_mfdn_task_data.
- 07/03/19 (mac): Restore task_handler_post_run_no_cleanup().
- 07/14/19 (mac): Update archive_handler_mfdn() to use archive_handler_subarchives().
- 10/10/19 (pjf):
    + Change default MFDn driver to mfdn_v15.
    + Use tbme.generate_diagonalization_tbme() instead of tbme.generate_tbme().
- 10/24/19 (mac):
    + Add task_handler_oscillator_mfdn_decomposition().
    + Update archive_handler_mfdn() to archive lanczos files.
    + Clean up task_handler_oscillator() to call task_handler_oscillator_mfdn().
- 12/11/19 (pjf): Use new results storage helper functions from mcscript.
- 06/03/20 (pjf): Make natural orbital base state selected by quantum numbers.
- 09/16/20 (pjf):
    + Revert to general tbme.generate_tbme().
    + Fix obdme archiving.
- 09/19/20 (pjf): Separate out calls for OBME and xform generation.
- 09/20/20 (pjf): Add task handler for transitions runs.
- 10/21/20 (pjf):
    + Split out pre and post phases from task_handler_postprocessor().
    + Add explicit call to postprocessing.init_postprocessor_db().
- 05/14/21 (pjf): Use partitioning from task-data for decompositions.
- 02/25/22 (pjf): Only call task_handler_postprocessor_pre from
    task_handler_postprocessor if not task is not being resumed.
- 05/09/22 (pjf): Call generate_mfdn_input() in addition to run_mfdn().
- 05/29/22 (pjf): Implement task_handler_postprocessor_post.
- 06/30/22 (pjf):
    + Harmonize/standardize task handler names.
    + Provide predefined lists of handlers.
- 07/05/22 (pjf): Add task_handler_relative().
- 07/06/22 (pjf): Improve relative task handlers.
- 08/15/22 (pjf): Implement cleanup in task_handler_mfdn_postprocessor_post.
- 05/31/23 (pjf): Add postprocessor archive handlers.
- 10/12/23 (slv): Add mfdn_menj_pre handler and a function that runs all three phase sequentially
- 10/19/23 (slv): Remove the menj_pre handler and use the modes.VariantMode.kMENJ as the 
                  determining condition to copy the interaction files.
- 01/16/23 (zz): Generate mfdn_smwf.info for menj runs.
- 02/05/24 (mac): Add -tbme archive to archive_handler_mfdn.
- 07/21/25 (mac):
  + Provide decomposition wf selection by "wf_source_runs" and "wf_source_selector".
  + Add sensible default task dictionary parameters for decomposition handlers.
- 07/22/25 (mac): Extract partitioning for decomposition runs from mfdn_smwf.info.
- 08/08/25 (mac): Add wf truncation capability for decomposition.
- 09/26/25 (mac): Add TBME generation run task handler task_handler_tbme.
- 10/22/25 (mac/seb): Move truncation before decomposition into task_handler_decomposition_pre.
- 01/30/26 (seb): Add task handler for strength function runs.
- 02/06/26 (seb): Update norm output for strength function runs.
- 02/09/26 (seb): Remove mistakenly added text from tbme handler.
"""
import glob
import os

import mcscript.exception
import mcscript.parameters
import mcscript.task
import mfdnres

from . import (
    environ,
    library,
    menj,
    mfdn_v15,
    modes,
    operators,
    postprocessing,
    radial,
    relative,
    tbme,
    utils,
)

# set default MFDn driver
default_mfdn_driver = mfdn_v15

################################################################
# counting-only run
################################################################

def task_handler_mfdn_dimension(task, postfix=""):
    """Task handler for dimension counting-only run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver
    radial.set_up_orbitals(task, postfix=postfix)
    mfdn_driver.generate_mfdn_input(
        task=task, run_mode=modes.MFDnRunMode.kDimension, postfix=postfix
    )
    mfdn_driver.run_mfdn(task=task, postfix=postfix)


def task_handler_mfdn_nonzeros(task, postfix=""):
    """Task handler for nonzero counting-only run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver
    radial.set_up_orbitals(task, postfix=postfix)
    mfdn_driver.generate_mfdn_input(
        task=task, run_mode=modes.MFDnRunMode.kNonzeros, postfix=postfix
    )
    mfdn_driver.run_mfdn(task=task, postfix=postfix)


################################################################
# generic cleanup and archive steps
################################################################

def task_handler_mfdn_post(task, postfix="", cleanup=True):
    """Task handler for serial components after MFDn run.

    If expect to use wave functions after initial results archive, invoke this
    handler with cleanup=False option, as

        phase_handler_list=[
            ...
            functools.partial(ncci.handlers.task_handler_post_run,cleanup=False),
            ...
            ]

    Unfortunately, this hides the docstring from being properly listed in the
    phase summary.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
        cleanup (bool, optional): whether or not to do cleanup after archiving

    """
    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver

    # generate mfdn_smwf.info for menj runs
    variant_mode = task.get("mfdn_variant", modes.VariantMode.kH2)
    if variant_mode is modes.VariantMode.kMENJ:
        descriptor = task["metadata"]["descriptor"]
        filename_prefix = "{:s}-mfdn15-{:s}{:s}".format(mcscript.parameters.run.name, descriptor, postfix)
        res_filename = os.path.join("..","results","res","{:s}.res".format(filename_prefix))
        mfdn_driver.generate_smwf_info(
            task=task,
            orbital_filename="orbitals.dat",
            partitioning_filename="work/mfdn_partitioning.generated",
            res_filename=res_filename,
            info_filename="work/mfdn_smwf.info"
        )

    # save OBDME files for next natural orbital iteration
    if task.get("natural_orbitals"):
        mfdn_driver.extract_natural_orbitals(task, postfix)

    mfdn_driver.save_mfdn_task_data(task, postfix=postfix)
    if task.get("save_obdme"):
        mfdn_driver.save_mfdn_obdme(task, postfix)
    if task.get("save_wavefunctions"):
        mfdn_driver.save_mfdn_wavefunctions(task, postfix)
    if (cleanup):
        mfdn_driver.cleanup_mfdn_workdir(task, postfix=postfix)

        
def task_handler_mfdn_post_no_cleanup(task, postfix=""):
    """ Task handler for serial components after MFDn run (no cleanup).

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    task_handler_mfdn_post(task,postfix=postfix,cleanup=False)


################################################################
# basic MFDn run
################################################################

def task_handler_mfdn_pre(task, postfix=""):
    """Task handler for serial components before MFDn phase of basic oscillator run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    variant_mode = task.get("mfdn_variant", modes.VariantMode.kH2)
    if variant_mode is modes.VariantMode.kH2:
        radial.set_up_interaction_orbitals(task, postfix=postfix)
        radial.set_up_orbitals(task, postfix=postfix)
        radial.set_up_xforms_analytic(task, postfix=postfix)
        radial.set_up_obme_analytic(task, postfix=postfix)
        tbme.generate_tbme(task, postfix=postfix)
        if task.get("save_tbme"):
            tbme.save_tbme(task, postfix=postfix)
    elif variant_mode is modes.VariantMode.kMENJ:
        radial.set_up_orbitals(task, postfix=postfix) # needed to generate mfdn_smwf.info
        menj.set_up_menj_files(task, postfix = postfix)
        
    else:
        raise(ValueError("unsupported variant mode"))

    
def task_handler_mfdn_run(task, postfix=""):
    """Task handler for MFDn phase of oscillator basis run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    # run MFDn
    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver
    mfdn_driver.generate_mfdn_input(task=task, postfix=postfix)
    mfdn_driver.run_mfdn(task=task, postfix=postfix)

    
def task_handler_mfdn(task, postfix=""):
    """Task handler for complete oscillator basis run, including serial pre and post
    steps.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files

    """

    task_handler_mfdn_pre(task, postfix=postfix)
    task_handler_mfdn_run(task, postfix=postfix)
    task_handler_mfdn_post(task, postfix=postfix)

    
task_handler_mfdn_phases = [
    task_handler_mfdn_pre,
    task_handler_mfdn_run,
    task_handler_mfdn_post,
]


def extract_partitioning_from_smwf_info_file(
        wf_source_dir,
        *,
        smwf_info_filename="mfdn_smwf.info",
        partitioning_info_filename="mfdn_partitioning.info",
):
    """Parse smwf info file to extract partitioning and write to partitioning info file.

    Arguments:

        wf_source_dir (str): Path to wave function directory.

        smwf_info_filename (str, optional): Filename for smwf info file within
        wave function directory.

        partitioning_info_filename (str, optional): Filename for partitioning
        info file within partitioning target directory.

    """

    # parse
    in_file = open(os.path.join(wf_source_dir, smwf_info_filename), "r")
    in_file_lines = [row for row in in_file]
    in_file.close()
    tokenized_lines = list(mfdnres.tools.split_and_prune_lines(in_file_lines))
                   
    # skip header (checking version)
    tokens = tokenized_lines.pop(0)
    if int(tokens[0]) != 15200:
        raise mcscript.exception.ScriptError("Unrecognized version number in smwf_info file")
    tokens = tokenized_lines.pop(0)
    tokens = tokenized_lines.pop(0)

    # skip orbitals
    tokens = tokenized_lines.pop(0)
    num_orbitals = int(tokens[0]) + int(tokens[1])
    for _ in range(num_orbitals):
        tokens = tokenized_lines.pop(0)

    # parse and store partitioning
    lines = []
    tokens = tokenized_lines.pop(0)
    lines.append(" ".join(tokens))
    num_partitions = int(tokens[0]) + int(tokens[1])
    num_partitions_read = 0
    while num_partitions_read < num_partitions:
        tokens = tokenized_lines.pop(0)
        lines.append(" ".join(tokens))
        num_partitions_read += len(tokens)
        
    # write output
    mcscript.utils.write_input(
        partitioning_info_filename,
        input_lines=lines,
    )    

    
def get_wf_source_info(task):
    """Identify 'source' directory and sequence number for single wf to process.

    Arguments:

        task (dict): Dictionary in the form of a standard task dictionary,
        providing specifically: wf_run_list, wf_selector, wf_qn, wf_res_format
        (optional), wf_glob_pattern (optional).

    Returns:
        
        wf_source_run [str]: Run string

        wf_source_descriptor [str]: Descriptor string

        res_data (mfdnres.ResultsData): Results data object providing level

        level_seq [int]: Sequence number

    """
    
    # legacy: support deprecated task key "source_wf_qn"
    if "source_wf_qn" in task:
        task.setdefault("wf_qn", task["source_wf_qn"])
    elif "decomposition_qn" in task:
        task.setdefault("wf_qn", task["decomposition_qn"])
    qn = task["wf_qn"]
    
    # set up run parameters
    if "wf_source_run_descriptor_seq" in task:
        # explicit designation of run and descriptor for wf
        #
        # Keys: "wf_source_run_descriptor_seq"
        wf_source_run, wf_source_descriptor = task["wf_source_run_descriptor"]

        # confirm existence of run and retrieve results data
        res_data = library.get_res_data(wf_source_run, wf_source_descriptor)
        
    elif "wf_source_info" in task:
        # legacy API: explicit construction of descriptor
        #
        # Keys: "wf_source_info"

        # process source wave function task/descriptor info
        wf_source_info = task["wf_source_info"]
        wf_source_info.setdefault("metadata",{})
        wf_source_info["metadata"]["descriptor"] = wf_source_info["descriptor"](wf_source_info)

        # retrieve level data
        wf_source_run = wf_source_info["run"]
        wf_source_descriptor = wf_source_info["metadata"]["descriptor"]

        # confirm existence of run and retrieve results data
        res_data = library.get_res_data(wf_source_run, wf_source_descriptor)
        
    elif "wf_source_selector" in task:
        # postprocessor-like API: obtain descriptor by hunting in res data
        #
        # Keys: "wf_source_run_list", "wf_source_selector"
        
        # process source wave function info
        print("Reading mesh data:")
        wf_source_run_list = task["wf_source_run_list"]
        wf_source_res_format = task.get("wf_source_res_format")
        wf_source_glob_pattern = task.get("wf_source_glob_pattern")
        wf_source_selector = task["wf_source_selector"]
        mesh_data, _ = postprocessing.select_source_wf_data(
            run_list=wf_source_run_list,
            selector=wf_source_selector,
            res_format=wf_source_res_format,
            filename_format="ALL",
            glob_pattern=wf_source_glob_pattern,
            verbose=True,
        )
        
        # diagnostic output
        print("Mesh points:")
        for mesh_point in mesh_data:
            print(" ", mesh_point.params.get("run"), mesh_point.params.get("descriptor"))

        # select run, descriptor, and sequence number
        res_data = None
        for mesh_point in mesh_data:
            if qn not in mesh_point.levels:
                continue
    
            wf_source_run = mesh_point.params["run"]
            wf_source_descriptor = mesh_point.params["descriptor"]
    
            res_data = mesh_point

        if res_data is None:
            raise mcscript.ScriptError("No source wave function found with given qn")

    # get sequence number for level within smwf file
    levels = res_data.levels
    level_seq_lookup = dict(map(reversed, enumerate(levels, 1)))
    level_seq = level_seq_lookup[qn]
    if level_seq is None:
        raise mcscript.ScriptError("No source wave function found with given qn")
    
    return wf_source_run, wf_source_descriptor, res_data, level_seq


def task_handler_mfdn_decomposition_pre(task, postfix=""):
    """Task handler for serial components before MFDn phase of Lanczos
    decomposition, assuming oscillator basis.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files

    """

    work_dir = "work{:s}".format(postfix)
    
    # set some defaults
    task.setdefault("diagonalization", True)  # to disable unnecessary obdme calculation
    task.setdefault("calculate_obdme", False)  # to disable unnecessary obdme calculation
    # 08/08/25 (mac): Setting calculate_tbo to false leads to intermittent and
    # nondeterministic memory deallocation errors with mfdn commit 3f34aa7,
    # dependent upon OpenMP parameters.
    ## task.setdefault("calculate_tbo", False)  # to disable unnecessary Ncm and rrel2 operators
    task.setdefault("tolerance", 0)  # iterate to max iterations

    # impose truncation
    if "truncation_model_info" in task:

        # locate wave function
        wf_source_run, wf_source_descriptor, res_data, level_seq = get_wf_source_info(task)
        wf_prefix = library.get_wf_prefix(wf_source_run, wf_source_descriptor)
        
        # validate selected wf basis (M) against basis parameters
        M = task["truncation_parameters"]["M"]
        wf_M = res_data.params["M"]
        if wf_M != M:
            raise mcscript.exception.ScriptError("Mismatched M for source wave function ({}) and present decomposition run ({})".format(wf_M, M))
        
        # locate model wf info
        model_info = task["truncation_model_info"]
        model_run = model_info["run"]
        model_descriptor = model_info["descriptor"](task | model_info)
        model_prefix = library.get_wf_prefix(model_run, model_descriptor)

        # validate selected truncation model basis (M and Nmax) against basis parameters
        M = task["truncation_parameters"]["M"]
        model_M = model_info["truncation_parameters"]["M"]
        if model_M != M:
            raise mcscript.exception.ScriptError("Mismatched M for wave function truncation model ({}) and present decomposition run ({})".format(model_M, M))
        Nmax = task["truncation_parameters"].get("Nmax")
        model_Nmax = model_info["truncation_parameters"]["Nmax"]
        if model_Nmax != Nmax:
            raise mcscript.exception.ScriptError("Mismatched Nmax for wave function truncation model ({}) and present decomposition run ({})".format(model_Nmax, Nmax))

        # truncate
        target_prefix = os.path.join(work_dir, "smwf")
        mcscript.utils.mkdir(target_prefix, parents=True, exist_ok=True)
        model_indexing_files = (
            [os.path.join(model_prefix, "mfdn_smwf.info")]
            + glob.glob(os.path.join(model_prefix, "mfdn_MBgroups*"))
        )
        mcscript.call(
            [
                "cp",
                "--target-directory={}".format(target_prefix),
            ] + model_indexing_files
        )
        
        mcscript.control.call(
            [
                environ.shell_filename("smwf-truncate"),
                wf_prefix,  # input wf directory
                model_prefix,  # truncation model wf directory
                target_prefix,  # target wf directory
                "{:d}".format(level_seq),  # state sequence number
                "multi-diag-test",  # TEMPORARY mode flag for slv
            ],
            mode=mcscript.control.CallMode.kSerial,
        )
    
    task_handler_mfdn_pre(task, postfix)

    
def task_handler_mfdn_decomposition_run(task, postfix=""):
    """Task handler for MFDn Lanczos decomposition, assuming oscillator basis.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    work_dir = "work{:s}".format(postfix)
    
    # set some defaults
    task.setdefault("diagonalization", True)  # to disable unnecessary obdme calculation
    task.setdefault("calculate_obdme", False)  # to disable unnecessary obdme calculation
    # 08/08/25 (mac): Setting calculate_tbo to false leads to intermittent and
    # nondeterministic memory deallocation errors with mfdn commit 3f34aa7,
    # dependent upon OpenMP parameters.
    # 10/22/25 (mac): Though these seem to very occasionally happen ("free(): invalid size"),
    # testing under Ubuntu, even otherwise.
    ## task.setdefault("calculate_tbo", False)  # to disable unnecessary Ncm and rrel2 operators 
    task.setdefault("tolerance", 0)  # iterate to max iterations

    # handle case where wf was truncated
    if "truncation_model_info" not in task:

        # locate wave function
        wf_source_run, wf_source_descriptor, res_data, level_seq = get_wf_source_info(task)
        wf_prefix = library.get_wf_prefix(wf_source_run, wf_source_descriptor)

        # validate selected wf basis (M and Nmax) against basis parameters
        M = task["truncation_parameters"]["M"]
        wf_M = res_data.params["M"]
        if wf_M != M:
            raise mcscript.exception.ScriptError("Mismatched M for source wave function ({}) and present decomposition run ({})".format(wf_M, M))
        Nmax = task["truncation_parameters"].get("Nmax")
        wf_Nmax = res_data.params.get("Nmax")
        if wf_Nmax != Nmax:
            raise mcscript.exception.ScriptError("Mismatched Nmax for source wave function ({}) and present decomposition run ({})".format(wf_Nmax, Nmax))
        
    else:
        # reset wf info for mfdn to point to truncated wf
        wf_prefix = os.path.join(work_dir, "smwf")
        level_seq = 1

    # extract partitioning info
    if task.get("partition_filename"):
        print("WARN: A partition_filename was specified but is being ignored.")
    extract_partitioning_from_smwf_info_file(wf_prefix)
            
    # set MFDn parameters
    task["mfdn_inputlist"] = {
        "selectpiv" : 4,
        "initvec_index": level_seq,
        "initvec_smwffilename": os.path.join("..", wf_prefix, "mfdn_smwf"),
    }
    task["partition_filename"] = "mfdn_partitioning.info"
    
    # run MFDn
    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver
    mfdn_driver.generate_mfdn_input(
        task=task, run_mode=modes.MFDnRunMode.kLanczosOnly, postfix=postfix
    )
    mfdn_driver.run_mfdn(task=task, postfix=postfix)

    # copy out lanczos file
    descriptor = task["metadata"]["descriptor"]
    filename_prefix = "{:s}-mfdn15-{:s}{:s}".format(mcscript.parameters.run.name, descriptor, postfix)
    lanczos_source_filename = os.path.join(work_dir, "mfdn_alphabeta.dat")
    lanczos_target_filename = "{:s}.lanczos".format(filename_prefix)
    mcscript.task.save_results_single(
        task, lanczos_source_filename, lanczos_target_filename, "lanczos"
    )

   
def task_handler_mfdn_decomposition_post(task, postfix="", cleanup=True):
    """Task handler for serial components after MFDn Lanczos decomposition run."""

    if(cleanup):
        mcscript.control.call(
                [
                    "rm", "-rf", "work/smwf",
                ],
                mode=mcscript.control.CallMode.kSerial
            )

    task_handler_mfdn_post(task, postfix, cleanup)

def task_handler_mfdn_decomposition(task, postfix=""):
    """Task handler for complete decomposition run, including serial pre and post
    steps.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    task_handler_mfdn_decomposition_pre(task, postfix=postfix)
    task_handler_mfdn_decomposition_run(task, postfix=postfix)
    task_handler_mfdn_decomposition_post(task, postfix=postfix)

    
task_handler_mfdn_decomposition_phases = [
    task_handler_mfdn_decomposition_pre,
    task_handler_mfdn_decomposition_run,
    task_handler_mfdn_decomposition_post,
]


################################################################
# basic natural orbital run
################################################################

def task_handler_mfdn_natorb_pre(task, source_postfix="", target_postfix=""):
    """Task handler for serial components before MFDn natural orbitals run.

    Precondition: This handler assumes a base run has already been
    carried out on the same task.

    Arguments:
        task (dict): as described in module docstring
    """
    # sanity checks
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals not enabled")
    utils.check_natorb_base_state(task)

    # set correct basis mode
    task["basis_mode"] = modes.BasisMode.kGeneric
    radial.set_up_natural_orbitals(
        task=task, source_postfix=source_postfix, target_postfix=target_postfix
        )
    radial.set_up_radial_natorb(
        task=task, source_postfix=source_postfix, target_postfix=target_postfix
        )
    tbme.generate_tbme(
        task=task, postfix=target_postfix
        )


def task_handler_mfdn_natorb_run(task, postfix):
    """Task handler for MFDn natural orbital run.

    Precondition: This handler assumes task_handler_natorb_pre() has been called.

    Arguments:
        task (dict): as described in module docstring
        postfix (string): identifier to add to generated files
    """
    # sanity checks
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals not enabled")
    utils.check_natorb_base_state(task)

    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver

    # set correct basis mode
    task["basis_mode"] = modes.BasisMode.kGeneric
    mfdn_driver.generate_mfdn_input(task=task, postfix=postfix)
    mfdn_driver.run_mfdn(task=task, postfix=postfix)

    
task_handler_mfdn_natorb_post = task_handler_mfdn_post


def task_handler_mfdn_natorb(task, cleanup=True):
    """Task handler for basic oscillator+natural orbital run.

    Arguments:
        task (dict): as described in module docstring
    """
    # sanity checks
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals not enabled")
    utils.check_natorb_base_state(task)

    # first do base oscillator run
    task_handler_mfdn(task, postfix=utils.natural_orbital_indicator(0))

    task_handler_mfdn_natorb_pre(
        task,
        source_postfix=utils.natural_orbital_indicator(0),
        target_postfix=utils.natural_orbital_indicator(1)
        )
    task_handler_mfdn_natorb_run(task=task, postfix=utils.natural_orbital_indicator(1))
    task_handler_mfdn_post(
        task=task, postfix=utils.natural_orbital_indicator(1), cleanup=cleanup
        )

    
task_handler_mfdn_natorb_phases = [
    task_handler_mfdn_natorb_pre,
    task_handler_mfdn_natorb_run,
    task_handler_mfdn_natorb_post,
]


################################################################
# TBME generation run
################################################################

def task_handler_tbme(task, postfix=""):
    """Task handler for generation of operator tbmes.

    Special keys:
      "number_operator_orbitals"  
      "tbme_conversion"

    Arguments:
        task (dict): as described in module docstring
        postfix (string): identifier to add to generated files
    """

    # set task dictionary defaults for oscillator-basis tbme generation
    task.setdefault("basis_mode", modes.BasisMode.kDirect)
    task.setdefault("sp_truncation_mode", modes.SingleParticleTruncationMode.kNmax)

    # set minimal orbital set for given truncation
    target_truncation = task["target_truncation"]
    code, cutoff = target_truncation
    if code not in ["ob", "tb"]:
        raise ValueError("Unexpected truncation code ({})".format(code))
    task.setdefault("truncation_parameters", dict(Nmax_orb=cutoff))

    # define orbitals
    radial.set_up_orbitals(task, postfix)

    # define orbital number operators
    #
    # NOTE (mac): Number operator generation may someday be absorbed into obmixer or h2mixer.
    task.setdefault("number_operator_orbitals", {})
    Nmax_orb = task["truncation_parameters"]["Nmax_orb"]
    task.setdefault("obme_sources", [])
    task.setdefault("tb_observables", [])
    orbital_filename = "orbitals.dat"
    for particle_species in ["p", "n"]:
        for n, l, j in task["number_operator_orbitals"]:
            number_operator_name = "N{:1d}{:1d}{:1d}{:1s}".format(n, l, int(2*j), particle_species)
            number_operator_filename = "{}_obme.dat".format(number_operator_name)
            mcscript.control.call(
                [
                    environ.shell_filename("number-op-gen"), orbital_filename,
                    str(n), str(l), str(int(2*j)), particle_species, str(Nmax_orb),
                    number_operator_filename,
                ],
                mode=mcscript.control.CallMode.kSerial
            )
            task["obme_sources"].append(
                (number_operator_name, {"filename": number_operator_filename, "qn": (0,0,0)}),
            )
            task["tb_observables"].append(
                (number_operator_name, (0,0,0), {"U[{}]".format(number_operator_name): 1.0}),
            )

    # generate tbmes
    radial.set_up_obme_analytic(task, postfix)
    tbme.generate_tbme(task, postfix)
            
    # convert tbme files
    tbme_conversion = task.get("tbme_conversion")
    if tbme_conversion:
        target_format = tbme_conversion["target_format"]
        keep_h2 = tbme_conversion.get("keep_h2")
        if target_format != "me2j":
            raise(ValueError("Unrecognized tbme target format ({})".format(target_format)))
        me2j_extension = tbme_conversion["me2j_extension"]
        me2j_precision = tbme_conversion.get("me2j_precision", "double")
        me2j_tag = "me2j-{}".format(me2j_precision) if me2j_extension=="bin" else "me2j"
        work_dir = "work{:s}".format(postfix)
        h2_filename_list = glob.glob(os.path.join(work_dir, "tbme-*"))
        for h2_filename in h2_filename_list:
            me2j_filename = "{}_{}.{}".format(h2_filename[:-4], me2j_tag, me2j_extension)
            mcscript.control.call(
                [
                    environ.shell_filename("h22me2j"), "--precision", me2j_precision, h2_filename, me2j_filename,
                ],
                mode=mcscript.control.CallMode.kSerial
            )
        if not keep_h2:
            mcscript.control.call(
                [
                    "rm", h2_filename,
                ],
                mode=mcscript.control.CallMode.kSerial
            )

    # save tbme files
    tbme.save_tbme(task, postfix=postfix)


################################################################
# postprocessing run
################################################################

def task_handler_mfdn_postprocessor_pre(task, postfix=""):
    """Task handler for components before postprocessor run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string): identifier to add to generated files
    """
    postprocessing.init_postprocessor_db(task, postfix)
    radial.set_up_orbitals(task, postfix)
    radial.set_up_obme_analytic(task, postfix)
    tbme.generate_tbme(task, postfix)

    
def task_handler_mfdn_postprocessor_run(task, postfix=""):
    """Task handler for MFDn postprocessor phase of postprocessor run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string): identifier to add to generated files
    """
    postprocessing.run_postprocessor_two_body(task, postfix=postfix, one_body=True)
    postprocessing.run_postprocessor_one_body(task, postfix=postfix)

    
def task_handler_mfdn_postprocessor_post(task, postfix="", cleanup=True):
    """Task handler for components after postprocessor run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string): identifier to add to generated files
    """
    postprocessing.evaluate_ob_observables(task, postfix)
    if task.get("convert_obdme"):
        postprocessing.convert_ob_densities(task, postfix)

    postprocessing.save_postprocessor_obdme(task, postfix)

    if cleanup:
        postprocessing.cleanup_workdir(task, postfix=postfix)

        
def task_handler_mfdn_postprocessor_post_no_cleanup(task, postfix=""):
    """ Task handler for serial components after postprocessor run (no cleanup).

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    task_handler_mfdn_postprocessor_post(task, postfix=postfix, cleanup=False)


def task_handler_mfdn_postprocessor(task, postfix="", cleanup=True):
    """Task handler for basic postprocessor run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string): identifier to add to generated files
    """
    if not task["metadata"].get("resumed"):
        task_handler_mfdn_postprocessor_pre(task)
    task_handler_mfdn_postprocessor_run(task, postfix)
    task_handler_mfdn_postprocessor_post(task, postfix, cleanup)

    
task_handler_mfdn_postprocessor_phases = [
    task_handler_mfdn_postprocessor_pre,
    task_handler_mfdn_postprocessor_run,
    task_handler_mfdn_postprocessor_post,
]


################################################################
# relative matrix element generation and Moshinsky transform
################################################################

def task_handler_relative_run(task):
    """Task handler for relative matrix element manipulation."""
    relative.generate_rel_targets(task)
    relative.generate_moshinsky_targets(task)

    
def task_handler_relative_post(task):
    """Task handler for components after relative run."""
    relative.save_rel(task)
    relative.save_moshinsky(task)

    
def task_handler_relative(task):
    """Task handler for basic relative/Moshinsky run."""
    task_handler_relative_run(task)
    task_handler_relative_post(task)

    
task_handler_relative_phases = [
    task_handler_relative_run,
    task_handler_relative_post,
]


################################################################
# mfdn archiving
################################################################

def archive_handler_mfdn():
    """Generate archives for MFDn results and MFDn wavefunctions."""

    archive_filename_list = mcscript.task.archive_handler_subarchives(
        [
            {"postfix" : "-out", "paths" : ["results/out"], "compress" : True, "include_metadata" : True},
            {"postfix" : "-res", "paths" : ["results/res"], "compress" : True},
            {"postfix" : "-lanczos", "paths" : ["results/lanczos"], "compress" : True},
            {"postfix" : "-task-data", "paths" : ["results/task-data"], "compress" : True},
            {"postfix" : "-obdme", "paths" : ["results/obdme"], "compress" : True},
            {"postfix" : "-dens", "paths" : ["results/obdme"], "compress" : True},  # retabulated densities
            {"postfix" : "-tbme", "paths" : ["results/tbme"], "compress" : False},
            {"postfix" : "-wf", "paths" : ["results/wf"]},
        ]
    )
    return archive_filename_list


def archive_handler_mfdn_lightweight():
    """Generate archives for MFDn results (but not task data or wavefunctions).

    This is useful as a follow-up archive after running the postprocessor.
    """

    archive_filename_list = mcscript.task.archive_handler_subarchives(
        [
            {"postfix" : "-out", "paths" : ["results/out"], "compress" : True, "include_metadata" : True},
            {"postfix" : "-res", "paths" : ["results/res"], "compress" : True},
            {"postfix" : "-lanczos", "paths" : ["results/lanczos"], "compress" : True},
        ]
    )
    return archive_filename_list


def archive_handler_mfdn_hsi(split_large_archives=False):
    """Generate archives for MFDn and save to tape.

    Arguments:

        split_large_archives (bool, optional): whether or not to split large
        archives into segments (pass-through option to
        mcscript.task.archive_handler_hsi()

    """

    # generate archives
    archive_filename_list = archive_handler_mfdn()

    # save to tape
    mcscript.task.archive_handler_hsi(archive_filename_list, split_large_archives=split_large_archives)

    
def archive_handler_mfdn_postprocessor():
    """Generate archives for MFDn postprocessor results."""

    archive_filename_list = mcscript.task.archive_handler_subarchives(
        [
            {"postfix" : "-transitions-output", "paths" : ["results/transitions-output"], "compress" : True, "include_metadata" : True},
            {"postfix" : "-res", "paths" : ["results/res"], "compress" : True},
            {"postfix" : "-obdme", "paths" : ["results/obdme"], "compress" : True},
            {"postfix" : "-dens", "paths" : ["results/dens"], "compress" : True},
        ]
    )
    print(archive_filename_list)
    return archive_filename_list


def archive_handler_mfdn_postprocessor_hsi():
    """Generate archives for MFDn postprocessor and save to tape."""

    # generate archives
    archive_filename_list = archive_handler_mfdn_postprocessor()
    print(archive_filename_list)

    # save to tape
    mcscript.task.archive_handler_hsi(archive_filename_list)

################################################################
# strength function run
################################################################

def task_handler_mfdn_strength_pre(task, postfix=""):
    """Task handler for serial components before MFDn phase of Lanczos trick
    strength function calculation, assuming oscillator basis.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files

    """

    work_dir = "work{:s}".format(postfix)

    # set some defaults
    task.setdefault("diagonalization", True)  # to disable unnecessary obdme calculation
    task.setdefault("calculate_obdme", False)  # to disable unnecessary obdme calculation
    # 08/08/25 (mac): Setting calculate_tbo to false leads to intermittent and
    # nondeterministic memory deallocation errors with mfdn commit 3f34aa7,
    # dependent upon OpenMP parameters.
    ## task.setdefault("calculate_tbo", False)  # to disable unnecessary Ncm and rrel2 operators
    task.setdefault("tolerance", 0)  # iterate to max iterations

    task_handler_mfdn_pre(task, postfix)

    print("DONE WITH TASKPRE, NOW TBME")

    tbme.generate_tbme(task, postfix=postfix)

def task_handler_mfdn_strength_apply(task, postfix=""):
    """Task handler for apply operator phase of Lanczos trick strength function
    calculation, assuming oscillator basis.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files

    """
    # set some defaults
    task.setdefault("diagonalization", True)  # to disable unnecessary obdme calculation
    task.setdefault("calculate_obdme", False)  # to disable unnecessary obdme calculation
    # 08/08/25 (mac): Setting calculate_tbo to false leads to intermittent and
    # nondeterministic memory deallocation errors with mfdn commit 3f34aa7,
    # dependent upon OpenMP parameters.
    ## task.setdefault("calculate_tbo", False)  # to disable unnecessary Ncm and rrel2 operators
    task.setdefault("tolerance", 0)  # iterate to max iterations
        # convenience variables
    descriptor = task["metadata"]["descriptor"]
    work_dir = "work{:s}".format(postfix)
    transitions_executable = environ.mfdn_postprocessor_filename(
        task.get("mfdn-transitions_executable", "xapply")
    )


    # create work directory if it doesn't exist yet
    mcscript.utils.mkdir(work_dir, exist_ok=True, parents=True)

   # get template model run

    print("Reading template mesh data:")
    wf_template_run_list = task["wf_template_run_list"]
    wf_template_selector = task["wf_template_selector"]

    #Get Operator qn
    tb_observables = operators.tb.get_tbme_targets(task)

    for qn, operator_list in tb_observables.items():
        for operator in operator_list:
            print(operator, qn)
            if operator == task["transition_operator"]:
                operator_qn = qn

    #Get template qn from operator qn, assuming 0+ g.s.
    template_qn = (operator_qn[0], operator_qn[1], 1)

    #Construct 'source' dictionary
    template_dict = {
                     "wf_source_run_list": wf_template_run_list,
                     "wf_source_selector": wf_template_selector,
                     "wf_qn": template_qn,
            }


    wf_template_run, wf_template_descriptor, res_data, level_seq  = get_wf_source_info(template_dict)

   #copy template directory

    template_prefix = library.get_wf_prefix(wf_template_run, wf_template_descriptor)

    print(template_prefix)

    pivot_prefix = "pivot"
    mcscript.utils.mkdir(pivot_prefix, exist_ok=True)
    template_indexing_files = (
        [os.path.join(template_prefix, "mfdn_smwf.info")]
        + glob.glob(os.path.join(template_prefix, "mfdn_MBgroups*"))
    )
    mcscript.control.call(
        [
            "cp",
            "--target-directory={}".format(pivot_prefix),
        ] + template_indexing_files,
    )

   # get source wf

    wf_source_run, wf_source_descriptor, res_data, level_seq = get_wf_source_info(task)

    source_prefix = library.get_wf_prefix(wf_source_run, wf_source_descriptor)

    source_qn = task["wf_qn"]
    
    operator_file_loc = os.path.join(work_dir, "tbme-"+task["transition_operator"])

    #construct apply input file
    apply_inputlist = {
            "infofilename_ket": "{:s}/mfdn_smwf.info".format(source_prefix),
            "basisfilename_ket": "{:s}/mfdn_MBgroups".format(source_prefix),
            "smwffilename_ket": "{:s}/mfdn_smwf".format(source_prefix),
            "TwoJ_ket(1)": int(source_qn[0]),
            "n_ket(1)": int(source_qn[2]),

            "infofilename_bra": "{:s}/mfdn_smwf.info".format(pivot_prefix),
            "basisfilename_bra": "{:s}/mfdn_MBgroups".format(pivot_prefix),
            "smwffilename_bra": "{:s}/mfdn_smwf".format(pivot_prefix),
            "TwoJ_out(1)": 2*int(template_qn[0]),
            "n_out(1)": int(template_qn[2]),

            "TBMEoperators(1)": operator_file_loc,
            "normalize": False,
    }
    mcscript.utils.write_namelist(
        "apply.input",
        input_dict={"transition_data": apply_inputlist}
    )
    #Run xapply
    mcscript.control.call(["rm", "--force", "apply.out"])  # remove old output so file watchdog can work
    mcscript.control.call(
        [transitions_executable],
        mode=mcscript.control.CallMode.kHybrid,
        file_watchdog=mcscript.control.FileWatchdog("apply.out"),
        file_watchdog_restarts=3
    )

    # copy out norm
    norm_file = open("apply.out")
    norm_file_lines = [row for row in norm_file]
    norm_file.close()
    tokenized_lines = list(mfdnres.tools.split_and_prune_lines(norm_file_lines))

    for row in tokenized_lines:
        if len(row) < 6:
            continue
        if row[2] == "norm":
            print("NORM SQUARED: ", row[5])
            norm_sq = float(row[5])
    
    lines = []
    lines += ["[Two-body observable]"]
    lines += ["# {:>3s} {:>3s} {:>3s}  {:s}".format("J0", "g0", "Tz0", "name")]
    lines += ["  {:>3d} {:>3d} {:>3d}  {:s}".format(
        operator_qn[0], operator_qn[1], operator_qn[2], task["transition_operator"]
            )
        ]
    lines += ["# {:>4s} {:>3s} {:>3s}  {:>15s}".format( "Ji", "gi", "ni", "rme")]
    lines += ["  {:>4.1f} {:>3d} {:>3d}  {:15.8e}".format(
        source_qn[0], source_qn[1], source_qn[2], norm_sq
            )
        ]

    filename_prefix = "{:s}-transitions-tb-{:s}{:s}".format(mcscript.parameters.run.name, descriptor, postfix)
    res_filename = "{:s}.res".format(filename_prefix)

    mcscript.utils.write_input(res_filename, lines, verbose=False)

    mcscript.task.save_results_single(
        task, res_filename, res_filename, "res"
    )
def task_handler_mfdn_strength_decomp(task, postfix= ""):
    """Task handler for decomposition phase of Lanczos trick strength function
    calculation, assuming oscillator basis.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files

    """

    work_dir = "work{:s}".format(postfix)
    wf_prefix = "pivot"
    level_seq = 1

    task["mfdn_inputlist"] = {
        "selectpiv" : 4,
        "initvec_index": level_seq,
        "initvec_smwffilename": os.path.join("..", wf_prefix, "mfdn_smwf"),
    }

    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver
    mfdn_driver.generate_mfdn_input(
        task=task, run_mode=modes.MFDnRunMode.kNormal, postfix=postfix
    )
    mfdn_driver.run_mfdn(task=task, postfix=postfix)

    # copy out lanczos file
    descriptor = task["metadata"]["descriptor"]
    filename_prefix = "{:s}-mfdn15-{:s}{:s}".format(mcscript.parameters.run.name, descriptor, postfix)
    lanczos_source_filename = os.path.join(work_dir, "mfdn_alphabeta.dat")
    lanczos_target_filename = "{:s}.lanczos".format(filename_prefix)
    mcscript.task.save_results_single(
        task, lanczos_source_filename, lanczos_target_filename, "lanczos"
    )

task_handler_mfdn_strength_post = task_handler_mfdn_post

task_handler_mfdn_strength_phases=[
            task_handler_mfdn_strength_pre,
            task_handler_mfdn_strength_apply,
            task_handler_mfdn_strength_decomp,
            task_handler_mfdn_strength_post,
            ]


################################################################
# deprecated handler names
################################################################
from deprecated import deprecated

task_handler_dimension = deprecated(reason="use task_handler_mfdn_dimension")(task_handler_mfdn_dimension)
task_handler_nonzeros = deprecated(reason="use task_handler_mfdn_nonzeros")(task_handler_mfdn_nonzeros)
task_handler_post_run = deprecated(reason="use task_handler_mfdn_post")(task_handler_mfdn_post)
task_handler_post_run_no_cleanup = deprecated(reason="use task_handler_mfdn_post_no_cleanup")(task_handler_mfdn_post_no_cleanup)

task_handler_oscillator_pre = deprecated(reason="use task_handler_mfdn_pre")(task_handler_mfdn_pre)
task_handler_oscillator_mfdn = deprecated(reason="use task_handler_mfdn_run")(task_handler_mfdn_run)
task_handler_oscillator = deprecated(reason="use task_handler_mfdn")(task_handler_mfdn)
task_handler_oscillator_mfdn_decomposition = deprecated(reason="use task_handler_mfdn_decomposition_run")(task_handler_mfdn_decomposition_run)

task_handler_natorb_pre = deprecated(reason="use task_handler_mfdn_natorb_pre")(task_handler_mfdn_natorb_pre)
task_handler_natorb_run = deprecated(reason="use task_handler_mfdn_natorb_run")(task_handler_mfdn_natorb_run)
task_handler_natorb = deprecated(reason="use task_handler_mfdn_natorb")(task_handler_mfdn_natorb)

task_handler_postprocessor_pre = deprecated(reason="use task_handler_mfdn_postprocessor_pre")(task_handler_mfdn_postprocessor_pre)
task_handler_postprocessor_post = deprecated(reason="use task_handler_mfdn_postprocessor_post")(task_handler_mfdn_postprocessor_post)
task_handler_postprocessor = deprecated(reason="use task_handler_mfdn_postprocessor")(task_handler_mfdn_postprocessor)
