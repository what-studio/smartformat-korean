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
from .particles import CombinableParticle, Euro, Ida, Particle


__all__ = ['ko']


#: Known Korean particles.
PARTICLES = [
    # Simple allomorphic rule.
    Particle(u'은', u'는'),
    Particle(u'이', u'가'),
    Particle(u'을', u'를'),
    CombinableParticle(u'과', u'와'),
    # Special rule after 'ㄹ'.
    Euro,
    # Vocative particles.
    Particle(u'아', u'야'),
    Particle(u'이여', u'여'),
    Particle(u'이시여', u'시여'),
    # Invariant particles.
    Particle(u'의'),
    Particle(u'도'),
    CombinableParticle(u'만'),
    CombinableParticle(u'에'),
    CombinableParticle(u'께'),
    CombinableParticle(u'뿐'),
    CombinableParticle(u'보다'),
    CombinableParticle(u'밖에'),
    CombinableParticle(u'같이'),
    CombinableParticle(u'부터'),
    CombinableParticle(u'까지'),
    CombinableParticle(u'마저'),
    CombinableParticle(u'조차'),
    CombinableParticle(u'마냥'),
    CombinableParticle(u'처럼'),
    CombinableParticle(u'하고'),
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
