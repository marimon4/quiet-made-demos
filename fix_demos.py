#!/usr/bin/env python3
"""HTML構造に合わせた正確な置換"""

import re, os

OUTPUT_DIR = '/Users/marika/Desktop/quietmade/'

def fix_file(filename, fixes):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
        else:
            print(f'  ⚠ NOT FOUND: {repr(old[:60])}')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  ✅ {filename}')

# ──────────────────────────────────────────────
# showen-demo.html
# ──────────────────────────────────────────────
fix_file('showen-demo.html', [
    # H1 ヒーロー（spanタグ入り）
    (
        '<h1 class="hero-title">\n      <span class="ai">藍</span>と<span class="beni">紅</span>が、<br>\n      布に宿る。\n    </h1>',
        '<h1 class="hero-title">\n      紐は、<br>\n      縁を結ぶ。\n    </h1>'
    ),
    # ストーリー見出し
    (
        '<h2 class="intro-heading">\n      土から生まれた色が、<br>\n      <em>千年後も残る。</em>\n    </h2>',
        '<h2 class="intro-heading">\n      紐が結ぶ、<br>\n      <em>千年の縁。</em>\n    </h2>'
    ),
    # ストーリー本文（<br>入り）
    (
        '<p class="intro-body">\n      京都・西陣の路地奥に、昇苑くみひもがあります。<br>\n      初代・山田清次郎が1934年に開いたこの工房では、<br>\n      今も化学染料を一切使いません。<br><br>\n      藍は阿波から。紅花は山形から。<br>\n      季節と天候によって、色は毎年微妙に違います。<br>\n      それが、山田の布に宿る「生きた色」の正体です。\n    </p>',
        '<p class="intro-body">\n      京都・宇治の地で、昇苑くみひもは京くみひもを作り続けています。<br>\n      帯締め、羽織紐、装身具——一本一本、手で組み上げる紐は<br>\n      機械生産では決して生まれない微妙な張りとしなやかさを持ちます。<br><br>\n      「紐はモノとモノを結ぶ、紐は人と人を結ぶ、紐は縁を結ぶ」。<br>\n      その信念のもと、職人の手が今日も糸を紡いでいます。\n    </p>'
    ),
    # コンタクト見出し
    (
        '藍 と 紅 の布を、',
        '京の組紐を、'
    ),
])

# ──────────────────────────────────────────────
# suzuemon-demo.html
# ──────────────────────────────────────────────
fix_file('suzuemon-demo.html', [
    # H1 英語ヒーロー
    (
        '<h1 class="hero-en">\n        The space<br>\n        <em>between things</em><br>\n        is where beauty lives.\n      </h1>',
        '<h1 class="hero-en">\n        Handcrafted pure tin,<br>\n        <em>shaped by 45 years</em><br>\n        of mastery.\n      </h1>'
    ),
    # 哲学見出し
    (
        '<h2 class="concept-heading">\n      The vessel holds<br>\n      <em>what words cannot.</em>\n    </h2>',
        '<h2 class="concept-heading">\n      Pour once.<br>\n      <em>Taste the difference.</em>\n    </h2>'
    ),
    # コンタクト見出し
    (
        '<h2 class="contact-heading">\n      Find your<br>\n      <em>perfect vessel.</em>\n    </h2>',
        '<h2 class="contact-heading">\n      Find your<br>\n      <em>perfect tin piece.</em>\n    </h2>'
    ),
    # Hero desc（まだテンプレ文言が残っている場合）
    (
        '京都錫右衛門は、京都の茶室文化から生まれた花器工房です。<br>\n      使うほどに深まる、静かな美しさを追求しています。',
        '京都の錫職人・小泉仁が手がける、純錫器の工房。<br>\n      99.9%の純錫を砂型鋳造で成形し、一点一点手で仕上げます。'
    ),
    # 哲学本文
    (
        '花器は、花を飾るための道具ではありません。<br>\n      空間に「間」を生み出すための存在です。<br>\n      山田花器は、茶道の美意識を現代に翻訳します。<br>\n      過剰ではなく、不足でもなく——ちょうどいい静けさ。<br>\n      その一点を、ひとつひとつ手で作り続けています。',
        '錫は、ビールを注げば泡がきめ細かくなり、日本酒は丸みを帯びる。<br>\n      この作用は、錫の熱伝導性と微弱なイオン効果によるもの。<br>\n      京都錫右衛門では、その錫を砂型に流し込み、<br>\n      職人が手で削り、磨いて一つの器に仕上げます。<br>\n      45年の経験が積み重なった、完全手作りの錫器です。'
    ),
    # ギャラリー引用
    (
        '"I do not make vessels. I make the silence around a flower."',
        '"I do not sell tin. I sell the taste of a better drink."'
    ),
    (
        '器を作るのではない。<br>\n           花を包む、沈黙を作る。',
        '錫を売るのではない。<br>\n           一杯を、美味しくする道具を作る。'
    ),
])

# ──────────────────────────────────────────────
# mori-demo.html
# ──────────────────────────────────────────────
fix_file('mori-demo.html', [
    # H1
    (
        '<h1 class="hero-title">\n      土から生まれる、<br><em>静かな器</em>\n    </h1>',
        '<h1 class="hero-title">\n      炎が育む、<br><em>大谷の土</em>\n    </h1>'
    ),
    # Story H2
    (
        '<h2 class="intro-heading">\n      手の記憶が、<br>かたちになる。<br><em>それが器です。</em>\n    </h2>',
        '<h2 class="intro-heading">\n      炎が育てる、<br>大谷の土。<br><em>それが大谷焼です。</em>\n    </h2>'
    ),
    # Story body
    (
        '<p class="intro-body">\n      京都の山あいで、山田太郎は土と向き合い続けています。<br>\n      釉薬の偶然性、炎の揺らぎ、冷ます時間の長さ。<br>\n      ひとつひとつの器に、繰り返しのない一瞬が宿っています。\n    </p>',
        '<p class="intro-body">\n      徳島県鳴門市大谷町に、森陶器窯元があります。<br>\n      国登録有形文化財の窯で焼かれる大谷焼は、<br>\n      薪の炎と地元の土だけが生み出せる温かみを持ちます。<br>\n      轆轤体験・絵付け体験も受け付けており、<br>\n      工房を訪れる人を器の世界へと誘います。\n    </p>'
    ),
    # Quote
    (
        '"使うたびに手に馴染み、<br>\n              時間が経つほど深みを増す。<br>\n              それが、真の道具だと思っています。"',
        '"土と炎が生み出す偶然の色こそが、<br>\n              大谷焼の魂です。<br>\n              同じ器は、二度と生まれません。"'
    ),
    # Contact heading
    (
        '器との\n              出会いを、\n              ここから。',
        '大谷焼との\n              出会いを、\n              ここから。'
    ),
])

# ──────────────────────────────────────────────
# wazan-demo.html
# ──────────────────────────────────────────────
fix_file('wazan-demo.html', [
    # H1
    (
        '<h1 class="hero-title">\n      土から生まれる、<br><em>静かな器</em>\n    </h1>',
        '<h1 class="hero-title">\n      現代の食卓に、<br><em>波佐見の美</em>\n    </h1>'
    ),
    # Story H2
    (
        '<h2 class="intro-heading">\n      手の記憶が、<br>かたちになる。<br><em>それが器です。</em>\n    </h2>',
        '<h2 class="intro-heading">\n      日常の食卓を、<br>少しだけ豊かに。<br><em>それが波佐見焼です。</em>\n    </h2>'
    ),
    # Story body
    (
        '<p class="intro-body">\n      京都の山あいで、山田太郎は土と向き合い続けています。<br>\n      釉薬の偶然性、炎の揺らぎ、冷ます時間の長さ。<br>\n      ひとつひとつの器に、繰り返しのない一瞬が宿っています。\n    </p>',
        '<p class="intro-body">\n      長崎県波佐見町に、和山の窯元があります。<br>\n      400年の歴史を持つ波佐見焼の伝統を受け継ぎながら、<br>\n      カフェやレストランのような食卓を家庭で実現するデザインを追求。<br>\n      マットな質感、シンプルなフォルム——<br>\n      毎日使うからこそ、美しくあってほしいという思いが込められています。\n    </p>'
    ),
    # Quote
    (
        '"使うたびに手に馴染み、<br>\n              時間が経つほど深みを増す。<br>\n              それが、真の道具だと思っています。"',
        '"毎日使う器だからこそ、<br>\n              飽きのこないデザインが大切です。<br>\n              波佐見焼の伝統と現代の感覚を、一枚に込めています。"'
    ),
    # Contact heading
    (
        '器との\n              出会いを、\n              ここから。',
        '波佐見焼との\n              出会いを、\n              ここから。'
    ),
])

# ──────────────────────────────────────────────
# hiromi-demo.html
# ──────────────────────────────────────────────
fix_file('hiromi-demo.html', [
    # H1（spanタグ入り）
    (
        '<h1 class="hero-title">\n      <span class="ai">藍</span>と<span class="beni">紅</span>が、<br>\n      布に宿る。\n    </h1>',
        '<h1 class="hero-title">\n      炎と七色が、<br>\n      金属に宿る。\n    </h1>'
    ),
    # ストーリー見出し
    (
        '<h2 class="intro-heading">\n      土から生まれた色が、<br>\n      <em>千年後も残る。</em>\n    </h2>',
        '<h2 class="intro-heading">\n      炎が宿した色は、<br>\n      <em>千年後も残る。</em>\n    </h2>'
    ),
    # ストーリー本文
    (
        '<p class="intro-body">\n      京都・西陣の路地奥に、京七宝ヒロミ・アートがあります。<br>\n      初代・山田清次郎が1934年に開いたこの工房では、<br>\n      今も化学染料を一切使いません。<br><br>\n      藍は阿波から。紅花は山形から。<br>\n      季節と天候によって、色は毎年微妙に違います。<br>\n      それが、山田の布に宿る「生きた色」の正体です。\n    </p>',
        '<p class="intro-body">\n      京都・東山のギャラリーショップで、ヒロミ・アートは七宝を作り続けています。<br>\n      七宝焼とは、銅や銀の台地にガラス質の釉薬を重ね、炉で焼き固める工芸。<br>\n      1970年から続くこの工房では、制作・販売・体験教室をすべて行っています。<br><br>\n      外国人観光客にも人気の七宝体験は英語でも受け付けています。<br>\n      作品はCreema・東山店で購入可能。免税対応（Tax Free）もあります。\n    </p>'
    ),
    # コンタクト見出し
    (
        '藍 と 紅 の布を、',
        '京七宝の輝きを、'
    ),
])

print('\n✅ 全5ファイル修正完了')
