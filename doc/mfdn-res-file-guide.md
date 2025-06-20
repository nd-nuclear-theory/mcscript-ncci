# A quick tour of an MFDn results file #

Mark A. Caprio
University of Notre Dame

+ 06/21/24 (mac): Created.

----------------------------------------------------------------

The overall format of an MFDn results file is based on the Microscoft Windows
INI file format (see documentation for the Python `configparser` library).  That
said, our actual parser in `mfdnres` (see `mfdnres/data_parsers/mfdn_v15.py`) is
homegrown.

The following examples are from:

  `runmfdn13-mfdn15-Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax02-Mj0.0-lan600-tol1.0e-06.res`

This is a run of MFDn 15, CPU version, h2 variant, with the Lanczos solver.
Details of the file contents may vary with other variants of the code.

## MFDn ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[MFDn]
Version = 15
Revision = v15b01-92-g099fafe
Platform = 
Username = 
ndiags   =        1
MPIranks  =        1
OMPthreads =       32
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section contains basic diagnostics about the MFDn version and OpenMP/MPI
parallel environment.

## PARAMETERS ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[PARAMETERS]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This "section" is empty, and simply flags that the next several sections of the file
will contain run parameters.

## Basis ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Basis]
Nprotons  =        3
Nneutrons =        3
# Orbitals read in from file
TwoMj  =        0
parity =        1
Nmin   =        0
Nmax   =        2
DeltaN =        2
WTmax  =     4.1000
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

This section contains parameters defining the many-body basis.  These are
primarily input parameters.

- `Nprotons`, `Nneutrons`: int

  - (Z,N) for nucleus
  
- `TwoMj`: int

  - Twice the M quantum number for constructing the M-scheme basis.
  
  - E.g., `TwoMj`=0 indicates M=0.0, or `TwoMj`=1 indicates M=0.5.
    
- Etc.

## Diagonalization ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Diagonalization]
neivals   =        4
maxits    =      600
startit   =        0
selectpiv =        3
tol       =     0.0000
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section documents the input parameters provided to the eigensolver.

- `neivals`: int

  - Number of eigenstates requested by the user.
  
  - This is the number of states included in the convergence test for the
  eigensolver's termination condition.  Note that MFDn may output results for
  more states (generally a multiple of 4 or 8 states), but those states beyond
  the number of requested states were not included in the convergence test and
  are therefore to be regarded with particular suspicion.  The `mfdnres` parser
  simply throws out the calculated data for these states.
  
- Etc.  

## Many-body matrix ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Many-body matrix]
dimension  =              17040
numnonzero =            2081236
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section contains the calculated properties of the many-body matrix:
dimension and number of a priori nonzero matrix elements (based on particle rank
selection rules).

## Interaction ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Interaction]
# reading complete TBMEs in H2 format
Hrank  =        2
hbomeg =    15.0000
fmass  =   938.9200

TBMEfile = tbme-H.bin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- TODO

## Observables ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Observables]
numTBops   =       15
# TBME file for relative R2 operator
TBMEfile(1) = tbme-rrel2.bin

# TBME files for additional operators
TBMEfile(2) = tbme-H.bin
TBMEfile(3) = tbme-Ncm.bin
TBMEfile(4) = tbme-Tintr.bin
TBMEfile(5) = tbme-Tcm.bin
TBMEfile(6) = tbme-VNN.bin
TBMEfile(7) = tbme-VC.bin
TBMEfile(8) = tbme-L2.bin
TBMEfile(9) = tbme-Sp2.bin
TBMEfile(*) = tbme-Sn2.bin
TBMEfile(*) = tbme-S2.bin
TBMEfile(*) = tbme-J2.bin
TBMEfile(*) = tbme-T2.bin
TBMEfile(*) = tbme-CSU3.bin
TBMEfile(*) = tbme-CSp3R.bin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- TODO

## RESULTS ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[RESULTS]
# following Condon-Shortley phase conventions
# for conventions of reduced matrix elements and
# for Wigner-Eckart theorem, see Suhonen (2.27)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This "section" is empty, and simply flags that the next several sections of the file
will contain run results.

## Energies ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Energies]
# Seq       J    n      T        Eabs        Eexc        Error    J-full
    1      1.0   1   0.000      -29.500      0.000     0.15E-04    1.0000
    2      3.0   1   0.000      -27.898      1.602     0.17E-04    3.0000
    3      0.0   1   1.000      -26.140      3.360     0.16E-04    0.0000
    4      2.0   1   1.000      -23.820      5.681     0.18E-04    2.0000
    5      2.0   2   0.001      -23.137      6.364     0.17E-04    2.0000
    6      1.0   2   0.000      -21.292      8.209     0.15E-04    1.0000
    7      2.0   3   1.000      -18.815     10.685     0.34E-03    2.0000
    8      1.0   3   1.000      -17.370     12.130     0.18E-04    1.0000
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section contains the basic listing of eigenvalues and corresponding quantum
numbers.

Notice that results for 8 states were printed here, even though only 4 states
were requested (see parameter `neivals` in section `Diagonalization` above).
This behavior of MFDn is due to support for block eigensolvers such as LOBPCG.

- Seq: int

  - "Sequence" number of state, i.e., 1-based index in the ordered set of
  eigenpairs coming out of the diagonalization.
  
  - Note that the same "state" might have different sequence numbers in runs of
  different M.  E.g., in an M=3 run, the J=1.0 state would disappear, and the
  J=3.0 state would become the "ground state" of the calculation, with sequence
  number 1.

- J, float

  - Total angular momentum of the state as deduced a posteriori by evaluating
  <J^2> for that state and extracting the corresponding quantum number J by
  solution of the quadratic equation <J^2>=J(J+1).
  
  - Here the result is truncated to one decimal place, on
  the assumption that only (integer or) half-integer values are expected (but see
  `J-full` below).
  
  - J can deviate from (integer or) half-integer due to incomplete convergence.
  
  - It can also deviate from (integer or) half-integer in the event of a
  degenerate subspace spanned by basis states of different J, as often happens
  for spurious states (see, e.g., Fig. 8 of Caprio, Maris & Vary 2012
  [http://dx.doi.org/10.1103/PhysRevC.86.034312]).
  
- `n`, int

  - Counting number (1-based) for state within given J and parity, as in
  traditional spectroscopic notation J^P_n, e.g., 3^+_1 for the first 3+ state.
  
  - This is based simply on counting the states, making use of the `J` values,
  calculated as described above, rounded to the nearest half integer
  (`subrts_Observables.f`). 

- T, float

  - Isospin of the state as deduced a posteriori by evaluating
  <T^2> for that state and extracting the corresponding quantum number T by
  solution of the quadratic equation <T^2>=T(T+1).
  
  - Here the result is carried to several decimal places.
  Although integer or half-integer values would be expected for an isoscalar interaction, in
  general, isospin is not strictly conserved, and isospin mixing happens to a
  greater or lesser extent.

- `Eabs`, float

  - "Absolute energy" E, i.e., eigenvalue.
  
  - This is conventionally in MeV, assuming the input Hamiltonian matrix
  elements are provided in MeV.
  
- `Eexc`, float

  - "Excitation energy" Ex.
  
  - Beware that this excitation energy is simply calculated by subtracting the
  energy of the lowest state in *this* calculation (i.e., `Seq`=1).  This might
  not be the global ground state, which might be of different parity, or of a J less
  than the M for this calculation.
  
- `Error`, float

  - Error estimate for eigenstate.
  
  - TODO: Document how caculated.
  
- `J-full`, float

  - The same `J` deduced as above, but with more decimal places displayed.
  
  - This provides a diagnostic of convergence.  Small deviations from (integer
  or) half-integer suggest incomplete convergence.

## Oscillator quanta ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Oscillator quanta]
# Seq    J    n      T      Amp(N)^2 
    1   1.0   1   0.000      0.8818      0.1182    
    2   3.0   1   0.000      0.8867      0.1133    
    3   0.0   1   1.000      0.8928      0.1072    
    4   2.0   1   1.000      0.8937      0.1063    
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- TODO

## M1 moments ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[M1 moments]
# M1 moments only calculated for runs with nonzero M_j
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- TODO

Alternatively, in the output from the M=1.0 run (`runmfdn13-mfdn15-Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax02-Mj1.0-lan600-tol1.0e-06.res`), we find

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[M1 moments]
# for M1 moment conventions, see Suhonen (6.52)
# Seq    J    n      T        mu       Dl(p)      Dl(n)      Ds(p)      Ds(n)    sum(=J)
    1   1.0   1   0.000     0.8545     0.0320     0.0357     0.4664     0.4660     1.0000
    2   3.0   1   0.000     1.8789     1.0023     1.0018     0.4980     0.4979     3.0000
    3   2.0   1   1.000     1.0368     0.8470     0.8389     0.1479     0.1663     2.0000
    4   2.0   2   0.001     1.1685     0.8203     0.8368     0.1764     0.1665     2.0000
    5   1.0   2   0.000     0.3418     0.6857     0.6907    -0.1895    -0.1868     1.0000
    6   2.0   3   1.000     1.3062     0.6620     0.6522     0.3472     0.3386     2.0000
    7   1.0   3   1.000     0.6305     0.2632     0.2532     0.2356     0.2480     1.0000
    8   1.0   4   0.000     0.5532     0.5196     0.5202    -0.0126    -0.0272     1.0000
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- TODO

## E2 moments ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[E2 moments]
# for Q moment conventions, see Suhonen (6.53)
# Seq    J    n      T       Q(p)       Q(n)
    1   1.0   1   0.000     0.0746     0.0730
    2   3.0   1   0.000    -3.3416    -3.3110
    4   2.0   1   1.000    -2.0904    -1.9972
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- TODO

## Angular momenta ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Angular momenta]
# Seq    J    n      T      <L^2>      <S^2>      <Lp^2>     <Sp^2>     <Ln^2>     <Sn^2>        <J^2>
    1   1.0   1   0.000     0.2358     1.9653     2.0822     0.7664     2.0835     0.7663       2.0000
    2   3.0   1   0.000     6.1210     2.0880     2.2244     0.7827     2.2234     0.7824      12.0000
    3   0.0   1   1.000     0.3130     0.3130     2.1046     0.7796     2.1063     0.7794       0.0000
    4   2.0   1   1.000     4.8333     0.7182     2.2090     0.7813     2.2095     0.7814       6.0000
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- TODO

## Relative radii ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Relative radii]
# Seq    J    n      T      r(p)       r(n)    r(matter)     r_pp       r_nn       r_pn
    1   1.0   1   0.000     2.0904     2.0830     2.0867     0.9681     0.9641     1.5773
    2   3.0   1   0.000     2.0438     2.0364     2.0401     0.9406     0.9366     1.5492
    3   0.0   1   1.000     2.0752     2.0677     2.0715     0.9621     0.9580     1.5645
    4   2.0   1   1.000     2.0651     2.0562     2.0606     0.9502     0.9454     1.5651
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- TODO

## Other 2-body observables ##

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Other 2-body observables]
# Seq    J    n      T     see header for TBME file names of observables
    1   1.0   1   0.000     -25.5777         0.140447E-09      75.1700          11.2500         -102.499          1.75138         0.235849         0.766417         0.766280          1.96525          2.00000         0.924290E-04      6.90693          3.55330    
    2   3.0   1   0.000     -24.1482        -0.852232E-09      78.1560          11.2500         -104.095          1.79071          6.12105         0.782653         0.782393          2.08795          12.0000         0.101911E-03      7.19302          3.78729    
    3   0.0   1   1.000     -22.6890        -0.763713E-09      75.8739          11.2500         -100.323          1.76028         0.313024         0.779569         0.779362         0.313023         0.261175E-06      1.99999          6.51294          3.17475    
    4   2.0   1   1.000     -19.9833        -0.950663E-09      76.5757          11.2500         -98.3325          1.77357          4.83330         0.781337         0.781361         0.718191          6.00000          1.99959          5.99659          2.61148    
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- TODO

## Occupation probabilities ##

This section contains average occupancies (occupation probabilities) for each of the nlj shells,
in each of the many-body eigenstates.  That is, these are the expectation values <N_(n,l,j,t_z)>.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Occupation probabilities]
# orb      n_rad   l   2*j
    1   pro    0    0    1     1.936        1.935        1.937        1.940        1.940        1.923        1.942        1.945    
    2   pro    0    1    1    0.2451       0.3324E-01   0.1039       0.9336E-01   0.4515       0.4789       0.3968       0.4635    
    3   pro    0    1    3    0.7704       0.9891       0.9177       0.9261       0.5264       0.5136       0.5977       0.5213    
    4   pro    1    0    1    0.1409E-01   0.1913E-01   0.1596E-01   0.1864E-01   0.1263E-01   0.2038E-01   0.1588E-01   0.1759E-01
...
# sum of proton occ.prob.     3.000        3.000        3.000        3.000        3.000        3.000        3.000        3.000    

    1   neu    0    0    1     1.935        1.933        1.936        1.939        1.939        1.923        1.942        1.944    
    2   neu    0    1    1    0.2436       0.3357E-01   0.1042       0.8485E-01   0.4463       0.4749       0.4133       0.4653    
    3   neu    0    1    3    0.7730       0.9896       0.9183       0.9360       0.5338       0.5204       0.5831       0.5234    
    4   neu    1    0    1    0.1480E-01   0.2025E-01   0.1687E-01   0.1950E-01   0.1267E-01   0.2020E-01   0.1629E-01   0.1738E-01
...
# sum of neutron occ.prob.    3.000        3.000        3.000        3.000        3.000        3.000        3.000        3.000    
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Each row contains the occupancies for a given orbital, with (n,l,j,t_z) values as indicated by the
  species column (unlabeled) and the `n_rad`, `l`, and `2*j` columns.

- Then the numerical columns are for successive many-body eigenstates.

- Summed occupancies, for the proton orbitals and neutron orbtals separately,
  are provided as comment lines.  These sums should match the total number of
  protons and neutrons, respectively.

