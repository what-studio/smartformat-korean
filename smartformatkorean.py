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


INITIALS = list(u'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
VOWELS = list(u'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ')
FINALS = [None]
FINALS.extend(u'ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')

NUM_INITIALS = len(INITIALS)
NUM_VOWELS = len(VOWELS)
NUM_FINALS = len(FINALS)

FORM1, FORM2, DEFAULT = 0, 1, 2
FIRST_HANGUL_OFFSET = ord(u'가')
ENDING_BRACKET_PATTERN = re.compile(r'\(.*?\)$')


def combine_forms(form1, form2):
    """Generates a general combination form for Korean particles."""
    return u'%s(%s)' % (form1, form2)


def split_phonemes(letter, initial=True, vowel=True, final=True):
    """Splits Korean phonemes as known as "자소" from a Hangul letter.

    :returns: (initial, vowel, final)
    :raises ValueError: `letter` is not a Hangul single letter.

    """
    if not u'가' <= letter <= u'힣' or len(letter) != 1:
        raise ValueError('Not Hangul letter: %r' % letter)
    offset = ord(letter) - FIRST_HANGUL_OFFSET
    phonemes = [None] * 3
    if initial:
        phonemes[0] = INITIALS[offset / (NUM_VOWELS * NUM_FINALS)]
    if vowel:
        phonemes[1] = VOWELS[(offset / NUM_FINALS) % NUM_VOWELS]
    if final:
        phonemes[2] = FINALS[offset % NUM_FINALS]
    return tuple(phonemes)


class Particle(object):
    """Represents a Korean particle as known as "조사" in Korean."""

    def __init__(self, form1, form2, default=None):
        self.form1 = form1
        self.form2 = form2
        if default is None:
            self.default = combine_forms(form1, form2)
        else:
            self.default = default

    def __call__(self, word):
        """Selects an allomorphic form for the given word."""
        word = ENDING_BRACKET_PATTERN.sub(u'', word)
        try:
            __, __, final = split_phonemes(word[-1], initial=False,
                                           vowel=False, final=True)
        except ValueError:
            return self.default
        else:
            return self.allomorph(final)

    def __iter__(self):
        """Iterates for all allomorphic forms."""
        return iter([self.default, self.form1, self.form2])

    def allomorph(self, final):
        """Determines one of allomorphic forms based on a Hangul jongseung."""
        return self.form2 if final is None else self.form1


class ParticleRieulSpecialized(Particle):
    """The special case of Korean particle after final Rieul such as
    "으로".
    """

    def allomorph(self, final):
        if final is None or final == u'ㄹ':
            return self.form2
        else:
            return self.form1


class VerbalParticle(Particle):
    """The special case of Korean verbal particle "이다"."""

    def normalize_verb(self, verb):
        return re.sub(r'^이|\(이\)', u'', verb)

    def __call__(self, word, verb):
        word = ENDING_BRACKET_PATTERN.sub(u'', word)
        verb = self.normalize_verb(verb)
        try:
            final = pick_final(word)
        except ValueError:
            return self.default
        else:
            return self.allomorph(final)

    # def allormorph(self, final):



#: Supported Korean particles.
PARTICLES = [
    # Simple allomorphic rule.
    Particle(u'은', u'는'),
    Particle(u'이', u'가'),
    Particle(u'을', u'를'),
    Particle(u'과', u'와'),
    # Except after 'ㄹ'.
    ParticleRieulSpecialized(u'으로', u'로', u'(으)로'),
    # Vocative particles.
    Particle(u'아', u'야'),
    Particle(u'이여', u'여', u'(이)여'),
    Particle(u'이시여', u'시여', u'(이)시여'),
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
