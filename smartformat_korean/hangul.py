# -*- coding: utf-8 -*-
"""
   smartformat_korean
   ~~~~~~~~~~~~~~~~~~

   SmartFormat extensions for Korean.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""

__all__ = ['is_hangul', 'join_phonemes', 'split_phonemes']


# Korean phonemes as known as "자소".
INITIALS = list(u'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
VOWELS = list(u'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ')
FINALS = [None]
FINALS.extend(u'ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')

# Lengths of the phonemes.
NUM_INITIALS = len(INITIALS)
NUM_VOWELS = len(VOWELS)
NUM_FINALS = len(FINALS)

FIRST_HANGUL_OFFSET = ord(u'가')


def is_hangul(letter):
    return u'가' <= letter <= u'힣'


def join_phonemes(*args):
    """Joins a Hangul letter from Korean phonemes."""
    # Normalize arguments as initial, vowel, final.
    if len(args) == 1:
        # tuple of (initial, vowel[, final])
        args = args[0]
    if len(args) == 2:
        args += (None,)
    try:
        initial, vowel, final = args
    except ValueError:
        raise TypeError('join_phonemes() takes at most 3 arguments')
    offset = (
        (INITIALS.index(initial) * NUM_VOWELS + VOWELS.index(vowel)) *
        NUM_FINALS + FINALS.index(final)
    )
    return unichr(FIRST_HANGUL_OFFSET + offset)


def split_phonemes(letter, initial=True, vowel=True, final=True):
    """Splits Korean phonemes as known as "자소" from a Hangul letter.

    :returns: (initial, vowel, final)
    :raises ValueError: `letter` is not a Hangul single letter.

    """
    if len(letter) != 1 or not is_hangul(letter):
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
