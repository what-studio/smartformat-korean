# -*- coding: utf-8 -*-
import pytest
from smartformat import SmartFormatter
from smartformat.ext.korean import ko
from smartformat.ext.korean.hangul import join_phonemes, split_phonemes


@pytest.fixture
def f():
    smart = SmartFormatter('ko_KR', [ko])
    return smart.format


def test_split_phonemes():
    assert split_phonemes(u'쏚') == (u'ㅆ', u'ㅗ', u'ㄲ')
    assert split_phonemes(u'섭') == (u'ㅅ', u'ㅓ', u'ㅂ')
    assert split_phonemes(u'투') == (u'ㅌ', u'ㅜ', u'')
    assert split_phonemes(u'투', onset=False) == (None, u'ㅜ', u'')
    with pytest.raises(ValueError):
        split_phonemes(u'X')
    with pytest.raises(ValueError):
        split_phonemes(u'섭섭')


def test_join_phonemes():
    assert join_phonemes(u'ㅅ', u'ㅓ', u'ㅂ') == u'섭'
    assert join_phonemes((u'ㅅ', u'ㅓ', u'ㅂ')) == u'섭'
    assert join_phonemes(u'ㅊ', u'ㅠ') == u'츄'
    assert join_phonemes(u'ㅊ', u'ㅠ', u'') == u'츄'
    assert join_phonemes((u'ㅊ', u'ㅠ')) == u'츄'
    with pytest.raises(TypeError):
        join_phonemes(u'ㄷ', u'ㅏ', u'ㄹ', u'ㄱ')


def test_explicit(f):
    assert f(u'{:ko(아):{}} 안녕', u'피카츄') == u'피카츄야 안녕'
    assert f(u'{:ko(아):{}} 안녕', u'버터플') == u'버터플아 안녕'
    assert f(u'{:ko(아):{}} 안녕', u'고라파덕') == u'고라파덕아 안녕'
    assert f(u'{:ko(을):*{}*} 깎는다.', u'사과') == u'*사과*를 깎는다.'
    assert f(u'{:ko(을):}', u'수박') == u'을'


def test_implicit(f):
    assert f(u'{:아} 안녕', u'피카츄') == u'피카츄야 안녕'
    assert f(u'{:아} 안녕', u'버터플') == u'버터플아 안녕'
    assert f(u'{:아} 안녕', u'고라파덕') == u'고라파덕아 안녕'
    assert f(u'{:을} 칼로 깎는다.', u'사과') == u'사과를 칼로 깎는다.'
    assert f(u'{:-을}', u'수박') == u'을'
    assert f(u'{:ㄱ나니?}', u'서태지') == u'서태지'
    # All option letters have to be Hangul.
    assert f(u'{:을!}', u'서태지') == u'서태지'


def test_euro(f):
    assert f(u'{:ko(으로):{}}', u'피카츄') == u'피카츄로'
    assert f(u'{:ko(으로):{}}', u'버터플') == u'버터플로'
    assert f(u'{:ko(으로):{}}', u'고라파덕') == u'고라파덕으로'
    assert f(u'{:ko(으로):{}}', u'Pikachu') == u'Pikachu(으)로'
    assert f(u'{:ko(로서):{}}', u'피카츄') == u'피카츄로서'
    assert f(u'{:ko(로서):{}}', u'버터플') == u'버터플로서'
    assert f(u'{:ko(로서):{}}', u'고라파덕') == u'고라파덕으로서'
    assert f(u'{:ko(로써):{}}', u'피카츄') == u'피카츄로써'
    assert f(u'{:ko(로써):{}}', u'버터플') == u'버터플로써'
    assert f(u'{:ko(로써):{}}', u'고라파덕') == u'고라파덕으로써'
    assert f(u'{:ko(로부터):{}}', u'피카츄') == u'피카츄로부터'
    assert f(u'{:ko(로부터):{}}', u'버터플') == u'버터플로부터'
    assert f(u'{:ko(로부터):{}}', u'고라파덕') == u'고라파덕으로부터'
    assert f(u'{:ko(로부터도):{}}', u'고라파덕') == u'고라파덕으로부터도'
    assert f(u'{:ko((으)로부터의):{}} 편지', u'그녀') == u'그녀로부터의 편지'


def test_exceptions(f):
    # Empty.
    assert f(u'{:를}', u'') == u'을(를)'
    # Onsets only.
    assert f(u'{:를}', u'ㅋㅋㅋ') == u'ㅋㅋㅋ을(를)'


def test_blind(f):
    assert f(u'{:ko(으로):{}}', u'피카츄(Lv.25)') == u'피카츄(Lv.25)로'
    assert f(u'{:ko(으로):{}}', u'피카(?)츄') == u'피카(?)츄로'
    assert f(u'{:ko(으로):{}}', u'헬로월드!') == u'헬로월드!로'
    assert f(u'{:ko(으로):{}}', u'?_?') == u'?_?(으)로'
    assert f(u'{:가}?', u'임창정,,,') == u'임창정,,,이?'
    assert f(u'{:을} 샀다.', u'<듀랑고>') == u'<듀랑고>를 샀다.'


def test_vocative_particles(f):
    assert f(u'{:야}', u'친구') == u'친구야'
    assert f(u'{:야}', u'사랑') == u'사랑아'
    assert f(u'{:아}', u'사랑') == u'사랑아'
    assert f(u'{:여}', u'친구') == u'친구여'
    assert f(u'{:여}', u'사랑') == u'사랑이여'
    assert f(u'{:이시여}', u'하늘') == u'하늘이시여'
    assert f(u'{:이시여}', u'바다') == u'바다시여'


def test_ida(f):
    """Cases for '이다' which is a copulative and existential verb."""
    # Do or don't inject '이'.
    assert f(u'{:이다}', u'피카츄') == u'피카츄다'
    assert f(u'{:이다}', u'버터플') == u'버터플이다'
    # Merge with the following vowel as /j/.
    assert f(u'{:이에요}', u'피카츄') == u'피카츄예요'
    assert f(u'{:이에요}', u'버터플') == u'버터플이에요'
    # No allomorphs.
    assert f(u'{:입니다}', u'피카츄') == u'피카츄입니다'
    assert f(u'{:입니다}', u'버터플') == u'버터플입니다'
    # Give up to select an allomorph.
    assert f(u'{:이다}', u'God') == u'God(이)다'
    assert f(u'{:이에요}', u'God') == u'God(이)에요'
    assert f(u'{:입니다}', u'God') == u'God입니다'
    assert f(u'{:였습니다}', u'God') == u'God(이)었습니다'
    # Many examples.
    assert f(u'{:였습니다}', u'버터플') == u'버터플이었습니다'
    assert f(u'{:였습니다}', u'피카츄') == u'피카츄였습니다'
    assert f(u'{:이었다}', u'피카츄') == u'피카츄였다'
    assert f(u'{:이었지만}', u'피카츄') == u'피카츄였지만'
    assert f(u'{:이지만}', u'피카츄') == u'피카츄지만'
    assert f(u'{:이지만}', u'버터플') == u'버터플이지만'
    assert f(u'{:지만}', u'피카츄') == u'피카츄지만'
    assert f(u'{:지만}', u'버터플') == u'버터플이지만'
    assert f(u'{:다}', u'피카츄') == u'피카츄다'
    assert f(u'{:다}', u'버터플') == u'버터플이다'
    assert f(u'{:이에요}', u'피카츄') == u'피카츄예요'
    assert f(u'{:이에요}', u'버터플') == u'버터플이에요'
    assert f(u'{:고}', u'피카츄') == u'피카츄고'
    assert f(u'{:고}', u'버터플') == u'버터플이고'
    assert f(u'{:고}', u'리자몽') == u'리자몽이고'
    assert f(u'{:여서}', u'피카츄') == u'피카츄여서'
    assert f(u'{:여서}', u'버터플') == u'버터플이어서'
    assert f(u'{:이어서}', u'피카츄') == u'피카츄여서'
    assert f(u'{:라고라}?', u'버터플') == u'버터플이라고라?'
    assert f(u'{:든지}', u'버터플') == u'버터플이든지'
    assert f(u'{:던가}?', u'버터플') == u'버터플이던가?'


@pytest.mark.xfail
def test_invariant_particles(f):
    assert f(u'{:도}', u'피카츄') == u'피카츄도'
    assert f(u'{:도}', u'고라파덕') == u'고라파덕도'
