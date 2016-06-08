# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean.particles
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Models for Korean allomorphic particles.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from itertools import chain
import re

from bidict import bidict
from six import PY2, python_2_unicode_compatible, with_metaclass

from .coda import guess_coda, pick_coda_from_letter
from .hangul import combine_words, join_phonemes, split_phonemes
from .utils import cached_property


__all__ = ['generate_tolerances', 'Euro', 'Ida', 'Particle']


def generate_tolerances(form1, form2):
    """Generates all reasonable tolerant particle forms::

    >>> set(generate_tolerances(u'이', u'가'))
    set([u'이(가)', u'(이)가', u'가(이)', u'(가)이'])
    >>> set(generate_tolerances(u'이면', u'면'))
    set([u'(이)면'])

    """
    if form1 == form2:
        # Tolerance not required.
        return
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


class ParticleMeta(type):

    def __new__(meta, name, bases, attrs):
        if '__slots__' in attrs:
            attrs['__slots__'] += ('__cache__',)
        return super(ParticleMeta, meta).__new__(meta, name, bases, attrs)


@python_2_unicode_compatible
class Particle(with_metaclass(ParticleMeta)):
    """Represents a Korean allomorphic particle as known as "조사".

    This also implements the general allomorphic rule for most common
    particles.

    """

    __slots__ = ('form1', 'form2', 'final')

    def __init__(self, form1, form2=None, final=False):
        self.form1 = form1
        self.form2 = form1 if form2 is None else form2
        self.final = final

    @cached_property
    def tolerances(self):
        """The tuple containing all the possible tolerant forms."""
        return tuple(generate_tolerances(self.form1, self.form2))

    def tolerance(self, style=0):
        """Gets a tolerant form."""
        try:
            return self.tolerances[style]
        except IndexError:
            return self.tolerances[0]

    def rule(self, coda, tolerance_style=0):
        """Determines one of allomorphic forms based on a coda."""
        if coda is None:
            return self.tolerance(tolerance_style)
        elif coda:
            return self.form1
        else:
            return self.form2

    def allomorph(self, word, form, tolerance_style=0):
        """Determines one of allomorphic forms based on a word.

        .. see also:: :meth:`allomorph`.

        """
        suffix = self.match(form)
        if suffix is None:
            return None
        coda = guess_coda(word)
        return combine_words(self.rule(coda, tolerance_style), suffix)

    def __getitem__(self, key):
        """The syntax sugar to determine one of allomorphic forms based on a
        word::

           eun = Particle(u'은', u'는')
           assert eun[u'나오'] == u'는'
           assert eun[u'모리안'] == u'은'

        """
        if isinstance(key, slice):
            word, form, tolerance_style = key.start, key.stop, key.step or 0
        else:
            word, form, tolerance_style = key, self.form1, 0
        return self.allomorph(word, form, tolerance_style)

    @cached_property
    def regex(self):
        return re.compile(self.regex_pattern())

    @cached_property
    def forms(self):
        """The tuple containing the given forms and all the possible tolerant
        forms.  Longer is first.
        """
        seen = set()
        saw = seen.add
        forms = chain([self.form1, self.form2], self.tolerances)
        unique_forms = (x for x in forms if x and not (x in seen or saw(x)))
        return tuple(sorted(unique_forms, key=len, reverse=True))

    def match(self, form):
        m = self.regex.match(form)
        if m is None:
            return None
        x = m.end()
        if self.final or m.group() == self.forms[m.lastindex - 1]:
            return form[x:]
        coda = pick_coda_from_letter(form[x - 1])
        return coda + form[x:]

    def regex_pattern(self):
        if self.final:
            return u'^(?:%s)$' % u'|'.join(re.escape(f) for f in self.forms)
        patterns = []
        for form in self.forms:
            try:
                onset, nucleus, coda = split_phonemes(form[-1])
            except ValueError:
                coda = None
            if coda == u'':
                start = form[-1]
                end = join_phonemes(onset, nucleus, u'ㅎ')
                pattern = re.escape(form[:-1]) + u'[%s-%s]' % (start, end)
            else:
                pattern = re.escape(form)
            patterns.append(pattern)
        return u'^(?:%s)' % u'|'.join(u'(%s)' % p for p in patterns)

    def __str__(self):
        return self.tolerance

    def __repr__(self):
        return '<Particle: ' + (repr if PY2 else str)(self.tolerance) + '>'


class SingletonParticleMeta(ParticleMeta):

    def __new__(meta, name, bases, attrs):
        base_meta = super(SingletonParticleMeta, meta)
        cls = base_meta.__new__(meta, name, bases, attrs)
        if not issubclass(cls, Particle):
            raise TypeError('Not particle class')
        # Instantiate directly instead of returning a class.
        return cls()


class SingletonParticle(Particle):

    # Concrete classes should set these strings.
    form1 = form2 = final = NotImplemented

    def __init__(self):
        pass


def singleton_particle(*bases):
    """Defines a singleton instance immediately when defining the class.  The
    name of the class will refer the instance instead.
    """
    return with_metaclass(SingletonParticleMeta, SingletonParticle, *bases)


class Euro(singleton_particle(Particle)):
    """Particles starting with "으로" have a special allomorphic rule after
    coda "ㄹ".  "으로" can also be extended with some of suffixes such as
    "으로서", "으로부터".
    """

    __slots__ = ()

    form1 = u'으로'
    form2 = u'로'
    final = False

    def rule(self, coda, tolerance_style=0):
        if coda is None:
            return self.tolerance(tolerance_style)
        elif coda and coda != u'ㄹ':
            return self.form1
        else:
            return self.form2


class Ida(singleton_particle(Particle)):
    """"이다" is a verbal prticle.  Like other Korean verbs, it is also
    fusional.
    """

    __slots__ = ()

    form1 = u'이'
    form2 = u''
    final = False

    #: Matches with initial "이" or "(이)" to normalize fusioned verbal forms.
    I_PATTERN = re.compile(u'^이|\(이\)')

    #: The mapping for vowels which should be transformed by /j/ injection.
    J_INJECTIONS = bidict({u'ㅓ': u'ㅕ', u'ㅔ': u'ㅖ'})

    def allomorph(self, word, form, tolerance_style=0):
        suffix = self.I_PATTERN.sub(u'', form)
        coda = guess_coda(word)
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
        return self.rule(coda, tolerance_style) + suffix
