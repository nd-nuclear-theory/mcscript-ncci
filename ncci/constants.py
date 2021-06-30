"""constants.py -- useful physical and mathematical constants

- 11/13/20 (pjf): Created, extracted from ncci.utils.
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

k_alpha   = 7.297_352_5693e-3 # fine-structure constant [1,2]
k_mp_csqr = 938.272_088_16    # proton mass in MeV/c^2 [1,2]
k_mn_csqr = 939.565_420_52    # neutron mass in MeV/c^2 [1,2]
k_md_csqr = 1875.612_942_57   # deuteron mass in MeV/c^2 [1,2]
k_hbar_c  = 197.326_980_4     # (hbar c) in MeV fm [1,2]
k_gp      = 5.585_694_6893    # proton g factor [1]
k_gn      = -3.826_085_45     # neutron g factor [1]

k_mN_csqr = (k_mp_csqr+k_mn_csqr)/2  # (m_N c^2) in MeV [1]
