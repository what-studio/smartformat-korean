# -*- coding: utf-8 -*-
"""
   smartformat_korean
   ~~~~~~~~~~~~~~~~~~

   SmartFormat extensions for Korean.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import re

from smartformat import ext


FORM1, FORM2, DEFAULT = 0, 1, 2
KA_ORD = ord(u'가')
JONGSEONGS = [None]
JONGSEONGS.extend(u'ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')
NUM_JONGSEONGS = len(JONGSEONGS)
ENDING_BRACKET_PATTERN = re.compile(r'\(.*?\)$')


def combine_forms(form1, form2):
    """Generates a general combination form for Korean particles."""
    return u'%s(%s)' % (form1, form2)


def pick_final_jongseong(word):
    """Picks a Hangul jongseong of the final letter of a word.

    :returns: ``None`` or a Hangul jaeum.
    :raises ValueError: given word doesn't end with Hangul.

    """
    final = word[-1]
    if u'가' <= final <= u'힣':
        return JONGSEONGS[(ord(final) - KA_ORD) % NUM_JONGSEONGS]
    else:
        raise ValueError('Not ends with Hangul: %r' % word)


class Particle(object):
    """Represents a Korean particle as known as "조사" in Korean."""

    def __init__(self, form1, form2, default=None):
        self.form1 = form1
        self.form2 = form2
        if default is None:
            self.default = combine_forms(form1, form2)
        else:
            self.default = default

    def allomorph(self, jongseong):
        """Determines one of allomorphic forms based on a Hangul jongseung."""
        return FORM2 if jongseong is None else FORM1

    def __call__(self, word):
        """Selects an allomorphic form for the given word."""
        word = ENDING_BRACKET_PATTERN.sub(u'', word)
        try:
            jongseong = pick_final_jongseong(word)
        except ValueError:
            x = DEFAULT
        else:
            x = self.allomorph(jongseong)
        return {FORM1: self.form1, FORM2: self.form2, DEFAULT: self.default}[x]

    def __iter__(self):
        """Iterates for all allomorphic forms."""
        return iter([self.form1, self.form2, self.default])


class ParticleRieulSpecialized(Particle):
    """The special case of Korean particle after jongseong Rieul such as
    "으로".
    """

    def allomorph(self, jongseong):
        return FORM2 if jongseong is None or jongseong == u'ㄹ' else FORM1


#: Supported Korean particles.
PARTICLES = [
    Particle(u'은', u'는'),
    Particle(u'이', u'가'),
    Particle(u'을', u'를'),
    Particle(u'과', u'와'),
    Particle(u'아', u'야'),
    ParticleRieulSpecialized(u'으로', u'로', u'(으)로'),
]


# Index particles by their forms.
_particle_index = {}
for p in PARTICLES:
    for form in p:
        if form in _particle_index:
            raise KeyError('Form %r duplicated' % form)
        _particle_index[form] = p


@ext(['ko', ''], pass_formatter=True)
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
    try:
        pp = _particle_index[option]
    except KeyError:
        if not name:
            # Just skip to handle when selected implicitly.
            return
        raise ValueError('Unknown Korean particle: %r' % option)
    return formatter.format(format, value) + pp(value)
