# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean
   ~~~~~~~~~~~~~~~~~~~~~~

   A SmartFormat extension for Korean.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import re

from .hangul import is_hangul
from .particles import Euro, Ida, Particle


__all__ = ['ko', 'KoreanExtension']


#: Known Korean particles.
PARTICLES = [
    # Simple allomorphic rule:
    Particle(u'이', u'가', final=True),
    Particle(u'을', u'를', final=True),
    Particle(u'은', u'는'),  # "은(는)" includes "은(는)커녕".
    Particle(u'과', u'와'),
    # Vocative particles:
    Particle(u'아', u'야', final=True),
    Particle(u'이여', u'여', final=True),
    Particle(u'이시여', u'시여', final=True),
    # Invariant particles:
    Particle(u'의', final=True),
    Particle(u'도', final=True),
    Particle(u'만'),
    Particle(u'에'),
    Particle(u'께'),
    Particle(u'뿐'),
    Particle(u'하'),
    Particle(u'보다'),
    Particle(u'밖에'),
    Particle(u'같이'),
    Particle(u'부터'),
    Particle(u'까지'),
    Particle(u'마저'),
    Particle(u'조차'),
    Particle(u'마냥'),
    Particle(u'처럼'),
    Particle(u'커녕'),
    # Special particles:
    Euro,
]


# Index the particles.
patterns = []
_particles = {}
for x, p in enumerate(PARTICLES):
    group = u'_%d' % x
    _particles[group] = p
    patterns.append(u'(?P<%s>%s)' % (group, p.regex_pattern()))
_particle_pattern = re.compile(u'|'.join(patterns))


def resolve_tolerance_style(style):
    if isinstance(style, int):
        return style
    m = _particle_pattern.match(style)
    particle = _particles[m.lastgroup]
    if len(particle.tolerances) != 4:
        raise ValueError('Set tolerance style by general allomorphic particle')
    return particle.tolerances.index(style)


class KoreanExtension(object):
    """Chooses different allomorphic forms for Korean particles.

    Implicit Spec: `{:[-]particle}`
    Explicit Spec: `{:ko(particle):item}`

    Example::

       >>> smart.format(u'{name:은} {alt:로} 불린다.',
       ...              name=u'나오', alt=u'검은사신')
       나오는 검은사신으로 불린다.
       >>> smart.format(u'{subj:는} {obj:다}.',
       ...              subj=u'대한민국', obj=u'민주공화국')
       대한민국은 민주공화국이다.

    """

    names = ['ko', '']

    def __init__(self, tolerance_style=0):
        self.tolerance_style = resolve_tolerance_style(tolerance_style)

    def __call__(self, formatter, value, name, option, format):
        if not name:
            # Resolve implicit arguments.
            if format.startswith(u'-'):
                __, __, option = format.partition(u'-')
                format = u''
            else:
                option, format = format, u'{}'
            if not option:
                return
            elif not all(is_hangul(l) or l in u'()' for l in option):
                # All option letters have to be Hangul
                # to use this extension implicitly.
                return
        m = _particle_pattern.match(option)
        if m is None:
            particle = Ida
        else:
            particle = _particles[m.lastgroup]
        suffix = particle[value:option:self.tolerance_style]
        return formatter.format(format, value) + suffix


#: The default Korean extension object with the most common tolerance style.
ko = KoreanExtension()
