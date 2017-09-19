#!/usr/bin/env python
# encoding: utf-8


"""
Gramfuzz utility functions
"""


import gramfuzz


def val(val, pre=None, shortest=False):
    """Build the provided value, while properly handling
    native Python types, :any:`gramfuzz.fields.Field` instances, and :any:`gramfuzz.fields.Field`
    subclasses.

    :param list pre: The prerequisites list
    :returns: str
    """
    if pre is None:
        pre = []

    fields = gramfuzz.fields
    MF = fields.MetaField
    F = fields.Field
    if type(val) is MF:
        val = val()

    if isinstance(val, F):
        val = str(val.build(pre, shortest=shortest))

    return str(val)
