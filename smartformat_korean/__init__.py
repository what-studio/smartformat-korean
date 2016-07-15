# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean
   ~~~~~~~~~~~~~~~~~~~~~~

   A SmartFormat extension for Korean.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from numbers import Number

import six

from tossi import parse_tolerance_style, registry
from tossi.coda import guess_coda
from tossi.hangul import is_hangul
from tossi.particles import TOLERANCE_STYLE


__all__ = ['ko', 'KoreanExtension']


class KoreanExtension(object):
    """Chooses different allomorphic forms for Korean particles.

    Implicit Spec: `{:[-]particle}`
    Explicit Spec: `{:ko(particle):item}`

    Example::

       >>> smart.format(u'{name:은} {alt:로} 불린다.',
       ...              name=u'나오', alt=u'검은사신')
       나오는 검은사신으로 불린다.
       >>> smart.format(u'{subj:는} {obj:다}.',
       ...              subj=u'대한민국', obj=u'민주공화국')
       대한민국은 민주공화국이다.

    """

    names = ['ko', '']

    def __init__(self, tolerance_style=TOLERANCE_STYLE, guess_coda=guess_coda,
                 registry=registry):
        self.tolerance_style = parse_tolerance_style(tolerance_style, registry)
        self.guess_coda = guess_coda
        self.registry = registry

    def __call__(self, formatter, value, name, option, format):
        if not name:
            # Resolve implicit arguments.
            if format.startswith(u'-'):
                __, __, option = format.partition(u'-')
                format = u''
            else:
                option, format = format, u'{}'
            if not option:
                return
            elif not all(is_hangul(l) or l in u'()' for l in option):
                # All option letters have to be Hangul
                # to use this extension implicitly.
                return
        word, form = value, option
        if isinstance(word, six.string_types):
            pass
        elif isinstance(word, Number):
            word = six.text_type(word)
        particle = self.registry.get(form)
        suffix = particle.allomorph(word, form,
                                    tolerance_style=self.tolerance_style,
                                    guess_coda=self.guess_coda)
        return formatter.format(format, value) + suffix


#: The default Korean extension object with the most common tolerance style.
ko = KoreanExtension()
