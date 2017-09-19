#!/usr/bin/env python
# encoding: utf-8


"""
``rand`` is a module that provides ``random`` utilities,
such as:

* globally setting a seed value
* random integers between a range
* random floats between a range
* return ``True`` or ``False`` based on a probability (the ``maybe`` function)
* return random data
"""


import random as r


RANDOM = r.Random()
_randint = RANDOM.randint
random = _random = RANDOM.random
choice = _choice = RANDOM.choice


def seed(val):
    """Set the seed for any subsequent random values/choices

    :param val: The random seed value
    """
    RANDOM.seed(val)


def randint(a, b=None):
    """Return a random integer

    :param int a: Either the minimum value (inclusive) if ``b`` is set, or
    the maximum value if ``b`` is not set (non-inclusive, in which case the minimum
    is implicitly 0)
    :param int b: The maximum value to generate (non-inclusive)
    :returns: int
    """
    # need to minus 1 b/c randint has an inclusive maximum
    if b is None:
        return _randint(0, a-1)
    else:
        return _randint(a, b-1)


def randfloat(a, b=None):
    """Return a random float

    :param float a: Either the minimum value (inclusive) if ``b`` is set, or
    the maximum value if ``b`` is not set (non-inclusive, in which case the minimum
    is implicitly 0.0)
    :param float b: The maximum value to generate (non-inclusive)
    :returns: float
    """
    if b is None:
        max_ = a
        min_ = 0.0
    else:
        min_ = a
        max_ = b

    diff = max_ - min_
    res = _random()
    res *= diff
    res += min_
    return res


def maybe(prob=0.5):
    """Return ``True`` with ``prob`` probability.

    :param float prob: The probability ``True`` will be returned
    :returns: bool
    """
    return _random() < prob


def data(length, charset):
    """Generate ``length`` random characters from charset ``charset``

    :param int length: The number of characters to randomly generate
    :param str charset: The charset of characters to choose from
    :returns: str
    """
    return "".join(_choice(charset) for x in range(length))
