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
- 08/14/20 (pjf): Implement generation of weak interaction one-body observables.
- 08/24/20 (pjf):
    + Implement one- and two-body postprocessing.
    + Remove old postprocessing scripting.
- 08/26/20 (pjf): Fix formatting of one-body electric transition operator names.
"""
import collections
import glob
import hashlib
import itertools
import os
import re
import sqlite3

import mcscript
import mfdnres
import am

from . import (
    environ,
    library,
    mfdn_v15,
    modes,
    tbme,
    utils,
    )


def generate_electroweak(task, postfix=""):
    """Generate electroweak matrix elements.

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
    for isospin_type in ["t+", "t-"]:
        lines.append("define-isospin-source {type:s} {filename:s}".format(
            type=isospin_type, filename=environ.obme_filename(postfix, isospin_type)
        ))

    radial_power_set = set()
    target_lines = []
    for (operator, operator_qn) in task.get("ob_observables", []):
        (j0,g0,tz0) = operator_qn
        if isinstance(operator, (tuple, list)):
            operator_type, order = operator
            if order != j0:
                raise ValueError("invalid J0={} for operator {}".format(j0, operator))
        else:
            operator_type = operator

        if operator_type == 'E':
            radial_power_set.add(order)
            for species in ["p", "n"]:
                target_lines.append(
                    "define-em-target E {order:d} {species:s} {output_filename:s}".format(
                        order=order, species=species,
                        output_filename=environ.observable_me_filename(postfix, operator_type, order, species)
                        )
                    )
        elif operator_type == 'M':
            radial_power_set.add(order-1)
            for species in ["p", "n"]:
                target_lines.append(
                    "define-em-target Dl {order:d} {species:s} {output_filename:s}".format(
                        order=order, species=species,
                        output_filename=environ.observable_me_filename(postfix, "Dl", order, species)
                        )
                    )
                target_lines.append(
                    "define-em-target Ds {order:d} {species:s} {output_filename:s}".format(
                        order=order, species=species,
                        output_filename=environ.observable_me_filename(postfix, "Ds", order, species)
                        )
                    )
        elif operator_type in {"F", "GT"}:
            target_lines.append(
                "define-weak-target {operator_type:s} {output_filename:s}".format(
                    operator_type=operator_type,
                    output_filename=environ.observable_me_filename(postfix, operator_type, "", "")
                    )
                )
        else:
            raise mcscript.exception.ScriptError("unknown one-body operator {}".format(operator))

    # load non-trivial solid harmonic RMEs
    for radial_power in sorted(radial_power_set):
        if radial_power != 0:
            operator_id = "rY{:d}".format(radial_power)
            lines.append("define-radial-source {type:s} {order:d} {filename:s}".format(
                type='r', order=radial_power,
                filename=environ.obme_filename(postfix, operator_id)
                ))

    # insert target lines after radial input lines
    lines += target_lines

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
            environ.shell_filename("ew-gen")
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
        "set-output-file {:s} append".format(environ.obscalc_ob_res_filename(postfix)),
        ]

    # set up operators
    for (operator, operator_qn) in task.get("ob_observables", []):
        (j0,g0,tz0) = operator_qn
        if isinstance(operator, (tuple, list)):
            operator_type, order = operator
            if order != j0:
                raise ValueError("invalid J0={} for operator {}".format(j0, operator))
        else:
            operator_type = operator

        if operator_type == "M":
            for species in ["p", "n"]:
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
        elif operator_type == "E":
            for species in ["p", "n"]:
                lines.append(
                    "define-operator {:s}{:d}({:s}) {:s}".format(
                        operator_type, order,
                        species,
                        environ.observable_me_filename(postfix, operator_type, order, species)
                        )
                    )
        else:
            lines.append(
                "define-operator {:s} {:s}".format(
                    operator_type,
                    environ.observable_me_filename(postfix, operator_type, "", "")
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
    filenames = glob.glob(os.path.join(work_dir, "*.robdme.*"))
    regex = re.compile(
        r"{}".format(os.path.join(work_dir, "")) +
        # prolog
        r"(?P<code>.+)\.robdme"
        # final sequence number (MFDn only)
        r"(\.seq(?P<seqf>\d+))?"
        # final 2J
        r"\.2J(?P<twoJf>\d+)"
        # final parity (v14/postprocessor only)
        r"(\.(p|g)(?P<gf>\d))?"
        # final n
        r"\.n(?P<nf>\d+)"
        # final 2T (MFDn only)
        r"(\.2T(?P<twoTf>\d+))?"
        # initial sequence number (MFDn only)
        r"(\.seq(?P<seqi>\d+))?"
        # initial 2J
        r"\.2J(?P<twoJi>\d+)"
        # initial parity (v14/postprocessor only)
        r"(\.(p|g)(?P<gi>\d))?"
        # initial n
        r"\.n(?P<ni>\d+)"
        # inital 2T (MFDn only)
        r"(\.2T(?P<twoTi>\d+))?"
        )
    conversions = {
        "code": str,
        "seqf": lambda x: int(x) if x is not None else 0,
        "twoJf": int,
        "gf": lambda x: int(x) if x is not None else 0,
        "nf": int,
        "twoTf": lambda x: int(x) if x is not None else 0,
        "seqi": lambda x: int(x) if x is not None else 0,
        "twoJi": int,
        "gi": lambda x: int(x) if x is not None else 0,
        "ni": int,
        "twoTi": lambda x: int(x) if x is not None else 0,
        }
    for filename in filenames:
        match = regex.match(filename)
        if match is None:
            raise ValueError("bad robdme filename: {}".format(filename))
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

        obdme_files[qn_pair] = (filename, info["code"])

    # sort by sequence number of final state, then sequence number of initial state
    for qn_pair,(filename,code) in obdme_files.items():
        ((J_bra, g_bra, n_bra), (J_ket, g_ket, n_ket)) = qn_pair
        if code == "mfdn":
            lines.append(
                "define-densities {J_bra:4.1f} {g_bra:d} {n_bra:d}  {J_ket:4.1f} {g_ket:d} {n_ket:d} {filename:s} {info_filename:s}".format(
                    J_bra=J_bra, g_bra=g_bra, n_bra=n_bra,
                    J_ket=J_ket, g_ket=g_ket, n_ket=n_ket,
                    filename=filename,
                    info_filename=os.path.join(work_dir, "mfdn.rppobdme.info"),
                )
            )
        elif code == "transitions":
            lines.append(
                "define-densities {J_bra:4.1f} {g_bra:d} {n_bra:d}  {J_ket:4.1f} {g_ket:d} {n_ket:d} {filename:s}".format(
                    J_bra=J_bra, g_bra=g_bra, n_bra=n_bra,
                    J_ket=J_ket, g_ket=g_ket, n_ket=n_ket,
                    filename=filename,
                )
            )
        else:
            raise mcscript.exception.ScriptError("unknown density code {}".format(info["code"]))

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


def allowed_by_multipolarity(qn_pair, Tz_pair, operator_qn):
    """Apply multipolarity selection to qn_pair.

    Arguments:
        qn_pair (tuple of tuple): (qnf,qni)
        Tz_pair (tuple of int): (Tzf,Tzi)
        operator (tuple of int): (J0, g0, Tz0)

    Returns:
        allowed (bool): whether or not qn pair satisfies multipolarity condition
    """

    # apply multipolarity configuration
    (bra_qn, ket_qn) = qn_pair
    (bra_J, bra_g, bra_n) = bra_qn
    (ket_J, ket_g, ket_n) = ket_qn
    (bra_Tz, ket_Tz) = Tz_pair
    (J0, g0, Tz0) = operator_qn
    allowed = True
    allowed = allowed and mfdnres.am.allowed_triangle(bra_J,J0,ket_J)
    allowed = allowed and (bra_g+ket_g+g0)%2 == 0
    allowed = allowed and (ket_Tz + Tz0) == bra_Tz

    return allowed


def allowed_by_masks(task,qn_pair):
    """Apply masking functions to qn_pair.

    Each mask function should have a declaration the form

        mask_function(task,mask_params,qn_pair,verbose=False)

    Task dictionary fields:
        "postprocessor_mask"
        "postprocessor_mask_verbose"

    Arguments:
        task (dict): task dictionary
        qn_pair (tuple of tuple): (qnf,qni)

    Returns:
        allowed (bool): whether or not qn pair satisfies masks
    """

    # extract mask configuration
    mask_list = task.get("postprocessor_mask", [])
    verbose = task.get("postprocessor_mask_verbose", False)

    # apply masks
    if verbose:
        print("Vetting {}".format(qn_pair))
    allowed = True
    for mask_function_params in mask_list:
        if not isinstance(mask_function_params, tuple):
            # wrap mask without parameters in tuple
            mask_function_params = (mask_function_params, {})
        (mask_function, mask_params) = mask_function_params
        mask_function_value = mask_function(task, mask_params, qn_pair, verbose=verbose)
        if verbose:
            print("  mask {}: {}".format(mask_function.__name__, mask_function_value))
        allowed &= mask_function_value
    if verbose:
        print("  Vetted {}: {}".format(qn_pair, allowed))

    return allowed


def get_run_descriptor_pair(bra_mesh_data, ket_mesh_data, qn_pair, operator_qn):
    """Get (run, descriptor) pair for a given set of state and operator quantum numbers.

    Arguments:
        bra_mesh_data (list of mfdnres.MFDnResultsData): results mesh for bra sources
        ket_mesh_data (list of mfdnres.MFDnResultsData): results mesh for ket sources
        qn_pair (tuple of tuples): (qnf,qni)
        operator_qn (tuple): (J0,g0,Tz0)

    Returns:
        (tuple of tuples): ((bra_run,bra_descriptor),(ket_run,ket_descriptor))
    """
    # convenience variables
    (bra_qn, ket_qn) = qn_pair
    (bra_J, bra_g, bra_n) = bra_qn
    (ket_J, ket_g, ket_n) = ket_qn
    (J0, g0, Tz0) = operator_qn
    bra_J = am.HalfInt(int(2*bra_J), 2)
    ket_J = am.HalfInt(int(2*ket_J), 2)

    bra_run_descriptor_pair = None
    ket_run_descriptor_pair = None
    for bra_mesh_point in bra_mesh_data:
        if bra_qn not in bra_mesh_point.levels:
            continue
        # extract convenience variables
        bra_M = am.HalfInt(int(2*bra_mesh_point.params["M"]),2)

        for ket_mesh_point in ket_mesh_data:
            if ket_qn not in ket_mesh_point.levels:
                continue
            ket_M = am.HalfInt(int(2*ket_mesh_point.params["M"]),2)

            # check for Clebsch zero
            cg_coefficient = am.ClebschGordan(
                bra_J, bra_M, J0, ket_M-bra_M, ket_J, ket_M
            )
            if abs(cg_coefficient) < 1e-6:
                continue

            # update runs and descriptors
            bra_run_descriptor_pair = (
                bra_mesh_point.params["run"],
                bra_mesh_point.params["descriptor"]
                )
            ket_run_descriptor_pair = (
                ket_mesh_point.params["run"],
                ket_mesh_point.params["descriptor"]
                )

    return (bra_run_descriptor_pair, ket_run_descriptor_pair)

def init_postprocessor_db(task):
    """Initialize sqlite3 database for postprocessor runs.

    Sets up database structure and populates it with operators, and (bra,ket)
    pairs for two-body observables.

    Arguments:
        task (dict): as described in module docstring

    Returns:
        db (sqlite3.Connection): database connection
    """

    # connect to database
    db = sqlite3.connect("transitions.sqlite")
    db.row_factory = sqlite3.Row

    # check if two-body transition table exists
    res = db.execute(
        """SELECT name FROM sqlite_master
        WHERE type='table' AND name='tb_transitions';"""
        )
    if len(res.fetchall()):
        return db

    # create tables
    db.execute("PRAGMA foreign_keys = ON;")
    db.execute(
        """CREATE TABLE bra_levels (
        bra_level_id INTEGER NOT NULL  PRIMARY KEY  UNIQUE,
        bra_J  REAL    NOT NULL,
        bra_g  INTEGER NOT NULL,
        bra_n  INTEGER NOT NULL
        );"""
    )
    db.execute(
        """CREATE TABLE ket_levels (
        ket_level_id INTEGER NOT NULL  PRIMARY KEY  UNIQUE,
        ket_J  REAL    NOT NULL,
        ket_g  INTEGER NOT NULL,
        ket_n  INTEGER NOT NULL
        );"""
    )
    db.execute(
        """CREATE TABLE tb_operators (
            operator_id  TEXT  NOT NULL  PRIMARY KEY  UNIQUE,
            J0  INTEGER NOT NULL,
            g0  INTEGER NOT NULL,
            Tz0 INTEGER NOT NULL
        );"""
    )
    db.execute(
        """CREATE TABLE ob_transitions (
            bra_run        TEXT NOT NULL,
            bra_descriptor TEXT NOT NULL,
            bra_level_id   INTEGER  NOT NULL
                REFERENCES bra_levels (bra_level_id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE,
            ket_run        TEXT NOT NULL,
            ket_descriptor TEXT NOT NULL,
            ket_level_id   INTEGER  NOT NULL
                REFERENCES ket_levels (ket_level_id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE,
            finished BOOL,
            CONSTRAINT uniq UNIQUE (
                bra_run, bra_descriptor, bra_level_id,
                ket_run, ket_descriptor, ket_level_id
                )
        );"""
    )
    db.execute(
        """CREATE TABLE tb_transitions (
            bra_run        TEXT NOT NULL,
            bra_descriptor TEXT NOT NULL,
            bra_level_id   INTEGER  NOT NULL
                REFERENCES bra_levels (bra_level_id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE,
            ket_run        TEXT NOT NULL,
            ket_descriptor TEXT NOT NULL,
            ket_level_id   INTEGER  NOT NULL
                REFERENCES ket_levels (ket_level_id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE,
            operator_id TEXT NOT NULL
                REFERENCES tb_operators (operator_id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE,
            rme NUMERIC,
            CONSTRAINT uniq UNIQUE (bra_level_id, ket_level_id, operator_id)
        );"""
    )
    db.commit()

    # populate operator information
    for (operator_name, operator_qn, _) in task.get("tb_observables", []):
        db.execute("INSERT INTO tb_operators VALUES (?,?,?,?)", (operator_name, *operator_qn))

    ################################################################
    # populate transitions table from slurped res files
    ################################################################
    SORT_KEY_DESCRIPTOR = (("lanczos", int), ("M", float))
    # slurp source wave function info
    wf_source_res_dir_list = []
    for run in task["wf_source_run_list"]:
        wf_source_res_dir_list += [library.get_res_directory(run)]
    wf_source_mesh_data = mfdnres.input.slurp_res_files(wf_source_res_dir_list, filename_format="mfdn_format_7_ho", verbose=True)

    # construct bra and ket info
    bra_selector = task["wf_source_bra_selector"]
    ket_selector = task["wf_source_ket_selector"]
    bra_mesh_data = mfdnres.analysis.selected_mesh_data(
            wf_source_mesh_data, bra_selector
        )
    bra_mesh_data = mfdnres.analysis.sorted_mesh_data(
            bra_mesh_data, SORT_KEY_DESCRIPTOR
        )
    bra_merged_data = mfdnres.analysis.merged_mesh(
            bra_mesh_data, bra_selector.keys()
        )
    assert len(bra_merged_data) == 1
    bra_merged_data = bra_merged_data[0]
    if bra_selector == ket_selector:
        # special case where bra and ket selection is equal:
        # allow canonicalization of transitions, and don't duplicate work
        canonicalize = True
        ket_mesh_data = bra_mesh_data[:]
        ket_merged_data = bra_merged_data
    else:
        canonicalize = False
        ket_mesh_data = mfdnres.analysis.selected_mesh_data(
            wf_source_mesh_data, ket_selector
            )
        ket_mesh_data = mfdnres.analysis.sorted_mesh_data(
            ket_mesh_data, SORT_KEY_DESCRIPTOR
            )
        ket_merged_data = mfdnres.analysis.merged_mesh(
            ket_mesh_data, ket_selector.keys()
            )
        assert len(ket_merged_data) == 1
        ket_merged_data = ket_merged_data[0]

    # populate level tables
    db.executemany(
        "INSERT INTO bra_levels (bra_J,bra_g,bra_n) VALUES (?,?,?)",
        bra_merged_data.levels
    )
    bra_id_list = db.execute(
        "SELECT bra_J,bra_g,bra_n,bra_level_id FROM bra_levels"
        )
    bra_id_dict = {(J,g,n): level_id for (J,g,n,level_id) in bra_id_list}

    db.executemany(
        "INSERT INTO ket_levels (ket_J,ket_g,ket_n) VALUES (?,?,?)",
        ket_merged_data.levels
    )
    ket_id_list = db.execute(
        "SELECT ket_J,ket_g,ket_n,ket_level_id FROM ket_levels"
        )
    ket_id_dict = {(J,g,n): level_id for (J,g,n,level_id) in ket_id_list}

    # # augment wf info as needed
    # for wf_source_info in wf_source_info_list:
    #     ncci.library.generate_smwf_info_in_library(wf_source_info)

    # extract Tz for bra and ket
    (bra_Z, bra_N) = bra_merged_data.params["nuclide"]
    bra_Tz = (bra_Z - bra_N)/2
    (ket_Z, ket_N) = ket_merged_data.params["nuclide"]
    ket_Tz = (ket_Z - ket_N)/2

    # construct list of (bra,ket,tbo) tuples
    bra_ket_tbo_product = itertools.product(
        bra_merged_data.levels, ket_merged_data.levels, task.get("tb_observables", [])
        )
    for (bra_qn, ket_qn, tb_operator) in bra_ket_tbo_product:
        (operator_name, operator_qn, _) = tb_operator

        # check canonical order
        if canonicalize and not (bra_qn <= ket_qn):
            continue

        # apply masks
        if not allowed_by_multipolarity((bra_qn,ket_qn), (bra_Tz,ket_Tz), operator_qn):
            continue
        if not allowed_by_masks(task, (bra_qn,ket_qn)):
            continue

        (bra_run_descriptor_pair, ket_run_descriptor_pair) = get_run_descriptor_pair(
            bra_mesh_data, ket_mesh_data, (bra_qn, ket_qn), operator_qn
            )
        if (bra_run_descriptor_pair is None) or (ket_run_descriptor_pair is None):
            continue
        db.execute(
            "INSERT INTO tb_transitions VALUES (?,?,?, ?,?,?, ?, NULL)",
            (*bra_run_descriptor_pair, bra_id_dict[bra_qn],
            *ket_run_descriptor_pair, ket_id_dict[ket_qn],
            operator_name)
            )
    db.commit()

    # construct list of (bra,ket,ob_qn) tuples
    ob_qn_set = {}
    bra_ket_ob_qn_product = itertools.product(
        bra_merged_data.levels, ket_merged_data.levels,
        {operator_qn for (operator,operator_qn) in task.get("ob_observables", [])}
    )
    for (bra_qn, ket_qn, operator_qn) in bra_ket_ob_qn_product:
        # check canonical order
        if canonicalize and not (bra_qn <= ket_qn):
            continue

        # apply masks
        if not allowed_by_multipolarity((bra_qn,ket_qn), (bra_Tz,ket_Tz), operator_qn):
            continue
        if not allowed_by_masks(task, (bra_qn,ket_qn)):
            continue

        (bra_run_descriptor_pair, ket_run_descriptor_pair) = get_run_descriptor_pair(
            bra_mesh_data, ket_mesh_data, (bra_qn, ket_qn), operator_qn
            )
        if (bra_run_descriptor_pair is None) or (ket_run_descriptor_pair is None):
            continue
        db.execute(
            "INSERT OR IGNORE INTO ob_transitions VALUES (?,?,?, ?,?,?, NULL)",
            (*bra_run_descriptor_pair, bra_id_dict[bra_qn],
            *ket_run_descriptor_pair, ket_id_dict[ket_qn])
            )
        db.commit()


    return db


def parse_two_body_observable(res, tokenized_lines):
    """
    """
    (J0,g0,Tz0,operator_id) = tokenized_lines[0]
    tb_observable_dict = res.setdefault("two_body_observables", {})
    transition_dict = tb_observable_dict.setdefault(operator_id,{})
    for tokenized_line in tokenized_lines[1:]:
        qnf = (float(tokenized_line[0]), int(tokenized_line[1]), int(tokenized_line[2]))
        qni = (float(tokenized_line[3]), int(tokenized_line[4]), int(tokenized_line[5]))
        rme = float(tokenized_line[6])
        transition_dict[(qnf,qni)] = rme


def parse_transitions_results(in_file, verbose=False):
    """Parse transitions results file.

    Arguments:
        in_file (stream): input file stream (already opened by caller)
        verbose (bool,optional): enable verbose output
    """
    section_handlers = {
        "Two-body observable": parse_two_body_observable,
    }

    # perform high-level parsing into sections
    res_file_lines = [row for row in in_file]
    tokenized_lines = mfdnres.tools.split_and_prune_lines(res_file_lines)
    sections = mfdnres.tools.extracted_sections(tokenized_lines)

    res = {}
    for (section_name,tokenized_lines) in sections:
        if section_name in section_handlers:
            section_handlers[section_name](res, tokenized_lines)

    return res


def run_postprocessor_two_body(task, one_body=False):
    """Evaluate matrix elements of two-body operators using mfdn-transitions.

    This handler calls initialize_postprocessor_db().

    Arguments:
        task (dict): as described in module docstring
        one_body (bool): calculate incidental one-body densities
    """
    # convenience variables
    descriptor = task["metadata"]["descriptor"]
    postfix = ""
    work_dir = "work{:s}".format(postfix)
    transitions_executable = environ.mfdn_postprocessor_filename(
        task.get("mfdn-transitions_executable", "xtransitions")
    )

    # create work directory if it doesn't exist yet
    mcscript.utils.mkdir(work_dir, exist_ok=True, parents=True)

    # make debugging output directories
    mcscript.utils.mkdir("transitions-output", exist_ok=True)

    # open database
    db = init_postprocessor_db(task)

    # get set of operator quantum numbers
    cursor = db.execute(
        """SELECT DISTINCT `J0`,`g0`,`Tz0`
        FROM `tb_operators` LEFT JOIN `tb_transitions` USING(`operator_id`)
        WHERE rme IS NULL;
        """
        )
    operator_qn_list = list(cursor)

    ################################################################
    # begin master loop for two-body operators
    ################################################################
    timer = mcscript.utils.TaskTimer(remaining_time=mcscript.parameters.run.get_remaining_time())
    while db.execute("SELECT * FROM `tb_transitions` WHERE rme is NULL;").fetchone():
        timer.start_timer()

        # go to work directory
        os.chdir(work_dir)

        # get operator quantum numbers
        operator_qn = db.execute(
            """SELECT `J0`,`g0`,`Tz0`
            FROM `tb_operators` INNER JOIN `tb_transitions` USING(`operator_id`)
            WHERE rme IS NULL
            ORDER BY J0 ASC, g0 ASC, Tz0 ASC
            LIMIT 1;
            """
        ).fetchone()

        # get bra wavefunction specifier
        (bra_run, bra_descriptor, bra_level_id, bra_J, bra_g, bra_n) = db.execute(
            """SELECT bra_run, bra_descriptor, bra_level_id, bra_J, bra_g, bra_n
            FROM tb_transitions
                INNER JOIN tb_operators USING(operator_id)
                INNER JOIN bra_levels USING(bra_level_id)
            WHERE rme IS NULL AND (J0,g0,Tz0) = (?,?,?)
            ORDER BY bra_run ASC, bra_descriptor ASC, bra_J ASC, bra_g ASC, bra_n ASC
            LIMIT 1;
            """,
            operator_qn
        ).fetchone()

        # get operators
        operator_id_list = [row['operator_id'] for row in db.execute(
            """SELECT DISTINCT operator_id
            FROM tb_operators
                INNER JOIN tb_transitions USING(operator_id)
            WHERE rme IS NULL AND (J0,g0,Tz0) = (?,?,?)
                AND (bra_run,bra_descriptor,bra_level_id) = (?,?,?)
            ORDER BY operator_id ASC
            LIMIT 8;
            """,
            (*operator_qn, bra_run, bra_descriptor, bra_level_id)
        ).fetchall()]

        # get ket source
        (ket_run, ket_descriptor) = db.execute(
            """SELECT ket_run, ket_descriptor
            FROM tb_transitions
            WHERE rme IS NULL
                AND (bra_run,bra_descriptor,bra_level_id) = (?,?,?)
                AND operator_id IN ({:s})
            ORDER BY ket_run ASC, ket_descriptor ASC
            LIMIT 1;
            """.format(','.join('?'*len(operator_id_list))),
            (bra_run, bra_descriptor, bra_level_id, *operator_id_list)
        ).fetchone()

        # get ket quantum numbers
        ket_qn_id_list = db.execute(
            """SELECT DISTINCT ket_J, ket_g, ket_n, ket_level_id
            FROM tb_transitions
                INNER JOIN ket_levels USING(ket_level_id)
            WHERE rme IS NULL
                AND (bra_run,bra_descriptor,bra_level_id) = (?,?,?)
                AND operator_id IN ({:s})
                AND (ket_run, ket_descriptor) = (?,?)
            ORDER BY ket_J ASC, ket_g ASC, ket_n ASC
            LIMIT 8;
            """.format(','.join('?'*len(operator_id_list))),
            (bra_run, bra_descriptor, bra_level_id, *operator_id_list, ket_run, ket_descriptor)
        ).fetchall()
        ket_qn_list = [(J,g,n) for (J,g,n,ket_id) in ket_qn_id_list]
        ket_id_list = [ket_id for (J,g,n,ket_id) in ket_qn_id_list]

        # locate wave functions
        bra_wf_prefix = library.get_wf_prefix(bra_run,bra_descriptor)
        ket_wf_prefix = library.get_wf_prefix(ket_run,ket_descriptor)

        # check if we can pick up some OBDMEs for free
        if one_body:
            (num_free_obdmes,) = db.execute(
                """SELECT COUNT(*) FROM ob_transitions
                WHERE finished IS NULL
                    AND (bra_run,bra_descriptor,bra_level_id) = (?,?,?)
                    AND (ket_run,ket_descriptor) = (?,?)
                    AND ket_level_id IN ({:s});
                """.format(','.join('?'*len(ket_id_list))),
                (bra_run, bra_descriptor, bra_level_id,
                ket_run, ket_descriptor, *ket_id_list)
            ).fetchone()
        else:
            num_free_obdmes = None

        # do calculation
        max_ket_J = max([ket_J for (ket_J,_,_) in ket_qn_list])
        min_ket_J = min([ket_J for (ket_J,_,_) in ket_qn_list])
        max_deltaJ = max(abs(max_ket_J-bra_J), max_ket_J+bra_J, abs(min_ket_J-bra_J), min_ket_J+bra_J)
        max_J0 = max([J0 for _,(J0,_,_) in task["ob_observables"]])
        max2K = 2*int(min(max_deltaJ, max_J0))
        transitions_inputlist = {
            "basisfilename_bra": "{:s}/mfdn_MBgroups".format(bra_wf_prefix),
            "smwffilename_bra": "{:s}/mfdn_smwf".format(bra_wf_prefix),
            "infofilename_bra": "{:s}/mfdn_smwf.info".format(bra_wf_prefix),
            "TwoJ_bra": int(2*bra_J),
            "n_bra": int(bra_n),

            "basisfilename_ket": "{:s}/mfdn_MBgroups".format(ket_wf_prefix),
            "smwffilename_ket": "{:s}/mfdn_smwf".format(ket_wf_prefix),
            "infofilename_ket": "{:s}/mfdn_smwf.info".format(ket_wf_prefix),
            "TwoJ_ket": [int(2*ket_J) for (ket_J,ket_g,ket_n) in ket_qn_list],
            "n_ket": [int(ket_n) for (ket_J,ket_g,ket_n) in ket_qn_list],

            "obdme": True if num_free_obdmes else False,
            "max2K": max2K,
            "numTBtrans": len(operator_id_list),
            "TBMEoperators": ["tbme-{}".format(basename) for basename in operator_id_list],
        }
        mcscript.utils.write_namelist(
            "transitions.input",
            input_dict={"transition_data": transitions_inputlist}
            )
        mcscript.call(["rm", "--force", "transitions.out", "transitions.res"])  # remove old output so file watchdog can work
        mcscript.call(
            [transitions_executable],
            mode=mcscript.CallMode.kHybrid,
            file_watchdog=mcscript.control.FileWatchdog("transitions.out"),
            file_watchdog_restarts=3
        )

        fp = open('transitions.res')
        res = parse_transitions_results(fp)
        fp.close()

        for (operator_id, transition_dict) in res["two_body_observables"].items():
            operator_id = operator_id.replace('tbme-','')
            for ((bra_qn,ket_qn), rme) in transition_dict.items():
                db.execute(
                    """UPDATE tb_transitions
                    SET rme = ?
                    WHERE (bra_level_id,ket_level_id,operator_id) =
                        (SELECT bra_level_id,ket_level_id,operator_id
                        FROM tb_transitions
                            INNER JOIN bra_levels USING(bra_level_id)
                            INNER JOIN ket_levels USING(ket_level_id)
                        WHERE (bra_J, bra_g, bra_n, ket_J, ket_g, ket_n, operator_id) =
                        (?,?,?,?,?,?,?)
                        )
                    LIMIT 1;
                    """,
                    (rme, *bra_qn, *ket_qn, operator_id)
                )
        db.commit()

        # mark free OBDMEs as finished
        if one_body:
            db.executemany("""
                UPDATE ob_transitions SET finished = 1
                WHERE (bra_run,bra_descriptor,bra_level_id) = (?,?,?)
                    AND (ket_run,ket_descriptor,ket_level_id) = (?,?,?)
                """,
                [(bra_run,bra_descriptor,bra_level_id,ket_run,ket_descriptor,ket_level_id) for ket_level_id in ket_id_list]
                )
            db.commit()

        # save output (for debugging)
        filename_template = "{:s}-transitions-{:s}{:s}-{:s}.{:s}"
        transitions_output_dir = os.path.join("..", "transitions-output")
        group_hash = hashlib.sha1(
            repr(
                ((bra_J,bra_g,bra_n), ket_qn_list, operator_id_list)
                ).encode()
            ).hexdigest()[:8]
        out_filename = os.path.join(
            transitions_output_dir,
            filename_template.format(
                mcscript.parameters.run.name, descriptor, postfix, group_hash, "out"
            )
        )
        mcscript.call(["cp", "--verbose", "transitions.out", out_filename])
        res_filename = os.path.join(
            transitions_output_dir,
            filename_template.format(
                mcscript.parameters.run.name, descriptor, postfix, group_hash, "res"
            )
        )
        mcscript.call(["cp", "--verbose", "transitions.res", res_filename])
        timer.stop_timer()

        # return to task directory
        os.chdir("..")

    # save out results
    postfix=""
    filename_prefix = "{:s}-transitions-{:s}{:s}".format(mcscript.parameters.run.name, descriptor, postfix)
    res_filename = "{:s}.res".format(filename_prefix)

    # get operators and loop
    cursor = db.execute(
        """SELECT J0, g0, Tz0, operator_id
        FROM tb_operators
        ORDER BY operator_id ASC;
        """
        )
    lines = []
    for (J0, g0, Tz0, operator_id) in cursor:
        lines += ["[Two-body observable]"]
        lines += ["# {:>3s} {:>3s} {:>3s}  {:s}".format("J0", "g0", "Tz0", "name")]
        lines += ["  {:>3d} {:>3d} {:>3d}  {:s}".format(J0, g0, Tz0, operator_id)]
        data = db.execute("""
            SELECT bra_J, bra_g, bra_n, ket_J, ket_g, ket_n, rme
            FROM tb_transitions
                INNER JOIN bra_levels USING(bra_level_id)
                INNER JOIN ket_levels USING(ket_level_id)
            WHERE operator_id = ?
            ORDER BY bra_J ASC, bra_g ASC, bra_n ASC,
                ket_J ASC, ket_g ASC, ket_n ASC;
            """,
            (operator_id,)
        )
        lines += ["# {:>4s} {:>3s} {:>3s}  {:>4s} {:>3s} {:>3s}  {:>15s}".format(
            "Jf", "gf", "nf", "Ji", "gi", "ni", "rme"
            )
        ]
        for row in data:
            lines += ["  {bra_J:>4.1f} {bra_g:>3d} {bra_n:>3d}  {ket_J:>4.1f} {ket_g:>3d} {ket_n:>3d}  {rme:15.8e}".format(**row)]
        lines += [""]
    mcscript.utils.write_input(res_filename, lines, verbose=False)


    # copy results out (if in multi-task run)
    if mcscript.task.results_dir is not None:
        res_dir = os.path.join(mcscript.task.results_dir, "res")
        mcscript.utils.mkdir(res_dir, exist_ok=True)
        mcscript.call(
            [
            "cp",
                "--verbose",
                res_filename,
                "--target-directory={}".format(res_dir)
            ]
        )

def run_postprocessor_one_body(task):
    """Evaluate one-body density matrix elements using the postprocessor.

    Arguments:
        task (dict): as described in module docstring
    """
    # convenience variables
    descriptor = task["metadata"]["descriptor"]
    postfix = ""
    work_dir = "work{:s}".format(postfix)
    transitions_executable = environ.mfdn_postprocessor_filename(
        task.get("mfdn-transitions_executable", "xtransitions")
    )

    # create work directory if it doesn't exist yet
    mcscript.utils.mkdir(work_dir, exist_ok=True, parents=True)

    # make debugging output directories
    mcscript.utils.mkdir("transitions-output", exist_ok=True)

    # open database
    db = init_postprocessor_db(task)

    ################################################################
    # begin master loop for one-body operators
    ################################################################
    timer = mcscript.utils.TaskTimer(remaining_time=mcscript.parameters.run.get_remaining_time())
    while db.execute("SELECT * FROM `ob_transitions` WHERE finished is NULL;").fetchone():
        timer.start_timer()

        # go to work directory
        os.chdir(work_dir)

        # get bra wavefunction specifier
        (bra_run, bra_descriptor, bra_level_id, bra_J, bra_g, bra_n) = db.execute(
            """SELECT bra_run, bra_descriptor, bra_level_id, bra_J, bra_g, bra_n
            FROM ob_transitions
                INNER JOIN bra_levels USING(bra_level_id)
            WHERE finished IS NULL
            ORDER BY bra_run ASC, bra_descriptor ASC, bra_J ASC, bra_g ASC, bra_n ASC
            LIMIT 1;
            """).fetchone()

        # get ket source
        (ket_run, ket_descriptor) = db.execute(
            """SELECT ket_run, ket_descriptor
            FROM ob_transitions
            WHERE finished IS NULL
                AND (bra_run,bra_descriptor,bra_level_id) = (?,?,?)
            ORDER BY ket_run ASC, ket_descriptor ASC
            LIMIT 1;
            """,
            (bra_run, bra_descriptor, bra_level_id)
        ).fetchone()

        # get ket quantum numbers
        ket_qn_id_list = db.execute(
            """SELECT DISTINCT ket_J, ket_g, ket_n, ket_level_id
            FROM ob_transitions
                INNER JOIN ket_levels USING(ket_level_id)
            WHERE finished IS NULL
                AND (bra_run,bra_descriptor,bra_level_id) = (?,?,?)
                AND (ket_run, ket_descriptor) = (?,?)
            ORDER BY ket_J ASC, ket_g ASC, ket_n ASC
            LIMIT 8;
            """,
            (bra_run, bra_descriptor, bra_level_id, ket_run, ket_descriptor)
        ).fetchall()
        ket_qn_list = [(J,g,n) for (J,g,n,ket_id) in ket_qn_id_list]
        ket_id_list = [ket_id for (J,g,n,ket_id) in ket_qn_id_list]

        # locate wave functions
        bra_wf_prefix = library.get_wf_prefix(bra_run,bra_descriptor)
        ket_wf_prefix = library.get_wf_prefix(ket_run,ket_descriptor)

        # do calculation
        max_ket_J = max([ket_J for (ket_J,_,_) in ket_qn_list])
        min_ket_J = min([ket_J for (ket_J,_,_) in ket_qn_list])
        max_deltaJ = max(abs(max_ket_J-bra_J), max_ket_J+bra_J, abs(min_ket_J-bra_J), min_ket_J+bra_J)
        max_J0 = max([J0 for _,(J0,_,_) in task["ob_observables"]])
        max2K = 2*int(min(max_deltaJ, max_J0))
        transitions_inputlist = {
            "basisfilename_bra": "{:s}/mfdn_MBgroups".format(bra_wf_prefix),
            "smwffilename_bra": "{:s}/mfdn_smwf".format(bra_wf_prefix),
            "infofilename_bra": "{:s}/mfdn_smwf.info".format(bra_wf_prefix),
            "TwoJ_bra": int(2*bra_J),
            "n_bra": int(bra_n),

            "basisfilename_ket": "{:s}/mfdn_MBgroups".format(ket_wf_prefix),
            "smwffilename_ket": "{:s}/mfdn_smwf".format(ket_wf_prefix),
            "infofilename_ket": "{:s}/mfdn_smwf.info".format(ket_wf_prefix),
            "TwoJ_ket": [int(2*ket_J) for (ket_J,ket_g,ket_n) in ket_qn_list],
            "n_ket": [int(ket_n) for (ket_J,ket_g,ket_n) in ket_qn_list],

            "obdme": True,
            "max2K": max2K
        }
        mcscript.utils.write_namelist(
            "transitions.input",
            input_dict={"transition_data": transitions_inputlist}
            )
        mcscript.call(["rm", "--force", "transitions.out", "transitions.res"])  # remove old output so file watchdog can work
        mcscript.call(
            [transitions_executable],
            mode=mcscript.CallMode.kHybrid,
            file_watchdog=mcscript.control.FileWatchdog("transitions.out"),
            file_watchdog_restarts=3
        )

        # mark OBDMEs as finished
        db.executemany("""
            UPDATE ob_transitions SET finished = 1
            WHERE (bra_run,bra_descriptor,bra_level_id) = (?,?,?)
                AND (ket_run,ket_descriptor,ket_level_id) = (?,?,?)
            """,
            [(bra_run,bra_descriptor,bra_level_id,ket_run,ket_descriptor,ket_level_id) for ket_level_id in ket_id_list]
            )
        db.commit()

        # save output (for debugging)
        filename_template = "{:s}-transitions-{:s}{:s}-{:s}.{:s}"
        transitions_output_dir = os.path.join("..", "transitions-output")
        group_hash = hashlib.sha1(
            repr(
                ((bra_J,bra_g,bra_n), ket_qn_list)
                ).encode()
            ).hexdigest()[8:16]
        out_filename = os.path.join(
            transitions_output_dir,
            filename_template.format(
                mcscript.parameters.run.name, descriptor, postfix, group_hash, "out"
            )
        )
        mcscript.call(["cp", "--verbose", "transitions.out", out_filename])
        res_filename = os.path.join(
            transitions_output_dir,
            filename_template.format(
                mcscript.parameters.run.name, descriptor, postfix, group_hash, "res"
            )
        )
        mcscript.call(["cp", "--verbose", "transitions.res", res_filename])
        timer.stop_timer()

        # return to task directory
        os.chdir("..")

    # # copy results out (if in multi-task run)
    # if mcscript.task.results_dir is not None:
    #     res_dir = os.path.join(mcscript.task.results_dir, "res")
    #     mcscript.utils.mkdir(res_dir, exist_ok=True)
    #     mcscript.call(
    #         [
    #         "cp",
    #             "--verbose",
    #             res_filename,
    #             "--target-directory={}".format(res_dir)
    #         ]
    #     )


def run_postprocessor(task):
    """Execute both phases of postprocessor.

    Arguments:
        task (dict): as described in module docstring
    """
    run_postprocessor_two_body(task, one_body=True)
    run_postprocessor_one_body(task)
    evaluate_ob_observables(task)
