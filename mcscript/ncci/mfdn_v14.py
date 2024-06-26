"""mfdn_v14.py -- driver module for MFDn v14.

Patrick Fasano
University of Notre Dame

- 03/22/17 (pjf): Created, split from __init__.py.
- 04/06/17 (pjf): Correctly reference config submodule (mfdn.config).
- 04/07/17 (pjf):
  + Update for mcscript namespace changes.
  + Fix format call for ndiag.
- 04/11/17 (pjf): Fix broken imports.
- 06/03/17 (pjf): Remove explicit references to natural orbitals from bulk of
    scripting.
- 06/05/17 (pjf):
  + Add postfix to tbo_names.dat.
  + Make function names generic so that drivers are swappable.
- 06/07/17 (pjf): Clean up style.
- 06/10/17 (pjf): Make sure reference state 2J is an int.
- 06/22/17 (pjf): Update references to mcscript.exception.ScriptError.
- 07/31/17 (pjf): Create work directory if nonexistent when running mfdn.
- 08/11/17 (pjf):
  + Use new TruncationModes.
  + Fix FCI truncation.
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
- 06/02/19 (mac):
  + Remove save_mfdn_output_out_only.
  + Rename save_mfdn_output to save_mfdn_task_data.
- 06/04/19 (pjf): Save mfdn.out and mfdn.res to subdirectories of results.
- 06/07/19 (pjf): Check that MFDn launches successfully with
    mcscript.control.FileWatchdog on mfdn.out.
- 09/04/19 (pjf): Rename Trel->Tintr.
- 09/07/19 (pjf): Remove Nv from truncation_parameters.
- 10/10/19 (pjf): Get tbo basenames from tbme.get_tbme_targets().
- 12/11/19 (pjf):
    + Use new results storage helper functions from mcscript.
    + Deprecate save_mfdn_task_data().
- 09/09/20 (pjf): Use operators module instead of tbme for operator names.
- 09/16/20 (pjf):
    + Check that diagonalization is enabled.
    + Add "tbme-" to operator id to form basename.
- 11/13/20 (pjf): Use constants module.
- 11/24/20 (pjf): Fix natorb filename globbing for non-integer J.
- 05/09/22 (pjf): Split generate_mfdn_input() from run_mfdn().
"""
import errno
import os
import glob
import warnings

import mcscript.control
import mcscript.exception
import mcscript.parameters
import mcscript.task
import mcscript.utils

from . import (
    constants,
    environ,
    modes,
    operators,
    utils,
)


def generate_mfdn_input(task, run_mode=modes.MFDnRunMode.kNormal, postfix=""):
    """Generate input file for MFDn version 14 beta 06.

    Arguments:
        task (dict): as described in module docstring
        run_mode (modes.MFDnRunMode): run mode for MFDn
        postfix (string, optional): identifier to add to generated files

    Raises:
        mcscript.exception.ScriptError: if MFDn output not found
    """
    # check that diagonalization is enabled
    if not task.get("diagonalization"):
        raise mcscript.exception.ScriptError(
            'Task dictionary "diagonalization" flag not enabled.'
        )

    # validate truncation modes
    allowed_sp_truncations = (modes.SingleParticleTruncationMode.kNmax,)
    allowed_mb_truncations = (modes.ManyBodyTruncationMode.kNmax, modes.ManyBodyTruncationMode.kFCI)
    if task["sp_truncation_mode"] not in allowed_sp_truncations:
        raise ValueError("expecting sp_truncation_mode to be one of {} but found {sp_truncation_mode}".format(allowed_sp_truncations, **task))
    if task["mb_truncation_mode"] not in allowed_mb_truncations:
        raise ValueError("expecting mb_truncation_mode to be one of {} but found {mb_truncation_mode}".format(allowed_mb_truncations, **task))

    # accumulate MFDn input lines
    lines = []

    # base parameters
    truncation_parameters = task["truncation_parameters"]
    twice_Mj = int(2*truncation_parameters["M"])
    if task["mb_truncation_mode"] == modes.ManyBodyTruncationMode.kNmax:
        Nmax_orb = truncation_parameters["Nmax"] + utils.Nv_for_nuclide(task["nuclide"])
        Nmax = truncation_parameters["Nmax"]
    elif task["mb_truncation_mode"] == modes.ManyBodyTruncationMode.kFCI:
        Nmax_orb = truncation_parameters["Nmax"]
        Nmax = sum(task["nuclide"]) * Nmax_orb
    Nshell = Nmax_orb+1
    if (task["basis_mode"] in {modes.BasisMode.kDirect, modes.BasisMode.kDilated}):
        hw_for_trans = task["hw"]
    else:
        hw_for_trans = 0  # disable MFDn hard-coded oscillator one-body observables
    ## ndiag = int(os.environ.get("MFDN_NDIAG",0))  # allows override for spares, not so elegant
    ndiag = task.get("ndiag")
    if ndiag is None:
        ndiag = 0
    Nstep = truncation_parameters["Nstep"]
    if (Nstep == 2):
        Nmin = truncation_parameters["Nmax"] % 2
    else:
        Nmin = 1

    lines.append("{:d}  # IFLAGMBSI".format(run_mode))
    lines.append("{ndiag:d}  # ndiag (0: no spares, automatic ndiag)".format(ndiag=ndiag))
    lines.append("{:d}  # number of classes".format(2))
    lines.append("{nuclide[0]:d}  # protons (class 1 particles)".format(**task))
    lines.append("{nuclide[1]:d}  # protons (class 2 particles)".format(**task))
    lines.append("1 {Nshell:d}  # min, max # S.P. shells for class 1 particles".format(Nshell=Nshell, **task))
    lines.append("1 {Nshell:d}  # min, max # S.P. shells for class 2 particles".format(Nshell=Nshell, **task))
    lines.append("{Nmin:d} {Nmax:d} {Nstep:d}  # N_min, N_max, delta_N".format(Nmin=Nmin, Nmax=Nmax, Nstep=Nstep))
    lines.append("{:d}   # Total 2 M_j".format(twice_Mj))
    lines.append("{eigenvectors:d} {max_iterations:d} {initial_vector:d} {tolerance:e}  # number of eigenvalues/vectors, max number of its, ...)".format(**task))
    lines.append("{:d} {:d}  # rank of input Hamiltonian/interaction".format(2, 2))
    lines.append("{hw_for_trans:g} {k_mN_csqr:g}  # h-bar*omega, Nucleon mass (MeV) ".format(
        hw_for_trans=hw_for_trans, k_mN_csqr=constants.k_mN_csqr, **task
    ))

    # tbo: collect tbo names
    obs_basename_list = [
        "tbme-{}".format(id_)
        for id_ in operators.tb.get_tbme_targets(task)[(0,0,0)].keys()
    ]

    # do not evaluate Hamiltonian as observable
    obs_basename_list.remove("tbme-H")

    # tbo: log tbo names in separate file to aid future data analysis
    mcscript.utils.write_input("tbo_names{:s}.dat".format(postfix), input_lines=obs_basename_list)

    # tbo: write list of operators
    lines.append("tbme-H")  # Hamiltonian basename
    num_obs = 2 + len(obs_basename_list)
    if (num_obs > 9):
        raise mcscript.exception.ScriptError("Too many observables for MFDn v14")
    lines.append("{:d}   # number of observables (J, T, R2, ...)".format(num_obs))
    lines += obs_basename_list

    # obdme: parameters
    lines.append("{enable_obd:d} {twice_multipolarity:d} # static one-body density matrix elements (0: no one-body densities), twice multipolarity".format(
        enable_obd=1, twice_multipolarity=2*task["obdme_multipolarity"]
    ))
    lines.append("{num_reference_states:d} {max_delta_J:d} # number of reference states for transitions (0: no transitions, -1: all2all), max delta2J (?)".format(
        num_reference_states=len(task["obdme_reference_state_list"]),
        max_delta_J=2*task["obdme_multipolarity"]
    ))

    # obdme: validate reference state list
    #
    # guard against pathetically common mistakes
    for (J, g_rel, i) in task["obdme_reference_state_list"]:
        # validate integer/half-integer character of angular momentum
        twice_J = int(2*J)
        if ((twice_J % 2) != (sum(task["nuclide"]) % 2)):
            raise ValueError("invalid angular momentum for reference state")
        # validate grade (here taken relative to natural grade)
        if ((g_rel != (truncation_parameters["Nmax"] % 2)) and (truncation_parameters["Nstep"] != 1)):
            raise ValueError("invalid parity for reference state")

    # obdme: write reference state list
    for reference_state in task["obdme_reference_state_list"]:
        lines.append("{:d} {:d} {:d}".format(int(2*reference_state[0]), reference_state[1], reference_state[2]))

    # ensure terminal line
    lines.append("")

    # create work directory if it doesn't exist yet (-p)
    work_dir = "work{:s}".format(postfix)
    mcscript.control.call(["mkdir", "-p", work_dir])

    # generate MFDn input file
    mcscript.utils.write_input(work_dir+"/mfdn.dat", input_lines=lines)

    # import partitioning file
    partition_filename = task.get("partition_filename")
    if partition_filename is not None:
        partition_filename = mcscript.utils.expand_path(partition_filename)
        if not os.path.exists(partition_filename):
            raise mcscript.exception.ScriptError("partition file not found")
        mcscript.control.call([
            "cp", "--verbose",
            partition_filename,
            os.path.join(work_dir, "mfdn_partitioning.info")
            ])


def run_mfdn(task, postfix=""):
    """Execute MFDn version 14 beta 06.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files

    Raises:
        mcscript.exception.ScriptError: if MFDn output not found
    """
    # check that diagonalization is enabled
    if not task.get("diagonalization"):
        raise mcscript.exception.ScriptError(
            'Task dictionary "diagonalization" flag not enabled.'
        )

    # enter work directory
    work_dir = "work{:s}".format(postfix)
    os.chdir(work_dir)

    # check that mfdn.input exists
    if not os.path.isfile("mfdn.input"):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), "mfdn.input"
        )

    # invoke MFDn
    mcscript.control.call(
        [
            environ.mfdn_filename(task["mfdn_executable"])
        ],
        mode=mcscript.control.CallMode.kHybrid,
        check_return=True,
        file_watchdog=mcscript.control.FileWatchdog("mfdn.out")
    )

    # test for basic indications of success
    if (not os.path.exists("mfdn.out")):
        raise mcscript.exception.ScriptError("mfdn.out not found")
    if (not os.path.exists("mfdn.res")):
        raise mcscript.exception.ScriptError("mfdn.res not found")

    # leave work directory
    os.chdir("..")

    # save quick inspection copies of mfdn.{res,out}
    descriptor = task["metadata"]["descriptor"]
    work_dir = "work{:s}".format(postfix)
    print("Saving basic output files...")
    filename_prefix = "{:s}-mfdn-{:s}{:s}".format(mcscript.parameters.run.name, descriptor, postfix)
    res_filename = "{:s}.res".format(filename_prefix)
    out_filename = "{:s}.out".format(filename_prefix)

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
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    # save OBDME files for next natural orbital iteration
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals not enabled")

    work_dir = "work{:s}".format(postfix)
    obdme_info_filename = "mfdn.rppobdme.info"
    try:
        (J, g, n) = task["natorb_base_state"]
        obdme_filename = glob.glob(
            "{:s}/mfdn.statrobdme.seq*.2J{:02d}.p*.n{:02d}.2T*".format(work_dir, int(2*J), n)
            )
    except TypeError:
        obdme_filename = glob.glob(
            "{:s}/mfdn.statrobdme.seq{:03d}*".format(work_dir, task["natorb_base_state"])
            )

    print("Saving OBDME files for natural orbital generation...")
    mcscript.control.call(
        [
            "cp", "--verbose",
            os.path.join(work_dir, obdme_info_filename),
            environ.natorb_info_filename(postfix)
        ]
    )
    mcscript.control.call(
        [
            "cp", "--verbose",
            obdme_filename[0],
            environ.natorb_obdme_filename(postfix)
        ]
    )

def save_mfdn_task_data(task, postfix=""):
    """Collect and save MFDn output.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files

    Raises:
        mcscript.exception.ScriptError: if MFDn output not found
    """
    warnings.warn("MFDn v14 task-data archiving is deprecated.", FutureWarning)
    # save quick inspection copies of mfdn.{res,out}
    natural_orbitals = task.get("natural_orbitals")
    descriptor = task["metadata"]["descriptor"]
    work_dir = "work{:s}".format(postfix)
    print("Saving basic output files...")
    filename_prefix = "{:s}-mfdn-{:s}{:s}".format(mcscript.parameters.run.name, descriptor, postfix)
    res_filename = "{:s}.res".format(filename_prefix)
    mcscript.control.call(["cp", "--verbose", work_dir+"/mfdn.res", res_filename])
    out_filename = "{:s}.out".format(filename_prefix)
    mcscript.control.call(["cp", "--verbose", work_dir+"/mfdn.out", out_filename])

    # append obscalc-ob output to res file
    if os.path.exists(environ.obscalc_ob_res_filename(postfix)):
        print("Appending obscalc-ob output to res file...")
        with open(res_filename, 'a') as res_file:
            res_file.write("\n")
            with open(environ.obscalc_ob_res_filename(postfix), 'r') as obs_file:
                for line in obs_file:
                    res_file.write(line)

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
    archive_file_list += [
        environ.radial_xform_filename(postfix),
        # environ.radial_me_filename(postfix, operator_type, power),
        environ.radial_olap_int_filename(postfix),
        ]
    # Coulomb information:
    if task["use_coulomb"]:
        archive_file_list += [
            environ.orbitals_coul_filename(postfix),
            environ.radial_olap_coul_filename(postfix),
        ]
    # natural orbital information
    if natural_orbitals:
        archive_file_list += [
            environ.natorb_info_filename(postfix),
            environ.natorb_obdme_filename(postfix),
            ]
        # glob for natural orbital xform
        archive_file_list += glob.glob(environ.natorb_xform_filename(postfix))
    # MFDn output
    archive_file_list += [
        work_dir+"/mfdn.dat", work_dir+"/mfdn.out", work_dir+"/mfdn.res",
        work_dir+"/mfdn_partitioning.generated", work_dir+"/mfdn_spstates.info"
    ]
    # partitioning file
    if os.path.isfile(work_dir+"/mfdn_partitioning.info"):
        archive_file_list += [work_dir+"/mfdn_partitioning.info"]
    # renamed versions
    archive_file_list += [out_filename, res_filename]
    # MFDN obdme
    if (task["save_obdme"]):
        archive_file_list += glob.glob(work_dir+"/*obdme*")
    # observable output
    archive_file_list += glob.glob("em-gen.in")
    archive_file_list += glob.glob("obscalc-ob.*")
    # generate archive (outside work directory)
    archive_filename = "{:s}.tgz".format(filename_prefix)
    mcscript.control.call(
        [
            "tar", "zcvf", archive_filename,
            "--transform=s,{:s}/,,".format(work_dir),
            "--transform=s,^,{:s}/{:s}{:s}/,".format(mcscript.parameters.run.name, descriptor, postfix),
            "--show-transformed"
        ] + archive_file_list
    )

    # save wavefunctions (smwf files)
    if task.get("save_wavefunctions"):
        smwf_archive_file_list = glob.glob(work_dir+"/mfdn_smwf*")
        smwf_archive_file_list += glob.glob(work_dir+"/mfdn_MBgroups*")
        smwf_archive_filename = "{:s}-wf.tar".format(filename_prefix)
        mcscript.control.call(
            [
                "tar", "cvf", smwf_archive_filename,
                "--transform=s,{:s}/,,".format(work_dir),
                "--transform=s,^,{:s}/{:s}{:s}/,".format(mcscript.parameters.run.name, descriptor, postfix),
                "--show-transformed"
            ] + smwf_archive_file_list
        )

    # copy results out (if in multi-task run)
    if (mcscript.task.results_dir is not None):
        mcscript.control.call(
            [
                "cp",
                "--verbose",
                res_filename, out_filename, archive_filename,
                "--target-directory={}".format(mcscript.task.results_dir)
            ]
        )
        if task.get("save_wavefunctions"):
            wavefunction_dir = os.path.join(mcscript.parameters.run.work_dir, "wavefunctions")
            mcscript.control.call(["mkdir", "-p", wavefunction_dir])
            mcscript.control.call(
                [
                    "mv",
                    "--verbose",
                    smwf_archive_filename,
                    "--target-directory={}".format(wavefunction_dir)
                ]
            )


def cleanup_mfdn_workdir(task, postfix=""):
    """Remove temporary MFDn work files.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    # cleanup of wave function files
    scratch_file_list = glob.glob("work{:s}/*".format(postfix))
    mcscript.control.call(["rm", "-vf"] + scratch_file_list)
