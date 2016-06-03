# -*- coding: utf-8 -*-
import pytest
from smartformat import SmartFormatter
from smartformat.ext.korean import ko
from smartformat.ext.korean.coda import pick_coda_from_decimal
from smartformat.ext.korean.hangul import join_phonemes, split_phonemes
from smartformat.ext.korean.particles import combine_tolerances


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


def test_particle_tolerances():
    c = lambda _1, _2: set(combine_tolerances(_1, _2))
    s = lambda x: set(x.split())
    assert c(u'이', u'가') == s(u'이(가) (이)가 가(이) (가)이')
    assert c(u'이', u'') == s(u'(이)')
    assert c(u'으로', u'로') == s(u'(으)로')
    assert c(u'이여', u'여') == s(u'(이)여')
    assert c(u'이시여', u'시여') == s(u'(이)시여')
    assert c(u'아', u'야') == s(u'아(야) (아)야 야(아) (야)아')


def test_explicit(f):
    assert f(u'{:ko(아):{}} 안녕', u'나오') == u'나오야 안녕'
    assert f(u'{:ko(아):{}} 안녕', u'키홀') == u'키홀아 안녕'
    assert f(u'{:ko(아):{}} 안녕', u'모리안') == u'모리안아 안녕'
    assert f(u'{:ko(을):*{}*} 깎는다.', u'사과') == u'*사과*를 깎는다.'
    assert f(u'{:ko(을):}', u'수박') == u'을'


def test_implicit(f):
    assert f(u'{:아} 안녕', u'나오') == u'나오야 안녕'
    assert f(u'{:아} 안녕', u'키홀') == u'키홀아 안녕'
    assert f(u'{:아} 안녕', u'모리안') == u'모리안아 안녕'
    assert f(u'{:을} 칼로 깎는다.', u'사과') == u'사과를 칼로 깎는다.'
    assert f(u'{:-을}', u'수박') == u'을'
    assert f(u'{:ㄱ나니?}', u'서태지') == u'서태지'
    # All option letters have to be Hangul.
    assert f(u'{:을!}', u'서태지') == u'서태지'


def test_euro(f):
    assert f(u'{:ko(으로):{}}', u'나오') == u'나오로'
    assert f(u'{:ko(으로):{}}', u'키홀') == u'키홀로'
    assert f(u'{:ko(으로):{}}', u'모리안') == u'모리안으로'
    assert f(u'{:ko(으로):{}}', u'Nao') == u'Nao(으)로'
    assert f(u'{:ko(로서):{}}', u'나오') == u'나오로서'
    assert f(u'{:ko(로서):{}}', u'키홀') == u'키홀로서'
    assert f(u'{:ko(로서):{}}', u'모리안') == u'모리안으로서'
    assert f(u'{:ko(로써):{}}', u'나오') == u'나오로써'
    assert f(u'{:ko(로써):{}}', u'키홀') == u'키홀로써'
    assert f(u'{:ko(로써):{}}', u'모리안') == u'모리안으로써'
    assert f(u'{:ko(로부터):{}}', u'나오') == u'나오로부터'
    assert f(u'{:ko(로부터):{}}', u'키홀') == u'키홀로부터'
    assert f(u'{:ko(로부터):{}}', u'모리안') == u'모리안으로부터'
    assert f(u'{:ko(로부터도):{}}', u'모리안') == u'모리안으로부터도'
    assert f(u'{:ko((으)로부터의):{}} 편지', u'그녀') == u'그녀로부터의 편지'


def test_gwaneun(f):
    assert f(u'{:과는} 별개로', u'그것') == u'그것과는 별개로'
    assert f(u'{:과는} 별개로', u'그 친구') == u'그 친구와는 별개로'


def test_exceptions(f):
    # Empty.
    assert f(u'{:를}', u'') == u'을(를)'
    # Onsets only.
    assert f(u'{:를}', u'ㅋㅋㅋ') == u'ㅋㅋㅋ을(를)'


def test_insignificant(f):
    assert f(u'{:ko(으로):{}}', u'나오(Lv.25)') == u'나오(Lv.25)로'
    assert f(u'{:ko(으로):{}}', u'나(?)오') == u'나(?)오로'
    assert f(u'{:ko(으로):{}}', u'헬로월드!') == u'헬로월드!로'
    assert f(u'{:ko(으로):{}}', u'?_?') == u'?_?(으)로'
    assert f(u'{:가}?', u'임창정,,,') == u'임창정,,,이?'
    assert f(u'{:을} 샀다.', u'《듀랑고》') == u'《듀랑고》를 샀다.'
    assert f(u'{:은} 어떨까?', u'불완전괄호)') == u'불완전괄호)는 어떨까?'
    assert f(u'{:은} 어떨까?', u'이상한괄호)))') == u'이상한괄호)))는 어떨까?'
    assert f(u'{:은} 어떨까?', u'이상한괄호)()') == u'이상한괄호)()는 어떨까?'
    assert f(u'{:은} 어떨까?', u'이상한괄호())') == u'이상한괄호())는 어떨까?'
    assert f(u'{:이었다}.', u'^_^') == u'^_^(이)었다.'
    assert f(u'{:이었다}.', u'웃는얼굴^_^') == u'웃는얼굴^_^이었다.'
    assert f(u'{:이었다}.', u'폭탄(가짜)...') == u'폭탄(가짜)...이었다.'
    assert f(u'{:으로}', u'16(7)?!') == u'16(7)?!으로'
    assert f(u'{:으로}', u'7(16)?!') == u'7(16)?!로'


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
    assert f(u'{:이다}', u'나오') == u'나오다'
    assert f(u'{:이다}', u'키홀') == u'키홀이다'
    # Merge with the following vowel as /j/.
    assert f(u'{:이에요}', u'나오') == u'나오예요'
    assert f(u'{:이에요}', u'키홀') == u'키홀이에요'
    # No allomorphs.
    assert f(u'{:입니다}', u'나오') == u'나오입니다'
    assert f(u'{:입니다}', u'키홀') == u'키홀입니다'
    # Give up to select an allomorph.
    assert f(u'{:이다}', u'God') == u'God(이)다'
    assert f(u'{:이에요}', u'God') == u'God(이)에요'
    assert f(u'{:입니다}', u'God') == u'God입니다'
    assert f(u'{:였습니다}', u'God') == u'God(이)었습니다'
    # Many examples.
    assert f(u'{:였습니다}', u'키홀') == u'키홀이었습니다'
    assert f(u'{:였습니다}', u'나오') == u'나오였습니다'
    assert f(u'{:이었다}', u'나오') == u'나오였다'
    assert f(u'{:이었지만}', u'나오') == u'나오였지만'
    assert f(u'{:이지만}', u'나오') == u'나오지만'
    assert f(u'{:이지만}', u'키홀') == u'키홀이지만'
    assert f(u'{:지만}', u'나오') == u'나오지만'
    assert f(u'{:지만}', u'키홀') == u'키홀이지만'
    assert f(u'{:다}', u'나오') == u'나오다'
    assert f(u'{:다}', u'키홀') == u'키홀이다'
    assert f(u'{:이에요}', u'나오') == u'나오예요'
    assert f(u'{:이에요}', u'키홀') == u'키홀이에요'
    assert f(u'{:고}', u'나오') == u'나오고'
    assert f(u'{:고}', u'키홀') == u'키홀이고'
    assert f(u'{:고}', u'모리안') == u'모리안이고'
    assert f(u'{:여서}', u'나오') == u'나오여서'
    assert f(u'{:여서}', u'키홀') == u'키홀이어서'
    assert f(u'{:이어서}', u'나오') == u'나오여서'
    assert f(u'{:라고라}?', u'키홀') == u'키홀이라고라?'
    assert f(u'{:든지}', u'키홀') == u'키홀이든지'
    assert f(u'{:던가}?', u'키홀') == u'키홀이던가?'
    assert f(u'{:여도}', u'키홀') == u'키홀이어도'
    assert f(u'{0:나} {1:나}', u'나오', u'키홀') == u'나오나 키홀이나'
    assert f(u'{:야말로}', u'키홀') == u'키홀이야말로'


def test_invariant_particles(f):
    assert f(u'{:도}', u'나오') == u'나오도'
    assert f(u'{:도}', u'모리안') == u'모리안도'
    assert f(u'{:에서}', u'판교') == u'판교에서'
    assert f(u'{:에서는}', u'판교') == u'판교에서는'
    assert f(u'{:께서도}', u'선생님') == u'선생님께서도'
    assert f(u'{:의}', u'나오') == u'나오의'
    assert f(u'{:만}', u'모리안') == u'모리안만'
    assert f(u'{:하고}', u'키홀') == u'키홀하고'


def test_tolerances(f):
    assert f(u'{:은(는)}', u'나오') == u'나오는'
    assert f(u'{:(은)는}', u'나오') == u'나오는'
    assert f(u'{:는(은)}', u'나오') == u'나오는'
    assert f(u'{:(는)은}', u'나오') == u'나오는'


def test_decimal(f):
    assert f(u'{:이}', u'레벨30') == u'레벨30이'
    assert f(u'{:이}', u'레벨34') == u'레벨34가'
    assert f(u'{:으로}', u'레벨7') == u'레벨7로'
    assert f(u'{:으로}', u'레벨42') == u'레벨42로'
    assert f(u'{:으로}', u'레벨100') == u'레벨100으로'
    assert pick_coda_from_decimal('1') == u'ㄹ'
    assert pick_coda_from_decimal('2') == u''
    assert pick_coda_from_decimal('3') == u'ㅁ'
    assert pick_coda_from_decimal('10') == u'ㅂ'
    assert pick_coda_from_decimal('16') == u'ㄱ'
    assert pick_coda_from_decimal('19') == u''
    assert pick_coda_from_decimal('200') == u'ㄱ'
    assert pick_coda_from_decimal('30000') == u'ㄴ'
    assert pick_coda_from_decimal('400000') == u'ㄴ'
    assert pick_coda_from_decimal('500000000') == u'ㄱ'
    assert pick_coda_from_decimal('1' + '0' * 50) == u'ㄱ'
    assert pick_coda_from_decimal('1' + '0' * 100) is None
    assert pick_coda_from_decimal('0') == u'ㅇ'
    assert pick_coda_from_decimal('1.0') == u'ㅇ'
    assert pick_coda_from_decimal('1.234567890') == u'ㅇ'
    assert pick_coda_from_decimal('3.14') == u''
