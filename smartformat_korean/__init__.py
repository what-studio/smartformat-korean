# -*- coding: utf-8 -*-
"""
   smartformat.ext.korean
   ~~~~~~~~~~~~~~~~~~~~~~

   A SmartFormat extension for Korean.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from .hangul import is_hangul
from .registry import registry
from .tolerance import tolerance_style as _tolerance_style


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

    def __init__(self, tolerance_style=0, registry=registry):
        self.tolerance_style = _tolerance_style(tolerance_style, registry)
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
        particle = self.registry.find(form)
        suffix = particle[word:form:self.tolerance_style]
        return formatter.format(format, value) + suffix


#: The default Korean extension object with the most common tolerance style.
ko = KoreanExtension()
