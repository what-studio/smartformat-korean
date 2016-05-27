# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean.particles
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Models for Korean allomorphic particles.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
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
        [!@#$%^&*?]+
    )$
''', re.VERBOSE)


def pick_final(letter):
    """Picks only a final Hangul consonant from a Hangul letter."""
    __, __, final = \
        split_phonemes(letter, initial=False, vowel=False, final=True)
    return final


class Particle(object):
    """Represents a Korean allomorphic particle as known as "조사".

    This also implements the general allomorphic rule for most common
    particles.  If some particle has a exceptional rule, inherit
    :class:`SpecialParticle` instead.

    """

    def __init__(self, form1, form2, default=None):
        self.form1 = form1
        self.form2 = form2
        if default is None:
            self.default = self.combine_forms(form1, form2)
        else:
            self.default = default

    def __call__(self, word):
        """Selects an allomorphic form for the given word."""
        word = BLIND_PATTERN.sub(u'', word)
        try:
            final = pick_final(word[-1])
        except (ValueError, IndexError):
            return self.default
        else:
            return self.allomorph(final)

    def __iter__(self):
        """Iterates for all allomorphic forms."""
        return iter([self.default, self.form1, self.form2])

    def allomorph(self, final):
        """Determines one of allomorphic forms based on a Hangul jongseung."""
        return self.form2 if final is None else self.form1

    def __unicode__(self):
        return self.default

    def __repr__(self):
        return '<Particle: ' + (repr if PY2 else str)(self.default) + '>'

    @staticmethod
    def combine_forms(form1, form2):
        """Generates a general combination form for Korean particles."""
        return u'%s(%s)' % (form1, form2)


class SpecialParticleMeta(type):

    def __new__(meta, name, bases, attrs):
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

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        arg = self.__class__.__name__ if PY2 else self.default
        return '<Particle(special): %s>' % arg


class Euro(SpecialParticle):
    """"으로" has a special allomorphic rule after final Rieul."""

    form1 = u'으로'
    form2 = u'로'
    default = u'(으)로'

    def allomorph(self, final):
        return self.form2 if final is None or final == u'ㄹ' else self.form1


class Ida(SpecialParticle):
    """"이다" is a verbal prticle.  Like other Korean verbs, it is also
    fusional.
    """

    form1 = u'이'
    form2 = u''
    default = u'(이)'

    j_injections = bidict({u'ㅓ': u'ㅕ', u'ㅔ': u'ㅖ'})
    allomorph = NotImplemented  # This method is not used.

    def normalize_verb(self, verb):
        """Normalizes a verb by removing initial "이" or "(이)"s."""
        return re.sub(u'^이|\(이\)', u'', verb)

    def __call__(self, word, verb):
        word = BLIND_PATTERN.sub(u'', word)
        verb = self.normalize_verb(verb)
        try:
            final = pick_final(word[-1])
        except ValueError:
            final = u''
        next_initial, next_vowel, next_final = split_phonemes(verb[0])
        if next_initial == u'ㅇ':
            if next_vowel == u'ㅣ':
                # No allomorphs when a verb starts with "이" and has a final.
                return verb
            mapping = None
            if final is None and next_vowel in self.j_injections:
                # Squeeze "이어" or "이에" to "여" or "예"
                # after a word which ends with a vowel.
                mapping = self.j_injections
            elif final is not None and next_vowel in self.j_injections.inv:
                # Lengthen "여" or "예" to "이어" or "이에"
                # after a word which ends with a consonant.
                mapping = self.j_injections.inv
            if mapping is not None:
                next_vowel = mapping[next_vowel]
                verb = join_phonemes(u'ㅇ', next_vowel, next_final) + verb[1:]
        # Select an allomorph.
        if final is None:
            return verb
        elif final == u'':
            return u'(이)' + verb
        else:
            return u'이' + verb


if not PY2:
    locals().update({u'으로': Euro, u'이다': Ida})
    __all__.extend([u'으로', u'이다'])
