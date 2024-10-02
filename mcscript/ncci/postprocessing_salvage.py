"""postprocessing_salvage.py -- run postprocessor to fix up MFDn run aborted before observables stage

Mark A. Caprio and Zhou Zhou
University of Notre Dame

- 10/01/24 (mac/zz): Created, using some code from postprocessing.py.
"""

import os

import am
import numpy as np
import mfdnres.tools

import mcscript.control
import mcscript.parameters
import mcscript.utils

from . import (
    environ,
    postprocessing,
    )

def task_handler_mfdn_postprocessor_salvage_mfdn_levels(task):
    """Task handler to use postprocessor to find E/J/T for wf from aborted MFDn run.

    Preconditions:

        - TBME files for the J2 and T2 operators must already be in the working
          directory.  If they are not already available due to there inclusion
          as two-body observables in the original run, add them to the task
          dictionary now, and re-run the task_handler_mfdn_pre phase:

              "tb_observable_sets": ["am-sqr", "isospin"],

    Arguments:
        task (dict): as described in module docstring

    """

    # convenience variables
    postfix = ""
    descriptor = task["metadata"]["descriptor"]
    work_dir = "work{:s}".format(postfix)
    transitions_executable = environ.mfdn_postprocessor_filename(
        task.get("mfdn-transitions_executable", "xtransitions")
    )

    # create work directory if it doesn't exist yet
    mcscript.utils.mkdir(work_dir, exist_ok=True, parents=True)
    # go to work directory
    os.chdir(work_dir)

    # generate mfdn_smwf.info with dummy tail
    dummy_J=task["truncation_parameters"]["M"]
    num_eigenvectors = task["eigenvectors"]
    if not os.path.isfile("mfdn_smwf.info_stub"):
        mcscript.control.call(["cp", "--verbose", "mfdn_smwf.info", "mfdn_smwf.info_stub"])
    mcscript.control.call(["cp", "--verbose", "mfdn_smwf.info_stub", "mfdn_smwf.info"])
    info_file = open("mfdn_smwf.info", mode="a")
    info_lines = []
    info_lines.append("")
    info_lines.append(
        "{:8d}    ! n_states, followed by (i, 2J, nJ, T, -Eb, res)".format(num_eigenvectors)
        + " -- dummy for fix-up after aborted MFDn run"
    )
    for eigenstate_index in range(num_eigenvectors):
        n = eigenstate_index+1
        i = eigenstate_index+1
        E = 0.
        J = dummy_J
        n = i
        T = 0.
        res = 0.
        info_lines.append(
            "{:8d} {:7d} {:7d} {:7.2f} {:15.4f} {:15.2e}".format(i, round(2*J), n, T, E, res)
        )
    info_string = "\n".join(info_lines) + "\n"
    info_file.write(info_string)
    info_file.close()

    # convert existing TBME files to v15200
    #
    # postprocessor does not support v15099 binary input
    operator_id_list = ["H", "J2", "T2"]
    for operator_id in operator_id_list:
        mcscript.control.call(["h2conv", "15200", "tbme-{}.bin".format(operator_id), "tbme-{}-v15200.bin".format(operator_id)])
        
    
    # for each state: run postprocessor and harvest observables
    dummy_J=task["truncation_parameters"]["M"]
    wigner_eckart_factor = 1/np.sqrt(2*dummy_J+1)
    dummy_g = 0
    num_free_obdmes = 0
    max2K = 0
    operator_id_list = ["H-v15200", "J2-v15200", "T2-v15200"]
    state_info_list = []
    for eigenstate_index in range(num_eigenvectors):

        # generate postprocessor intput
        ket_J, ket_g, ket_n = dummy_J, dummy_g, eigenstate_index +1
        bra_J, bra_g, bra_n = dummy_J, dummy_g, eigenstate_index +1
        ket_qn_list = [(ket_J, ket_g, ket_n)]
        bra_wf_prefix = "."
        ket_wf_prefix = "."
        transitions_inputlist = {
            "basisfilename_bra": "{:s}/mfdn_MBgroups".format(bra_wf_prefix),
            "smwffilename_bra": "{:s}/mfdn_smwf".format(bra_wf_prefix),
            "infofilename_bra": "{:s}/mfdn_smwf.info".format(bra_wf_prefix),
            "TwoJ_bra": round(2*bra_J),
            "n_bra": int(bra_n),

            "basisfilename_ket": "{:s}/mfdn_MBgroups".format(ket_wf_prefix),
            "smwffilename_ket": "{:s}/mfdn_smwf".format(ket_wf_prefix),
            "infofilename_ket": "{:s}/mfdn_smwf.info".format(ket_wf_prefix),
            "TwoJ_ket": [round(2*ket_J) for (ket_J,ket_g,ket_n) in ket_qn_list],
            "n_ket": [int(ket_n) for (ket_J,ket_g,ket_n) in ket_qn_list],

            "obdme": True if num_free_obdmes > 0 else False,
            "max2K": max2K,
            "hbomeg": task.get("hw", 0.0),
            "numTBtrans": len(operator_id_list),
            "TBMEoperators": ["tbme-{}".format(basename) for basename in operator_id_list],
        }
        mcscript.utils.write_namelist(
            "transitions.input",
            input_dict={"transition_data": transitions_inputlist}
            )

        # run postprocessor
        mcscript.control.call(["rm", "--force", "transitions.out", "transitions.res"])  # remove old output so file watchdog can work
        mcscript.control.call(
            [transitions_executable],
            mode=mcscript.control.CallMode.kHybrid,
            file_watchdog=mcscript.control.FileWatchdog("transitions.out"),
            file_watchdog_restarts=3
        )

        # parse postprocessor results
        fp = open('transitions.res')
        res = postprocessing.parse_transitions_results(fp)
        fp.close()

        # harvest relevant info
        state_info = {}
        for (operator_id, transition_dict) in res["two_body_observables"].items():
            operator_id = operator_id.replace('tbme-','').replace("-v15200","")
            (bra_qn,ket_qn), rme = transition_dict.popitem()
            state_info[operator_id] = wigner_eckart_factor*rme
        state_info_list.append(state_info)

    # interpret calculated expectation values
    twice_J_counts = {}
    for state_info in state_info_list:
        J = mfdnres.tools.effective_am(state_info["J2"])
        twice_J_counts.setdefault(round(2*J), 0)
        twice_J_counts[round(2*J)]+=1
        n = twice_J_counts[round(2*J)]
        T = mfdnres.tools.effective_am(state_info["T2"])
        state_info["J"] = J
        state_info["n"] = n
        state_info["T"] = T
    print("Extracted state data: {}".format(state_info_list))
    
    # generate mfdn_smwf.info with dummy tail
    dummy_J=task["truncation_parameters"]["M"]
    num_eigenvectors = task["eigenvectors"]
    if not os.path.isfile("mfdn_smwf.info_stub"):
        mcscript.control.call(["cp", "--verbose", "mfdn_smwf.info", "mfdn_smwf.info_stub"])
    mcscript.control.call(["cp", "--verbose", "mfdn_smwf.info_stub", "mfdn_smwf.info"])
    info_file = open("mfdn_smwf.info", mode="a")
    info_lines = []
    info_lines.append("")
    info_lines.append(
        "{:8d}    ! n_states, followed by (i, 2J, nJ, T, -Eb, res)".format(num_eigenvectors)
        + " -- generated in fix-up after aborted MFDn run"
    )
    for eigenstate_index in range(num_eigenvectors):
        state_info = state_info_list[eigenstate_index]
        i = eigenstate_index+1
        E = state_info["H"]
        J = state_info["J"]
        n = state_info["n"]
        T = state_info["T"]
        res = 0.
        info_lines.append(
            "{:8d} {:7d} {:7d} {:7.2f} {:15.4f} {:14.2e}".format(i, round(2*J), n, T, E, res)
        )
    info_string = "\n".join(info_lines) + "\n"
    info_file.write(info_string)
    info_file.close()
        
    # generate Energies section for mfdn.out
    if not os.path.isfile("mfdn.res_stub"):
        mcscript.control.call(["cp", "--verbose", "mfdn.res", "mfdn.res_stub"])
    mcscript.control.call(["cp", "--verbose", "mfdn.res_stub", "mfdn.res"])
    res_file = open("mfdn.res", mode="a")
    res_lines = [
        "",
        "[RESULTS]",
        "# generated in fix-up after aborted MFDn run",
        "#",
        "# following Condon-Shortley phase conventions",
        "# for conventions of reduced matrix elements and",
        "# for Wigner-Eckart theorem, see Suhonen (2.27)",
        "",
        "[Energies]",
        "# Seq       J    n      T        Eabs        Eexc        Error    J-full",
    ]
    Eref = state_info_list[0]["H"]
    for eigenstate_index in range(num_eigenvectors):
        state_info = state_info_list[eigenstate_index]
        i = eigenstate_index+1
        E = state_info["H"]
        J = state_info["J"]
        n = state_info["n"]
        T = state_info["T"]
        Ex = E - Eref
        res = 0.
        res_lines.append(
            "{:5d} {:8.1f} {:3d} {:7.3f} {:12.3f} {:10.3f} {:12.2e} {:9.4f}".format(i, J, n, T, E, Ex, res, J)
        )
    res_string = "\n".join(res_lines) + "\n"
    res_file.write(res_string)
    res_file.close()
        
    # copy out mfdn.res and mfdn.out
    #
    # as in mfdn_v15.run_mfdn()
    
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

    
