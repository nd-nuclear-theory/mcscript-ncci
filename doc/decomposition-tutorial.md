# Decomposition tutorial #

03/26/25-03/27/25 (mac): Write as live tutorial (with pg, hh, slv).

04/07/25 (mac): Add note on number of iterations.

----------------------------------------------------------------

## 1. Background

Our purpose here is to illustrate how to decompose a wave function with respect
to the eigenspaces of some Hermitian operator, via the Lanczos trick, as
described in Ref. [johnson2015:spin-orbit].  The end result, after proper
binning, is the "probabilities" (norm contribution) lying within each
eigenspace.  One can thus decompose with respect to group symmetry subspaces, if
one decomposes into the eigenspaces of the Casimir operator of a group
[gueorguiev2000:fp-su3-breaking, zbikowski2021:beyond-elliott].  By taking
appropriate linear combinations of mutually commuting Hermitian operators, one
can *simultaneously* decompose into the eigenspaces of these operators.  This is
useful for decomposing into the symmetry subspaces of complementary groups,
e.g., an LS decomposition is simultanous decomposition with respect to SO(3) for
orbital angular momentum and SU(2) for spin, or, we can simultaneoulsy decompose
with respect to U(3) and spin [caprio2022:10be-shape-sdanca21].

But let us start simple.  Let us do a decomposition of an NCCI eigenfunction
with respect to the number of oscilator quanta.  The total number of oscillator
quanta is measured by the one-body operator, where here we use the notation of
Ref. [caprio2020:intrinsic],

   Ntot = U[N]
     = sum_i N_i
     
Here N=2*n+l for a single particle harmonic oscillator eigenfunction, but it can
be represented in terms of coordinate and momentum operators for the single
particle as usual for the harmonic oscillator in Dirac's formulation (and
summarized again in Ref. [caprio2020:intrinsic]). This is equivalent, to within
a constant shift in eigenvalue, to decomposing with respect to

   Nex = Ntot - N0

which is the number of "excitations" relative to the lowest oscillator filling
N0.  That is, in shell model parlance, we are decomposing the many-body wave
function into (Nex)hw contribution, e.g., 0hw, 2hw, 4hw.  The corresponding
operator is

   Nex = U[N] - N0 * I
       
where I is the identity operator on the many-body space.

For our example, we will take an Nmax=4 wave function for 6Li, generated in the
example run `runmfdn13`.  So there will be three subspaces:

   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   Nex    Ntot
   0      2
   2      4
   4      6
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
Now, this decomposition is in some sense "trivial", assuming we are doing the
NCCI calculations in an oscillator basis.  The basis states are eigenstates of
Ntot (or Nex), so we can get this decomposition "natively" from an oscillator
basis wave function, no Lanczos decomposition needed.  That is, we can just sum
up squared amplitudes for basis states of each Nex.  In fact, let us look in the
results file:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    runmfdn13-mfdn15-Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06.res
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We see this decomposition is included in the results output from MFDn as the
`[Oscillator quanta]`:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ...
    
    [Energies]
    # Seq       J    n      T        Eabs        Eexc        Error    J-full
        1      1.0   1   0.000      -29.500      0.000     0.19E-04    1.0000

    ...
    
    [Oscillator quanta]
    # Seq    J    n      T      Amp(N)^2 
        1   1.0   1   0.000      0.8212      0.1204      0.5835E-01
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tells us the decomposition is

   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   Nex    Ntot   P
   0      2      0.8212
   2      4      0.1204
   4      6      0.5835E-01
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

But now, let's see how we would get this by the Lanczos trick.  Note that the
Lanczos trick could still be used here even if we were not working in an
oscillator basis.
   
Decomposition with respect to Nex is actually explicitly supported as a
predefined "decomposition type" in our decomposition scripting in
`mcscript.ncci.decomposition`.  However, for greater transparency, let's set
this up "from scratch", without using the predefined decomposition types.

## 2. A basic decomposition: With respect to Ntot

There is an interesting question here.  Which operator would it be better to
provide as the Hermitian operator for the Lanczos process: Nex or Ntot?  Or are
both equally good?  In principle, Nex and Ntot are equivalent, the eigenvalues
are just shifted.  In fact, the predefined Nex decomposition in
`mcscript.ncci.decomposition` uses Nex.  However, Nex has 0 as an eigenvalue.  A
zero eigenvalue (with high degeneracy no less) can sometimes crash the Lanczos
algorithm.  So let's first try to use Ntot, but then we can compare.  (Exercise:
Extend `mcscript.ncci.decomposition` to include Nex decomposition by way of the
Ntot operator!)
   
It is assumed the reader has absorbed the ideas in
Ref. [johnson2015:spin-orbit].  So let us focus on how they relate to the
workflow here.  For a standard diagonalization run of MFDn, the initial Lanczos
pivot vector is some simple and/or random trial vector, and the operator
repeatedly applied to it in the Lanczos iterations is the Hamiltonian itself.
(This decomposes the pivot vector onto eigenspaces of the Hamiltonian, voila,
eigenproblem solved.)  Now, our pivot vector is the previously found Hamiltonian
eigenvector, and the applied operator is the decomposition operator, here Ntot.
In more detail:

(1) We need the existing wave function, from a diagonalization run, that we want
to decompose, and we must tell MFDn to use this as its pivot vector.  The
location of the wave function files must be specified, as must must be any
information needed to build the many-body basis (including many-body truncation
and "partitioning" of single particle orbitals).  For practical reasons, this
means the decomposition run has to run with the exact same such basis
parameters, and with the same number of MPI ranks (equivalently, the same number
of "diagonal blocks") as the original diagonalization run, so that the
eigenvector can be read back in directly, without any rearrangement.

(2) We also need to provide the Hermitian operator.  This will be as a TBME file
in h2 format.  The mcscript-ncci scripting can help automate generating these,
but, under the hood, the scripting is calling `h2mixer` and some other utilities
from the `shell` package.

(3) The output of interest is a file, which for normal diagonalization runs, is
just an ignored byproduct.  Namely, MFDn generates a file listing the Lanczos
alpha and beta coefficients.  The length of this list is (more or less) the
number of Lancoz iterations.  To find out the results of the decomposition, we
will have to read these in to some subsequent analysis code (e.g., in Python),
interpret them as the entries of a tridiagonal matrix, diagonalize, and do
something with the results, as described in Ref. [johnson2015:spin-orbit] (to be
seen below)...

You may ask, how many iterations do we need, and how do we tell if the results are
"converged"?  Should we do several runs, with different numbers of Lanczos
iterations, to check convergence?  The answer is, we only need to do one run,
with the maximal number of Lanczos iterations that we want to check.  In
analysis, later, we can always chop off the list of alpha and beta coefficients,
to simulate a run with fewer Lanczos iteractions, and compare the results.

- - - -

Let's first set this up taking advantage of mcscript-ncci scripting, then look
at the log of the run to see how the underlying numerical codes were actually
invoked.  See `runmfdndecomp01.py`.  Parameters specified in the task dictionary
serve various purposes:

   - Generating the filename of the existing wave function to be sought.  E.g.,
     even though we do not use the interaction "Daejeon16" here, we need to know
     it for the wave function filename (the existing wave function's
     "descriptor").  This is mostly contained in `"wf_source_info"`.
     
   - Generating the desciptor for this run (for output filenames).  Much of this
     is matches the input descriptor, e.g., again the interaction name!
     
   - Generating the decomposition operator TBMEs.
   
   - Running MFDn itself.  This includes information on basis setup (e.g.,
     truncation), as well as the number of Lanczos iterations.
   
Here is the task dictionary we created:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{'nuclide': (3, 3), 'interaction': 'Daejeon16', 'use_coulomb': True,
'a_cm': 40.0, 'hw_cm': None, 
'hamiltonian': {'U[ik.ik]': -1.382367999140773, 'U[r.r]': 0.1808490938414304, 'identity': -9.0}, 
'decomposition_type': 'Ntot', 'source_wf_qn': (1.0, 0, 1),
'wf_source_info': {'run': 'mfdn13', 'nuclide': (3, 3), 'interaction': 'Daejeon16', 
'use_coulomb': True, 'hw': 15, 'truncation_parameters': {'M': 1.0, 'Nmax': 4}, 'a_cm': 50.0, 
'max_iterations': 600, 'tolerance': 1e-06, 
'descriptor': <function task_descriptor_7 at 0x7ed85d2de5f0>, 
'basis_mode': <BasisMode.kDirect: 0>, 'sp_truncation_mode': <SingleParticleTruncationMode.kNmax: 1>,
'mb_truncation_mode': <ManyBodyTruncationMode.kNmax: 1>}, 'truncation_int': ('tb', 6), 'truncation_coul': ('tb', 20),
'basis_mode': <BasisMode.kDirect: 0>, 'hw': 15, 'sp_truncation_mode': <SingleParticleTruncationMode.kNmax: 1>, 
'mb_truncation_mode': <ManyBodyTruncationMode.kNmax: 1>, 'truncation_parameters': {'M': 1.0, 'Nmax': 4, 'Nstep': 2}, 
'diagonalization': True, 'max_iterations': 1200, 'tolerance': 0, 'partition_filename': None, 
'calculate_obdme': False, 'h2_format': 15099, 
'mfdn_executable': 'xmfdn-h2-lan', 
'mfdn_driver': <module 'mcscript.ncci.mfdn_v15' from '/home/mcaprio/.local/lib/python3.10/site-packages/mcscript/ncci/mfdn_v15.py'>}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Look at the `hamiltonian` entry.  For present purposes, this refers to the
Hermitian operator we want to feed into the Lanczos process, i.e., our
decomposition operator, not the (energy) Hamiltonian of the diagonalization run.
This is a list of coefficients of basic, built-in two-body operators for which
the scripting in conjunction with `shell` know how to construct TBMEs, basically
the one-body k^2 and r^2 operators and the identity operator.

The resulting descriptor (name for output files) is

    Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06-J01.0-g0-n01-Ntot-dlan1200

Let's run phase 0.  Looking at the output, we see `obmixer` was called to make
OBME files of the r^2 and k^2 operators...

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
...
define-target ik.ik obme-ik.ik.dat
...
define-target r.r obme-r.r.dat
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Then `h2mixer` was called to generate the "Hamiltonian" from these, with
coefficients that match those specified above.  This is stored in `tbme-H.bin`.
You can ingore the `rrel2` and `Ncm` operators, which are only needed for
diagonalization runs.  (Exercise: Clean up the scripting so that these are not
superflously generated in decomposition runs.  But they are harmless.)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
...
define-target work/tbme-H.bin
  add-source U[ik.ik] -1.38236799914077291e+00
  add-source U[r.r] 1.80849093841430386e-01
  add-source identity -9.00000000000000000e+00
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

So now let's run phase 1, to run MFDn.  We've thrown 1200 Lanczos iterations at
it.

And let's look at the logged output.  Notice that the scripting first searches,
based on the information we have given, for the data from the old
diagonalization run, and it finds the res file, the task data directory (for
paritioning info), and the wave function directory (for wave function files):

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    /home/mcaprio/scratch/runs/runmfdn13/results/res/runmfdn13-mfdn15-Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06.res
    /home/mcaprio/scratch/runs/runmfdn13/results/task-data/Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06
    /home/mcaprio/scratch/runs/runmfdn13/results/wf/Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Then the actual `mfdn.input` file generated as a control file form MFDn
contains:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    &inputlist
    IFLAG_mode = 0,
    Nprotons = 3,
    Nneutrons = 3,
    Hrank = 2,
    Nmin = 0,
    Nmax = 4,
    deltaN = 2,
    TwoMj = 2,
    hbomeg = 1.500000d+01,
    neivals = 4,
    maxits = 1200,
    tol = 0.000000d+00,
    orbitalfile = 'orbitals.dat',
    TBMEfile = 'tbme-H',
    numTBops = 3,
    obdme = .false.,
    selectpiv = 4,
    initvec_index = 1,
    initvec_smwffilename = '/home/mcaprio/scratch/runs/runmfdn13/results/wf/Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06/mfdn_smwf'
    /
    &obslist
    TBMEoperators(1) = 'tbme-rrel2',
    TBMEoperators(2) = 'tbme-H',
    TBMEoperators(3) = 'tbme-Ncm'
    /
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The key things to note are...

  - The mode `selectpiv=4` tells MFDn to take its Lanczos pivot vector from an
    external wf file.
    
  - The external wf filename is given via `initvec_smwffilename`.
  
  - Within that file, which contains several eigenvectors, `initvec_index=1`
    says pick the first eigenvector.  How did the scripting know our eigenvector
    of interest was the first one?  We gave the quantum numbers `(1.0,0,1)` for
    the first 1+ state, and the scripting read the res file, and saw that this
    was the eigenstate with "sequence" number 1 (see res file quoted way above).
    If these quantum numbers were not found in the diagonalation, the scripting
    would have thrown an exception.
    
  - The `neivals=4` is mostly irrelevant, since we are not doing a
    diagonalization, but it has to be at least 1 to keep MFDn happy, and
    controls how much (occasionally useful) diagnostic information comes out of
    the Lanczos process.
    
  - As in a diagonalizaton run, `maxits = 1200, tol = 0.000000d+00,` controls
    the termination condition for the Lanczos algorithm.  By setting the
    tolerance to 0, we ensure the tolerance termination condition will never be
    met, and the iterations will continue all the way to the given maximum of
    1200.

  - And `TBMEfile = 'tbme-H'` is where we feed our constructed
    decomposition operator in as the operator for the Lanczos algorithm.
    
  - Ignore the `TBMEoperators`.  This is baggage from diagonalization runs which
    hasn't been cleaned up.

After MFDn ran, notice that the file `mfdn_alphabeta.dat` was moved out to the
`results/lanczos` directory, where it is now called

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    runmfdndecomp01-mfdn15-Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06-J01.0-g0-n01-Ntot-dlan1200.lanczos
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
This is the file we need!  But the contents are not particularly illuminating by
eye:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
               1   2.4742275561099767        1.0910266760900069     
               2   4.9083578277037905        1.0210349953529745     
               3   4.6174151757721944        5.5757194634331024E-007
               4   5.6240326019341804       0.87346143599469628     
               5   3.6522822713457215        1.0214606694326518     
               6   2.7236856155939413        3.9098056355349678E-006
               7   5.9959541098453775        9.0286793599862233E-002
               8   3.9668397229421557       0.27037726509702592     
               9   2.0372067499338189        1.6894665489537678E-004
              10   5.9999742583237641        7.2144524344840170E-003
              11   4.0000214718045433        3.1448936484383037E-003
              12   2.0037227118985488       0.12188998739073630     
              13   5.9962805811694437        1.9361951975455098E-003
              14   4.0000022242528601        5.1304419320892644E-004
    ...
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although we can see that, after a while, most of the diagonal entries seem to
resemble the integer eigenvalues of Ntot...

So now let us interpret these numbers in the Python code to accompany this
tutorial, given in `decoposition_tutorial_example.py`.

1) First read in the alpha and beta coefficients...  This is done with
`mfdnres.decomposition.read_lanczos`.  With 1200 Lanczos decompositions, we have
1200 alphas (diagonal entries) and 1199 betas (off-diagonal entries).

2) Then we generate a "raw" (i.e., unbinned) decomposition from these.  This is
done with `mfdnres.decomposition.generate_raw_decomposition`.  This is quite
straighforward, mostly a call to `linalg.eigh_tridiagonal`.  The default is 1200
eigenvalues, each paired with a squared amplitude (taken from the leading entry
of the corresponding eigenvector).  If we format the results as an array, the
table looks like this...

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     [1.99999996e+00 1.32810609e-03]
     [1.99999998e+00 2.81308180e-19]
     [1.99999999e+00 7.33802319e-17]
     [2.00000000e+00 2.25331459e-18]
     [2.00000000e+00 9.51724189e-02]
     [2.00000002e+00 1.07748019e-05]
     [2.00000003e+00 5.53631512e-10]
     [2.00000004e+00 7.24721937e-01]
     [3.99999990e+00 0.00000000e+00]
    ...
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notice the first several entries are for the lowest eigenvalue of our
decomposition operator, which in this case is 2, but with some numerical spread.
Many have near-vanishing (numerical noise) squared amplitudes, but a few squared
amplitudes are significant.  We need to sum these up.  Then we get into the
contributions for the next eigenvalue, in this case 4...

Let's see how this would change if we had used fewer Lanczos iterations.  We can
emulate this by chopping off the end of our alpha and beta list.  And
`generate_raw_decomposition` will do this for us.  For instance, with just 5
Lanczos iteration, we instead get

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    lanczos_iterations 5
    [[2.00000003e+00 8.21233238e-01]
     [3.32100721e+00 8.40219841e-15]
     [4.00000041e+00 1.20419789e-01]
     [5.95530766e+00 2.82311314e-12]
     [6.00000012e+00 5.83469736e-02]]
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notice that some of the eigenvalues are pretty far from the integers we are
expecting, though `3.32` comes with a negligible amplitude.  With 10 iterations,
we now get

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    lanczos_iterations 10
    [[1.99999996e+00 1.32863648e-03]
     [2.00000000e+00 9.51808192e-02]
     [2.00000004e+00 7.24723782e-01]
     [4.00000001e+00 1.82068028e-02]
     [4.00000041e+00 3.21254850e-02]
     [4.00000051e+00 7.00875008e-02]
     [5.99997426e+00 9.92532613e-13]
     [5.99999971e+00 1.22994715e-02]
     [6.00000014e+00 4.05791972e-02]
     [6.00000085e+00 5.46830484e-03]]
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notice that the stray noninteger eigenvalue has gone away, and we get more
instances of each eigenvalue, sometimes several with significant squared
amplitudes

But how "good" are these values?  Are the sums changing with the number of
Lanczos iterations, or has these stabilized.  We would have to add them up to
see.

If we were patient, we would sit down with a calculator (or abacus) and do this
manually.  We are not patient.  So we write a histogramming routine.  This
routine is told the expected eigenvalue, and it bins the squared amplitudes
accordingly.  This is fine, so long as the spread of actual eigenvalues is much
smaller than the separation of the expected eigenvalues.  If the spread is large
on that scale, we are sunk, anyway.  We also tell the histogramming routine what
"labels" should go with each eigenvalue.  For instance, though we used Ntot as
our decomposition operator, now is when we can translate back to the shell modeler's Nex as
the label.

This is done with `mfdnres.decomposition.generate_decomposition`.  This function
takes care of calling `generate_raw_decomposition`, and then bundles up the
results, in a special data structure.

We provide a mapping from eigenvalue (of Ntot) to label (which here we remap to
Nex).

Let's look at the verbose output for the case where we truncate to 5 Lanczos
iterations:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    lanczos_iterations 5
    Raw decomposition
    [[2.00000003e+00 8.21233238e-01]
     [3.32100721e+00 8.40219841e-15]
     [4.00000041e+00 1.20419789e-01]
     [5.95530766e+00 2.82311314e-12]
     [6.00000012e+00 5.83469736e-02]]
    Expected eigenvalue -> label group
      +2.000 -> (0,)
      +4.000 -> (2,)
      +6.000 -> (4,)
    DEPRECATED: Call to mfdnres.decomposition.generate_decomposition() without decomposition_type argument is deprecated.
    Binned results (sorted by eigenvalue)
      +2.000 : 0.821233
      +4.000 : 0.120420
      +6.000 : 0.058347
    Decomposition (by labels)
    (0,) : 0.821233
    (2,) : 0.120420
    (4,) : 0.058347
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notice the eigenvalue to label mapping (which we provided).  Then the binning by
eigenvalue.  And finally translating the eigenvalues to labels.

Now compare the results for different numbers of iteratations in the Lanczos
decomposition.  By the way, we are using
`mfdnres.decomposition.print_decomposition` to print these as tables, rather
than a raw Python dict:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    lanczos_iterations 5
    0.821233 (0,)
    0.120420 (2,)
    0.058347 (4,)

    lanczos_iterations 10
    0.821233 (0,)
    0.120420 (2,)
    0.058347 (4,)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wow, we were already converged at 5 lanczos iterations, despite that wifty stray
non-integer eigenvalue!  (The eigenvalue 3.32 was lumped in with 4.0, but it was
also so small that it didn't matter.)  This is maybe *too* nice of an example!
In fact, how low can we push the number of Lanczos iterations?  We clearly need
at least three iterations to cover three eigenvalues!

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    lanczos_iterations 2
    0.872305 (0,)
    0.000000 (2,)
    0.127695 (4,)
    
    lanczos_iterations 3
    0.821233 (0,)
    0.120420 (2,)
    0.058347 (4,)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

But 3 iterations seems to do it.

In fact, convergence is to be expected, when the number of iterations is equal
to the number of distinct eigenvalues.  See Sec. 5.2.1 "Decomposition" of
Ref. [johnson2018:bigstick].

Incidentally, if we try the same thing using Nex itself as the decomposition
operator, the raw eigenvalues are shifted, but the end result is the same:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Binned decomposition (Nex operator)...
    lanczos_iterations 5
    Raw decomposition
    [[-3.04615426e-08  8.21233243e-01]
     [ 1.09951853e+00  2.37494664e-15]
     [ 2.00000008e+00  1.20419784e-01]
     [ 3.96730077e+00  3.38362807e-12]
     [ 4.00000006e+00  5.83469728e-02]]
    Expected eigenvalue -> label group
      +0.000 -> (0,)
      +2.000 -> (2,)
      +4.000 -> (4,)
    Binned results (sorted by eigenvalue)
      +0.000 : 0.821233
      +2.000 : 0.120420
      +4.000 : 0.058347
    Decomposition (by labels)
    (0,) : 0.821233
    (2,) : 0.120420
    (4,) : 0.058347
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## 3. Using predefined decomposition types

See `runmfdndecomp02.py`.


## References

[caprio2022:10be-shape-sdanca21] "Symmetry and shape coexistence in
10Be". http://dx.doi.org/10.55318/bgjp.2022.49.1.057

[caprio2020:intrinsic] "Intrinsic operators for the translationally-invariant many-body
problem", JPG 47, 122001 (2020). http://dx.doi.org/10.1088/1361-6471/ab9d38

[gueorguiev2000:fp-su3-breaking] "SU(3) symmetry breaking in lower fp-shell
nuclei". http://dx.doi.org/10.1103/PhysRevC.63.014318

[johnson2015:spin-orbit] "Spin-orbit decomposition of \textit{ab initio} nuclear wave
functions", PRC 91, 034313 (2015). http://dx.doi.org/10.1103/PhysRevC.91.034313

[johnson2018:bigstick] "BIGSTICK: A flexible configuration-interaction
shell-model code". https://arxiv.org/abs/1801.08432
  
[zbikowski2021:beyond-elliott] "Rotational bands beyond the {E}lliott
model". http://dx.doi.org/10.1088/1361-6471/abdd8e

