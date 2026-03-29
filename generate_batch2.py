#!/usr/bin/env python3
"""Quiet Made – Batch 2 デモ生成スクリプト"""

import re, os, shutil

BASE = '/Users/marika/Desktop/quietmade/'

WORKSHOPS = [
    {
        'id': 'aoya',
        'base': 'wazan-demo.html',   # 静・ミニマルLight
        'name_ja': '谷口・青谷和紙',
        'name_en': 'AOYA WASHI',
        'location': 'Tottori, Japan',
        'location_ja': '鳥取県鳥取市青谷町',
        'tagline_ja': '紙は、生きている。',
        'tagline_en': 'Paper that breathes, shaped by hand.',
        'story_h2': '光を通す、\n      和紙の記憶。\n      <em>それが青谷和紙です。</em>',
        'story_body': (
            '鳥取県青谷町に、谷口・青谷和紙があります。<br>\n'
            '立体漉き和紙という独自の製法で、厚みと表情を持つ和紙を作り続けています。<br>\n'
            '光に透かすと見える繊維のゆらぎが、手漉きならではの証。<br><br>\n'
            '照明・インテリア・アート作品にも使われるその和紙は、<br>\n'
            '暮らしの中に静かな美しさをもたらします。'
        ),
        'philosophy': '「光と影と、紙のあいだ。<br>\n    その余白に、暮らしの豊かさが宿ると信じています。」',
        'philosophy_author': '— 谷口・青谷和紙',
        'contact_intro': '和紙との\n              出会いを、\n              ここから。',
        'products': [
            {'name': '立体漉き和紙', 'sub': 'Handmade washi', 'img': 'https://www.aoyawashi.co.jp/wp-content/themes/taniguchi/images/04-00-01.jpg'},
            {'name': '照明用和紙', 'sub': 'Lighting paper', 'img': 'https://www.aoyawashi.co.jp/wp-content/themes/taniguchi/images/04-00-02.jpg'},
            {'name': 'インテリア和紙', 'sub': 'Interior washi', 'img': 'https://www.aoyawashi.co.jp/wp-content/themes/taniguchi/images/04-00-03.jpg'},
            {'name': 'by n meister', 'sub': 'Design series', 'img': 'https://www.aoyawashi.co.jp/wp-content/themes/taniguchi/images/prd_nmeister.jpg'},
            {'name': '一般和紙', 'sub': 'Traditional paper', 'img': 'https://www.aoyawashi.co.jp/wp-content/themes/taniguchi/images/04-00-04.jpg'},
        ],
        'hero_img': 'https://www.aoyawashi.co.jp/wp-content/themes/taniguchi/images/main.jpg',
        'story_img': 'https://www.aoyawashi.co.jp/wp-content/themes/taniguchi/images/04-00-05.jpg',
        'ticker': 'TOTTORI · HANDMADE WASHI · 立体漉き · JAPANESE PAPER · 鳥取 · AOYA WASHI · ',
        'nav_items': ['作品', '工房について', 'お問い合わせ'],
        'email': 'info@aoyawashi.co.jp',
        'output': 'aoya-demo.html',
    },
    {
        'id': 'shinkukan',
        'base': 'showen-demo.html',  # 華・伝統工芸
        'name_ja': '真空館',
        'name_en': 'SHINKUKAN',
        'location': 'FUKUOKA, JAPAN',
        'location_ja': '福岡県',
        'tagline_ja': '藍は、百年を生きる。',
        'tagline_en': 'A century of indigo, worn today.',
        'story_h2': '100年の藍が、\n      現代の衣に\n      <em>宿る。</em>',
        'story_body': (
            '福岡に、真空館があります。<br>\n'
            '100年の伝統を持つ本藍染の技術で、現代の衣類を染め上げる工房です。<br>\n'
            'Tシャツ・ジーンズ・帯まで、天然の藍が染み込んだ製品は<br>\n'
            '洗うたびに色落ちし、使うほどに味が出る。<br><br>\n'
            'その経年変化こそが、藍染の醍醐味です。'
        ),
        'philosophy': '「藍は生きている。<br>\n      染めた瞬間から、時間と共に変化し続ける。<br>\n      それが、100年変わらない藍染の魅力です。」',
        'philosophy_author': '— 真空館',
        'products': [
            {'name': '藍染め帯', 'sub': 'Traditional obi', 'img': 'https://img14.shop-pro.jp/PA01080/748/product/184721001.jpg'},
            {'name': '藍染めTシャツ', 'sub': 'Indigo T-shirt', 'img': 'https://img14.shop-pro.jp/PA01080/748/product/184721002.jpg'},
            {'name': '紺藍シリーズ', 'sub': 'Deep indigo', 'img': 'https://img14.shop-pro.jp/PA01080/748/product/184721003.jpg'},
            {'name': '藍染め雑貨', 'sub': 'Lifestyle goods', 'img': 'https://img14.shop-pro.jp/PA01080/748/product/184721004.jpg'},
            {'name': 'レディース', 'sub': "Women's line", 'img': 'https://img14.shop-pro.jp/PA01080/748/product/184721005.jpg'},
        ],
        'email': 'https://sinkukan.shop-pro.jp/customer/inquiries/new',
        'output': 'shinkukan-demo.html',
    },
    {
        'id': 'rampuya',
        'base': 'showen-demo.html',  # 華・伝統工芸
        'name_ja': '藍布屋',
        'name_en': 'RAMPUYA',
        'location': 'TOKUSHIMA, JAPAN',
        'location_ja': '徳島県徳島市国府町',
        'tagline_ja': '大正から続く、藍の織り。',
        'tagline_en': 'Woven in indigo since 1912.',
        'story_h2': '大正元年の機が、\n      今日も\n      <em>動いている。</em>',
        'story_body': (
            '徳島県徳島市に、織工房 藍布屋があります。<br>\n'
            '大正元年創業の株式会社岡本織布工場が手掛ける、阿波正藍・しじら織の工房です。<br>\n'
            '旧式の力織機で丁寧に織り上げたデニム生地と藍染め製品は、<br>\n'
            '機械大量生産では出せない風合いと強さを持ちます。<br><br>\n'
            '甚平・作務衣・シャツから暖簾まで、<br>\n'
            '阿波の伝統が現代の暮らしに溶け込みます。'
        ),
        'philosophy': '「阿波の風土が育てた藍と、\n      100年を超えて動き続ける機。<br>\n      その交差点に、藍布屋の布があります。」',
        'philosophy_author': '— 岡本織布工場',
        'products': [
            {'name': '阿波正藍しじら織', 'sub': 'Traditional weave', 'img': 'https://rampuya.com/wp-content/uploads/2017/03/com-logo.png'},
            {'name': '甚平・作務衣', 'sub': 'Japanese wear', 'img': 'https://rampuya.com/wp-content/uploads/top1.jpg'},
            {'name': 'デニム製品', 'sub': 'Denim series', 'img': 'https://rampuya.com/wp-content/uploads/denim.jpg'},
            {'name': 'ストール・スカーフ', 'sub': 'Stole & scarf', 'img': 'https://rampuya.com/wp-content/uploads/stole.jpg'},
            {'name': '暖簾', 'sub': 'Noren curtain', 'img': 'https://rampuya.com/wp-content/uploads/noren.jpg'},
        ],
        'email': 'rampuya@cosmos.ocn.ne.jp',
        'output': 'rampuya-demo.html',
    },
    {
        'id': 'futaai',
        'base': 'tsujiwa-demo.html',  # 技・職人感ダーク
        'name_ja': '藍工房 ふたあい',
        'name_en': 'FUTAAI',
        'location': 'NARUTO, TOKUSHIMA',
        'location_ja': '徳島県鳴門市大麻町',
        'tagline_ja': '藍に魅せられて、半世紀。',
        'tagline_en': 'Half a century devoted to indigo.',
        'story_h2': '型染めの藍が、\n      縁を\n      <em>つなぐ。</em>',
        'story_body': (
            '徳島県鳴門市、阿讃山脈の麓に藍工房 ふたあいがあります。<br>\n'
            '藍染め半世紀——型染め技法を主とする創作藍染の工房です。<br>\n'
            '「藍」を「愛」と読み、「ふたあい」は二つの愛が出会う場所。<br><br>\n'
            '伝統的な藍と現代の藍をクロスオーバーさせた作品は、<br>\n'
            '一点ものの着物からインテリアまで幅広く展開しています。'
        ),
        'philosophy': '「藍に魅せられて半世紀。\n      ひと品の藍染でつながるご縁を、\n      大切にしています。」',
        'philosophy_author': '— 藍工房 ふたあい',
        'products': [
            {'name': '型染め藍染', 'sub': 'Katazome indigo', 'img': 'https://cdn.goope.jp/184721/230306151803rbkb_l.png'},
            {'name': '藍染め着物', 'sub': 'Indigo kimono', 'img': 'https://cdn.goope.jp/184721/211202150533q56c_l.jpg'},
            {'name': 'インテリア作品', 'sub': 'Interior art', 'img': 'https://cdn.goope.jp/184721/211213140239jdv9_l.jpg'},
            {'name': '藍染め小物', 'sub': 'Accessories', 'img': 'https://cdn.goope.jp/184721/211213140239jdv9_l.jpg'},
            {'name': '一点もの', 'sub': 'One of a kind', 'img': 'https://cdn.goope.jp/184721/230306151803rbkb_l.png'},
        ],
        'email': 'tel:088-689-1392',
        'output': 'futaai-demo.html',
    },
    {
        'id': 'yano',
        'base': 'tsujiwa-demo.html',  # 技・職人感ダーク
        'name_ja': '本藍染 矢野工場',
        'name_en': 'YANO KOZYOU',
        'location': 'JAPAN',
        'location_ja': '本藍染製品',
        'tagline_ja': '本物の藍は、嘘をつかない。',
        'tagline_en': 'Authentic indigo. Nothing else.',
        'story_h2': '化学染料ゼロ。\n      本藍だけで\n      <em>染める工場。</em>',
        'story_body': (
            '本藍染 矢野工場は、化学染料を一切使わない本藍染の工場です。<br>\n'
            '天然藍の発酵建て染めによる深い色合いは、<br>\n'
            '機械染めでは絶対に出せない重厚さを持ちます。<br><br>\n'
            'Tシャツ・デニム・帆布まで、すべて本藍のみで染め上げる——<br>\n'
            'その一点に、矢野工場のこだわりが集約されています。'
        ),
        'philosophy': '「化学染料を使えば早い。でも、それは本藍じゃない。<br>\n      手間をかけることが、本物の色を生む唯一の方法です。」',
        'philosophy_author': '— 本藍染 矢野工場',
        'products': [
            {'name': '本藍染Tシャツ', 'sub': 'Indigo T-shirt', 'img': 'http://yanokozyou.com/images/product1.jpg'},
            {'name': '本藍染デニム', 'sub': 'Indigo denim', 'img': 'http://yanokozyou.com/images/product2.jpg'},
            {'name': '本藍染帆布', 'sub': 'Indigo canvas', 'img': 'http://yanokozyou.com/images/product3.jpg'},
            {'name': '本藍染手ぬぐい', 'sub': 'Indigo tenugui', 'img': 'http://yanokozyou.com/images/product4.jpg'},
            {'name': '本藍染小物', 'sub': 'Accessories', 'img': 'http://yanokozyou.com/images/product5.jpg'},
        ],
        'email': 'http://yanokozyou.com/contact.html',
        'output': 'yano-demo.html',
    },
]

def generate_from_wazan(w):
    """静・ミニマルLightスタイル（wazan-demo.htmlベース）"""
    with open(BASE + 'wazan-demo.html', 'r') as f:
        c = f.read()

    # 基本情報
    c = c.replace('WAZAN — Hasami, Nagasaki', f'{w["name_en"]} — {w["location"]}')
    c = c.replace('和 山', w['name_ja'].replace(' ', '　'))
    c = c.replace('WAZAN', w['name_en'])
    c = c.replace('Hasami, Nagasaki', w['location'])
    c = c.replace('波佐見焼との\n              出会いを、\n              ここから。',
                  w.get('contact_intro', f'{w["name_ja"]}との\n              出会いを、\n              ここから。'))

    # キャッチコピー
    c = c.replace('現代の食卓に、<br><em>波佐見の美</em>',
                  w['tagline_ja'].replace('、', '、<br><em>').replace('。', '</em>'))
    c = c.replace('日常の食卓が、少し豊かになる。', w['tagline_en'])

    # ストーリー
    c = re.sub(r'<h2 class="intro-heading">.*?</h2>',
               f'<h2 class="intro-heading">\n      {w["story_h2"]}\n    </h2>', c, flags=re.DOTALL)
    c = re.sub(r'<p class="intro-body">.*?</p>',
               f'<p class="intro-body">\n      {w["story_body"]}\n    </p>', c, flags=re.DOTALL)

    # Philosophy
    c = re.sub(r'<blockquote class="philosophy-quote reveal">.*?</blockquote>',
               f'<blockquote class="philosophy-quote reveal">\n    {w["philosophy"]}\n  </blockquote>',
               c, flags=re.DOTALL)
    c = re.sub(r'<p class="philosophy-author reveal">.*?</p>',
               f'<p class="philosophy-author reveal">{w["philosophy_author"]}</p>', c)

    # ヒーロー画像
    if w.get('hero_img'):
        c = re.sub(r'background-image:\s*url\(["\']?wazan-hero\.jpg["\']?\)',
                   f'background-image: url("{w["hero_img"]}")', c)
    if w.get('story_img'):
        c = c.replace('src="wazan-story.jpg"', f'src="{w["story_img"]}"')

    # 商品
    for i, p in enumerate(w['products'][:5], 1):
        c = c.replace(f'src="wazan-{i}.jpg"', f'src="{p["img"]}"')

    return c

def generate_from_showen(w):
    """華・伝統工芸スタイル（showen-demo.htmlベース）"""
    with open(BASE + 'showen-demo.html', 'r') as f:
        c = f.read()

    c = c.replace('昇 苑 く み ひ も', w['name_ja'])
    c = c.replace('SHOWEN KUMIHIMO — UJI, KYOTO', f'{w["name_en"]} — {w["location"]}')
    c = c.replace('昇苑くみひも', w['name_ja'])
    c = c.replace('SHOWEN KUMIHIMO', w['name_en'])
    c = c.replace('UJI, KYOTO', w['location'])
    c = c.replace('紐は、<br>\n      縁を結ぶ。', w['tagline_ja'].replace('、', '、<br>'))
    c = c.replace('Where every thread binds objects, people, and fate.', w['tagline_en'])

    # ストーリー
    c = re.sub(r'<h2 class="intro-heading">.*?</h2>',
               f'<h2 class="intro-heading">\n      {w["story_h2"]}\n    </h2>', c, flags=re.DOTALL)
    c = re.sub(r'<p class="intro-body">.*?</p>',
               f'<p class="intro-body">\n      {w["story_body"]}\n    </p>', c, flags=re.DOTALL)

    # Philosophy
    c = re.sub(r'<blockquote class="philosophy-quote reveal">.*?</blockquote>',
               f'<blockquote class="philosophy-quote reveal">\n    {w["philosophy"]}\n  </blockquote>',
               c, flags=re.DOTALL)
    c = re.sub(r'<p class="philosophy-author reveal">.*?</p>',
               f'<p class="philosophy-author reveal">{w["philosophy_author"]}</p>', c)

    # ナビ・フッター
    c = c.replace('京の組紐を、', f'{w["name_ja"]}の作品を、')

    # 作品画像
    for i, p in enumerate(w['products'][:5], 1):
        c = c.replace(f'src="showen-{i}.jpg"', f'src="{p["img"]}"')

    # ヒーロー背景
    c = c.replace('src="showen-story.jpg"', f'src="{w.get("story_img", "showen-story.jpg")}"')

    return c

def generate_from_tsujiwa(w):
    """技・職人感ダークスタイル（tsujiwa-demo.htmlベース）"""
    with open(BASE + 'tsujiwa-demo.html', 'r') as f:
        c = f.read()

    c = c.replace('辻和金網', w['name_ja'])
    c = c.replace('TSUJIWA KANAAMI', w['name_en'])
    c = c.replace('KYOTO, JAPAN', w['location'])
    c = c.replace('京都府京都市中京区', w['location_ja'])

    # ストーリー見出し
    c = re.sub(r'<h2 class="story-heading">.*?</h2>',
               f'<h2 class="story-heading">\n      {w["story_h2"]}\n    </h2>', c, flags=re.DOTALL)

    # ストーリー本文
    c = re.sub(r'<p class="story-body">.*?</p>',
               f'<p class="story-body">\n      {w["story_body"]}\n    </p>', c, flags=re.DOTALL)

    # 商品画像
    for i, p in enumerate(w['products'][:5], 1):
        c = c.replace(f'src="tsujiwa-{i}.jpg"', f'src="{p["img"]}"')

    return c

# ── 生成実行 ──
generators = {
    'wazan-demo.html': generate_from_wazan,
    'showen-demo.html': generate_from_showen,
    'tsujiwa-demo.html': generate_from_tsujiwa,
}

for w in WORKSHOPS:
    gen_fn = generators[w['base']]
    html = gen_fn(w)
    out = BASE + w['output']
    with open(out, 'w') as f:
        f.write(html)
    print(f"✅ {w['output']} 生成完了")

print('\n🎉 全5件のデモ生成完了！')
print('\n各デモのURL:')
for w in WORKSHOPS:
    print(f"  https://marimon4.github.io/quiet-made-demos/{w['output']}")
