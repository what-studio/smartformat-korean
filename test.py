# -*- coding: utf-8 -*-
import pytest
import tossi

from smartformat import SmartFormatter
from smartformat.ext.korean import ko, KoreanExtension


Euro = tossi.get_particle(u'으로')


@pytest.fixture
def f():
    smart = SmartFormatter('ko_KR', [ko])
    return smart.format


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
    # () is ok.
    assert f(u'{:을(를)}', u'서태지') == u'서태지를'


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
    assert f(u'{:ko(으론):{}}', u'밖') == u'밖으론'


def test_combinations(f):
    assert f(u'{:만으로는}', u'이 방법') == u'이 방법만으로는'
    assert f(u'{:조차도}', u'나') == u'나조차도'
    assert f(u'{:과는} 별개로', u'그 친구') == u'그 친구와는 별개로'
    assert f(u'{:와는} 별개로', u'그것') == u'그것과는 별개로'
    assert f(u'{:과(와)는} 별개로', u'사건') == u'사건과는 별개로'
    assert f(u'{:관} 별개로', u'그 친구') == u'그 친구완 별개로'


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
    assert f(u'{:를}', u'검색\ue000') == u'검색\ue000을'


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
    assert f(u'{:인양}', u'키홀') == u'키홀인양'
    assert f(u'{:인양}', u'나오') == u'나오인양'


def test_invariant_particles(f):
    assert f(u'{:도}', u'나오') == u'나오도'
    assert f(u'{:도}', u'모리안') == u'모리안도'
    assert f(u'{:에서}', u'판교') == u'판교에서'
    assert f(u'{:에서는}', u'판교') == u'판교에서는'
    assert f(u'{:께서도}', u'선생님') == u'선생님께서도'
    assert f(u'{:의}', u'나오') == u'나오의'
    assert f(u'{:만}', u'모리안') == u'모리안만'
    assert f(u'{:하고}', u'키홀') == u'키홀하고'
    assert f(u'{:만큼}', u'콩') == u'콩만큼'
    assert f(u'{:마냥}', u'콩') == u'콩마냥'
    assert f(u'{:처럼}', u'콩') == u'콩처럼'


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


def test_igyuho2006(f):
    """Particles from <Classification and List of Conjunctive Particles>,
    I Gyu-ho, 2006.
    """
    def ff(particle_string):
        format_string = u'{:%s}' % particle_string
        return f(format_string, u'남'), f(format_string, u'나')
    # p181-182:
    assert ff(u'의') == (u'남의', u'나의')
    assert ff(u'과') == (u'남과', u'나와')
    assert ff(u'와') == (u'남과', u'나와')
    assert ff(u'하고') == (u'남하고', u'나하고')
    assert ff(u'이랑') == (u'남이랑', u'나랑')
    assert ff(u'이니') == (u'남이니', u'나니')
    assert ff(u'이다') == (u'남이다', u'나다')
    assert ff(u'이라든가') == (u'남이라든가', u'나라든가')
    assert ff(u'이라든지') == (u'남이라든지', u'나라든지')
    assert ff(u'이며') == (u'남이며', u'나며')
    assert ff(u'이야') == (u'남이야', u'나야')
    assert ff(u'이요') == (u'남이요', u'나요')
    assert ff(u'이랴') == (u'남이랴', u'나랴')
    assert ff(u'에') == (u'남에', u'나에')
    assert ff(u'하며') == (u'남하며', u'나하며')
    assert ff(u'커녕') == (u'남커녕', u'나커녕')
    assert ff(u'은커녕') == (u'남은커녕', u'나는커녕')
    assert ff(u'이고') == (u'남이고', u'나고')
    assert ff(u'이나') == (u'남이나', u'나나')
    assert ff(u'에다') == (u'남에다', u'나에다')
    assert ff(u'에다가') == (u'남에다가', u'나에다가')
    assert ff(u'이란') == (u'남이란', u'나란')
    assert ff(u'이면') == (u'남이면', u'나면')
    assert ff(u'이거나') == (u'남이거나', u'나거나')
    assert ff(u'이건') == (u'남이건', u'나건')
    assert ff(u'이든') == (u'남이든', u'나든')
    assert ff(u'이든가') == (u'남이든가', u'나든가')
    assert ff(u'이든지') == (u'남이든지', u'나든지')
    assert ff(u'인가') == (u'남인가', u'나인가')
    assert ff(u'인지') == (u'남인지', u'나인지')
    # p188-189:
    assert ff(u'인') == (u'남인', u'나인')
    assert ff(u'는') == (u'남은', u'나는')
    assert ff(u'이라는') == (u'남이라는', u'나라는')
    assert ff(u'이네') == (u'남이네', u'나네')
    assert ff(u'도') == (u'남도', u'나도')
    assert ff(u'이면서') == (u'남이면서', u'나면서')
    assert ff(u'이자') == (u'남이자', u'나자')
    assert ff(u'하고도') == (u'남하고도', u'나하고도')
    assert ff(u'이냐') == (u'남이냐', u'나냐')


def test_tolerance_style():
    smart = SmartFormatter('ko_KR', [KoreanExtension(u'는(은)')])
    assert \
        smart.format(u'{0:은} {1:을} {2:다}.', u'Hello', u'World', u'Bye') == \
        u'Hello는(은) World를(을) Bye(이)다.'
    smart = SmartFormatter('ko_KR', [KoreanExtension(u'(이)가')])
    assert \
        smart.format(u'{0:은} {1:을} {2:다}.', u'Hello', u'World', u'Bye') == \
        u'Hello(은)는 World(을)를 Bye(이)다.'


def test_custom_guess_coda():
    def dont_guess_coda(word):
        return None
    assert Euro.allomorph(u'밖', u'으로',
                          guess_coda=dont_guess_coda) == u'(으)로'
    ko = KoreanExtension(guess_coda=dont_guess_coda)
    smart = SmartFormatter('ko_KR', [ko])
    assert smart.format(u'{0:으로}', u'밖') == u'밖(으)로'
