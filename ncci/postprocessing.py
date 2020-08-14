"""postprocessing.py -- perform postprocessing and observable calculation tasks

Patrick Fasano
University of Notre Dame

- 10/25/17 (pjf): Created.
- 05/30/19 (pjf): Move obscalc-ob.res out to results subdirectory.
- 09/04/19 (pjf): Update for new em-gen, using l and s one-body RMEs.
- 09/11/19 (pjf): Update for new obscalc-ob input format (single vs. multi-file).
- 10/11/19 (pjf): Implement initial (basic) two-body postprocessing.
- 10/12/19 (pjf): Fix call to generation of mfdn_smwf.info.
- 12/11/19 (pjf): Use new results storage helper functions from mcscript.
"""
import collections
import os
import glob
import re

import mcscript

from . import modes, environ, utils, tbme
from . import mfdn_v15


def generate_em(task, postfix=""):
    """Generate electromagnetic matrix elements.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    # accumulate em-gen input lines
    lines = []

    # set up orbitals
    lines += [
        "set-indexing {:s}".format(environ.orbitals_filename(postfix)),
        "set-basis-scale-factor {:e}".format(utils.oscillator_length(task["hw"])),
        ]

    for am_type in ["l", "s"]:
        lines.append("define-am-source {type:s} {filename:s}".format(
            type=am_type, filename=environ.obme_filename(postfix, am_type)
        ))

    for (operator_type, order) in task.get("ob_observables", []):
        if operator_type == 'E':
            radial_power = order
        elif operator_type == 'M':
            radial_power = order-1
        else:
            raise mcscript.exception.ScriptError("only E or M transitions currently supported")

        # load non-trivial solid harmonic RMEs
        if radial_power > 0:
            operator_id = "rY{:d}".format(radial_power)
            lines.append("define-radial-source {type:s} {order:d} {filename:s}".format(
                type='r', order=radial_power,
                filename=environ.obme_filename(postfix, operator_id)
                ))

        for species in ["p", "n"]:
            if operator_type == "E":
                lines.append(
                    "define-target E {order:d} {species:s} {output_filename:s}".format(
                        order=order, species=species,
                        output_filename=environ.observable_me_filename(postfix, operator_type, order, species)
                        )
                    )
            elif operator_type == "M":
                lines.append(
                    "define-target Dl {order:d} {species:s} {output_filename:s}".format(
                        order=order, species=species,
                        output_filename=environ.observable_me_filename(postfix, "Dl", order, species)
                        )
                    )
                lines.append(
                    "define-target Ds {order:d} {species:s} {output_filename:s}".format(
                        order=order, species=species,
                        output_filename=environ.observable_me_filename(postfix, "Ds", order, species)
                        )
                    )

    # ensure trailing line
    lines.append("")

    # write input file
    mcscript.utils.write_input(
        environ.emgen_filename(postfix),
        input_lines=lines,
        verbose=False
        )

    # invoke em-gen
    mcscript.call(
        [
            environ.shell_filename("em-gen")
        ],
        input_lines=lines,
        mode=mcscript.CallMode.kSerial
    )

def evaluate_ob_observables(task, postfix=""):
    """Evaluate one-body observables with obscalc-ob.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    work_dir = "work{:s}".format(postfix)

    # accumulate obscalc-ob input lines
    lines = []

    # initial comment
    lines.append("# task: {}".format(task))
    lines.append("")

    # indexing setup
    lines += [
        "set-indexing {:s}".format(environ.orbitals_filename(postfix)),
        "set-output-file {:s}".format(environ.obscalc_ob_res_filename(postfix)),
        ]

    # set up operators
    for (operator_type, order) in task.get("ob_observables", []):
        lines.append("define-radial-source {:s}".format(
            environ.radial_me_filename(postfix, operator_type, order)
            ))
        for species in ["p", "n"]:
            if operator_type == "M":
                # convenience definition for M observable
                lines.append(
                    "define-operator Dl({:s}) {:s}".format(
                        species,
                        environ.observable_me_filename(postfix, "Dl", order, species)
                        )
                    )
                lines.append(
                    "define-operator Ds({:s}) {:s}".format(
                        species,
                        environ.observable_me_filename(postfix, "Ds", order, species)
                        )
                    )
            else:
                lines.append(
                    "define-operator {:s}({:s}) {:s}".format(
                        operator_type,
                        species,
                        environ.observable_me_filename(postfix, operator_type, order, species)
                        )
                    )

    # get filenames for static densities and extract quantum numbers
    obdme_files = {}
    filenames = glob.glob(os.path.join(work_dir, "mfdn.statrobdme.*"))
    regex = re.compile(
        # directory prefix
        r"{}".format(os.path.join(work_dir, "")) +
        # prolog
        r"mfdn\.statrobdme"
        # sequence number
        r"\.seq(?P<seq>\d{3})"
        # 2J
        r"\.2J(?P<twoJ>\d{2})"
        # parity (v14 only)
        r"(\.p(?P<g>\d))?"
        # n
        r"\.n(?P<n>\d{2})"
        # 2T
        r"\.2T(?P<twoT>\d{2})"
        )
    conversions = {
        "seq": int,
        "twoJ": int,
        "g": lambda x: int(x) if x is not None else 0,
        "n": int,
        "twoT": int
        }
    for filename in filenames:
        match = regex.match(filename)
        if match is None:
            print(regex)
            raise ValueError("bad statrobdme filename: {}".format(filename))
        info = match.groupdict()

        # convert fields
        for key in info:
            conversion = conversions[key]
            info[key] = conversion(info[key])
        if "g" not in info:
            info["g"] = 0

        # extract quantum numbers
        qn = (info["twoJ"]/2., info["g"], info["n"])
        qn_pair = (qn, qn)

        obdme_files[qn_pair] = filename

    # define-transition-densities 2Jf gf nf 2Ji gi fi robdme_info_filename robdme_filename
    # get filenames for static densities and extract quantum numbers
    filenames = glob.glob(os.path.join(work_dir, "mfdn.robdme.*"))
    regex = re.compile(
        r"{}".format(os.path.join(work_dir, "")) +
        # prolog
        r"mfdn\.robdme"
        # final sequence number
        r"\.seq(?P<seqf>\d{3})"
        # final 2J
        r"\.2J(?P<twoJf>\d{2})"
        # final parity (v14 only)
        r"(\.p(?P<gf>\d))?"
        # final n
        r"\.n(?P<nf>\d{2})"
        # final 2T
        r"\.2T(?P<twoTf>\d{2})"
        # initial sequence number
        r"\.seq(?P<seqi>\d{3})"
        # initial 2J
        r"\.2J(?P<twoJi>\d{2})"
        # initial parity (v14 only)
        r"(\.p(?P<gi>\d))?"
        # initial n
        r"\.n(?P<ni>\d{2})"
        # inital 2T
        r"\.2T(?P<twoTi>\d{2})"
        )
    conversions = {
        "seqf": int,
        "twoJf": int,
        "gf": lambda x: int(x) if x is not None else 0,
        "nf": int,
        "twoTf": int,
        "seqi": int,
        "twoJi": int,
        "gi": lambda x: int(x) if x is not None else 0,
        "ni": int,
        "twoTi": int
        }
    for filename in filenames:
        match = regex.match(filename)
        if match is None:
            raise ValueError("bad statrobdme filename format")
        info = match.groupdict()

        # convert fields
        for key in info:
            conversion = conversions[key]
            info[key] = conversion(info[key])

        if "gf" not in info:
            info["gf"] = 0
        if "gi" not in info:
            info["gi"] = 0

        # extract quantum numbers
        qn_bra = (info["twoJf"]/2., info["gf"], info["nf"])
        qn_ket = (info["twoJi"]/2., info["gi"], info["ni"])
        qn_pair = (qn_bra, qn_ket)

        obdme_files[qn_pair] = filename

    # sort by sequence number of final state, then sequence number of initial state
    for qn_pair,filename in obdme_files.items():
        ((J_bra, g_bra, n_bra), (J_ket, g_ket, n_ket)) = qn_pair
        lines.append(
            "define-densities {J_bra:4.1f} {g_bra:d} {n_bra:d}  {J_ket:4.1f} {g_ket:d} {n_ket:d} {filename:s} {info_filename:s}".format(
                J_bra=J_bra, g_bra=g_bra, n_bra=n_bra,
                J_ket=J_ket, g_ket=g_ket, n_ket=n_ket,
                filename=filename,
                info_filename=os.path.join(work_dir, "mfdn.rppobdme.info"),
            )
        )

    # ensure trailing line
    lines.append("")

    # write input file
    mcscript.utils.write_input(
        environ.obscalc_ob_filename(postfix),
        input_lines=lines,
        verbose=False
        )

    # invoke em-gen
    mcscript.call(
        [
            environ.shell_filename("obscalc-ob")
        ],
        input_lines=lines,
        mode=mcscript.CallMode.kSerial
    )

    # copy results out (if in multi-task run)
    print("Saving basic output files...")
    descriptor = task["metadata"]["descriptor"]
    filename_prefix = "{:s}-obscalc-{:s}{:s}".format(mcscript.parameters.run.name, descriptor, postfix)
    res_filename = "{:s}.res".format(filename_prefix)
    mcscript.task.save_results_single(
        task, environ.obscalc_ob_res_filename(postfix), res_filename, "res"
    )


def run_mfdn_transitions(task, postfix=""):
    """Generate input file and execute MFDn Transitions postprocessor.

        Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files

    Raises:
        mcscript.exception.ScriptError: if work directory not found
        mcscript.exception.ScriptError: if MFDn output not found
    """
    # convenience variables
    nuclide = task["nuclide"]
    interaction = task["interaction"]
    hw = task["hw"]
    Nmax = task["truncation_parameters"]["Nmax"]  # TODO(pjf): fix hard-coded Nmax
    xtransitions_executable = environ.mfdn_postprocessor_filename(
        task.get("mfdn-transitions_executable", "xtransitions")
    )

    # TODO(pjf): wf must be in work directory
    work_dir = "work{:s}".format(postfix)
    if not os.path.isdir(work_dir):
        raise mcscript.exception.ScriptError(
            "work directory {:s} not found".format(work_dir)
        )

    # TODO(pjf): generalize to arbitary wf directories
    if not os.path.exists(os.path.join(work_dir, "mfdn_smwf.info")):
        partitioning_filename = os.path.join(work_dir, "mfdn_partitioning.info")
        if not os.path.exists(partitioning_filename):
            print("using mfdn_partitioning.generated")
            partitioning_filename = os.path.join(work_dir, "mfdn_partitioning.generated")
        mfdn_v15.generate_smwf_info(
            task,
            environ.orbitals_filename(postfix),
            partitioning_filename,
            os.path.join(work_dir, "mfdn.res"),
            os.path.join(work_dir, "mfdn_smwf.info")
        )

    operator_qn_set = set()
    if task.get("tb_observables"):
        for (basename, qn, operator) in task["tb_observables"]:
            operator_qn_set.add(qn)
    operator_qn_set.discard((0,0,0))

    for operator_qn in sorted(operator_qn_set):
        for (bra_qn, ket_qn_list) in task["tb_transitions"]:
            # transition_data namelist dictionary
            transition_data = collections.OrderedDict()

            if (task["basis_mode"] in {modes.BasisMode.kDirect, modes.BasisMode.kDilated}):
                transition_data["hbomeg"] = float(hw)

            # TODO(pjf): tb transitions only
            transition_data["obdme"] = False

            # TODO(pjf): hard-coded wf location
            transition_data["infofilename_bra"] = "mfdn_smwf.info"
            transition_data["smwffilename_bra"] = "mfdn_smwf"
            transition_data["basisfilename_bra"] = "mfdn_MBgroups"
            transition_data["infofilename_ket"] = "mfdn_smwf.info"
            transition_data["smwffilename_ket"] = "mfdn_smwf"
            transition_data["basisfilename_ket"] = "mfdn_MBgroups"

            # operator TBMEs with given quantum numbers
            targets = tbme.get_tbme_targets(task, operator_qn)
            transition_data["TBMEoperators"] = [basename for (basename, operator) in targets.items()]
            transition_data["numTBtrans"] = len(transition_data["TBMEoperators"])

            if transition_data["numTBtrans"] > 8:
                raise mcscript.exception.ScriptError(
                    "too many two-body transitions: {:d}".format(transition_data["numTBtrans"])
                )

            # state information
            (J0, g0, Tz0) = operator_qn
            (bra_J, bra_g, bra_n) = bra_qn
            transition_data["TwoJ_bra"] = int(2*bra_J)
            transition_data["n_bra"] = int(bra_n)

            transition_data["TwoJ_ket"] = []
            transition_data["n_ket"] = []
            for (ket_J, ket_g, ket_n) in ket_qn_list:
                if (abs(ket_J-J0) > bra_J) or (ket_J+J0 < bra_J):
                    # skip due to triangularity
                    continue
                if (ket_g+g0+bra_g)%2 != 0:
                    # skip due to parity
                    continue
                transition_data["TwoJ_ket"] += [int(2*ket_J)]
                transition_data["n_ket"] += [ket_n]

            mcscript.utils.write_namelist(
                os.path.join(work_dir, "transitions.input"),
                input_dict={"transition_data": transition_data}
            )

            # enter work directory
            os.chdir(work_dir)

            # invoke MFDn transitions
            mcscript.call(
                [xtransitions_executable],
                mode=mcscript.CallMode.kHybrid
            )

            # leave work directory
            os.chdir("..")

            # save output
            transitions_output_dir = "transitions-output"
            mcscript.utils.mkdir(transitions_output_dir, exist_ok=True)
            filename_template = (
                "transitions.Z{Z:d}-N{N:d}-{interaction:s}-hw{hw:06.3f}-Nmax{Nmax:02d}-"
                "Jop{J0:03.1f}-gop{g0:d}-Tzop{Tz0:1d}-"
                "Jf{Jf:03.1f}-gf{gf:d}-nf{nf:02d}.{ext:s}"
                )
            out_filename = filename_template.format(
                Z=nuclide[0], N=nuclide[1], interaction=interaction,
                hw=hw, Nmax=Nmax,
                J0=J0, g0=g0, Tz0=Tz0,
                Jf=bra_J, gf=bra_g, nf=bra_n,
                ext="out"
            )
            mcscript.call([
                "cp", "--verbose",
                os.path.join(work_dir, "transitions.out"),
                os.path.join(transitions_output_dir, out_filename)
            ])
            res_filename = filename_template.format(
                Z=nuclide[0], N=nuclide[1], interaction=interaction,
                hw=hw, Nmax=Nmax,
                J0=J0, g0=g0, Tz0=Tz0,
                Jf=bra_J, gf=bra_g, nf=bra_n,
                ext="res"
            )
            mcscript.call([
                "cp", "--verbose",
                os.path.join(work_dir, "transitions.res"),
                os.path.join(transitions_output_dir, res_filename)
            ])

            # copy results out
            mcscript.task.save_results_single(
                task, os.path.join(work_dir, "transitions.res"), res_filename, "res"
            )
