# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean.tolerance
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Utilities for tolerant particle forms.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from six import integer_types


__all__ = ['generate_tolerances', 'tolerance_style']


# Tolerance styles:
FORM1_AND_OPTIONAL_FORM2 = 0
OPTIONAL_FORM1_AND_FORM2 = 1
FORM2_AND_OPTIONAL_FORM1 = 2
OPTIONAL_FORM2_AND_FORM1 = 3


def generate_tolerances(form1, form2):
    """Generates all reasonable tolerant particle forms::

    >>> set(generate_tolerances(u'이', u'가'))
    set([u'이(가)', u'(이)가', u'가(이)', u'(가)이'])
    >>> set(generate_tolerances(u'이면', u'면'))
    set([u'(이)면'])

    """
    if form1 == form2:
        # Tolerance not required.
        return
    if not (form1 and form2):
        # Null allomorph exists.
        yield u'(%s)' % (form1 or form2)
        return
    len1, len2 = len(form1), len(form2)
    if len1 != len2:
        longer, shorter = (form1, form2) if len1 > len2 else (form2, form1)
        if longer.endswith(shorter):
            # Longer form ends with shorter form.
            yield u'(%s)%s' % (longer[:-len(shorter)], shorter)
            return
    # No similarity between two forms.
    for form1, form2 in [(form1, form2), (form2, form1)]:
        yield u'%s(%s)' % (form1, form2)
        yield u'(%s)%s' % (form1, form2)


def tolerance_style(style, registry):
    """Resolves a tolerance style of the given tolerant particle form::

    >>> tolerance_style(u'은(는)', registry)
    0
    >>> tolerance_style(u'(은)는', registry)
    1
    >>> tolerance_style(OPTIONAL_FORM2_AND_FORM1, registry)
    3

    """
    if isinstance(style, integer_types):
        return style
    particle = registry.get(style)
    if len(particle.tolerances) != 4:
        raise ValueError('Set tolerance style by general allomorphic particle')
    return particle.tolerances.index(style)
