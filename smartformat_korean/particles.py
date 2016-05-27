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

    def __call__(self, word, *args, **kwargs):
        """Selects an allomorphic form for the given word."""
        word = BLIND_PATTERN.sub(u'', word)
        coda = pick_coda(word[-1]) if word else None
        return self.allomorph(coda, *args, **kwargs)

    def __iter__(self):
        """Iterates for all allomorphic forms."""
        return iter([self.default, self.form1, self.form2])

    def allomorph(self, coda):
        """Determines one of allomorphic forms based on a Hangul jongseung."""
        if coda is None:
            return self.default
        elif coda:
            return self.form1
        else:
            return self.form2

    def __unicode__(self):
        return self.default

    def __repr__(self):
        return '<Particle: ' + (repr if PY2 else str)(self.default) + '>'

    @staticmethod
    def combine_forms(form1, form2):
        """Defines a general combination form for Korean particles."""
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

    # Concrete classes should set these strings.
    form1 = form2 = default = NotImplemented

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, word, form):
        return super(SpecialParticle, self).__call__(word, form)

    def __repr__(self):
        arg = self.__class__.__name__ if PY2 else self.default
        return '<Particle(special): %s>' % arg


class Euro(SpecialParticle):
    """Particles starting with "으로" have a special allomorphic rule after
    coda Rieul.  "으로" can be extended with some of suffixes such as
    "으로서", "으로부터".
    """

    form1 = u'으'
    form2 = u''
    default = u'(으)'

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
            prefix = self.default
        elif coda and coda != u'ㄹ':
            prefix = self.form1
        else:
            prefix = self.form2
        return prefix + suffix


class Ida(SpecialParticle):
    """"이다" is a verbal prticle.  Like other Korean verbs, it is also
    fusional.
    """

    form1 = u'이'
    form2 = u''
    default = u'(이)'

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
