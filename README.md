# SmartFormat-Korean

[Python 용 SmartFormat][smartformat-python]에서 쓸 수 있는 한국어 확장입니다.

[smartformat-python]: https://github.com/what-studio/smartformat

## 설치

```console
$ pip install smartformat-korean
```

## 자연스러운 조사 선택

`의`, `도`, `만`, `보다`, `부터`, `까지`, `마저`, `조차`, `에~`,
`께~`, `하~`에는 어떤 단어가 앞서도 형태가 변하지 않습니다:

> 피카츄**의**, 버터플**의**, 야도란**도**, 피죤투**도**

반면 `은(는)`, `이(가)`, `을(를)`, `과(와)`는 앞선 단어의 마지막 음절의 받침
유무에 따라 형태가 달라집니다:

> 피카츄**는**, 버터플**은**

`(으)로~`도 비슷한 규칙을 따르지만 앞선 받침이 `ㄹ`일 경우엔 받침이 없는 것과
같게 취급합니다:

> 피카츄**로**,버터플**로**, 리자몽**으로**

서술격 조사 `(이)다`는 어미가 활용되어 다양한 형태로 변형될 수 있습니다:

> 피카츄**입니다**, 파이리**지만**, 성원숭**이지만**, 윤겔라**예요**, 버터플**이에요**

SmartFormat 한국어 확장은 자동으로 가장 자연스러운 조사 형태를 선택합니다.
만약 어떤 형태가 자연스러운지 알 수 없을 때에는 `은(는)`, `(으)로`처럼
모든 형태를 병기합니다.

```python
>>> from smartformat import SmartFormatter
>>> from smartformat.ext.korean import ko
>>> smart = SmartFormatter('ko_KR', [ko])
>>> smart.format(u'{subj:는} {obj:다}.',
...              subj=u'대한민국', obj=u'민주공화국')
대한민국은 민주공화국이다.
>>> smart.format(u'{pokemon:은} {skill:을} 시전했다!',
...              pokemon=u'피카츄', skill=u'전광석화')
피카츄는 전광석화를 시전했다!
>>> smart.format(u'바로 {pokemon:이에요}.', pokemon=u'피카츄')
바로 피카츄예요.
>>> smart.format(u'{material:로} 만들었다.', material=u'벽돌')
벽돌로 만들었다.
>>> smart.format(u'{material:로} 만들었다.', material=u'짚')
짚으로 만들었다.
>>> smart.format(u'{material:로} 만들었다.', material=u'黃金')
黃金(으)로 만들었다.
```

## 만든이와 사용권

[넥슨][nexon] [왓 스튜디오][what-studio]의 [이흥섭][sublee]과
[김찬웅][kexplo]이 만들었고 [제3조항을 포함하는 BSD 허가서][bsd-3-clause]를
채택했습니다.

[nexon]: http://nexon.com/
[what-studio]: https://github.com/what-studio
[sublee]: http://subl.ee/
[kexplo]: http://chanwoong.kim/
[bsd-3-clause]: http://opensource.org/licenses/BSD-3-Clause
