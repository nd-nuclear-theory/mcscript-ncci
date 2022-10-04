"""library.py -- utilities for accessing run library

Mark A. Caprio
University of Notre Dame

- 02/04/20 (mac): Created, extracted from runs/mcaprio
    task_handler_postprocessor.py and xfer scripting.
- 06/18/20 (mac): Add extraction function for legacy archives.
- 08/14/20 (pjf):
    + Configure LIBRARY_BASE from environment variable NCCI_LIBRARY_BASE
    + Fix default arguments to path-getting functions.
    + Add get_res_directory() for use with mfdnres slurp.
    + Remove library alias hack.
- 09/02/20 (pjf):
    + Modify library functions to allow searching in multiple
      library base directories.
    + Make NCCI_LIBRARY_PATH a colon-delimited list.
- 09/07/20 (pjf): Fix hard-coded file format in get_res_data().
- 10/09/20 (mac): Fix hard-coded file format in get_res_data(), again.
- 10/16/20 (pjf): Add (pass-thru) verbose option to path utilities.
- 11/22/20 (pjf): Add get_obdme_prefix().
- 11/24/20 (pjf): Add retrieve_natorb_obdme().
- 02/17/21 (mac): Fix chown to act on whole run directory.
- 05/14/21 (mac): Provide task handler for HSI retrieval.
- 07/07/21 (mac): Add legacy mfdnv5b00/b01 wf support to hsi extraction handler.
- 07/13/21 (zz): Fix typos in generate_smwf_info_in_library().
- 07/15/21 (zz): Fix parts that make unnecessary error messages in generate_smwf_info_in_library().
- 07/25/21 (mac): Remove temporary generate_smwf_info_in_library_handler().
- 05/05/22 (mac): Provide keep_archives, keep_metadata, and keep_obdme flags for modern his archives.

"""

import glob
import os

import mcscript
import mfdnres

from . import (
    environ,
    mfdn_v15,
)

################################################################
# HSI run retrieval scripting -- legacy
################################################################

def recover_from_hsi_legacy(
        year,run,date,library_base,
        keep_archives=False,keep_metadata=False,keep_obdme=False,
):
    """Extract results subarchives from hsi for "legacy" archives (until 2018), before archives
    were broken down by results type.

    The archives should be <basename>.tgz for everything except wave functions
    and <basename>-wf.tar for wavefunctions.

    Args
        year (str): year code (for archive file hsi subdirectory)
        run (str): run name
        date (str): date code (for archive filename)
        library_base (str): path to library directory
        keep_archives (bool, optional): whether or not to save unextracted archives (useful in debugging this scripting)
        keep_metadata (bool, optional): whether or not to keep flags/batch/output directories (useful for diagnostics)
        keep_obdme (bool, optional): whether or not to retrieve/keep obdme results -- IGNORED for legacy archive

    """

    # set up general paths
    target_run_top_prefix = os.path.join(library_base,"run{run}".format(run=run))
    target_run_results_prefix = os.path.join(library_base,"run{run}".format(run=run),"results")

    # go to base directory for extraction
    mcscript.utils.mkdir(library_base,exist_ok=True,parents=True)
    os.chdir(library_base)

    print("Retrieving {}...".format((year,run,date)))

    # retrieve and expand results subarchives to run directory
    for archive_tail in [".tgz","-wf.tar"]:
            archive_filename = "run{run}-archive-{date}{archive_tail}".format(run=run,date=date,archive_tail=archive_tail)
            if (not os.path.isfile(archive_filename)):
                print("Retrieving {}...".format(archive_filename))
                hsi_command_string = "cd {year}; get {archive_filename}".format(year=year,archive_filename=archive_filename)
                mcscript.call(["hsi",hsi_command_string],check_return=False)
            if (os.path.isfile(archive_filename)):
                print("Extracting {}...".format(archive_filename))
                mcscript.call(["tar","xvf",archive_filename],check_return=False)
                if (not keep_archives):
                    mcscript.call(["rm",archive_filename],check_return=False)

    # eliminate metadata subdirectories if not desired
    if (not keep_metadata):
        for subdirectory in ["batch","flags","output"]:
            mcscript.call([
                "rm","-r",os.path.join(target_run_top_prefix,subdirectory)
            ],check_return=False)

    # break results files out by subdirectories
    mcscript.utils.mkdir(os.path.join(target_run_results_prefix,"out"),exist_ok=True,parents=True)
    for filename in glob.glob(os.path.join(target_run_results_prefix,"*.out")):
        mcscript.call([
            "mv","-v",filename,os.path.join(target_run_results_prefix,"out")
        ])
    mcscript.utils.mkdir(os.path.join(target_run_results_prefix,"res"),exist_ok=True,parents=True)
    for filename in glob.glob(os.path.join(target_run_results_prefix,"*.res")):
        mcscript.call([
            "mv","-v",filename,os.path.join(target_run_results_prefix,"res")
        ])
    mcscript.utils.mkdir(os.path.join(target_run_results_prefix,"task-data"),exist_ok=True,parents=True)
    for filename in glob.glob(os.path.join(target_run_results_prefix,"*.tgz")):
        mcscript.call([
            "mv","-v",filename,os.path.join(target_run_results_prefix,"task-data")
        ])

    # relocate old wave functions to results subdirectory
    mcscript.utils.mkdir(os.path.join(target_run_results_prefix,"wf"),exist_ok=True,parents=True)
    target_run_old_wavefunctions_prefix = os.path.join(library_base,"run{run}".format(run=run),"wavefunctions")
    for filename in glob.glob(os.path.join(target_run_old_wavefunctions_prefix,"*.tar")):
        mcscript.call([
            "mv","-v",filename,os.path.join(target_run_results_prefix,"wf")
        ])
    mcscript.call([
            "rmdir","-v",target_run_old_wavefunctions_prefix
    ])

    # extract individual task tarballs (legacy)
    os.chdir(os.path.join(target_run_results_prefix,"task-data"))
    for filename in glob.glob("*.tgz"):
        mcscript.call([
            "tar","xvf",filename,
            "--strip-components=1",
            "--exclude=mfdn*obdme*",
        ])
        mcscript.call(["rm","-v",filename])
    os.chdir(os.path.join(target_run_results_prefix,"wf"))
    for filename in glob.glob("*.tar"):
        mcscript.call([
            "tar","xvf",filename,
            "--strip-components=1",
            "--totals"
        ])
        mcscript.call(["rm","-v",filename])

    os.chdir(library_base)


################################################################
# HSI run retrieval scripting
################################################################

def recover_from_hsi(
        year,run,date,library_base,
        keep_archives=False,keep_metadata=False,keep_obdme=False,
):
    """Extract results subarchives from hsi.

    Limitation: This routine fails for legacy archives where the results
    directory was not broken down by results type, and thus neither was the
    archive.

    The archives should be <basename>-{res,task-data,wf}.<ext>, where <ext> can
    be any of {tar,tar.gz,.tgz}.  Automatic support is still provided for
    extracting individual task task-data tarballs (legacy).

    Args
        year (str): year code (for archive file hsi subdirectory)
        run (str): run name
        date (str): date code (for archive filename)
        library_base (str): path to library directory
        keep_archives (bool, optional): whether or not to save unextracted archives (useful in debugging this scripting)
        keep_metadata (bool, optional): whether or not to retrieve/keep flags/batch/output directories (useful for diagnostics)
        keep_obdme (bool, optional): whether or not to retrieve/keep obdme results

    """

    # go to base directory for extraction
    mcscript.utils.mkdir(library_base,exist_ok=True,parents=True)
    os.chdir(library_base)

    print("Retrieving {}...".format((year,run,date)))

    # determine archive types to retrieve
    archive_types = ["res","task-data","wf"]
    if (keep_metadata):
        archive_types.append("out")
    if (keep_obdme):
        archive_types.append("obdme")

    # retrieve results subarchives from hsi
    hsi_command_string = "cd {year}; get run{run}-archive-{date}-{{{archive_types_str}}}.t*".format(
        year=year,run=run,date=date,
        archive_types_str=",".join(archive_types)
    )
    mcscript.call(["hsi",hsi_command_string],check_return=False)

    # expand results subarchives to run directory
    for archive_type in archive_types:
        for extension in ["tgz","tar.gz","tar"]:
            archive_filename = "run{run}-archive-{date}-{archive_type}.{extension}".format(run=run,date=date,archive_type=archive_type,extension=extension)
            if os.path.isfile(archive_filename):
                print("Extracting {}...".format(archive_filename))
                mcscript.call(["tar","xvf",archive_filename],check_return=False)
                mcscript.call(["rm",archive_filename],check_return=False)

    # extract individual task tarballs (legacy)
    target_run_results_prefix = os.path.join(library_base,"run{run}".format(run=run),"results")
    os.chdir(os.path.join(target_run_results_prefix,"task-data"))
    for filename in glob.glob("*.tgz"):
        mcscript.call([
            "tar","xvf",filename,
            "--strip-components=1",
            "--exclude=mfdn*obdme*",
        ])
        if not keep_archives:
            mcscript.call(["rm","-v",filename])
    os.chdir(os.path.join(target_run_results_prefix,"wf"))
    for filename in glob.glob("*.tar"):
        mcscript.call([
            "tar","xvf",filename,
            "--strip-components=1",
            "--totals"
        ])
        if not keep_archives:
            mcscript.call(["rm","-v",filename])

    os.chdir(library_base)

################################################################
# HSI run retrieval task handler
################################################################

def hsi_retrieval_handler(task):
    """ Task handler for HSI run retrieval.

    Task dictionary:

        run (str): run name
        legacy (bool): if legacy format (pre-subarchives)
        year (str): year code (for archive file hsi subdirectory)
        date (str): date code (for archive filename)
        library_base (str): path to library directory
        keep_archives (bool, optional): whether or not to save unextracted archives (useful in debugging this scripting)
        keep_metadata (bool, optional): whether or not to retrieve/keep flags/batch/output directories (useful for diagnostics)
        keep_obdme (bool, optional): whether or not to retrieve/keep obdme results
        repo_str (str,optional): group name for file permissions

    Example:

      {
          "run": "mac0451", "legacy": False, "year": "2020", "date": "200501",
          "library_base": library_base, "repo_str": "m2032"
      }

    Arguments:
        task (dict): as described above
    """

    # extract run retrieval parameters from task dictionary
    run = task["run"]
    legacy = task["legacy"]
    year = task["year"]
    date = task["date"]
    library_base= task["library_base"]
    keep_archives = task.get("keep_archives",False)
    keep_metadata = task.get("keep_metadata",False)
    keep_obdme = task.get("keep_obdme",False)
    repo_str = task.get("repo_str",None)

    # construct paths
    target_run_top_prefix = os.path.join(library_base,"run{run}".format(run=run))
    target_run_results_prefix = os.path.join(target_run_top_prefix,"results")

    # call hsi extraction handler
    if task["legacy"]:
        # keep archives to facilitate resumption on error; keep metadata to facilitate rebundling into modern archive
        recover_from_hsi_legacy(
            year,run,date,library_base,
            keep_archives=True,keep_metadata=True,keep_obdme=False,
        )
    else:
        recover_from_hsi(
            year,run,date,library_base,
            keep_archives=keep_archives,keep_metadata=keep_metadata,keep_obdme=keep_obdme
        )

    # provide wf info files if needed (for mfdn v15b00/b01)
    generate_smwf_info_in_library(target_run_results_prefix)

    # make retrieved results available to group
    if repo_str is not None:
        mcscript.call([
            "chown","--recursive",":{}".format(repo_str),target_run_top_prefix
        ])
        mcscript.call([
            "chmod","--recursive","g+rX",target_run_top_prefix
        ])


def hsi_retrieval_task_descriptor(task):
    """ Provide task descriptor for HSI run retrieval.

    Also useful as task pool.
    """
    return task["run"]

################################################################
# library accessors
################################################################

LIBRARY_BASE = os.environ.get("NCCI_LIBRARY_PATH", "").split(":")

def get_res_directory(run, library_base=None, verbose=True):
    """Construct directory for MFDn res directory in library.

    Arguments:
        run (str): run identifier
        library_base (str,optional): root for library tree
        verbose (bool, optional): whether to print log messages

    Returns:
        res_directory (str): Filename
    """
    if library_base is None:
        library_base = LIBRARY_BASE
    res_directory = mcscript.utils.search_in_subdirectories(
        mcscript.utils.expand_path(library_base),
        "run{run:s}".format(run=run), "results", "res",
        verbose=verbose
    )
    return res_directory

def get_res_filename(run, descriptor, library_base=None, verbose=True):
    """ Construct filename for mfdn res file in library.

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        library_base (str,optional): root for library tree
        verbose (bool, optional): whether to print log messages

    Returns:
        res_filename (str): Filename
    """
    if library_base is None:
        library_base = LIBRARY_BASE
    res_filename = mcscript.utils.search_in_subdirectories(
        mcscript.utils.expand_path(library_base),
        "run{run:s}".format(run=run), "results", "res",
        "run{run:s}-mfdn15-{descriptor:s}.res".format(run=run, descriptor=descriptor),
        verbose=verbose
    )
    return res_filename

def get_res_data(run, descriptor, library_base=None, verbose=True):
    """Get results data object for given run and descriptor.

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        library_base (str,optional): root for library tree
        verbose (bool, optional): whether to print log messages

    Returns:
        res_data (MFDnResultsData): Data object
    """
    if library_base is None:
        library_base = LIBRARY_BASE

    import mfdnres
    res_filename = get_res_filename(run,descriptor,library_base=library_base,verbose=verbose)
    res_data = mfdnres.input.read_file(res_filename,filename_format="ALL")[0]
    return res_data

def get_obdme_prefix(run, descriptor, library_base=None, verbose=True):
    """ Construct prefix for obdme dir in library.

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        library_base (str,optional): root for library tree
        verbose (bool, optional): whether to print log messages

    Returns:
        task_data_prefix (str): Directory name
    """
    if library_base is None:
        library_base = LIBRARY_BASE
    obdme_prefix = mcscript.utils.search_in_subdirectories(
        mcscript.utils.expand_path(library_base),
        "run{run:s}".format(run=run), "results", "obdme", descriptor,
        verbose=verbose
    )
    return obdme_prefix

def get_task_data_prefix(run, descriptor, library_base=None, verbose=True):
    """ Construct prefix for task-data dir in library.

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        library_base (str,optional): root for library tree
        verbose (bool, optional): whether to print log messages

    Returns:
        task_data_prefix (str): Directory name
    """
    if library_base is None:
        library_base = LIBRARY_BASE
    task_data_prefix = mcscript.utils.search_in_subdirectories(
        mcscript.utils.expand_path(library_base),
        "run{run:s}".format(run=run), "results", "task-data", descriptor,
        verbose=verbose
    )
    return task_data_prefix

def get_wf_prefix(run, descriptor, library_base=None, verbose=True):
    """ Construct prefix for wf dir in library.

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        library_base (str,optional): root for library tree
        verbose (bool, optional): whether to print log messages

    Returns:
        wf_prefix (str): Directory name
    """
    if library_base is None:
        library_base = LIBRARY_BASE
    wf_prefix = mcscript.utils.search_in_subdirectories(
        mcscript.utils.expand_path(library_base),
        "run{run:s}".format(run=run), "results", "wf", descriptor,
        verbose=verbose
    )
    return wf_prefix

def retrieve_natorb_obdme(
    run, descriptor, qn, source_postfix="", target_postfix="",
    library_base=None, verbose=True
):
    """Retrieve natorb OBDMEs from library and place in current working directory.

    First checks res/task-data, then checks res/obdme.

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        qn (tuple): quantum numbers of natural orbital base state
        source_postfix (str, optional):
        library_base (str, optional): root for library tree
        verbose (bool, optional): whether to print log messages
    """
    natorb_obdme_filename = environ.natorb_obdme_filename(source_postfix)
    natorb_obdme_info_filename = environ.natorb_info_filename(source_postfix)

    # first check for extracted obdmes
    try:
        task_data_dir = get_task_data_prefix(
            run, descriptor+source_postfix, library_base, verbose=verbose
        )
    except mcscript.exception.ScriptError:
        # fail gracefully if obdmes not found in task-data
        print("INFO: task-data not found for run {} descriptor {}".format(run, descriptor+source_postfix))
    else:
        natorb_obdme_path = os.path.join(task_data_dir, natorb_obdme_filename)
        natorb_obdme_info_path = os.path.join(task_data_dir, natorb_obdme_info_filename)
        if os.path.exists(natorb_obdme_path) and os.path.exists(natorb_obdme_info_path):
            mcscript.call([
                "cp", "--verbose",
                natorb_obdme_path,
                natorb_obdme_filename
            ])

            mcscript.call([
                "cp", "--verbose",
                natorb_obdme_info_path,
                natorb_obdme_info_filename
            ])

            return

    # look in saved obdmes
    obdme_dir = get_obdme_prefix(run, descriptor+source_postfix, library_base, verbose)
    obdme_info_filename = glob.glob(os.path.join(obdme_dir, "mfdn.rppobdme.info"))
    (J, g, n) = qn
    obdme_filename = glob.glob(
        os.path.join(obdme_dir, "mfdn.statrobdme.seq*.2J{:02d}.n{:02d}.2T*".format(round(2*J), n))
        )
    if (len(obdme_filename) == 1) and (len(obdme_info_filename) == 1):
        mcscript.call([
            "cp", "--verbose",
            obdme_filename[0],
            natorb_obdme_filename
        ])

        mcscript.call([
            "cp", "--verbose",
            obdme_info_filename[0],
            natorb_obdme_info_filename
        ])

        return

    # should not get here
    raise mcscript.exception.ScriptError("unable to find natorb obdmes")


################################################################
# mfdnv5b00/b01 wf support
################################################################

def generate_smwf_info_in_library(results_prefix):
    """Generate missing smwf_info file in situ in library.

    This is for mfdnv15b00/b01 legacy runs.  The smwf_info file is generated
    from the results file (in res) and partitioning (in task_data).

    As byproduct, provides task-data/mfdn_partitioning.info, if not already available.

    Caution: The code for generating smwf_info files involves calls to compiled
    utilities from shell (orbital-gen).  If you are running on a front end
    machine (e.g., xfer queue at NERSC), make sure shell is compiled for the
    appropriate architecture (e.g., haswell), and that the appropriate module
    environment is loaded for that architecture.

    Arguments:
        results_prefix (str): Path to run results directory

    """

    # set up subdirectory paths
    res_prefix = os.path.join(results_prefix,"res")
    task_data_prefix = os.path.join(results_prefix,"task-data")
    wf_prefix = os.path.join(results_prefix,"wf")
    if (not os.path.isdir(res_prefix)):
        raise mcscript.exception.ScriptError("Missing res directory {}".format(task_data_prefix))
    if (not os.path.isdir(task_data_prefix)):
        raise mcscript.exception.ScriptError("Missing task_data directory {}".format(task_data_prefix))
    if (not os.path.isdir(wf_prefix)):
        raise mcscript.exception.ScriptError("Missing wf directory {}".format(wf_prefix))

    # slurp res files
    res_format = "mfdn_v15"  # this function is mfdn_v15 specific
    filename_format="mfdn_format_7_ho"  # probably all legacy runs used this filename format, but might need to override
    mesh_data = mfdnres.res.slurp_res_files(
        res_prefix,res_format,filename_format,glob_pattern="*-mfdn15-*.res",verbose=False
    )

    # iterate over tasks
    for results_data in mesh_data:

        # extract descriptor
        descriptor = results_data.params["descriptor"]

        # set up task-specific filenames
        res_filename = results_data.params["filename"]
        orbital_filename=os.path.join(task_data_prefix,descriptor,"orbitals.dat")
        partitioning_filename=os.path.join(task_data_prefix,descriptor,"mfdn_partitioning.info")
        info_filename = os.path.join(wf_prefix,descriptor,"mfdn_smwf.info")

        # short circuit if info file exists
        if (os.path.isfile(info_filename)):
            continue
        print("Creating smwf_info file for {}...".format(descriptor))

        # validate existence of subdirectory and file paths
        #
        # The subdirectory paths are redundant to the file paths, but flagging
        # missing subdirectories is helpful for providing more useful error
        # messages.
        if (not os.path.isfile(res_filename)):
            raise mcscript.exception.ScriptError("Missing res file {}".format(res_filename))  # twilight zone -- should exist by construction
        if (not os.path.isdir(os.path.join(task_data_prefix,descriptor))):
            print("WARN: Missing task_data subdirectory for present descriptor {}".format(os.path.join(task_data_prefix,descriptor)))
            continue
        if (not os.path.isdir(os.path.join(wf_prefix,descriptor))):
            print("WARN: Missing wf subdirectory for present descriptor {}".format(os.path.join(wf_prefix,descriptor)))
            continue
        if (not os.path.isfile(orbital_filename)):
            print("WARN: Missing orbital file {}".format(orbital_filename))
            continue

        # ensure partitioning file exists
        #
        # If no mfdn_partitioning.info was provided at run time, none will be in
        # archive.  Must provide it from mfdn_partitioning.generated.
        if not os.path.isfile(partitioning_filename):
            generated_partitioning_filename = os.path.join(task_data_prefix,descriptor,"mfdn_partitioning.generated")
            if (not os.path.isfile(generated_partitioning_filename)):
                print("Missing generated partition file {}".format(generated_partitioning_filename))
                continue
            mcscript.call([
                "cp", "--verbose",
                generated_partitioning_filename,
                partitioning_filename
            ])

        # populate task dictionary
        #
        # ncci.mfdn_v15.generate_smwf_info requires task data:
        #     "nuclide", "truncation_parameters":"M", "metadata":"descriptor"
        task = dict()
        task["nuclide"] = results_data.params["nuclide"]
        task["truncation_parameters"] = dict(M=results_data.params["M"])
        task["metadata"] = dict(descriptor=results_data.params["descriptor"])

        # generate wf info file
        mfdn_v15.generate_smwf_info(
            task=task,
            orbital_filename=orbital_filename,
            partitioning_filename=partitioning_filename,
            res_filename=res_filename,
            info_filename=info_filename
        )

