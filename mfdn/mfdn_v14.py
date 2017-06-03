import os
import glob

import mcscript

from . import utils, config

def run_mfdn_v14_b06(task, postfix=""):
    """Generate input file and execute MFDn version 14 beta 06.

    Arguments:
        task (dict): as described in module docstring
        postfix (str, optional):
    Raises:
        mcscript.ScriptError: if MFDn output not found
    """

    # validate truncation mode
    if (task["truncation_mode"] is not config.TruncationMode.kHO):
        raise ValueError("expecting truncation_mode to be {} but found {ho_truncation}".format(config.TruncationMode.kHO,**task))

    # accumulate MFDn input lines
    lines = []

    # base parameters
    truncation_parameters = task["truncation_parameters"]
    twice_Mj = int(2*task["Mj"])
    if (truncation_parameters["many_body_truncation"]=="Nmax"):
        Nmax_orb = truncation_parameters["Nmax"] + truncation_parameters["Nv"]
    elif (truncation_parameters["many_body_truncation"]=="FCI"):
        Nmax_orb = truncation_parameters["Nmax"]
    Nshell = Nmax_orb+1
    if (task["basis_mode"] in {config.BasisMode.kDirect, config.BasisMode.kDilated}):
        hw_for_trans = task["hw"]
    else:
        hw_for_trans = 0  # disable MFDn hard-coded oscillator one-body observables
    ## ndiag = int(os.environ.get("MFDN_NDIAG",0))  # allows override for spares, not so elegant
    ndiag = task.get("ndiag")
    if ndiag is None:
        ndiag = 0
    if (truncation_parameters["Nstep"]==2):
        Nmin = truncation_parameters["Nmax"]%2
    else:
        Nmin = 1

    lines.append("{:d}  # IFLAGMBSI".format(0))
    lines.append("{ndiag:d}  # ndiag (0: no spares, automatic ndiag)".format(ndiag=ndiag))
    lines.append("{:d}  # number of classes".format(2))
    lines.append("{nuclide[0]:d}  # protons (class 1 particles)".format(**task))
    lines.append("{nuclide[1]:d}  # protons (class 2 particles)".format(**task))
    lines.append("1 {Nshell:d}  # min, max # S.P. shells for class 1 particles".format(Nshell=Nshell,**task))
    lines.append("1 {Nshell:d}  # min, max # S.P. shells for class 2 particles".format(Nshell=Nshell,**task))
    lines.append("{Nmin:d} {Nmax:d} {Nstep:d}  # N_min, N_max, delta_N".format(Nmin=Nmin,**mcscript.utils.dict_union(task,truncation_parameters)))
    lines.append("{:d}   # Total 2 M_j".format(twice_Mj))
    lines.append("{eigenvectors:d} {lanczos:d} {initial_vector:d} {tolerance:e}  # number of eigenvalues/vectors, max number of its, ...)".format(**task))
    lines.append("{:d} {:d}  # rank of input Hamiltonian/interaction".format(2,2))
    lines.append("{hw_for_trans:g} {k_mN_csqr:g}  # h-bar*omega, Nucleon mass (MeV) ".format(
        hw_for_trans=hw_for_trans,k_mN_csqr=utils.k_mN_csqr,**task
    ))

    # tbo: collect tbo names
    obs_basename_list = ["tbme-rrel2"]
    if ("H-components" in task["observable_sets"]):
        obs_basename_list += ["tbme-Trel","tbme-Ncm","tbme-VNN"]
        if (task["use_coulomb"]):
            obs_basename_list += ["tbme-VC"]
    if ("am-sqr" in task["observable_sets"]):
        obs_basename_list += ["tbme-L","tbme-Sp","tbme-Sn","tbme-S","tbme-J"]
    if ("observables" in task):
        obs_basename_list += list(task["observables"].keys())

    # tbo: log tbo names in separate file to aid future data analysis
    mcscript.utils.write_input("tbo_names{:s}.dat".format(postfix), input_lines=obs_basename_list)

    # tbo: write list of operators
    lines.append("tbme-H")  # Hamiltonian basename
    num_obs = 2 + len(obs_basename_list)
    if (num_obs > 9):
        raise mcscript.ScriptError("Too many observables for MFDn v14")
    lines.append("{:d}   # number of observables (J, T, R2, ...)".format(num_obs))
    lines += obs_basename_list

    # obdme: parameters
    lines.append("{enable_obd:d} {twice_multipolarity:d} # static one-body density matrix elements (0: no one-body densities), twice multipolarity".format(
        enable_obd=1,twice_multipolarity=2*task["obdme_multipolarity"]
    ))
    lines.append("{num_reference_states:d} {max_delta_J:d} # number of reference states for transitions (0: no transitions, -1: all2all), max delta2J (?)".format(
        num_reference_states=len(task["obdme_reference_state_list"]),
        max_delta_J=2*task["obdme_multipolarity"]
    ))

    # obdme: validate reference state list
    #
    # guard against pathetically common mistakes
    for (J,g_rel,i) in task["obdme_reference_state_list"]:
        # validate integer/half-integer character of angular momentum
        twice_J = int(2*J)
        if ((twice_J%2) != (sum(task["nuclide"])%2)):
            raise ValueError("invalid angular momentum for reference state")
        # validate grade (here taken relative to natural grade)
        if ((g_rel != (truncation_parameters["Nmax"]%2)) and (truncation_parameters["Nstep"] != 1)):
            raise ValueError("invalid parity for reference state")

    # obdme: write reference state list
    for reference_state in task["obdme_reference_state_list"]:
        lines.append("{:d} {:d} {:d}".format(2*reference_state[0],reference_state[1],reference_state[2]))

    # ensure terminal line
    lines.append("")

    # generate MFDn input file
    mcscript.utils.write_input("work/mfdn.dat",input_lines=lines)

    # import partitioning file
    if (task["partition_filename"] is not None):
        if (not os.path.exists(task["partition_filename"])):
            raise mcscript.ScriptError("partition file not found")
        mcscript.call(["cp","--verbose",task["partition_filename"],"work/mfdn_partitioning.info"])

    # enter work directory
    os.chdir("work")

    # invoke MFDn
    mcscript.call(
        [
            config.environ.mfdn_filename(task["mfdn_executable"])
        ],
        mode = mcscript.call.hybrid,
        check_return=True
    )

    # test for basic indications of success
    if (not os.path.exists("mfdn.out")):
        raise mcscript.ScriptError("mfdn.out not found")
    if (not os.path.exists("mfdn.res")):
        raise mcscript.ScriptError("mfdn.res not found")

    # leave work directory
    os.chdir("..")

def save_mfdn_v14_output(task, postfix=""):
    """Generate input file and execute MFDn version 14 beta 06.

    Arguments:
        task (dict): as described in module docstring

    Raises:
        mcscript.ScriptError: if MFDn output not found

    """

    # save quick inspection copies of mfdn.{res,out}
    natural_orbitals = task.get("natural_orbitals")
    descriptor = task["metadata"]["descriptor"]
    print("Saving basic output files...")
    res_filename = "{:s}-mfdn-{:s}{:s}.res".format(mcscript.parameters.run.name, descriptor, postfix)
    mcscript.call(["cp","--verbose","work/mfdn.res",res_filename])
    out_filename = "{:s}-mfdn-{:s}{:s}.out".format(mcscript.parameters.run.name, descriptor, postfix)
    mcscript.call(["cp","--verbose","work/mfdn.out",out_filename])

    # save OBDME files for next natural orbital iteration
    if natural_orbitals:
        print("Saving OBDME files for natural orbital generation...")
        obdme_info_filename = "mfdn.rppobdme.info"
        mcscript.call(
            [
                "cp","--verbose",
                "work/{}".format(obdme_info_filename),
                config.filenames.natorb_info_filename(postfix)
            ]
        )
        obdme_filename = glob.glob("work/mfdn.statrobdme.seq{:03d}*".format(task["natorb_base_state"]))
        mcscript.call(
            [
                "cp","--verbose",
                obdme_filename[0],
                config.filenames.natorb_obdme_filename(postfix)
            ]
        )

    # save full archive of input, log, and output files
    print("Saving full output files...")
    # logging
    archive_file_list = [
        config.filenames.h2mixer_filename(postfix),
        "tbo_names.dat"
        ]
    # orbital information
    archive_file_list += [
        config.filenames.orbitals_int_filename(postfix),
        config.filenames.orbitals_filename(postfix),
        ]
    # transformation information
    archive_file_list += [
        config.filenames.radial_xform_filename(postfix),
        # config.filenames.radial_me_filename(postfix, operator_type, power),
        config.filenames.radial_olap_int_filename(postfix),
        ]
    # Coulomb information:
    if task["use_coulomb"]:
        archive_file_list += [
            config.filenames.orbitals_coul_filename(postfix),
            config.filenames.radial_olap_coul_filename(postfix),
        ]
    # natural orbital information
    if natural_orbitals:
        archive_file_list += [
            config.filenames.natorb_info_filename(postfix),
            config.filenames.natorb_obdme_filename(postfix),
            ]
        # glob for natural orbital xform
        archive_file_list += glob.glob(config.filenames.natorb_xform_filename(postfix))
    # MFDn output
    archive_file_list += [
        "work/mfdn.dat","work/mfdn.out","work/mfdn.res","work/mfdn_partitioning.generated","work/mfdn_spstates.info"
    ]
    # renamed versions
    archive_file_list += [out_filename,res_filename]
    # MFDN obdme
    if (task["save_obdme"]):
        archive_file_list += glob.glob("work/*obdme*")
    # generate archive (outside work directory)
    archive_filename = "{:s}-mfdn-{:s}{:s}.tgz".format(mcscript.parameters.run.name, descriptor, postfix)
    mcscript.call(
        [
            "tar", "zcvf", archive_filename,
            "--transform=s,work/,,",
            "--show-transformed"
        ] + archive_file_list
    )

    # copy results out (if in multi-task run)
    if (mcscript.task.results_dir is not None):
        mcscript.call(
            [
                "cp",
                "--verbose",
                res_filename,out_filename,archive_filename,
                "--target-directory={}".format(mcscript.task.results_dir)
            ]
        )

    # cleanup of wave function files
    scratch_file_list = glob.glob("work/*")
    mcscript.call(["rm", "-vf"] + scratch_file_list)
