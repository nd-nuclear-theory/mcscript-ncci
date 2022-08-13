"""masks.py -- masks for state-pair selection in postprocessor runs

    - 05/11/22 (mac): Created, extracted from run scripts (runmac0633),
        originally task_handler_postprocessor.py.
    - 08/13/22 (pjf): Add mask_good_J().
"""

import math

import mcscript

from . import constants

def mask_allow_near_yrast(task,mask_params,qn_pair,verbose=False):
    """Mask function for transitions involving only low-lying states of each J.

    Mask parameters:
        "ni_max" (int or dict, optional): maximum ni, or dictionary Ji->ni_max (default 0), default 5
        "nf_max" (int or dict, optional): maximum nf, or dictionary Jf->nf_max (default 0), default 999

    Arguments:
        task (dict): task dictionary
        mask_params (dict): parameters specific to this mask
        qn_pair (tuple): (qnf,qni) for transition
        verbose (book, optional): verbosity (argument required by handler)

    Returns:
        allow (bool): mask value

    """

    # unpack quantum numbers
    (qnf,qni) = qn_pair
    (Ji,gi,ni) = qni
    (Jf,gf,nf) = qnf

    # calculate mask value
    ni_max = mask_params.get("ni_max",5)
    if (isinstance(ni_max, dict)):
        ni_max = ni_max.get(Ji,0)
    nf_max = mask_params.get("nf_max",999)
    if (isinstance(nf_max, dict)):
        nf_max = nf_max.get(Jf,0)
    if (verbose):
        print("  Mask yrast check: Jf {} nf {} nf_max {} {} ; Ji {} ni {} ni_max {} {}".format(Jf,nf,nf_max,(nf<=nf_max),Ji,ni,ni_max,(ni<=ni_max)))
    allow = (ni<=ni_max)
    allow &= (nf<=nf_max)

    return allow

def mask_no_self(task,mask_params,qn_pair,verbose=False):
    """Mask function eliminating self-transitions (moments).

    Mask parameters:
        N/A

    Arguments:
        task (dict): task dictionary
        mask_params (dict): parameters specific to this mask
        qn_pair (tuple): (qnf,qni) for transition
        verbose (book, optional): verbosity (argument required by handler)

    Returns:
        allow (bool): mask value

    """

    # unpack quantum numbers
    (qnf,qni) = qn_pair
    (Ji,gi,ni) = qni
    (Jf,gf,nf) = qnf

    # calculate mask value
    allow = (qnf!=qni)

    return allow

def mask_only_self(task,mask_params,qn_pair,verbose=False):
    """Mask function restricting to self-transitions (moments).

    Mask parameters:
        N/A

    Arguments:
        task (dict): task dictionary
        mask_params (dict): parameters specific to this mask
        qn_pair (tuple): (qnf,qni) for transition
        verbose (book, optional): verbosity (argument required by handler)

    Returns:
        allow (bool): mask value

    """

    # unpack quantum numbers
    (qnf,qni) = qn_pair
    (Ji,gi,ni) = qni
    (Jf,gf,nf) = qnf

    # calculate mask value
    allow = (qnf==qni)

    return allow

def mask_good_J(task:dict, mask_params:dict, qn_pair, verbose=False):
    """Mask function restricting to "good-J" levels.

    Mask parameters:
        "tolerance" (float, optional): maximum deviation of J from (half-)integral

    Arguments:
        task (dict): task dictionary
        mask_params (dict): parameters specific to this mask
        qn_pair (tuple): (qnf,qni) for transition
        verbose (book, optional): verbosity (argument required by handler)

    Returns:
        allow (bool): mask value
    """
    (qnf,qni) = qn_pair
    (Ji,gi,ni) = qni
    (Jf,gf,nf) = qnf

    if "nuclide" in task.get("wf_source_bra_selector", {}):
        bra_nuclide = task["wf_source_bra_selector"]["nuclide"]
    elif "bra_nuclide" in task:
        bra_nuclide = task["bra_nuclide"]
    else:
        bra_nuclide = task["nuclide"]
    bra_A = sum(bra_nuclide)

    if "nuclide" in task.get("wf_source_ket_selector", {}):
        ket_nuclide = task["wf_source_ket_selector"]["nuclide"]
    elif "ket_nuclide" in task:
        ket_nuclide = task["bra_nuclide"]
    else:
        ket_nuclide = task["nuclide"]
    ket_A = sum(ket_nuclide)

    tolerance = mask_params.get("tolerance", 1e-2)

    allow_bra = mcscript.utils.approx_equal(2*Jf, int(2*Jf), tolerance)
    allow_bra &= (int(2*Jf)%2 == bra_A%2)
    if verbose and not allow_bra:
        print(f"  WARNING: Invalid Jf={Jf} for nuclide {bra_nuclide}")

    allow_ket = mcscript.utils.approx_equal(2*Ji, int(2*Ji), tolerance)
    allow_ket &= (int(2*Ji)%2 == ket_A%2)
    if verbose and not allow_ket:
        print(f"  WARNING: Invalid Jf={Ji} for nuclide {bra_nuclide}")

    return (allow_bra and allow_ket)
