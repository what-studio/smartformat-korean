# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean.particles
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Models for Korean allomorphic particles.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import itertools
import re

from bidict import bidict
from six import PY2, with_metaclass

from .hangul import join_phonemes, split_phonemes


__all__ = ['Particle', 'SpecialParticle', 'Euro', 'Ida']


#: Matches to string should be ignored when selecting an allomorph.
BLIND_PATTERN = re.compile(r'''
    (?:
        \( .*? \)
    |
        [!@#$%^&*?,.:;'"\[\]{}<>]+
    )$
''', re.VERBOSE)


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


def combine_tolerant_forms(form1, form2):
    """Generates tolerant particle forms::

    >>> set(combine_tolerant_forms(u'이', u'가'))
    set([u'이(가)', u'(이)가', u'가(이)', u'(가)이'])
    >>> set(combine_tolerant_forms(u'이면', u'면'))
    set([u'(이)면'])

    """
    if not (form1 and form2):
        # Some of forms is empty.
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
            self._tolerance = next(self.tolerant_forms())
        return self._tolerance

    def tolerant_forms(self):
        """Yields all reasonable tolerant forms."""
        return combine_tolerant_forms(self.form1, self.form2)

    def __call__(self, word, *args, **kwargs):
        """Selects an allomorphic form for the given word."""
        word = BLIND_PATTERN.sub(u'', word)
        coda = pick_coda(word[-1]) if word else None
        return self.allomorph(coda, *args, **kwargs)

    def __iter__(self):
        """Iterates for all allomorphic forms."""
        return itertools.chain([self.form1, self.form2], self.tolerant_forms())

    def allomorph(self, coda):
        """Determines one of allomorphic forms based on a Hangul jongseung."""
        if coda is None:
            return self.tolerance
        elif coda:
            return self.form1
        else:
            return self.form2

    def __unicode__(self):
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
