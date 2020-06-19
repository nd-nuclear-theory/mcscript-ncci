"""library.py -- utilities for accessing run library

Mark A. Caprio
University of Notre Dame

- 02/04/20 (mac): Created, extracted from runs/mcaprio
    task_handler_postprocessor.py and xfer scripting.
- 06/18/20 (mac): Add extraction function for legacy archives.

"""

import glob
import os

import mcscript

from . import (
    mfdn_v15,
)

################################################################
# HSI run retrieval scripting -- legacy
################################################################

def recover_from_hsi_legacy(year,run,date,target_base,keep_metadata=False):
    """Extract results subarchives from hsi for "legacy" archives (until 2018), before archives
    were broken down by results type.

    Args
        year (str): year code (for archive file hsi subdirectory)
        run (str): run name
        date (str): date code (for archive filename)
        target_base (str): path to library directory
        keep_metadata (bool, optional): whether or not to keep flags/batch/output directories
    """

    # go to base directory for extraction
    mcscript.utils.mkdir(target_base,exist_ok=True,parents=True)
    os.chdir(target_base)

    print("Retrieving {}...".format((year,run,date)))

    # retrieve results subarchives from hsi
    hsi_command_string = "cd {year}; get run{run}-archive-{date}{{.tgz,-wf.tar}}".format(year=year,run=run,date=date)
    mcscript.call(["hsi",hsi_command_string],check_return=False)

    # expand results subarchives to run directory
    for archive_tail in [".tgz","-wf.tar"]:
            archive_filename = "run{run}-archive-{date}{archive_tail}".format(run=run,date=date,archive_tail=archive_tail)
            print(archive_filename)
            if os.path.isfile(archive_filename):
                print("Extracting {}...".format(archive_filename))
                mcscript.call(["tar","xvf",archive_filename],check_return=False)
                mcscript.call(["rm",archive_filename],check_return=False)

    # eliminate metadata subdirectories if not desired
    if (not keep_metadata):
        target_run_top_prefix = os.path.join(target_base,"run{run}".format(run=run))
        for subdirectory in ["batch","flags","output"]:
            mcscript.call([
                "rm","-r",os.path.join(target_run_top_prefix,subdirectory)
            ],check_return=False)

    # break results files out by subdirectories
    target_run_results_prefix = os.path.join(target_base,"run{run}".format(run=run),"results")
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
    mcscript.utils.mkdir(os.path.join(target_run_wavefunctions_prefix,"wf"),exist_ok=True,parents=True)
    target_run_old_wavefunctions_prefix = os.path.join(target_base,"run{run}".format(run=run),"wavefunctions")
    for filename in glob.glob(os.path.join(target_run_old_wavefunctions_prefix,"*.tar")):
        mcscript.call([
            "mv","-v",filename,os.path.join(target_run_results_prefix,"wf")
        ])
    mcscript.call([
            "rmdir","-v",target_run_old_wavefunctions_prefix
    ])
        
    # extract individual task tarballs (legacy)
    target_run_results_prefix = os.path.join(target_base,"run{run}".format(run=run),"results")
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

    # make retrieved results available to group
    mcscript.call([
        "chown","--recursive",":m2032",target_run_results_prefix
    ])
    mcscript.call([
        "chmod","--recursive","g+rX",target_run_results_prefix
    ])
        
    os.chdir(target_base)

    
################################################################
# HSI run retrieval scripting
################################################################

def recover_from_hsi(year,run,date,target_base):
    """Extract results subarchives from hsi.

    Limitation: This routine fails for legacy archives where the results
    directory was not broken down by results type, and thus neither was the
    archive.

    Args
        year (str): year code (for archive file hsi subdirectory)
        run (str): run name
        date (str): date code (for archive filename)
        target_base (str): path to library directory

    """

    # go to base directory for extraction
    mcscript.utils.mkdir(target_base,exist_ok=True,parents=True)
    os.chdir(target_base)

    print("Retrieving {}...".format((year,run,date)))

    # retrieve results subarchives from hsi
    hsi_command_string = "cd {year}; get run{run}-archive-{date}-{{res,task-data,wf}}.t*".format(year=year,run=run,date=date)
    mcscript.call(["hsi",hsi_command_string],check_return=False)

    # expand results subarchives to run directory
    for archive_type in ["res","task-data","wf"]:
        for extension in ["tgz","tar.gz","tar"]:
            archive_filename = "run{run}-archive-{date}-{archive_type}.{extension}".format(run=run,date=date,archive_type=archive_type,extension=extension)
            if os.path.isfile(archive_filename):
                print("Extracting {}...".format(archive_filename))
                mcscript.call(["tar","xvf",archive_filename],check_return=False)
                mcscript.call(["rm",archive_filename],check_return=False)

    # extract individual task tarballs (legacy)
    target_run_results_prefix = os.path.join(target_base,"run{run}".format(run=run),"results")
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

    # make retrieved results available to group
    mcscript.call([
        "chown","--recursive",":m2032",target_run_results_prefix
    ])
    mcscript.call([
        "chmod","--recursive","g+rX",target_run_results_prefix
    ])
        
    os.chdir(target_base)

################################################################
# library accessors
################################################################

LIBRARY_BASE = mcscript.utils.expand_path("$SCRATCH/runs/library")
LIBRARY_BASE_ALIAS = "library"  # workaround for FORTRAN path length limit

def make_library_base_alias():
    """ Set up symlick alias for libary in cwd, as path length workaround (ugly!).

    Ex:
        ncci.library.make_library_base_alias()  # path length workaround for postprocessor
        bra_wf_prefix = ncci.library.get_wf_prefix(bra_run,bra_descriptor,library_base=ncci.library.LIBRARY_BASE_ALIAS)

    """
    
    if (not os.path.exists(LIBRARY_BASE_ALIAS)):
        mcscript.call(["ln", "-s", LIBRARY_BASE,LIBRARY_BASE_ALIAS])

def get_res_filename(run,descriptor,library_base=LIBRARY_BASE):
    """ Construct filename for mfdn res file in library.

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        library_base (str,optional): root for library tree

    Returns:
        res_filename (str): Filename
    """
    res_filename = mcscript.utils.expand_path(os.path.join(library_base,"run{run:s}/results/res/run{run:s}-mfdn15-{descriptor:s}.res").format(
        run=run,
        descriptor=descriptor
    ))
    return res_filename

def get_res_data(run,descriptor,library_base=LIBRARY_BASE):
    """ Construct pat

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        library_base (str,optional): root for library tree

    Returns:
        res_data (MFDnResultsData): Data object
    """

    import mfdnres
    res_filename = get_res_filename(run,descriptor,library_base=library_base)
    res_data = mfdnres.res.read_file(res_filename, "mfdn_v15")[0]
    return res_data

def get_task_data_prefix(run,descriptor,library_base=LIBRARY_BASE):
    """ Construct prefix for wf dir in library.

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        library_base (str,optional): root for library tree

    Returns:
        task_data_prefix (str): Directory name
    """
    task_data_prefix = mcscript.utils.expand_path(os.path.join(library_base,"run{run:s}/results/task-data/{descriptor:s}").format(
        run=run,
        descriptor=descriptor
    ))
    return task_data_prefix

def get_wf_prefix(run,descriptor,library_base=LIBRARY_BASE):
    """ Construct prefix for wf dir in library.

    Arguments:
        run (str): run identifier
        descriptor (str): task descriptor
        library_base (str,optional): root for library tree

    Returns:
        wf_prefix (str): Directory name
    """
    wf_prefix = mcscript.utils.expand_path(os.path.join(library_base,"run{run:s}/results/wf/{descriptor:s}").format(
        run=run,
        descriptor=descriptor
    ))
    return wf_prefix

################################################################
# mfdnv5b00/b01 wf support
################################################################

def generate_smwf_info_in_library(wf_source_info):
    """Generate missing swmf_info file in situ in library.

    This is for mfdnv15b00/b01 legacy runs.  The swmf_info file is generated
    from the results file (in res) and partitioning (in task_data).


    Arguments:
        wf_source_info (dict): task-like dictionary with wf source task info

    """

    # set up paths
    run = wf_source_info["run"]
    descriptor = wf_source_info["metadata"]["descriptor"]
    
    res_filename = get_res_filename(run,descriptor)
    task_data_prefix = get_task_data_prefix(run,descriptor)
    wf_prefix = get_wf_prefix(run,descriptor)
    if (not os.path.isfile(res_filename)):
        raise mcscript.exception.ScriptError("Missing res file {}".format(res_filename))
    if (not os.path.isdir(task_data_prefix)):
        raise mcscript.exception.ScriptError("Missing task_data directory {}".format(task_data_prefix))
    if (not os.path.isdir(wf_prefix)):
        raise mcscript.exception.ScriptError("Missing wf directory {}".format(wf_prefix))
    
    # short circuit if info file exists
    if (os.path.isfile(os.path.join(wf_prefix,"mfdn_smwf.info"))):
        return

    # ensure partitioning file exists
    #
    # If no mfdn_partitioning.info was provided at run time, none will be in
    # archive.  Must provide it from mfdn_partitioning.generated.
    if not os.path.isfile(os.path.join(task_data_prefix,"mfdn_partitioning.info")):
        mcscript.call([
            "cp", "--verbose",
            os.path.join(task_data_prefix,"mfdn_partitioning.generated"),
            os.path.join(task_data_prefix,"mfdn_partitioning.info")
        ])
    
    # generate wf info file
    #
    # ncci.mfdn_v15.generate_smwf_info requires task data:
    #     "nuclide", "truncation_parameters":"M", "metadata":"descriptor"
    ncci.mfdn_v15.generate_smwf_info(
        wf_source_info,
        orbital_filename=os.path.join(task_data_prefix,"orbitals.dat"),
        partitioning_filename=os.path.join(task_data_prefix,"mfdn_partitioning.info"),
        res_filename=res_filename,
        info_filename=os.path.join(wf_prefix,"mfdn_smwf.info")
    )
