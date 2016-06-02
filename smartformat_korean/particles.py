# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean.particles
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Models for Korean allomorphic particles.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from bisect import bisect_right
from decimal import Decimal
import itertools
import re
import unicodedata

from bidict import bidict
from six import PY2, python_2_unicode_compatible, with_metaclass

from .hangul import join_phonemes, split_phonemes


__all__ = ['combine_tolerances', 'Euro', 'Ida', 'Particle', 'pick_coda',
           'pick_coda_from_decimal', 'SpecialParticle']


def pick_coda(letter):
    """Picks only a coda from a Hangul letter.  It returns ``None`` if the
    given letter is not Hangul.
    """
    try:
        __, __, coda = \
            split_phonemes(letter, onset=False, nucleus=False, coda=True)
    except ValueError:
        return None
    else:
        return coda


#: Matches to a decimal at the end of a word.
DECIMAL_PATTERN = re.compile(r'[0-9]+(\.[0-9]+)?$')


# Data for picking coda from a decimal.
DIGITS = u'영일이삼사오육칠팔구'
EXPS = {1: u'십', 2: u'백', 3: u'천', 4: u'만',
        8: u'억', 12: u'조', 16: u'경', 20: u'해',
        24: u'자', 28: u'양', 32: u'구', 36: u'간',
        40: u'정', 44: u'재', 48: u'극', 52: u'항하사',
        56: u'아승기', 60: u'나유타', 64: u'불가사의', 68: u'무량대수',
        72: u'겁', 76: u'업'}
DIGIT_CODAS = [pick_coda(x[-1]) for x in DIGITS]
EXP_CODAS = {exp: pick_coda(x[-1]) for exp, x in EXPS.items()}
EXP_INDICES = list(sorted(EXPS.keys()))


# Mark the first unreadable exponent.
_unreadable_exp = max(EXP_INDICES) + 4
EXP_CODAS[_unreadable_exp] = None
EXP_INDICES.append(_unreadable_exp)
del _unreadable_exp


def pick_coda_from_decimal(decimal):
    """Picks only a coda from a decimal."""
    decimal = Decimal(decimal)
    __, digits, exp = decimal.as_tuple()
    if exp < 0:
        return DIGIT_CODAS[digits[-1]]
    __, digits, exp = decimal.normalize().as_tuple()
    index = bisect_right(EXP_INDICES, exp) - 1
    if index < 0:
        return DIGIT_CODAS[digits[-1]]
    else:
        return EXP_CODAS[EXP_INDICES[index]]


# Patterns which match to insignificant letters at the end of words.
INSIGNIFICANT_PARENTHESIS_PATTERN = re.compile(r'\(.*?\)$')
INSIGNIFICANT_UNICODE_CATEGORY_PATTERN = re.compile(r'^([PZ].|Sk)$')


def pick_significant(word):
    """Gets a word which removes insignificant letters at the end of the given
    word::

    >>> pick_significant(u'넥슨(코리아)')
    넥슨
    >>> pick_significant(u'메이플스토리...')
    메이플스토리

    """
    if not word:
        return word
    x = len(word)
    while x > 0:
        x -= 1
        l = word[x]
        # Skip a complete parenthesis.
        if l == u')':
            m = INSIGNIFICANT_PARENTHESIS_PATTERN.search(word[:x + 1])
            if m is not None:
                x = m.start()
            continue
        # Skip unreadable characters such as punctuations.
        unicode_category = unicodedata.category(l)
        if INSIGNIFICANT_UNICODE_CATEGORY_PATTERN.match(unicode_category):
            continue
        break
    return word[:x + 1]


def combine_tolerances(form1, form2):
    """Generates all reasonable tolerant particle forms::

    >>> set(combine_tolerances(u'이', u'가'))
    set([u'이(가)', u'(이)가', u'가(이)', u'(가)이'])
    >>> set(combine_tolerances(u'이면', u'면'))
    set([u'(이)면'])

    """
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


@python_2_unicode_compatible
class Particle(object):
    """Represents a Korean allomorphic particle as known as "조사".

    This also implements the general allomorphic rule for most common
    particles.  If some particle has a exceptional rule, inherit
    :class:`SpecialParticle` instead.

    """

    __slots__ = ('form1', 'form2', '_tolerance')

    def __init__(self, form1, form2):
        self.form1 = form1
        self.form2 = form2

    @property
    def tolerance(self):
        """The representative tolerant form."""
        if not hasattr(self, '_tolerance'):
            self._tolerance = next(self.tolerances())
        return self._tolerance

    def tolerances(self):
        """Yields all reasonable tolerant forms."""
        return combine_tolerances(self.form1, self.form2)

    def __call__(self, word, *args, **kwargs):
        """Selects an allomorphic form for the given word."""
        word = pick_significant(word)
        decimal_match = DECIMAL_PATTERN.search(word)
        if decimal_match:
            coda = pick_coda_from_decimal(decimal_match.group(0))
        else:
            coda = pick_coda(word[-1]) if word else None
        return self.allomorph(coda, *args, **kwargs)

    def __iter__(self):
        """Iterates for all allomorphic forms."""
        return itertools.chain([self.form1, self.form2], self.tolerances())

    def allomorph(self, coda):
        """Determines one of allomorphic forms based on a Hangul jongseung."""
        if coda is None:
            return self.tolerance
        elif coda:
            return self.form1
        else:
            return self.form2

    def __str__(self):
        return self.tolerance

    def __repr__(self):
        return '<Particle: ' + (repr if PY2 else str)(self.tolerance) + '>'


class SpecialParticleMeta(type):

    def __new__(meta, name, bases, attrs):
        if '__slots__' in attrs:
            attrs['__slots__'] += ('_tolerance',)
        base_meta = super(SpecialParticleMeta, meta)
        cls = base_meta.__new__(meta, name, bases, attrs)
        if bases == (Particle,):
            return cls
        # Instantiate directly instead of returning a class.
        return cls()


class SpecialParticle(with_metaclass(SpecialParticleMeta, Particle)):
    """The base class for special particles which have uncommon allomorphic
    rule.
    """

    __slots__ = ()

    # Concrete classes should set these strings.
    form1 = form2 = NotImplemented

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, word, form):
        return super(SpecialParticle, self).__call__(word, form)

    def __repr__(self):
        arg = self.__class__.__name__ if PY2 else self.tolerance
        return '<Particle(special): %s>' % arg


class Euro(SpecialParticle):
    """Particles starting with "으로" have a special allomorphic rule after
    coda "ㄹ".  "으로" can also be extended with some of suffixes such as
    "으로서", "으로부터".
    """

    __slots__ = ()

    form1 = u'으'
    form2 = u''

    #: Matches with initial "으" or "(으)" before "로".
    PREFIX_PATTERN = re.compile(u'^(으|\(으\))?로')

    def allomorph(self, coda, form):
        m = self.PREFIX_PATTERN.match(form)
        if not m:
            # The given form doesn't start with "(으)로".  Don't handle.
            return
        # Remove initial "으" or "(으)" to make a suffix.
        suffix = form[max(0, m.end(1)):]
        if coda is None:
            prefix = self.tolerance
        elif coda and coda != u'ㄹ':
            prefix = self.form1
        else:
            prefix = self.form2
        return prefix + suffix


class Ida(SpecialParticle):
    """"이다" is a verbal prticle.  Like other Korean verbs, it is also
    fusional.
    """

    __slots__ = ()

    form1 = u'이'
    form2 = u''

    #: Matches with initial "이" or "(이)" to normalize fusioned verbal forms.
    I_PATTERN = re.compile(u'^이|\(이\)')

    #: The mapping for vowels which should be transformed by /j/ injection.
    J_INJECTIONS = bidict({u'ㅓ': u'ㅕ', u'ㅔ': u'ㅖ'})

    def allomorph(self, coda, form):
        suffix = self.I_PATTERN.sub(u'', form)
        next_onset, next_nucleus, next_coda = split_phonemes(suffix[0])
        if next_onset == u'ㅇ':
            if next_nucleus == u'ㅣ':
                # No allomorphs when a form starts with "이" and has a coda.
                return suffix
            mapping = None
            if coda == u'' and next_nucleus in self.J_INJECTIONS:
                # Squeeze "이어" or "이에" to "여" or "예"
                # after a word which ends with a nucleus.
                mapping = self.J_INJECTIONS
            elif coda != u'' and next_nucleus in self.J_INJECTIONS.inv:
                # Lengthen "여" or "예" to "이어" or "이에"
                # after a word which ends with a consonant.
                mapping = self.J_INJECTIONS.inv
            if mapping is not None:
                next_nucleus = mapping[next_nucleus]
                next_letter = join_phonemes(u'ㅇ', next_nucleus, next_coda)
                suffix = next_letter + suffix[1:]
        return Particle.allomorph(self, coda) + suffix
