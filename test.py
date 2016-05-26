# -*- coding: utf-8 -*-
import pytest
from smartformat import SmartFormatter

from smartformatkorean import ko, split_phonemes


@pytest.fixture
def smart():
    formatter = SmartFormatter()
    formatter.register([ko])
    return formatter


def test_split_phonemes():
    assert split_phonemes(u'쏚') == (u'ㅆ', u'ㅗ', u'ㄲ')
    assert split_phonemes(u'섭') == (u'ㅅ', u'ㅓ', u'ㅂ')
    assert split_phonemes(u'투') == (u'ㅌ', u'ㅜ', None)
    assert split_phonemes(u'투', initial=False) == (None, u'ㅜ', None)
    with pytest.raises(ValueError):
        split_phonemes(u'X')
    with pytest.raises(ValueError):
        split_phonemes(u'섭섭')


def test_explicit(smart):
    f = smart.format
    assert f(u'{:ko(아):{}} 안녕', u'피카츄') == u'피카츄야 안녕'
    assert f(u'{:ko(아):{}} 안녕', u'버터플') == u'버터플아 안녕'
    assert f(u'{:ko(아):{}} 안녕', u'고라파덕') == u'고라파덕아 안녕'
    assert f(u'{:ko(을):*{}*} 깎는다.', u'사과') == u'*사과*를 깎는다.'
    assert f(u'{:ko(을):}', u'수박') == u'을'


def test_implicit(smart):
    f = smart.format
    assert f(u'{:아} 안녕', u'피카츄') == u'피카츄야 안녕'
    assert f(u'{:아} 안녕', u'버터플') == u'버터플아 안녕'
    assert f(u'{:아} 안녕', u'고라파덕') == u'고라파덕아 안녕'
    assert f(u'{:을} 칼로 깎는다.', u'사과') == u'사과를 칼로 깎는다.'
    assert f(u'{:-을}', u'수박') == u'을'


def test_euro(smart):
    f = smart.format
    assert f(u'{:ko(으로):{}}', u'피카츄') == u'피카츄로'
    assert f(u'{:ko(으로):{}}', u'버터플') == u'버터플로'
    assert f(u'{:ko(으로):{}}', u'고라파덕') == u'고라파덕으로'
    assert f(u'{:ko(으로):{}}', u'Pikachu') == u'Pikachu(으)로'


def test_braket(smart):
    f = smart.format
    assert f(u'{:ko(으로):{}}', u'피카츄(Lv.25)') == u'피카츄(Lv.25)로'
    assert f(u'{:ko(으로):{}}', u'피카(?)츄') == u'피카(?)츄로'


def test_vocative_particles(smart):
    f = smart.format
    assert f(u'{:야}', u'친구') == u'친구야'
    assert f(u'{:야}', u'사랑') == u'사랑아'
    assert f(u'{:아}', u'사랑') == u'사랑아'
    assert f(u'{:여}', u'친구') == u'친구여'
    assert f(u'{:여}', u'사랑') == u'사랑이여'
    assert f(u'{:이시여}', u'하늘') == u'하늘이시여'
    assert f(u'{:이시여}', u'바다') == u'바다시여'


def test_ita(smart):
    """Cases for '이다' which is a copulative and existential verb."""
    f = smart.format
    # Do or don't inject '이'.
    assert f(u'{:이다}', u'피카츄') == u'피카츄다'
    assert f(u'{:이다}', u'버터플') == u'버터플이다'
    # Merge with the following vowel as /j/.
    assert f(u'{:이에요}', u'피카츄') == u'피카츄예요'
    assert f(u'{:이에요}', u'버터플') == u'버터플이에요'
    # Same forms.
    assert f(u'{:입니다}', u'피카츄') == u'피카츄입니다'
    assert f(u'{:입니다}', u'버터플') == u'버터플입니다'
