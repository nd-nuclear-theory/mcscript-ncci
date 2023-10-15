"""constants.py -- useful physical and mathematical constants

- 11/13/20 (pjf): Created, extracted from ncci.utils.
- 12/26/22 (pjf): Added SI base constants and k_hbar.
"""

################################################################
# physical constants
#
# constants from:
# [1] E. Tiesinga, P. J. Mohr, D. B. Newell, and B. N. Taylor (2020), "The 2018
#     CODATA Recommended Values of the Fundamental Physical Constants" (Web
#     Version 8.1). Database developed by J. Baker, M. Douma, and S.
#     Kotochigova. Available at http://physics.nist.gov/constants, National
#     Institute of Standards and Technology, Gaithersburg, MD
#     20899.
# [2] P.A. Zyla et al. (Particle Data Group), Prog. Theor. Exp. Phys. 2020,
#     083C01 (2020).
################################################################

import types
from math import pi

# SI base constants (exact by definition)
si_base = types.SimpleNamespace()
si_base.k_h = 6.626_070_15e-34  # Planck constant h in J s
si_base.k_e = 1.602_176_634e-19 # elementary charge in C
si_base.k_k = 1.380_649e-23     # Boltzmann constant in J/K
si_base.k_NA = 6.022_140_76e-23 # Avogadro constant in 1/mol
si_base.k_c = 299_792_458       # speed of light in m/s
si_base.k_nuCs = 9_192_631_770  # 133Cs hyperfine transition frequency in 1/s

si_base.k_hbar = si_base.k_h/(2*pi)  # reduced Planck constant hbar in J s

k_alpha   = 7.297_352_5693e-3 # fine-structure constant [1,2]
k_mp_csqr = 938.272_088_16    # proton mass in MeV/c^2 [1,2]
k_mn_csqr = 939.565_420_52    # neutron mass in MeV/c^2 [1,2]
k_md_csqr = 1875.612_942_57   # deuteron mass in MeV/c^2 [1,2]
k_hbar_c  = 197.326_980_4     # (hbar c) in MeV fm [1,2]
k_hbar    = 6.582_119_569e-7  # hbar in MeV fs [1]
k_gp      = 5.585_694_6893    # proton g factor [1]
k_gn      = -3.826_085_45     # neutron g factor [1]

k_mN_csqr = (k_mp_csqr+k_mn_csqr)/2  # (m_N c^2) in MeV [1]
