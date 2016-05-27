# SmartFormat-Korean

[Python 용 SmartFormat][smartformat-python]에서 쓸 수 있는 한국어 확장입니다.

[smartformat-python]: https://github.com/what-studio/smartformat

## 설치

```console
$ pip install smartformat-korean
```

## 사용법

```python
>>> from smartformat import SmartFormatter
>>> from smartformat.ext.korean import ko
>>> smart = SmartFormatter('ko_KR', [ko])
>>> smart.format(u'{pokemon:은} {skill:을} 시전했다!',
...              pokemon=u'피카츄', skill=u'전광석화')
피카츄는 전광석화를 시전했다!
>>> smart.format(u'{subj:는} {obj:다}.',
...              subj=u'대한민국', obj=u'민주공화국')
대한민국은 민주공화국이다.
```

## 이형태 조사 처리

지원하는 한국어의 이형태 조사는 다음과 같습니다:

- 은(는)
- 이(가)
- 을(를)
- 과(와)
- 아(야)
- (이)여
- (이)시여
- (으)로, (으)로부터, (으)로서, ...
- 이다, 입니다, 이어서, 이므로, ...

## 만든이와 사용권

넥슨 왓 스튜디오의 [이흥섭][sublee]과 [김찬웅][kexplo]이 만들었고 BSD 라이센스를
채택했습니다.

[sublee]: http://subl.ee/
[kexplo]: http://chanwoong.kim/
