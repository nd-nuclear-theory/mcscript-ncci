"""mfdn_v15.py -- driver module for MFDn v15.

Patrick Fasano
University of Notre Dame

- 06/08/17 (pjf): Initial version of MFDn v15 scripting, built from mfdn_v14.py.
- 06/22/17 (pjf): Update references to mcscript.exception.ScriptError.
- 07/31/17 (pjf): Create work directory if nonexistent when running mfdn.
- 08/11/17 (pjf):
  + Use new TruncationModes.
  + Fix FCI truncation.
- 08/25/17 (pjf): Implement general truncation:
  + Always use orbital file, even for Nmax runs.
  + Break out different many-body truncations into their own functions.
- 08/26/17 (pjf): Add parity constraints for general truncations.
- 09/12/17 (pjf): Update for config -> modes + environ split.
- 09/22/17 (pjf): Take "observables" as list of tuples instead of dict.
- 09/24/17 (pjf):
  + Archive wavefunction files in separate archive.
  + Create tar files with minimal directory structure for easy inflation.
- 09/27/17 (pjf): Allow for counting modes with run_mode.
- 10/05/17 (pjf): Add save_mfdn_output_out_only.
- 10/18/17 (pjf):
  + Use separate work directory for each postfix.
  + Factor out extract_natural_orbitals().
- 10/25/17 (pjf): Rename "observables" to "tb_observables".
- 02/11/18 (pjf): Correctly archive mfdn_partitioning.info.
- 07/23/18 (pjf): Archive partitioning with wave functions.
- 12/17/18 (pjf): Add "mfdn_inputlist" as pass-through override.
- 03/18/19 (pjf): Add "calculate_obdme" as flag to enable/disable OBDME calculation.
- 04/24/19 (pjf): Add extract_mfdn_output() to resume from archives.
- 04/30/19 (mac): Modify save_mfdn_output to store task data archive in separate
    directory and omit renamed .{res,out} files.
- 05/30/19 (mac): Update extract_mfdn_output() to retrieve from task_data_dir and add
    extract_wavefunctions().
- 05/30/19 (pjf):
    + Use new subarchive features in mcscript.
    + Move wave function saving into a separate function.
    + Always save mfdn.res and mfdn.out in results directory, at end of run.
    + Clean up observable output archiving.
- 06/07/19 (pjf): Check that MFDn launches successfully with
    mcscript.control.FileWatchdog on mfdn.out.
- 06/11/19 (pjf): Save task-data archives to correct place (under results_dir).
- 09/04/19 (pjf): Rename Trel->Tintr.
- 10/10/19 (pjf): Implement generation of mfdn_smwf.info from old runs.
- 10/13/19 (pjf): Fix inclusion of partitioning into mfdn_smwf.info.
- 12/11/19 (pjf): Use new results storage helper functions from mcscript.
- 06/03/20 (pjf):
    + Switch to using quantum numbers to specify natorb base state.
    + Fix saving of OBDMEs.
- 09/09/20 (pjf): Use operators module instead of tbme for operator names.
- 09/16/20 (pjf):
    + Check that diagonalization is enabled.
    + Add "tbme-" to operator id to form basename.
- 11/24/20 (pjf): Fix natorb filename globbing for non-integer J.
- 11/30/20 (pjf): Add "calculate_tbo" task option.
- 12/04/20 (pjf): Remove leftover mfdn.res and mfdn.out files before launching
    MFDn.
- 05/09/22 (pjf): Split generate_mfdn_input() from run_mfdn().
- 07/12/22 (pjf): Add sanity check on dimension and numnonzero.
- 06/05/23 (mac):
  + Make "eigenvectors" optional, e.g., for decomposition run.
  + Fix save_mfdn_task_data() to gracefully handle missing overlap files for decomposition run.
- 8/23/23 (slv): 
    + Created generate_menj_par()
    + Added a call to generate_menj_par() from generate_mfdn_input()
    + Added a menj.par file existence check in run_mfdn() 
- 8/28/23 (slv): 
    + used .format for strings inputs in generate_menj_par() 
    + lamHcm computed as a_cm/hw instead of getting it as an input in the task dictionary

"""
import errno
import os
import glob
import collections
import re
import warnings

import mcscript
import mcscript.exception

from . import modes, environ, operators


def set_up_Nmax_truncation(task, inputlist):
    """Generate Nmax truncation inputs for MFDn v15.

    Arguments:
        task(dict): as described in docs/task.md
        inputlist (dict): MFDn v15 inputlist
    """
    # sanity check
    if task["sp_truncation_mode"] is not modes.SingleParticleTruncationMode.kNmax:
        raise ValueError("expecting sp_truncation_mode to be {} but found {sp_truncation_mode}".format(modes.SingleParticleTruncationMode.kNmax, **task))
    if task["mb_truncation_mode"] is not modes.ManyBodyTruncationMode.kNmax:
        raise ValueError("expecting mb_truncation_mode to be {} but found {mb_truncation_mode}".format(modes.ManyBodyTruncationMode.kNmax, **task))

    truncation_parameters = task["truncation_parameters"]

    # many-body truncation: Nmin, Nmax, deltaN
    if (truncation_parameters["Nstep"] == 2):
        inputlist["Nmin"] = truncation_parameters["Nmax"] % 2
    else:
        inputlist["Nmin"] = 1
    inputlist["Nmax"] = int(truncation_parameters["Nmax"])
    inputlist["deltaN"] = int(truncation_parameters["Nstep"])
    inputlist["TwoMj"] = round(2*truncation_parameters["M"])


def set_up_WeightMax_truncation(task, inputlist):
    """Generate weight max truncation inputs for MFDn v15.

    Arguments:
        task(dict): as described in docs/task.md
        inputlist (dict): MFDn v15 inputlist
    """
    # sanity check
    if task["mb_truncation_mode"] is not modes.ManyBodyTruncationMode.kWeightMax:
        raise ValueError("expecting sp_truncation_mode to be {} but found {sp_truncation_mode}".format(modes.ManyBodyTruncationMode.kWeightMax, **task))

    truncation_parameters = task["truncation_parameters"]

    inputlist["WTmax"] = truncation_parameters["mb_weight_max"]
    inputlist["parity"] = truncation_parameters["parity"]
    inputlist["TwoMj"] = round(2*truncation_parameters["M"])


def set_up_FCI_truncation(task, inputlist):
    """Generate FCI truncation inputs for MFDn v15.

    Arguments:
        task(dict): as described in docs/task.md
        inputlist (dict): MFDn v15 inputlist
    """
    # sanity check
    if task["mb_truncation_mode"] is not modes.ManyBodyTruncationMode.kFCI:
        raise ValueError("expecting sp_truncation_mode to be {} but found {sp_truncation_mode}".format(modes.ManyBodyTruncationMode.kFCI, **task))

    truncation_parameters = task["truncation_parameters"]

    # maximum weight of an orbital is either Nmax or sp_weight_max
    if task["sp_truncation_mode"] is modes.SingleParticleTruncationMode.kNmax:
        max_sp_weight = truncation_parameters["Nmax"]
    else:
        max_sp_weight = truncation_parameters["sp_weight_max"]

    inputlist["WTmax"] = sum(task["nuclide"])*max_sp_weight
    inputlist["parity"] = int(truncation_parameters["parity"])
    inputlist["TwoMj"] = round(2*truncation_parameters["M"])


truncation_setup_functions = {
    modes.ManyBodyTruncationMode.kNmax: set_up_Nmax_truncation,
    modes.ManyBodyTruncationMode.kWeightMax: set_up_WeightMax_truncation,
    modes.ManyBodyTruncationMode.kFCI: set_up_FCI_truncation
}


def generate_mfdn_input(task, run_mode=modes.MFDnRunMode.kNormal, postfix=""):
    """Generate input file and menj.par (if needed) for MFDn version 15 

    Arguments:
        task (dict): as described in docs/task.md
        run_mode (modes.MFDnRunMode): run mode for MFDn
        postfix (string, optional): identifier to add to generated files

    Raises:
        mcscript.exception.ScriptError: if MFDn output not found
    """
    # check that diagonalization is enabled
    if (run_mode in (modes.MFDnRunMode.kNormal, modes.MFDnRunMode.kLanczosOnly)) and not task.get("diagonalization"):
        raise mcscript.exception.ScriptError(
            'Task dictionary "diagonalization" flag not enabled.'
        )

    # create work directory if it doesn't exist yet
    work_dir = "work{:s}".format(postfix)
    mcscript.utils.mkdir(work_dir, exist_ok=True, parents=True)

    # inputlist namelist dictionary
    inputlist = collections.OrderedDict()
    # tbo: two-body observable namelist
    obslist = collections.OrderedDict()

    # run mode
    if (run_mode==modes.MFDnRunMode.kLanczosOnly):
        # stopgap until MFDn mode implemented to stop after Lanczos
        print("stopgap until MFDn mode implemented to stop after Lanczos")
        inputlist["IFLAG_mode"] = int(modes.MFDnRunMode.kNormal)
    else:
        inputlist["IFLAG_mode"] = int(run_mode)

    # nucleus
    inputlist["Nprotons"], inputlist["Nneutrons"] = task["nuclide"]

    # single-particle orbitals
    inputlist["orbitalfile"] = environ.orbitals_filename(postfix)
    mcscript.call([
        "cp", "--verbose",
        environ.orbitals_filename(postfix),
        os.path.join(work_dir, environ.orbitals_filename(postfix))
    ])

    # truncation mode
    truncation_setup_functions[task["mb_truncation_mode"]](task, inputlist)

    if run_mode in [modes.MFDnRunMode.kNormal,modes.MFDnRunMode.kLanczosOnly]:
        if (task["basis_mode"] in {modes.BasisMode.kDirect, modes.BasisMode.kDilated}):
            inputlist["hbomeg"] = float(task["hw"])

        # diagonalization parameters
        inputlist["neivals"] = int(task.get("eigenvectors",4))
        inputlist["maxits"] = int(task["max_iterations"])
        inputlist["tol"] = float(task["tolerance"])
        if task.get("reduce_solver_threads"):
            inputlist["reduce_solver_threads"] = task["reduce_solver_threads"]

        # Hamiltonian input
        inputlist["TBMEfile"] = "tbme-H"

        # tbo: collect tbo names
        obs_basename_list = [
            "tbme-{}".format(id_)
            for id_ in operators.tb.get_tbme_targets(task)[(0,0,0)].keys()
        ]

        # do not evaluate Hamiltonian as observable
        #  NOTE (pjf): due to possible bug/precision issues in MFDn, evaluate H
        #    as a consistency check
        ##obs_basename_list.remove("tbme-H")

        # tbo: log tbo names in separate file to aid future data analysis
        mcscript.utils.write_input("tbo_names{:s}.dat".format(postfix), input_lines=obs_basename_list)

        # tbo: count number of observables
        num_obs = len(obs_basename_list)
        if num_obs > 32:
            raise mcscript.exception.ScriptError("Too many observables for MFDn v15")

        if task.get("calculate_tbo", True):
            inputlist["numTBops"] = num_obs
            obslist["TBMEoperators"] = obs_basename_list

        # obdme: parameters
        inputlist["obdme"] = task.get("calculate_obdme", True)
        if task.get("obdme_multipolarity") is not None:
            obslist["max2K"] = round(2*task["obdme_multipolarity"])

        # construct transition observable input if reference states given
        if task.get("obdme_reference_state_list") is not None:
            # obdme: validate reference state list
            #
            # guard against pathetically common mistakes
            for (J, g_rel, i) in task["obdme_reference_state_list"]:
                # validate integer/half-integer character of angular momentum
                twice_J = round(2*J)
                if ((twice_J % 2) != (sum(task["nuclide"]) % 2)):
                    raise ValueError("invalid angular momentum for reference state")
                # validate grade (here taken relative to natural grade)
                # if ((g_rel != (truncation_parameters["Nmax"] % 2)) and (truncation_parameters["Nstep"] != 1)):
                #     raise ValueError("invalid parity for reference state")

            # obdme: construct input
            inputlist["nrefstates"] = len(task["obdme_reference_state_list"])
            obslist["ref2J"] = []
            obslist["refseq"] = []
            for (J, g_rel, i) in task["obdme_reference_state_list"]:
                obslist["ref2J"].append(round(2*J))
                obslist["refseq"].append(i)

    # manual override inputlist
    inputlist.update(task.get("mfdn_inputlist", {}))

    # generate MFDn input file
    mcscript.utils.write_namelist(
        os.path.join(work_dir, "mfdn.input"),
        input_dict={"inputlist": inputlist, "obslist": obslist}
    )

    # import partitioning file
    partition_filename = task.get("partition_filename")
    if partition_filename is not None:
        partition_filename = mcscript.utils.expand_path(partition_filename)
        if not os.path.exists(partition_filename):
            print("Partition filename: {}".format(partition_filename))
            raise mcscript.exception.ScriptError("partition file not found")
        mcscript.call([
            "cp", "--verbose",
            partition_filename,
            os.path.join(work_dir, "mfdn_partitioning.info")
            ])

    if task["menj_enabled"]:
        generate_menj_par(task, postfix)


def run_mfdn(task, postfix=""):
    """Execute MFDn version 15.

    Arguments:
        task (dict): as described in docs/task.md
        postfix (string, optional): identifier to add to generated files

    Raises:
        mcscript.exception.ScriptError: if MFDn output not found
    """
    # enter work directory
    work_dir = "work{:s}".format(postfix)
    os.chdir(work_dir)

    # check that mfdn.input exists
    if not os.path.isfile("mfdn.input"):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), "mfdn.input"
        )
    # check menj.par exists if a flag in task show that menj extension is enabled
    if task["menj_enabled"]:
        if not os.path.isfile("menj.par"):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), "menj.par"
            )

    # remove any stray files from a previous run
    if os.path.exists("mfdn.out"):
        mcscript.call(["rm", "-v", "mfdn.out"])
    if os.path.exists("mfdn.res"):
        mcscript.call(["rm", "-v", "mfdn.res"])

    # invoke MFDn
    mcscript.call(
        [
            environ.mfdn_filename(task["mfdn_executable"])
        ],
        mode=mcscript.CallMode.kHybrid,
        check_return=True,
        file_watchdog=mcscript.control.FileWatchdog("mfdn.out"),
        file_watchdog_restarts=3,
    )

    # test for basic indications of success
    if (not os.path.exists("mfdn.out")):
        raise mcscript.exception.ScriptError("mfdn.out not found")
    if (not os.path.exists("mfdn.res")):
        raise mcscript.exception.ScriptError("mfdn.res not found")

    # check for basic sanity of dimension and numnonzero
    with open("mfdn.res", "r") as res:
        neg_dim_regex = re.compile(r"dimension.*=.*(-[0-9]+)")
        neg_nnz_regex = re.compile(r"numnonzero.*=.*(-[0-9]+)")
        for line in res:
            if match := neg_dim_regex.match(line):
                raise mcscript.exception.ScriptError(
                    f"negative MFDn dimension: {match.group(1)}"
                )
            if match := neg_nnz_regex.match(line):
                raise mcscript.exception.ScriptError(
                    f"negative MFDn numnonzero: {match.group(1)}"
                )

    with open("mfdn.out", "r") as out:
        for line in out:
            if "ERROR: group size larger than int(2)" in line:
                raise mcscript.exception.ScriptError(
                    f"group size larger than int(2)"
                )
            if "Dimension of M-basis" in line:
                # group size errors should have already happened
                break

    # leave work directory
    os.chdir("..")

    # copy results out
    print("Saving basic output files...")
    descriptor = task["metadata"]["descriptor"]
    work_dir = "work{:s}".format(postfix)
    filename_prefix = "{:s}-mfdn15-{:s}{:s}".format(mcscript.parameters.run.name, descriptor, postfix)

    # ...copy res file
    res_filename = "{:s}.res".format(filename_prefix)
    mcscript.task.save_results_single(
        task, os.path.join(work_dir, "mfdn.res"), res_filename, "res"
    )

    # ...copy out file
    out_filename = "{:s}.out".format(filename_prefix)
    mcscript.task.save_results_single(
        task, os.path.join(work_dir, "mfdn.out"), out_filename, "out"
    )


def extract_natural_orbitals(task, postfix=""):
    """Extract OBDME files for subsequent natural orbital iterations.

    Arguments:
        task (dict): as described in docs/task.md
        postfix (string, optional): identifier to add to generated files
    """
    # save OBDME files for next natural orbital iteration
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals not enabled")

    work_dir = "work{:s}".format(postfix)
    obdme_info_filename = "mfdn.rppobdme.info"
    (J, g, n) = task["natorb_base_state"]
    obdme_filename = glob.glob(
        "{:s}/mfdn.statrobdme.seq*.2J{:02d}.n{:02d}.2T*".format(work_dir, round(2*J), n)
        )

    print("Saving OBDME files for natural orbital generation...")
    mcscript.call(
        [
            "cp", "--verbose",
            os.path.join(work_dir, obdme_info_filename),
            environ.natorb_info_filename(postfix)
        ]
    )
    mcscript.call(
        [
            "cp", "--verbose",
            obdme_filename[0],
            environ.natorb_obdme_filename(postfix)
        ]
    )

def save_mfdn_task_data(task, postfix=""):
    """Collect and save working information.

    Arguments:
        task (dict): as described in docs/task.md
        postfix (string, optional): identifier to add to generated files
    """
    # convenience definitions
    descriptor = task["metadata"]["descriptor"]
    work_dir = "work{:s}".format(postfix)
    target_directory_name = descriptor + postfix

    # save full archive of input, log, and output files
    print("Saving full output files...")
    # logging
    archive_file_list = [
        environ.h2mixer_filename(postfix),
        "tbo_names{:s}.dat".format(postfix)
        ]
    # orbital information
    archive_file_list += [
        environ.orbitals_int_filename(postfix),
        environ.orbitals_filename(postfix),
        ]
    # transformation information
    # Use glob to allow for missing files (e.g., in decomposition run).
    archive_file_list += glob.glob(environ.radial_xform_filename(postfix))
    archive_file_list += glob.glob(environ.radial_olap_int_filename(postfix))
    # Coulomb information:
    if task["use_coulomb"]:
        archive_file_list += glob.glob(environ.orbitals_coul_filename(postfix))
        archive_file_list += glob.glob(environ.radial_olap_coul_filename(postfix))
    # natural orbital information
    if task.get("natural_orbitals"):
        archive_file_list += [
            environ.natorb_info_filename(postfix),
            environ.natorb_obdme_filename(postfix),
        ]
        # glob for natural orbital xform
        archive_file_list += glob.glob(environ.natorb_xform_filename(postfix))
    # MFDn input
    archive_file_list += [os.path.join(work_dir, "mfdn.input")]
    if os.path.isfile(os.path.join(work_dir, "mfdn_sp_orbitals.info")):
        archive_file_list += [os.path.join(work_dir, "mfdn_sp_orbitals.info")]
    # partitioning file
    if os.path.isfile(os.path.join(work_dir, "mfdn_partitioning.generated")):
        archive_file_list += [os.path.join(work_dir, "mfdn_partitioning.generated")]
    if os.path.isfile(os.path.join(work_dir, "mfdn_partitioning.info")):
        archive_file_list += [os.path.join(work_dir, "mfdn_partitioning.info")]
    # observable generation
    if os.path.isfile(environ.emgen_filename(postfix)):
        archive_file_list += [environ.emgen_filename(postfix)]
    if os.path.isfile(environ.obscalc_ob_filename(postfix)):
        archive_file_list += [environ.obscalc_ob_filename(postfix)]

    mcscript.task.save_results_multi(
        task, archive_file_list, target_directory_name, "task-data", command="cp"
    )


def save_mfdn_obdme(task, postfix=""):
    """Save MFDn-generated OBDME files.

    Arguments:
        task (dict): as described in docs/task.md
        postfix (str, optional): identifier to add to generated files
    """
    # convenience definitions
    descriptor = task["metadata"]["descriptor"]
    target_directory_name = descriptor + postfix
    work_dir = "work{:s}".format(postfix)

    # do nothing is obdme saving is turned off
    if (not task.get("save_obdme")) or (not task.get("calculate_obdme",True)):
        print("Cowardly refusing to save obdme...")
        return

    # glob for list of obdme files
    archive_file_list = glob.glob(os.path.join(work_dir, "mfdn*obdme*"))

    mcscript.task.save_results_multi(
        task, archive_file_list, target_directory_name, "obdme"
    )


def save_mfdn_wavefunctions(task, postfix=""):
    """Collect and save MFDn wave functions.

    Arguments:
        task (dict): as described in docs/task.md
        postfix (string, optional): identifier to add to generated files
    """
    # convenience definitions
    descriptor = task["metadata"]["descriptor"]
    target_directory_name = descriptor + postfix
    work_dir = "work{:s}".format(postfix)

    archive_file_list = glob.glob(os.path.join(work_dir, "mfdn_smwf*"))
    archive_file_list += glob.glob(os.path.join(work_dir, "mfdn_MBgroups*"))
    archive_file_list += glob.glob(os.path.join(work_dir, "mfdn_partitioning.*"))

    mcscript.task.save_results_multi(
        task, archive_file_list, target_directory_name, "wf"
    )


def cleanup_mfdn_workdir(task, postfix=""):
    """Remove temporary MFDn work files.

    Arguments:
        task (dict): as described in docs/task.md
        postfix (string, optional): identifier to add to generated files
    """
    # cleanup of wave function files
    scratch_file_list = glob.glob("work{:s}/*".format(postfix))
    mcscript.call(["rm", "-vf"] + scratch_file_list)


def extract_mfdn_task_data(
        task,
        task_data_dir=None,
        run_name=None,
        descriptor=None,
        postfix=""
):
    """Extract task directory from task data archive.

    Arguments:
        task (dict): as described in docs/task.md
        task_data_dir (str, optional): location where results archives can be found;
            defaults to current run results directory
        run_name (str, optional): run name for archive; defaults to current run name
        descriptor (str, optional): descriptor for archive; defaults to current
            descriptor
        postfix (str, optional): postfix for archive; defaults to empty string
    """
    warnings.warn("Extraction of old-style task-data archives is deprecated.", FutureWarning)
    # get defaults
    if task_data_dir is None:
        task_data_dir = os.path.join(mcscript.task.results_dir, "task-data")
    if run_name is None:
        run_name = mcscript.parameters.run.name
    if descriptor is None:
        descriptor = task["metadata"]["descriptor"]

    # expand results directory path
    task_data_dir = mcscript.utils.expand_path(task_data_dir)

    # construct archive path
    filename_prefix = "{:s}-mfdn15-{:s}{:s}".format(run_name, descriptor, postfix)
    task_data_archive_filename = "{:s}.tgz".format(filename_prefix)
    archive_path = os.path.join(task_data_dir, task_data_archive_filename)

    # extract archive
    mcscript.call(
        [
            "tar", "zxvf", archive_path,
        ]
    )

    # archive subdirectory inside expanded path
    extracted_dir = os.path.join(run_name, descriptor+postfix)

    # move MFDn files back into work directory
    work_dir = "work{:s}".format(postfix)
    mcscript.utils.mkdir(work_dir, exist_ok=True)
    file_list = [
        extracted_dir+"/mfdn.input", extracted_dir+"/mfdn.out",
        extracted_dir+"/mfdn.res",
    ]
    if os.path.isfile(extracted_dir+"/mfdn_partitioning.generated"):
        file_list += [extracted_dir+"/mfdn_partitioning.generated"]
    if os.path.isfile(extracted_dir+"/mfdn_sp_orbitals.info"):
        file_list += [extracted_dir+"/mfdn_sp_orbitals.info"]
    # partitioning file
    if os.path.isfile(extracted_dir+"/mfdn_partitioning.info"):
        file_list += [extracted_dir+"/mfdn_partitioning.info"]
    # MFDN obdme
    if (glob.glob(extracted_dir+"/mfdn.*obdme*")):
        file_list += glob.glob(extracted_dir+"/mfdn.*obdme*")
    mcscript.call(["mv", "-t", work_dir+"/",] + file_list)

    # move remaining files into task directory
    file_list = glob.glob(extracted_dir+"/*")
    mcscript.call(["mv", "-t", "./",] + file_list)

    # remove temporary directories
    mcscript.call(["rm", "-vfd", extracted_dir, run_name])


def extract_wavefunctions(
        task,
        wavefunctions_dir=None,
        run_name=None,
        descriptor=None,
        postfix="",
        target_dir=None
):
    """Extract wave functions to task directory from output archive.

    Arguments:
        task (dict): as described in docs/task.md
        wavefunctions_dir (str, optional): location where results archives can be found;
            defaults to current run results directory
        run_name (str, optional): run name for archive; defaults to current run name
        descriptor (str, optional): descriptor for archive; defaults to current
            descriptor
        postfix (str, optional): postfix for archive; defaults to empty string
        target_dir (str, optional): path for target directory for
            wavefunction files; defaults to current task directory and, if unqualified, will be
            taken relative to such as current working directory

    """
    warnings.warn("Extraction of old-style wave function archives is deprecated.", FutureWarning)
    # get defaults
    if wavefunctions_dir is None:
        wavefunctions_dir = os.path.join(mcscript.task.results_dir, "wf")
    if run_name is None:
        run_name = mcscript.parameters.run.name
    if descriptor is None:
        descriptor = task["metadata"]["descriptor"]
    if target_dir is None:
        target_dir = "work{:s}".format(postfix)
        mcscript.utils.mkdir(target_dir, exist_ok=True)

    # expand results directory path
    wavefunctions_dir = mcscript.utils.expand_path(wavefunctions_dir)

    # construct archive path
    filename_prefix = "{:s}-mfdn15wf-{:s}{:s}".format(run_name, descriptor, postfix)
    wavefunctions_archive_filename = "{:s}.tar".format(filename_prefix)
    archive_path = os.path.join(wavefunctions_dir, wavefunctions_archive_filename)
    if not os.path.exists(archive_path):
        # fall back to old filename convention
        filename_prefix = "{:s}-mfdn15-{:s}{:s}".format(run_name, descriptor, postfix)
        wavefunctions_archive_filename = "{:s}-wf.tar".format(filename_prefix)
        archive_path = os.path.join(wavefunctions_dir, wavefunctions_archive_filename)

    # extract archive
    mcscript.call(
        [
            "tar", "xvf", archive_path,
        ]
    )

    # archive subdirectory inside expanded path
    extracted_dir = os.path.join(run_name, descriptor+postfix)

    # move files into task directory
    file_list = glob.glob(os.path.join(extracted_dir,"*"))
    mcscript.call(["mv", "-t", target_dir,] + file_list)

    # remove temporary directories
    mcscript.call(["rm", "-vfd", extracted_dir, run_name])


def generate_smwf_info(task, orbital_filename, partitioning_filename, res_filename, info_filename='mfdn_smwf.info'):
    """Generate SMWF info file from given MFDn input files.

    Requires information from task dictionary:
      "nuclide", "truncation_parameters":"M", "metadata":"descriptor"

    Arguments:
        task (dict): as described in docs/task.md
        orbital_filename (str): name of orbital file to be included
        partitioning_filename (str): name of partitioning file to be included
        res_filename (str): name of results file to be parsed for state info
        info_filename (str): output info filename
    """

    import mfdnres
    import re

    lines = []
    lines.append("   15200    ! Version Number")
    lines.append(
        " {Z:>3d} {N:>3d} {TwoM:>3d}    ! Z, N, 2Mj".format(
            Z=task["nuclide"][0], N=task["nuclide"][1], TwoM=round(2*task["truncation_parameters"]["M"])
        )
    )
    lines.append(" {:127s}".format(task["metadata"]["descriptor"]))

    # blank line
    lines.append("")

    # convert orbitals to 15200
    mcscript.call(
        [
            environ.shell_filename("orbital-gen"),
            "--convert",
            "15099", "{:s}".format(orbital_filename),
            "15200", "{:s}".format(orbital_filename+"15200"),
        ],
        mode=mcscript.CallMode.kSerial
    )

    # append orbitals to info file
    with open(orbital_filename+"15200") as orbital_fp:
        for line in orbital_fp:
            if line.lstrip()[0] == '#':
                continue
            if line.lstrip().rstrip() == '15200':
                continue
            lines.append(line.rstrip())

    # remove temporary orbital file
    mcscript.call(["rm","-v",orbital_filename+"15200"])

    # blank line
    lines.append("")

    # append partitioning
    with open(partitioning_filename) as partitioning_fp:
        for line in partitioning_fp:
            # ignore lines containing anything other than numbers and whitespace
            if not re.search(r"[^0-9\s]", line):
                lines.append(line.rstrip())

    # blank line
    lines.append("")

    # parse res file
    res_data = mfdnres.res.read_file(res_filename, "mfdn_v15")[0]
    levels = res_data.levels

    # basis information
    lines.append(" {:>3d}  {:>12.4f} {:>15d} {:>7d}    ! Par, WTm, Dim, Npe".format(
        res_data.params["parity"], res_data.params["WTmax"],
        res_data.params["dimension"], res_data.params["ndiags"]
    ))

    # blank line
    lines.append("")

    # state table
    lines.append(" {:7d}    ! n_states, followed by (i, 2J, nJ, T, -Eb, res)".format(
        len(levels)
    ))
    for index, level in enumerate(levels):
        (J, g, n) = level
        T = res_data.get_isospin(level)
        en = res_data.get_energy(level)
        residual = res_data.mfdn_level_residuals[level]
        lines.append(" {:>7d} {:>7d} {:>7d} {:>7.2f} {:>15.4f} {:>15.2e}".format(
            index+1, round(2*J), n, T, en, residual
        ))

    mcscript.utils.write_input(info_filename, input_lines=lines, verbose=False)

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
    # inputlist namelist dictionary
    lines = []
    
    # nucleus
    # A       : total nucleon number
    #           (needs to be the same as (Z+N) in mfdn.input)
    
    Z, N = task["nuclide"]
    lines.append("A={:d}".format(Z+N))

    # hwHO    : HO basis parameter
    #

    lines.append("hwHO={:d}".format(task["hw"]))
    
    # lamHcm  : scaling factor for Hcm Hamiltonian (dimensionless)
    #
    
    lines.append("lamHcm={:.1f}".format(task["a_cm"]/task["hw"]))
    
    # NN      : compute 2-body matrix elements (0=no, 1=yes)
    # Hardcoded to be 1, since there is no point in using the menj
    # variant without two body interaction  

    lines.append("NN={:d}".format(1))
    
    # EMax    : maximum 2-body HO quantum number of the TBME file
    #
    lines.append("EMax={:d}".format(task["EMax"]))
            
    # MEID    : string containing path/ID of the 2B interaction
    #           matrix element file that is read in
    
    lines.append("MEID={:>1}".format(task["me2j_file_id"]))
            
    # TrelID  : string containing path/ID of the 2B kinetic energy
    #           matrix element file that is read in
    # Hardcoding "trel" as file ID
    
    lines.append("TrelID={:>1}".format("trel"))
            
    # RsqID   : string containing path/ID of the 2B squared radius
    #           matrix element file that is read in
    # Hardcoding "rsq" as file ID

    lines.append("RsqID={:>1}".format("rsq"))
    
    # NNN     : compute 3-body matrix elements (0=no, 1=yes)
    #

    lines.append("NNN={:d}".format(task["use_3b"]))
    
    # E3Max   : maximum 3-body HO quantum number
    # 

    lines.append("E3Max={:d}".format(task["E3Max"]))
    
    # ME3ID   : string containing path/ID of the 3B interaction
    #           matrix element file that is read in

    lines.append("ME3ID={:>1}".format(task["me3j_file_id"]))
            
    print(os.path)
    """
    if not os.path.isfile("{:>}_eMax{:d}_EMax{:d}_hwHO{:03d}.me2j.bin".format(task["MEID"],task["EMax"],task["E3Max"],task["hw"])):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), "{:>}_eMax{:d}_EMax{:d}_hwHO{:03d}.me2j.bin".format(task["MEID"],task["EMax"],task["E3Max"],task["hw"])
        )

    if not os.path.isfile("{:>}_eMax{:d}_E3Max{:d}.me2j.bin".format(task["TrelID"],task["EMax"],task["E3Max"])):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), "{:>}_eMax{:d}_E3Max{:d}.me2j.bin".format(task["TrelID"],task["EMax"],task["E3Max"])
        )
            
    if not os.path.isfile("{:>}_eMax{:d}_E3Max{:d}.me2j.bin".format(task["RsqID"],task["EMax"],task["E3Max"])):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), "{:>}_eMax{:d}_E3Max{:d}.me2j.bin".format(task["RsqID"],task["EMax"],task["E3Max"])
        )

    if not os.path.isfile("{:>}_eMax{:d}_EMax{:d}_hwHO{:03d}.me3j.bin".format(task["ME3ID"],task["EMax"],task["E3Max"],task["hw"])):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), "{:>}_eMax{:d}_EMax{:d}_hwHO{:03d}.me3j.bin".format(task["ME3ID"],task["EMax"],task["E3Max"],task["hw"])
        )            
    """
    # generate MFDn input file
    mcscript.utils.write_input(
        os.path.join(work_dir, "menj.par"), lines
    )
