# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean
   ~~~~~~~~~~~~~~~~~~~~~~

   A SmartFormat extension for Korean.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import functools

from smartformat import extension

from .hangul import is_hangul
from .particles import Euro, Ida, Particle


__all__ = ['ko']


#: Allomorphic Korean particles.
PARTICLES = [
    # Simple allomorphic rule.
    Particle(u'은', u'는'),
    Particle(u'이', u'가'),
    Particle(u'을', u'를'),
    Particle(u'과', u'와'),
    # Vocative particles.
    Particle(u'아', u'야'),
    Particle(u'이여', u'여', u'(이)여'),
    Particle(u'이시여', u'시여', u'(이)시여'),
    # Special particles.
    Euro,
]


# Index particles by their forms.
_particle_index = {}
for p in PARTICLES:
    for form in p:
        if form in _particle_index:
            raise KeyError('Form %r duplicated' % form)
        _particle_index[form] = p


@extension(['ko', ''])
def ko(formatter, value, name, option, format):
    """Chooses different allomorphic forms for Korean particles.

    Implicit Spec: `{:[-]post_position}`
    Explicit Spec: `{:ko(post_position):item}`

    Example::

       >>> smart.format(u'There {num:is an item|are {} items}.', num=1}
       There is an item.
       >>> smart.format(u'There {num:is an item|are {} items}.', num=10}
       There are 10 items.

    """
    if not name:
        if format.startswith(u'-'):
            __, __, option = format.partition(u'-')
            format = u''
        else:
            option, format = format, u'{}'
        if not option or not is_hangul(option[0]):
            return
    try:
        particle = _particle_index[option]
    except KeyError:
        # "이다" is the default particle.
        particle = functools.partial(Ida, verb=option)
    return formatter.format(format, value) + particle(value)
