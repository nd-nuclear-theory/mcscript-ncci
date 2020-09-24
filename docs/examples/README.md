runmfdn07: harmonic oscillator direct run with MFDn v15

    4He Nmax02 hw20 (direct)

    Interaction: example-data

    Usage: qsubm --here mfdn07

    We use tb-6 from example-data. Make sure to set NCCI_DATA_DIR_H2 to include
    `mcscript-ncci/docs/examples`.

runmfdn08: harmonic oscillator direct run with MFDn v15 b01

    4He Nmax02 hw20 (direct)

    Interaction: run0164-JISP16-tb-10

    Usage: qsubm --here mfdn08

    We use tb-10 as the smallest available set of files.

runmfdn09: general truncation direct run with MFDn v15

    4He weight=n+l<2.1 hw20 (direct)

    Interaction: run0164-JISP16-tb-10

    Usage: qsubm --here mfdn09

    We use tb-10 as the smallest available set of files.

runmfdn10: counting-only run with MFDn v15

    6He Nmax08 (counting)

    Usage: qsubm --here mfdn10

runmfdn11: manual orbital direct run with MFDn v15

    4He manual orbital file hw20 (direct)

    Interaction: run0164-JISP16-tb-10

    Usage: qsubm --here mfdn11

    We use tb-10 as the smallest available set of files.

runmfdn12: harmonic oscillator direct run with MFDn v15, plus custom input TBO

    4He Nmax02 hw20 (direct)

    Interaction: example-data

    Usage: qsubm --here mfdn12

    Uses operator TBMEs from example-data.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples`.

runmfdn13: harmonic oscillator direct run with MFDn v15, for use with postprocessor

    6Li Nmax02,Nmax04 hw15,hw20 (direct)

    Interaction: example-data

    Usage: qsubm --here --pool=ALL mfdn13

    Sets up for runtransitions00.

    Uses operator TBMEs from example-data.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples`.

    Make sure to set the task dictionary parameter "mfdn-transitions" to point
    to the mfdn executable file.

runtransitions00: mfdn-transitions postprocessor run

    6Li Nmax02,Nmax04, hw15,hw20

    Interaction/operator: example-data

    Usage: qsubm --here --pool=ALL transitions00

    Uses operator TBMEs from example-data.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples`.

    Uses wave functions created by runmfdn13.  Make sure to set
    NCCI_LIBRARY_PATH to include `mcscript-ncci/docs/examples`.

    Make sure to set the task dictionary parameter "mfdn-transitions_executable"
    to point to the mfdn-transitions executable file.
