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
from six import PY2, python_2_unicode_compatible, with_metaclass

from .coda import guess_coda
from .hangul import join_phonemes, split_phonemes


__all__ = ['combine_tolerances', 'Euro', 'Ida', 'Particle', 'SpecialParticle']


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


DEFAULT_SLOTS = ('_tolerance',)


@python_2_unicode_compatible
class Particle(object):
    """Represents a Korean allomorphic particle as known as "조사".

    This also implements the general allomorphic rule for most common
    particles.  If some particle has a exceptional rule, inherit
    :class:`SpecialParticle` instead.

    """

    __slots__ = ('form1', 'form2') + DEFAULT_SLOTS

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

    def allomorph(self, coda):
        """Determines one of allomorphic forms based on a coda."""
        if coda is None:
            return self.tolerance
        elif coda:
            return self.form1
        else:
            return self.form2

    def allomorph_by_word(self, word, *args, **kwargs):
        """Determines one of allomorphic forms based on a word.

        .. see also:: :meth:`allomorph`.

        """
        return self.allomorph(guess_coda(word), *args, **kwargs)

    def __getitem__(self, word):
        """The syntax sugar to determine one of allomorphic forms based on a
        word::

           eun = Particle(u'은', u'는')
           assert eun[u'나오'] == u'는'
           assert eun[u'모리안'] == u'은'

        """
        return self.allomorph_by_word(word)

    def __iter__(self):
        """Iterates for all allomorphic forms."""
        return itertools.chain([self.form1, self.form2], self.tolerances())

    def __str__(self):
        return self.tolerance

    def __repr__(self):
        return '<Particle: ' + (repr if PY2 else str)(self.tolerance) + '>'


class SingletonParticleMeta(type):

    def __new__(meta, name, bases, attrs):
        base_meta = super(SingletonParticleMeta, meta)
        cls = base_meta.__new__(meta, name, bases, attrs)
        if not issubclass(cls, Particle):
            raise TypeError('Not particle class')
        # Instantiate directly instead of returning a class.
        return cls()


def singleton_particle(*bases):
    return with_metaclass(SingletonParticleMeta, *bases)


class SpecialParticle(Particle):
    """The base class for special particles which have uncommon allomorphic
    rule.
    """

    # Concrete classes should set these strings.
    form1 = form2 = NotImplemented

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        arg = self.__class__.__name__ if PY2 else self.tolerance
        return '<Particle(special): %s>' % arg


class InflectingParticle(SpecialParticle):
    """The base class for special particles but can be inflected."""

    def __getitem__(self, word_and_form):
        word, form = word_and_form.start, word_and_form.stop,
        return self.allomorph_by_word(word, form)

    def allomorph(self, coda, form):
        raise NotImplementedError


class Euro(singleton_particle(InflectingParticle)):
    """Particles starting with "으로" have a special allomorphic rule after
    coda "ㄹ".  "으로" can also be extended with some of suffixes such as
    "으로서", "으로부터".
    """

    __slots__ = DEFAULT_SLOTS

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


class Ida(singleton_particle(InflectingParticle)):
    """"이다" is a verbal prticle.  Like other Korean verbs, it is also
    fusional.
    """

    __slots__ = DEFAULT_SLOTS

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
