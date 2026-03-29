#!/usr/bin/env python3
"""Quiet Made – Batch 3 デモ生成スクリプト
テンプレートから直接生成、山田/Yamada 等の残渣を完全除去
"""

import re, os

TMPL_DIR = '/Users/marika/Downloads/quiet-made-templates/'
OUT_DIR  = '/Users/marika/Desktop/quietmade/'

# ── Workshop データ ──────────────────────────────────────────

WORKSHOPS = [

    # 1. 伊勢形紙協同組合 → shokunin-template
    {
        'id':           'isekatagami',
        'template':     'shokunin-template.html',
        'output':       'isekatagami-demo.html',
        'name_ja':      '伊勢形紙',
        'name_ja_logo': '伊勢<span>/</span>形紙',
        'name_en':      'ISE KATAGAMI',
        'location':     'SUZUKA, MIE',
        'location_ja':  '三重県鈴鹿市',
        'since':        '千年以上の歴史',
        'title_tag':    '伊勢形紙 — Ise Katagami',
        'hero_label':   'Ise Katagami — Suzuka, Since 800',
        'hero_keyword': ['型', '紋', '美', '彫'],
        'hero_sub':     '千年、職人の刃が刻む文様。',
        'stats': [
            ('1,000+', 'Years',       '千年以上の伝統'),
            ('4',      'Techniques',  '四種の彫り技法'),
            ('30+',    'Countries',   '海外30カ国以上へ'),
            ('∞',      'Patterns',    '二つとない型'),
        ],
        'story_heading': '刃が紙に触れる、<br>\n      その一瞬だけが<br>\n      <em>型の命。</em>',
        'story_body':    (
            '三重県鈴鹿市に、伊勢形紙協同組合があります。<br>\n'
            '千年以上の歴史を持つ型染め用型紙の産地として、経済産業大臣指定の伝統的工芸品用具を製造しています。<br><br>\n'
            '柿渋で貼り合わせた和紙に、専用の彫刻刀で緻密な文様を彫り出す。<br>\n'
            '縞彫・突彫・道具彫・錐彫、四種の技法が織りなす細密な世界。<br>\n'
            'その型一枚から、着物の染め文様が生まれます。'
        ),
        'story_img_tag': 'Ise Katagami Studio',
        'works': [
            ('衣の型',   'Textile Stencil'),
            ('住の型',   'Interior Pattern'),
            ('楽の型',   'Gift & Art'),
        ],
        'process': [
            ('紙選び',  '柿渋で貼り合わせた<br>手漉き和紙を厳選。<br>型の強度を左右する<br>最初の一歩。'),
            ('下絵',    '文様の下絵を紙に<br>転写する。千年伝わる<br>文様と、現代の<br>デザインが交わる。'),
            ('彫刻',    '縞・突・道具・錐——<br>四種の彫り技法で、<br>0.3ミリ以下の<br>精緻な模様を刻む。'),
            ('仕上げ',  '型を強化する<br>燻煙仕上げ。<br>それが職人の<br>最後の仕事。'),
        ],
        'contact_heading': '型紙との<br>\n      <span>出会いを、</span><br>\n      ここから。',
        'contact_sub':     '体験・受注・取材のお問い合わせ',
        'email':           'ise-k@mecha.ne.jp',
        'footer_copy':     '© 2025 Ise Katagami Cooperative. All rights reserved.',
    },

    # 2. 華正工房 → modern-wa-template
    {
        'id':           'kasyo',
        'template':     'modern-wa-template.html',
        'output':       'kasyo-demo.html',
        'name_ja':      '華正工房',
        'name_en':      'KASYO STUDIO',
        'location':     'YAMANAKA, ISHIKAWA',
        'location_ja':  '石川県加賀市山中温泉',
        'since':        '1986',
        'title_tag':    '漆 / Urushi — 華正工房',
        'hero_vertical':'Kasyo Studio — Yamanaka, Since 1986',
        'hero_kanji':   '漆',
        'hero_kanji_en':'Urushi — Living Lacquer',
        'concept_text': (
            '石川県山中温泉に、よした華正工房があります。<br>\n'
            '山中漆器の蒔絵技法で茶道具と和食器を作り続ける漆芸の工房。<br>\n'
            '漆は、塗るたびに深みを増す。磨くたびに光を宿す。<br><br>\n'
            'その静かな輝きに魅せられた職人が、一筆一筆、金粉を置いていく。'
        ),
        'works': [
            ('茶道具',   'Tea Ceremony Ware'),
            ('蒔絵漆器', 'Makie Lacquerware'),
            ('和食器',   'Japanese Tableware'),
            ('アクセサリー', 'Accessories'),
            ('金継ぎ',   'Kintsugi Repair'),
            ('蒔絵体験', 'Makie Experience'),
        ],
        'philosophy': '「漆は生きている。<br>\n    塗るたびに表情が変わり、<br>\n    使うほどに艶が増す。<br>\n    それが山中漆器の醍醐味です。」',
        'philosophy_author': '— 吉田 華正',
        'email': 'info@kasyoustudio.co.jp',
        'footer_copy': '© 2025 Kasyo Studio. All rights reserved.',
    },

    # 3. 有馬籠 → shokunin-template
    {
        'id':           'arimakago',
        'template':     'shokunin-template.html',
        'output':       'arimakago-demo.html',
        'name_ja':      '有馬籠',
        'name_ja_logo': '有馬<span>/</span>籠',
        'name_en':      'ARIMAKAGO',
        'location':     'ARIMA, HYOGO',
        'location_ja':  '兵庫県神戸市有馬温泉',
        'since':        'Since 1585',
        'title_tag':    '有馬籠 — Arimakago',
        'hero_label':   'Arimakago — Arima, Since 1585',
        'hero_keyword': ['竹', '籠', '編', '美'],
        'hero_sub':     '千利休が愛した、竹の形。',
        'stats': [
            ('1585',   'Est.',        '安土桃山時代より'),
            ('1',      'Tradition',   '兵庫県知事指定工芸品'),
            ('30+',    'Countries',   '世界へ届いた竹籠'),
            ('∞',      'Unique',      '二つとない一点もの'),
        ],
        'story_heading': '竹が、人の手で<br>\n      命を持つ——<br>\n      <em>有馬の籠。</em>',
        'story_body':    (
            '兵庫県有馬温泉に、有馬籠があります。<br>\n'
            '1585年、千利休が豊臣秀吉のために有馬で花籠を作らせたのが起源。<br><br>\n'
            '安土桃山時代から続く竹工芸の伝統を、職人・杠 松竹斎が今に伝えています。<br>\n'
            '六甲山系の良質な竹を素材に、丁寧に編み上げた花籠は<br>\n'
            '兵庫県知事指定の伝統的工芸品。1873年ウィーン万博でも優秀賞を受けた技です。'
        ),
        'story_img_tag': 'Arimakago Studio',
        'works': [
            ('花籠',   'Flower Basket'),
            ('茶籠',   'Tea Basket'),
            ('一点もの', 'One of a Kind'),
        ],
        'process': [
            ('竹選び',  '六甲山系で育った<br>良質な竹を選ぶ。<br>素材選びが<br>仕上がりを決める。'),
            ('割き',   '竹を薄く均一に<br>割いていく。<br>この工程の精度が<br>編み目の美しさを決める。'),
            ('編み',   '伝統の編み技法で<br>一本ずつ丁寧に。<br>花籠の表情は<br>職人の指が作る。'),
            ('仕上げ', '竹の自然な艶を<br>活かした仕上げ。<br>時間と共に<br>飴色へと育つ。'),
        ],
        'contact_heading': '竹との<br>\n      <span>出会いを、</span><br>\n      ここから。',
        'contact_sub':     '購入・取材・展示のお問い合わせ',
        'email':           'info@arimakago.jp',
        'footer_copy':     '© 2025 Arimakago. All rights reserved.',
    },

    # 4. 青竹工房 桐山 → shokunin-template
    {
        'id':           'kiriyama',
        'template':     'shokunin-template.html',
        'output':       'kiriyama-demo.html',
        'name_ja':      '青竹工房 桐山',
        'name_ja_logo': '桐山<span>/</span>竹',
        'name_en':      'KIRIYAMA',
        'location':     'TAKETA, OITA',
        'location_ja':  '大分県竹田市',
        'since':        'Since 1992',
        'title_tag':    '青竹工房 桐山 — Kiriyama',
        'hero_label':   'Kiriyama — Taketa, Since 1992',
        'hero_keyword': ['青', '竹', '編', '形'],
        'hero_sub':     '使うほどに育つ、青竹の籠。',
        'stats': [
            ('30+',    'Years',       '竹一筋30余年'),
            ('20+',    'Awards',      '全国公募展受賞多数'),
            ('1',      'Artisan',     '全工程ひとりの手仕事'),
            ('∞',      'Forms',       '同じ籠は二つとない'),
        ],
        'story_heading': 'カゴのカタチは、<br>\n      暮らしの<br>\n      <em>カタチ。</em>',
        'story_body':    (
            '大分県竹田市に、青竹工房 桐山があります。<br>\n'
            '1992年から竹籠編みひとすじ、職人・桐山 浩実が青竹の素材と向き合い続けています。<br><br>\n'
            '竹の伐採から篩作り・籠編みまで、全工程を一人で担う。<br>\n'
            '青竹は使い込むほどに飴色へと変化し、それが「育つ籠」の醍醐味。<br>\n'
            '伊勢丹・三越・高島屋での個展実績を持つ、受賞歴豊かな工芸家の仕事です。'
        ),
        'story_img_tag': 'Kiriyama Studio',
        'works': [
            ('花籠',   'Flower Basket'),
            ('盛り籠', 'Fruit Basket'),
            ('一点もの', 'Exhibition Work'),
        ],
        'process': [
            ('竹の見極め', '竹林に入り、<br>伐り時の竹を<br>自ら選ぶ。<br>素材との対話から始まる。'),
            ('割き・磨き', '青竹を割き、<br>均一な幅に整える。<br>水分を含んだ生竹は<br>柔軟で加工しやすい。'),
            ('編み',   '伝統の技法と<br>独自の感性を融合。<br>一本一本の竹が<br>立体的な形になる。'),
            ('経年変化', '青から飴色へ——<br>使い続けるほどに<br>深みが増す。<br>それが竹籠の本質。'),
        ],
        'contact_heading': '籠との<br>\n      <span>出会いを、</span><br>\n      ここから。',
        'contact_sub':     '購入・展覧会・取材のお問い合わせ',
        'email':           'info@aotakekobo-kiriyama.com',
        'footer_copy':     '© 2025 Kiriyama Bamboo Studio. All rights reserved.',
    },

    # 5. 創作工房 中野竹藝 → shokunin-template
    {
        'id':           'nakano',
        'template':     'shokunin-template.html',
        'output':       'nakano-demo.html',
        'name_ja':      '中野竹藝',
        'name_ja_logo': '中野<span>/</span>竹藝',
        'name_en':      'NAKANO CHIKUGEI',
        'location':     'KURAYOSHI, TOTTORI',
        'location_ja':  '鳥取県倉吉市',
        'since':        'Est. 1912',
        'title_tag':    '中野竹藝 — Nakano Chikugei',
        'hero_label':   'Nakano Chikugei — Kurayoshi, Est. 1912',
        'hero_keyword': ['竹', '技', '伝', '美'],
        'hero_sub':     '皇室献上の技が、暮らしに宿る。',
        'stats': [
            ('1912',   'Est.',        '大正元年創業'),
            ('100+',   'Years',       '色褪せない染色技術'),
            ('∞',      'Patterns',    '丸竹加工の唯一無二'),
            ('3',      'Locations',   '倉吉に三つの拠点'),
        ],
        'story_heading': '竹を割らずに<br>\n      曲げる——<br>\n      <em>至難の技。</em>',
        'story_body':    (
            '鳥取県倉吉市に、創作工房 中野竹藝があります。<br>\n'
            '大正元年創業の老舗竹工芸工房。歴代天皇への献上品を製造してきた技の工房です。<br><br>\n'
            '「丸竹加工」——竹を割らずに曲げるという竹工芸界でも希少な技術。<br>\n'
            '植物染料を6ヶ月煮込み、100年以上色褪せない染色を実現。<br>\n'
            '中国山地産の鳳尾竹が、職人の手で現代の美しさに生まれ変わります。'
        ),
        'story_img_tag': 'Nakano Chikugei Studio',
        'works': [
            ('竹バッグ',  'Bamboo Bag'),
            ('花入れ',   'Flower Vase'),
            ('茶道具',   'Tea Ceremony'),
        ],
        'process': [
            ('素材選び', '中国山地産<br>鳳尾竹を厳選。<br>質と産地にこだわる<br>素材の目利き。'),
            ('丸竹加工', '割らずに曲げる——<br>竹工芸界でも<br>希少な至難の技。<br>職人の経験が全て。'),
            ('植物染色', '植物染料を<br>6ヶ月間煮込む。<br>100年色褪せない<br>染色が完成する。'),
            ('仕上げ',  '漆を施して<br>艶と強度を加える。<br>献上品に相応しい<br>最後の手仕事。'),
        ],
        'contact_heading': '竹藝との<br>\n      <span>出会いを、</span><br>\n      ここから。',
        'contact_sub':     '購入・取材・展示のお問い合わせ',
        'email':           'info@nakano-chikugei.com',
        'footer_copy':     '© 2025 Nakano Chikugei. All rights reserved.',
    },
]


# ── ジェネレーター ──────────────────────────────────────────

def gen_shokunin(w):
    with open(TMPL_DIR + 'shokunin-template.html', 'r') as f:
        c = f.read()

    # Title & meta
    c = c.replace('<title>山田窯 — Yamada Kiln</title>', f'<title>{w["title_tag"]}</title>')

    # Nav logo
    c = c.replace('山田<span>/</span>窯', w['name_ja_logo'])

    # Hero
    c = c.replace('Yamada Kiln — Kyoto, Since 1952', w['hero_label'])
    c = c.replace('三代にわたる、手仕事の誇り。', w['hero_sub'])

    # Hero keywords JS array
    kw = w['hero_keyword']
    old_kw = "const keywords = ['技', '土', '炎', '器'];"
    new_kw = f"const keywords = ['{kw[0]}', '{kw[1]}', '{kw[2]}', '{kw[3]}'];"
    c = c.replace(old_kw, new_kw)

    # Stats (4 stats)
    stats = w['stats']
    old_stats = [
        ('70+', 'Years',       '創業70余年'),
        ('3',   'Generations', '三代の職人技'),
        ('12',  'Countries',   '海外12カ国に届く'),
        ('∞',   'Unique Pieces','同じ器はひとつもない'),
    ]
    for old, new in zip(old_stats, stats):
        c = c.replace(f'<span class="stat-num">{old[0]}</span>', f'<span class="stat-num">{new[0]}</span>', 1)
        c = c.replace(f'<span class="stat-label">{old[1]}</span>', f'<span class="stat-label">{new[1]}</span>', 1)
        c = c.replace(f'<span class="stat-desc">{old[2]}</span>', f'<span class="stat-desc">{new[2]}</span>', 1)

    # Story heading
    c = re.sub(
        r'<h2 class="story-heading">.*?</h2>',
        f'<h2 class="story-heading">\n      {w["story_heading"]}\n    </h2>',
        c, flags=re.DOTALL
    )

    # Story body
    c = re.sub(
        r'<p class="story-body">.*?</p>',
        f'<p class="story-body">\n      {w["story_body"]}\n    </p>',
        c, flags=re.DOTALL
    )

    # Story img tag
    c = c.replace('Yamada Studio', w['story_img_tag'])

    # Works section title (keep as-is: 作品)
    # Work card names
    old_works = [('日常の器', 'Everyday Ware'), ('茶道具', 'Tea Ceremony'), ('一点もの', 'One of a Kind')]
    for old, new in zip(old_works, w['works']):
        c = c.replace(f'<div class="work-card-name">{old[0]}</div>', f'<div class="work-card-name">{new[0]}</div>', 1)
        c = c.replace(f'<div class="work-card-en">{old[1]}</div>', f'<div class="work-card-en">{new[1]}</div>', 1)

    # Process steps
    old_proc = [
        ('土選び',  '信楽、備前、京土。<br>作品の用途と<br>季節に合わせて<br>土を選ぶところから始まる。'),
        ('成形',    '轆轤を使わず、<br>手だけで土を<br>整える。形が生まれる<br>瞬間は二度とない。'),
        ('釉薬',    '配合は非公開。<br>炎の温度と<br>時間が、最終的な<br>表情を決める。'),
        ('焼成',    f'薪窯で72時間。<br>炎と対話しながら、<br>職人が番をする。<br>それが山田窯の流儀。'),
    ]
    for old, new in zip(old_proc, w['process']):
        c = c.replace(f'<div class="process-step-name">{old[0]}</div>', f'<div class="process-step-name">{new[0]}</div>', 1)
        c = c.replace(f'<p class="process-step-desc">{old[1]}</p>', f'<p class="process-step-desc">{new[1]}</p>', 1)

    # Contact
    c = re.sub(
        r'<h2 class="contact-heading">.*?</h2>',
        f'<h2 class="contact-heading">{w["contact_heading"]}</h2>',
        c, flags=re.DOTALL
    )
    c = re.sub(
        r'<p class="contact-sub">.*?</p>',
        f'<p class="contact-sub">{w["contact_sub"]}</p>',
        c, flags=re.DOTALL
    )
    c = c.replace('placeholder="山田 太郎"', f'placeholder="お名前"')
    c = c.replace(
        '購入のご相談、受注制作のご依頼、<br>\n      展示会・取材のお問い合わせ、<br>',
        f'購入のご相談、受注のご依頼、<br>\n      展示会・取材のお問い合わせ、<br>'
    )

    # Email/action
    old_mailto = 'action="mailto:yamada@kiln.jp"'
    c = c.replace(old_mailto, f'action="mailto:{w["email"]}"')

    # Footer
    c = c.replace(
        '<span class="footer-logo">山田<span>/</span>窯</span>',
        f'<span class="footer-logo">{w["name_ja_logo"]}</span>'
    )
    c = c.replace(
        '© 2025 Yamada Kiln. All rights reserved.',
        w['footer_copy']
    )

    return c


def gen_modern_wa(w):
    with open(TMPL_DIR + 'modern-wa-template.html', 'r') as f:
        c = f.read()

    # Title
    c = c.replace('<title>間 / Ma — 山田花器</title>', f'<title>{w["title_tag"]}</title>')

    # Nav logo
    c = re.sub(r'<a[^>]*class="nav-logo"[^>]*>.*?</a>', f'<a href="#" class="nav-logo">{w["name_en"]}</a>', c, count=1, flags=re.DOTALL)

    # Hero vertical text
    c = c.replace('Yamada Flower Vessel — Kyoto', w['hero_vertical'])

    # Hero kanji & en
    c = re.sub(r'<span class="scroll-kanji-en">Ma — Negative Space</span>',
               f'<span class="scroll-kanji-en">{w["hero_kanji_en"]}</span>', c)

    # Concept text
    c = re.sub(
        r'山田花器は、京都の茶室文化から生まれた花器工房です。.*?(?=<br><br>|</p>)',
        w['concept_text'],
        c, flags=re.DOTALL, count=1
    )

    # Concept body text
    c = c.replace(
        '花器は、花を飾るための道具ではありません。',
        '漆は、塗るほどに深みを増す素材です。'
    )
    c = c.replace(
        '山田花器は、茶道の美意識を現代に翻訳します。',
        f'{w["name_ja"]}は、山中漆器の蒔絵技法を現代に伝えます。'
    )

    # Philosophy quote
    c = c.replace(
        '"I do not make vessels.<br>\n      I make the silence<br>\n      <em>around a flower."</em>',
        w['philosophy']
    )
    c = c.replace('— 山田 誠一, 二代目', w['philosophy_author'])

    # Works
    old_works_ja = ['茶器', '花器', '酒器', '食器', 'オブジェ', '受注制作']
    old_works_en = ['Tea Ware', 'Flower Vase', 'Sake Ware', 'Tableware', 'Art Object', 'Custom Order']
    for old_ja, old_en, new in zip(old_works_ja, old_works_en, w['works']):
        c = c.replace(old_ja, new[0], 1)
        c = c.replace(old_en, new[1], 1)

    # Footer logo
    c = c.replace('Ma — 間', w['name_ja'])

    # Footer copy
    c = c.replace('山田花器', w['name_ja'])
    c = c.replace('Yamada Flower Vessel', w['name_en'])
    c = c.replace('© 2025 Yamada Flower Vessel', f'© 2025 {w["name_en"]}')

    return c


# ── 実行 ────────────────────────────────────────────────────

generators = {
    'shokunin-template.html': gen_shokunin,
    'modern-wa-template.html': gen_modern_wa,
}

for w in WORKSHOPS:
    gen_fn = generators[w['template']]
    html = gen_fn(w)
    out = OUT_DIR + w['output']
    with open(out, 'w') as f:
        f.write(html)
    print(f"✅ {w['output']} 生成完了")

print('\n🎉 全5件 Batch 3 生成完了！')
for w in WORKSHOPS:
    print(f"  → quiet-made.jp/{w['output']}")
