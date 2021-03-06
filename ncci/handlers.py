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
- 07/14/19 (mac): Update archive_handler_mfdn() to use archive_handler_subarchives()
"""
import os
import glob
import mcscript

from . import (
    modes,
    radial,
    tbme,
    utils,
    mfdn_v14,
)

# set default MFDn driver
default_mfdn_driver = mfdn_v14

################################################################
# counting-only run
################################################################

def task_handler_dimension(task, postfix=""):
    """Task handler for dimension counting-only run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver
    radial.set_up_orbitals(task, postfix=postfix)
    mfdn_driver.run_mfdn(
        task, run_mode=modes.MFDnRunMode.kDimension, postfix=postfix)


def task_handler_nonzeros(task, postfix=""):
    """Task handler for nonzero counting-only run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver
    radial.set_up_orbitals(task, postfix=postfix)
    mfdn_driver.run_mfdn(
        task, run_mode=modes.MFDnRunMode.kNonzeros, postfix=postfix)


################################################################
# generic cleanup and archive steps
################################################################

def task_handler_post_run(task, postfix="", cleanup=True):
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

    # save OBDME files for next natural orbital iteration
    if task.get("natural_orbitals"):
        mfdn_driver.extract_natural_orbitals(task, postfix)

    mfdn_driver.save_mfdn_task_data(task, postfix=postfix)
    if task.get("save_wavefunctions"):
        mfdn_driver.save_mfdn_wavefunctions(task, postfix)
    if (cleanup):
        mfdn_driver.cleanup_mfdn_workdir(task, postfix=postfix)

def task_handler_post_run_no_cleanup(task,postfix=""):
    """ Task handler for serial components after MFDn run (no cleanup).

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """
    task_handler_post_run(task,postfix=postfix,cleanup=False)

################################################################
# basic oscillator run
################################################################

def task_handler_oscillator_pre(task, postfix=""):
    """Task handler for serial components before MFDn phase of basic oscillator run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    radial.set_up_interaction_orbitals(task, postfix=postfix)
    radial.set_up_orbitals(task, postfix=postfix)
    radial.set_up_radial_analytic(task, postfix=postfix)
    tbme.generate_tbme(task, postfix=postfix)

def task_handler_oscillator_mfdn(task, postfix=""):
    """Task handler for MFDn phase of basic oscillator run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    # run MFDn
    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver
    mfdn_driver.run_mfdn(task, postfix=postfix)

def task_handler_oscillator(task, postfix=""):
    """Task handler for basic oscillator run.

    Arguments:
        task (dict): as described in module docstring
        postfix (string, optional): identifier to add to generated files
    """

    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver
    task_handler_oscillator_pre(task, postfix=postfix)
    mfdn_driver.run_mfdn(task, postfix=postfix)
    task_handler_post_run(task, postfix=postfix)


################################################################
# basic natural orbital run
################################################################

def task_handler_natorb_pre(task, source_postfix="", target_postfix=""):
    """Task handler for serial components before MFDn natural orbitals run.

    Precondition: This handler assumes a base run has already been
    carried out on the same task.

    Arguments:
        task (dict): as described in module docstring
    """
    # sanity checks
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals not enabled")

    natorb_base_state = task.get("natorb_base_state")
    if not isinstance(natorb_base_state, int):
        raise mcscript.exception.ScriptError(
            "invalid natorb_base_state: {}".format(natorb_base_state))

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


def task_handler_natorb_run(task, postfix):
    """Task handler for MFDn natural orbital run.

    Precondition: This handler assumes task_handler_natorb_pre() has been called.

    Arguments:
        task (dict): as described in module docstring
        postfix (string): identifier to add to generated files
    """
    # sanity checks
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals not enabled")

    natorb_base_state = task.get("natorb_base_state")
    if not isinstance(natorb_base_state, int):
        raise mcscript.exception.ScriptError(
            "invalid natorb_base_state: {}".format(natorb_base_state))

    mfdn_driver = task.get("mfdn_driver")
    if mfdn_driver is None:
        mfdn_driver = default_mfdn_driver

    # set correct basis mode
    task["basis_mode"] = modes.BasisMode.kGeneric
    mfdn_driver.run_mfdn(task=task, postfix=postfix)


def task_handler_natorb(task):
    """Task handler for basic oscillator+natural orbital run.

    Arguments:
        task (dict): as described in module docstring
    """
    # sanity checks
    if not task.get("natural_orbitals"):
        raise mcscript.exception.ScriptError("natural orbitals not enabled")

    natorb_base_state = task.get("natorb_base_state")
    if not isinstance(natorb_base_state, int):
        raise mcscript.exception.ScriptError(
            "invalid natorb_base_state: {}".format(natorb_base_state))

    # first do base oscillator run
    task_handler_oscillator(task, postfix=utils.natural_orbital_indicator(0))

    task_handler_natorb_pre(
        task,
        source_postfix=utils.natural_orbital_indicator(0),
        target_postfix=utils.natural_orbital_indicator(1)
        )
    task_handler_natorb_run(task=task, postfix=utils.natural_orbital_indicator(1))
    task_handler_post_run(
        task=task, postfix=utils.natural_orbital_indicator(1)
        )


################################################################
# mfdn archiving
################################################################

def archive_handler_mfdn():
    """Generate archives for MFDn results and MFDn wavefunctions."""

    archive_filename_list = mcscript.task.archive_handler_subarchives(
        [
            {"postfix" : "-out", "paths" : ["results/out"], "compress" : True, "include_metadata" : True},
            {"postfix" : "-res", "paths" : ["results/res"], "compress" : True},
            {"postfix" : "-task-data", "paths" : ["results/task-data"]},
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
        ]
    )
    return archive_filename_list

def archive_handler_mfdn_hsi():
    """Generate archives for MFDn and save to tape."""

    # generate archives
    archive_filename_list = archive_handler_mfdn()

    # save to tape
    mcscript.task.archive_handler_hsi(archive_filename_list)
