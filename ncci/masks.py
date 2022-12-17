"""masks.py -- masks for state-pair selection in postprocessor runs

    - 05/11/22 (mac): Created, extracted from run scripts (runmac0633),
        originally task_handler_postprocessor.py.
    - 08/13/22 (pjf): Add mask_good_J().
    - 11/20/22 (mac):
        + Support transition sense in mask_allow_near_yrast().
        + Add mask_by_energy_cutoff().
"""

import math

import mcscript

from . import constants

def mask_allow_near_yrast(task:dict, mask_params:dict, qn_pair, verbose=False):
    """Mask function for transitions involving only low-lying states of each J.

    Default is to only consider initial and final states in the "canonical"
    sense provided by the calling code (J decreasing, or n decreasing within J),
    but "sense"="both" allows "anticanonical" transitions to be considered as
    well.  E.g., if ni=2, to capture only transitions involving the yrast and
    yrare states, considering the anticanonical ordering when applying the
    filter permits J-increasing transitions from these states to be considered
    as well.

    Mask parameters:

        "ni_max" (int or dict, optional): maximum ni, or dictionary Ji->ni_max (default 0), default 5

        "nf_max" (int or dict, optional): maximum nf, or dictionary Jf->nf_max (default 0), default 999

        "sense" (str, optional): whether to interpret initial and final states
        as being for the "canonical" (f<=i), "anticanonical" (f>=i), or "both"
        sense of the transition, default "canonical"

    Arguments:

        task (dict): task dictionary

        mask_params (dict): parameters specific to this mask

        qn_pair (tuple): (qnf,qni) for transition

        verbose (book, optional): verbosity (argument required by handler)

    Returns:

        allow (bool): mask value

    """

    # get parameters
    ni_max = mask_params.get("ni_max", 5)
    if (isinstance(ni_max, dict)):
        ni_max = ni_max.get(Ji,0)
    nf_max = mask_params.get("nf_max", 999)
    if (isinstance(nf_max, dict)):
        nf_max = nf_max.get(Jf,0)
    sense = mask_params.get("sense", "canonical")
    if sense not in {"canonical", "anticanonical", "both"}:
        raise ValueError("unrecognized transition direction sense {}".format(sense))
        
    # calculate mask value
    allow = False
    if sense in {"canonical", "both"}:
        (qnf,qni) = qn_pair
        (Ji,gi,ni) = qni
        (Jf,gf,nf) = qnf
        if (verbose):
            print("  Mask yrast check (canonical): Jf {} nf {} nf_max {} {} ; Ji {} ni {} ni_max {} {}".format(
                Jf, nf, nf_max, (nf<=nf_max),
                Ji, ni, ni_max, (ni<=ni_max),
            ))
        allow |= (ni<=ni_max) and (nf<=nf_max)
    if sense in {"anticanonical", "both"}:
        (qnf,qni) = reversed(qn_pair)
        (Ji,gi,ni) = qni
        (Jf,gf,nf) = qnf
        if (verbose):
            print("  Mask yrast check (anticanonical): Jf {} nf {} nf_max {} {} ; Ji {} ni {} ni_max {} {}".format(
                Jf, nf, nf_max, (nf<=nf_max),
                Ji, ni, ni_max, (ni<=ni_max),
            ))
        allow |= (ni<=ni_max) and (nf<=nf_max)

    return allow


def mask_no_self(task:dict, mask_params:dict, qn_pair, verbose=False):
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

def mask_only_self(task:dict, mask_params:dict, qn_pair, verbose=False):
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


def mask_by_energy_cutoff(task:dict, mask_params:dict, qn_pair, verbose=False):
    """Mask function restricting to self-transitions (moments).

    Mask parameters:

        E_max (float, optional): max energy (for bra or ket), default None

        Ei_max (float, optional): max energy for ket, default None

        Ef_max (float, optional): max energy for bra, default None

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

    # extract parameters
    E_max = mask_params.get("E_max", None)
    Ei_max = mask_params.get("Ei_max", None)
    Ef_max = mask_params.get("Ef_max", None)
    
    # calculate mask value
    ket_results_data = task["metadata"]["ket_results_data"]
    bra_results_data = task["metadata"]["bra_results_data"]
    Ei = ket_results_data.get_energy(qni)
    Ef = ket_results_data.get_energy(qnf)
    allow = True
    allow &= E_max is None or Ei<=E_max
    allow &= E_max is None or Ef<=E_max
    allow &= Ei_max is None or Ei<=Ei_max
    allow &= Ef_max is None or Ef<=Ef_max

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
