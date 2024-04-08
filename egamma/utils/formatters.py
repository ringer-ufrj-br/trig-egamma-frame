import numpy as np
from numbers import Number
from typing import Tuple


def get_number_order(num: Number) -> np.integer:
    """
    Returns the order of a number in base 10
    Example:
    >>> get_number_order(100)
    2
    >>> get_number_order(0.1)
    -1

    Parameters
    ----------
    num : Number
        Number to extract the order

    Returns
    -------
    np.integer
        The number order in base 10
    """
    # Comment on the side is to avoid type checking errors
    # with python linting tools
    return np.floor(np.log10(np.abs(num)))  # type: ignore


def significant_around(val: Number,
                       err: Number) -> Tuple[np.floating, np.floating]:
    """
    Rounds a value and its error to the same order of magnitude,
    defined by the error value

    Parameters
    ----------
    val : Number
        Measured value
    err : Number
        Error over the measured value

    Returns
    -------
    Tuple[np.floating, np.floating]
        The rounded value and error
    """
    err_order = get_number_order(err)
    val_arounded = np.around(val, -err_order)  # type: ignore
    err_arounded = np.around(err, -err_order)  # type: ignore
    return val_arounded, err_arounded


def confidence_interval_str(val: Number, err: Number,
                            latex: bool = False, max_precision=5) -> str:
    """
    Returns a string representation of a value and its error
    in latex synthax

    Parameters
    ----------
    val : Number
        Value to be represented
    err : Number
        value error
    latex : bool, optional
        If true adds latex $$ for math mode, by default False
    max_precision : int, optional
        If the measurement precision exceeds max_precision
        only max_precision decimals are printed, by default 5

    Returns
    -------
    str
        String representation of the value and its error
    """
    rtol = 10**(-max_precision)
    if np.isclose(err, 0, rtol=rtol):
        repr_str = f'{val:.{max_precision}f}'
        return repr_str

    calc_precision = int(-get_number_order(err))  # type: ignore
    if calc_precision < max_precision:
        precision = calc_precision
    else:
        precision = calc_precision
    pm = '\\pm' if latex else '+-'
    repr_str = f'{val:.{precision}f} {pm} {err:.{precision}f}'
    if latex:
        repr_str = f'${repr_str}$'
    return repr_str
