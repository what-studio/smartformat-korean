# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean
   ~~~~~~~~~~~~~~~~~~~~~~

   A SmartFormat extension for Korean.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import re

from smartformat import extension

from .hangul import is_hangul
from .particles import Euro, Ida, Particle


__all__ = ['ko']


#: Known Korean particles.
PARTICLES = [
    # Simple allomorphic rule.
    Particle(u'이', u'가', final=True),
    Particle(u'을', u'를', final=True),
    Particle(u'은', u'는'),
    Particle(u'과', u'와'),
    # Special rule after 'ㄹ'.
    Euro,
    # Invariant particles.
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
    # Vocative particles.
    Particle(u'아', u'야', final=True),
    Particle(u'이여', u'여', final=True),
    Particle(u'이시여', u'시여', final=True),
]
patterns = []
_particles = {}
for x, p in enumerate(PARTICLES):
    group = u'_%d' % x
    _particles[group] = p
    patterns.append(u'(?P<%s>%s)' % (group, p.regex_pattern()))
_particle_pattern = re.compile(u'|'.join(patterns))


@extension(['ko', ''])
def ko(formatter, value, name, option, format):
    """Chooses different allomorphic forms for Korean particles.

    Implicit Spec: `{:[-]particle}`
    Explicit Spec: `{:ko(particle):item}`

    Example::

       >>> smart.format(u'{pokemon:은} {skill:을} 시전했다!',
       ...              pokemon=u'피카츄', skill=u'전광석화')
       피카츄는 전광석화를 시전했다!
       >>> smart.format(u'{subj:는} {obj:다}.',
       ...              subj=u'대한민국', obj=u'민주공화국')
       대한민국은 민주공화국이다.

    """
    if not name:
        if format.startswith(u'-'):
            __, __, option = format.partition(u'-')
            format = u''
        else:
            option, format = format, u'{}'
        if not option or not all(is_hangul(l) or l in u'()' for l in option):
            # All option letters have to be Hangul
            # to use this extension implicitly.
            return
    m = _particle_pattern.match(option)
    if m is None:
        particle = Ida
    else:
        particle = _particles[m.lastgroup]
    suffix = particle[value:option]
    return formatter.format(format, value) + suffix
