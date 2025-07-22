Switching to "postprocessor-like" wf selection parameters for decomposition

07/21/25 (mac)

----------------

Let us walk through the changes to the decomposition task parameters, taking
`runmfdndecomp02.py` as our example.

It used to be that you would have to specify great gobs of information about the
original diagonalization run, like the `a_cm` and `max_iterations` for that run,
so that the full descriptor for the source wave functions could be
reconstructed:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-         "wf_source_info": {
-             "run": wf_run_dir,
-             "nuclide": nuclide,
-             "interaction": interaction,
-             "use_coulomb": coulomb,
-             "hw": hw,
-             "truncation_parameters": {
-                 "M": wf_source_M(qn),
-                 "Nmax": Nmax
-             },
-             "a_cm": a_cm,
-             "max_iterations": max_iterations,
-             "tolerance": tolerance,
-             "descriptor": ncci.descriptors.task_descriptor_7,
-             # required modes to keep task descriptor function happy
-             "basis_mode": ncci.modes.BasisMode.kDirect,
-             "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
-             "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
-         },
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

That is no longer needed.  Now, like in the postprocessor scripting, you just
specify a set of runs to search, and then parameter values to filter by:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
+         "wf_source_run_list": ["mfdn13"],
+         "wf_source_selector": {
+             "nuclide": nuclide,
+             "interaction": interaction,
+             "hw": hw,
+             "Nmax": Nmax,
+             "M": wf_source_M(qn),
+             },
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(But worry not.  The `wf_source_info` dictionary is still supported as a legacy
parameter for your existing run scripts.)

This information about a_cm, etc., as also needed in the task dictionary, since
it was required by the task descriptor.  But it is not needed in the descriptor,
either, just like we don't include it in the descriptor in postprocessor runs.
So the task dictionary can be a bit neater:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-         "a_cm": 40.,
-         "hw_cm": None,
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remember to switch the descriptor function you use:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-     task_descriptor=ncci.descriptors.task_descriptor_decomposition_2,
+     task_descriptor=ncci.descriptors.task_descriptor_7_decomposition,
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The task dictionary can be streamlined even more, since the decomposition
handlers now provide sensible defaults for decomposition runs (e.g, of course
you want `tolerance` to be set to `0`):

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # diagonalization parameters
-        "diagonalization": True,
         "max_iterations": decomposition_max_iterations,
-        "tolerance": 0,  # iterate to max iterations
         "partition_filename": None,
 
-        # obdme parameters
-        "calculate_obdme": False,
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Incidentally, it seemed confusing having one parameter named `source_wf_qn`, and
a bunch of other starting instead with `wf_source_`.  So `source_wf_qn` is now
deprecated in favor of `decomposition_qn`:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-        "source_wf_qn": qn,
+        "decomposition_qn": qn,
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(But worry not.  The old, deprecated name is still supported as a legacy
parameter for your existing run scripts.)

See also `task-dictionary-guide.md`, as usual, for a summary of parameters.
