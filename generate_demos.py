#!/usr/bin/env python3
"""
Quiet Made — Demo Site Generator
5工房のデモHTMLを一括生成
"""

import os

TEMPLATES = {
    'senshoku':      '/Users/marika/Downloads/quiet-made-templates/senshoku-template.html',
    'modern-wa':     '/Users/marika/Downloads/quiet-made-templates/modern-wa-template.html',
    'yamada-pottery':'/Users/marika/Downloads/quiet-made-templates/yamada-pottery.html',
}

OUTPUT_DIR = '/Users/marika/Desktop/quietmade/'

def replace_all(content, replacements):
    for old, new in replacements:
        content = content.replace(old, new)
    return content

# ─────────────────────────────────────────────
# 1. 昇苑くみひも — senshoku テンプレ
# ─────────────────────────────────────────────
showen_replacements = [
    # <title>
    ('山田染色工房 — Yamada Dye Studio', '昇苑くみひも — Showen Kumihimo'),
    # ナビ
    ('山田染色工房', '昇苑くみひも'),
    ('Yamada Dye Studio — Kyoto, Since 1934', 'Showen Kumihimo — Uji, Kyoto'),
    # Hero キャッチ
    ('藍 と 紅 が、\n           布に宿る。', '紐は、\n           縁を結ぶ。'),
    ('藍 と 紅 が、 布に宿る。', '紐は、 縁を結ぶ。'),
    ('Where ancient pigments meet living cloth.', 'Where every thread binds objects, people, and fate.'),
    # Hero サブテキスト
    ('天然の藍と紅花だけで染める、山田染色工房。\n              90年の歴史が積み重なった色は、\n              化学染料には出せない深みを持っています。',
     '京都・宇治に伝わる組紐の技を守る、昇苑くみひも。\n              一本の紐が持つ力は、モノとモノ、人と人を結ぶこと。\n              機械では出せない手組みの質感と美しさを追求しています。'),
    ('天然の藍と紅花だけで染める、山田染色工房。', '京都・宇治に伝わる組紐の技を守る、昇苑くみひも。'),
    ('90年の歴史が積み重なった色は、', '一本の紐が持つ力は、モノとモノ、人と人を結ぶこと。'),
    ('化学染料には出せない深みを持っています。', '機械では出せない手組みの質感と美しさを追求しています。'),
    # ナビリンク
    ('作品', '作品'),
    ('制作工程', '制作工程'),
    # Story heading
    ('土から生まれた色が、\n           千年後も残る。', '紐が結ぶ、\n           千年の縁。'),
    ('土から生まれた色が、 千年後も残る。', '紐が結ぶ、 千年の縁。'),
    # Story body
    ('京都・西陣の路地奥に、山田染色工房があります。\n              初代・山田清次郎が1934年に開いたこの工房では、\n              今も化学染料を一切使いません。\n              藍は阿波から。紅花は山形から。\n              季節と天候によって、色は毎年微妙に違います。\n              それが、山田の布に宿る「生きた色」の正体です。',
     '京都・宇治の地で、昇苑くみひもは京くみひもを作り続けています。\n              帯締め、羽織紐、装身具——一本一本、手で組み上げる紐は\n              機械生産では決して生まれない微妙な張りとしなやかさを持ちます。\n              「紐はモノとモノを結ぶ、紐は人と人を結ぶ、紐は縁を結ぶ」。\n              その信念のもと、職人の手が今日も糸を紡いでいます。'),
    # 染め分類タグ
    ('藍染め作品', 'くみひも作品'),
    ('紅染め作品', '帯締め作品'),
    # コレクション
    ('01</span>\n              藍染めストール\n              <em>Indigo Stole</em>', '01</span>\n              帯締め\n              <em>Obi-jime</em>'),
    ('02</span>\n              絞り染め反物\n              <em>Shibori Cloth</em>', '02</span>\n              羽織紐\n              <em>Haori Cord</em>'),
    ('03</span>\n              天然顔料\n              <em>Natural Pigments</em>', '03</span>\n              くみひもアクセサリー\n              <em>Kumihimo Accessories</em>'),
    ('04</span>\n              掛け作品\n              <em>Hanging Works</em>', '04</span>\n              組紐キット\n              <em>Kumihimo Kit</em>'),
    ('05</span>\n              型染め布\n              <em>Stencil Dyed</em>', '05</span>\n              特注品\n              <em>Custom Orders</em>'),
    # 簡易マッチ（スペース等が異なる場合の保険）
    ('藍染めストール', '帯締め'),
    ('Indigo Stole', 'Obi-jime'),
    ('絞り染め反物', '羽織紐'),
    ('Shibori Cloth', 'Haori Cord'),
    ('天然顔料', 'くみひもアクセサリー'),
    ('Natural Pigments', 'Kumihimo Accessories'),
    ('掛け作品', '組紐キット'),
    ('Hanging Works', 'Kumihimo Kit'),
    ('型染め布', '特注品'),
    ('Stencil Dyed', 'Custom Orders'),
    # 哲学クォート
    ('「色は、自然からの\n                借り物です。\n                職人の仕事は、\n                その色を布に\n                お返しすること。」',
     '「紐は道具ではありません。\n                人と人を結ぶ、\n                目に見えない縁の\n                形です。」'),
    ('— 山田 三郎, 三代目', '— 昇苑くみひも'),
    ('「色は、自然からの 借り物です。 職人の仕事は、 その色を布に お返しすること。」', '「紐は道具ではありません。人と人を結ぶ、目に見えない縁の形です。」'),
    # 制作工程
    ('How We Dye', 'How We Braid'),
    ('素材選び', '糸選び'),
    ('Material', 'Material'),
    ('絹・麻・木綿。\n                染まりやすさと\n                色の出方は\n                素材で全て変わる。',
     '絹・綿・合繊。\n                組み上がりの質感と\n                光沢は素材で\n                全て変わる。'),
    ('灰汁引き', '台設け'),
    ('Preparation', 'Setup'),
    ('染料を定着させる\n                ための下処理。\n                ここを丁寧にすると\n                色が長持ちする。',
     '丸台・高台などの\n                組台に糸をセット。\n                ここでの精度が\n                仕上がりを決める。'),
    ('染め', '組み'),
    ('Dyeing', 'Braiding'),
    ('藍は発酵桶で。\n                紅は煮汁で。\n                温度と時間が、\n                色の深さを決める。',
     '数十本〜数百本の糸を\n                交差させながら組む。\n                均一な力加減が\n                美しさを生む。'),
    ('水洗い', '検反'),
    ('Washing', 'Inspection'),
    ('京都の伏流水で\n                丁寧に洗う。\n                色が落ち着き、\n                本来の表情が出る。',
     '完成した紐を広げ、\n                歪みやムラがないか\n                一本一本確認する。'),
    ('仕上げ', '仕上げ'),
    ('Finishing', 'Finishing'),
    ('乾燥・張り・検品。\n                一反ずつ手で確認し、\n                問題がなければ\n                初めて完成となる。',
     '端部処理・長さ調整。\n                職人が手で確認し、\n                問題がなければ\n                初めて完成となる。'),
    # お問い合わせ
    ('藍 と 紅 の布を、\n             あなたのもとへ。',
     '京の組紐を、\n             あなたのもとへ。'),
    ('作品のご購入、受注染めのご依頼、\n              工房見学のご予約など、\n              お気軽にお問い合わせください。',
     '作品のご購入、特注のご依頼、\n              工房見学のご予約など、\n              お気軽にお問い合わせください。'),
    # フッター
    ('© 2025 Yamada Dye Studio. Kyoto, Japan.', '© 2025 昇苑くみひも. Uji, Kyoto.'),
]

# ─────────────────────────────────────────────
# 2. SUZUEMON — modern-wa テンプレ
# ─────────────────────────────────────────────
suzuemon_replacements = [
    # title
    ('間 / Ma — 山田花器', '錫 / Suzu — 京都錫右衛門'),
    # ナビ
    ('Ma', 'Suzu'),
    ('山田花器', '京都錫右衛門'),
    # nav sub
    ('Yamada Flower Vessel', 'SUZUEMON'),
    # Hero大漢字
    ('間', '錫'),
    # コンセプトワード（ループバナー等）
    ('間\n              <em>Ma</em> — Negative Space', '錫\n              <em>Suzu</em> — Pure Tin'),
    ('静\n              <em>Sei</em> — Stillness', '純\n              <em>Jun</em> — Purity'),
    ('美\n              <em>Bi</em> — Beauty', '技\n              <em>Waza</em> — Craft'),
    ('器\n              <em>Utsuwa</em> — Vessel', '器\n              <em>Utsuwa</em> — Vessel'),
    # 簡易
    ('Ma — Negative Space', 'Suzu — Pure Tin'),
    ('Sei — Stillness', 'Jun — Purity'),
    ('Bi — Beauty', 'Waza — Craft'),
    # Hero英語
    ('The space between things is where beauty lives.', 'Handcrafted pure tin, shaped by 45 years of mastery.'),
    ('余白に宿る、美しさ。', '純錫が宿す、静かな美しさ。'),
    # Hero説明
    ('山田花器は、京都の茶室文化から生まれた花器工房です。\n              使うほどに深まる、静かな美しさを追求しています。',
     '京都の錫職人・小泉仁が手がける、純錫器の工房。\n              99.9%の純錫を砂型鋳造で成形し、一点一点手で仕上げます。'),
    # Explore
    ('Explore the Collection →', 'View the Collection →'),
    # サブタイトル
    ('Kyoto', 'Kyoto'),
    # Philosophy heading
    ('The vessel holds what words cannot.', 'Pour once. Taste the difference.'),
    ('言葉にできないものを、器は受け止める。', '注ぐだけで、味が変わる。'),
    # Philosophy body
    ('花器は、花を飾るための道具ではありません。\n              空間に「間」を生み出すための存在です。\n              山田花器は、茶道の美意識を現代に翻訳します。\n              過剰ではなく、不足でもなく——ちょうどいい静けさ。\n              その一点を、ひとつひとつ手で作り続けています。',
     '錫は、ビールを注げば泡がきめ細かくなり、日本酒は丸みを帯びる。\n              この不思議な作用は、錫の熱伝導性と微弱なイオン効果によるもの。\n              京都錫右衛門では、その錫を砂型に流し込み、\n              職人が手で削り、磨いて一つの器に仕上げます。\n              45年の経験が積み重なった、完全手作りの錫器です。'),
    # ギャラリークォート
    ('"I do not make vessels. I make the silence around a flower."',
     '"I do not sell tin. I sell the taste of a better drink."'),
    ('器を作るのではない。\n           花を包む、沈黙を作る。',
     '錫を売るのではない。\n           一杯を、美味しくする道具を作る。'),
    ('— 山田 誠一, 二代目', '— 小泉 仁, 京都錫右衛門'),
    # コレクション
    ('I</span>\n              Silence Series\n              <em>沈黙シリーズ</em>\n              Ceramic →',
     'I</span>\n              タンブラー\n              <em>Tin Tumbler</em>\n              Pure Tin →'),
    ('II</span>\n              Morning Light\n              <em>朝の光</em>\n              Stoneware →',
     'II</span>\n              ぐい呑み\n              <em>Sake Cup</em>\n              Handcrafted →'),
    ('III</span>\n              Wabi Form\n              <em>侘びの形</em>\n              Hand-built →',
     'III</span>\n              ペアセット\n              <em>Pair Set</em>\n              Gift Ready →'),
    ('IV</span>\n              Bespoke\n              <em>受注制作</em>\n              Custom →',
     'IV</span>\n              受注制作\n              <em>Custom Orders</em>\n              Bespoke →'),
    # 簡易
    ('Silence Series', 'タンブラー'),
    ('沈黙シリーズ', 'Tin Tumbler'),
    ('Morning Light', 'ぐい呑み'),
    ('朝の光', 'Sake Cup'),
    ('Wabi Form', 'ペアセット'),
    ('侘びの形', 'Pair Set'),
    ('Hand-built', 'Gift Ready'),
    # コンタクト
    ('Find your perfect vessel.', 'Find your perfect tin piece.'),
    ('作品のご購入、受注制作のご相談、\n              展示会・取材のお問い合わせはこちらから。',
     '作品のご購入、受注制作のご相談、\n              取材・卸のお問い合わせはこちらから。'),
    # フッター
    ('© 2025 Yamada Flower Vessel. Kyoto, Japan.', '© 2025 京都錫右衛門 SUZUEMON. Kyoto, Japan.'),
    ('Ma — 間', 'Suzu — 錫'),
]

# ─────────────────────────────────────────────
# 3. 森陶器 — yamada-pottery テンプレ
# ─────────────────────────────────────────────
mori_replacements = [
    # title / nav
    ('<title>山田陶芸</title>', '<title>森陶器 — Mori Pottery</title>'),
    ('山田陶芸', '森陶器'),
    # Hero
    ('Yamada Pottery — Kyoto, Japan', 'Mori Pottery — Naruto, Tokushima'),
    ('土から生まれる、\n              静かな器', '炎が育む、\n              大谷の土'),
    ('土から生まれる、 静かな器', '炎が育む、 大谷の土'),
    ('Born from earth. Made by hand. Meant to last.', 'Otani Ware. Born from fire. Built to endure.'),
    # ティッカー
    ('山田陶芸 ◦ Yamada Pottery ◦ 京都 ◦ Handmade Ceramics ◦ Since 1987',
     '森陶器 ◦ Mori Pottery ◦ 鳴門 ◦ 大谷焼 ◦ Otani Ware'),
    # Story heading
    ('手の記憶が、\n              かたちになる。\n              それが器です。',
     '炎が育てる、\n              大谷の土。\n              それが大谷焼です。'),
    ('手の記憶が、 かたちになる。 それが器です。', '炎が育てる、 大谷の土。 それが大谷焼です。'),
    # Story body
    ('京都の山あいで、山田太郎は土と向き合い続けています。\n              釉薬の偶然性、炎の揺らぎ、冷ます時間の長さ。\n              ひとつひとつの器に、繰り返しのない一瞬が宿っています。',
     '徳島県鳴門市大谷町に、森陶器窯元があります。\n              国登録有形文化財の窯で焼かれる大谷焼は、\n              薪の炎と地元の土だけが生み出せる温かみを持ちます。\n              轆轤体験・絵付け体験も受け付けており、\n              工房を訪れる人を器の世界へと誘います。'),
    # Studio label
    ('Yamada Studio, Kyoto', 'Mori Studio, Naruto'),
    # クォート
    ('"使うたびに手に馴染み、\n              時間が経つほど深みを増す。\n              それが、真の道具だと思っています。"',
     '"土と炎が生み出す偶然の色こそが、\n              大谷焼の魂です。\n              同じ器は、二度と生まれません。"'),
    ('— 山田 太郎', '— 森陶器 窯元'),
    # コレクション
    ('日常の器\n              Everyday Ceramics', '大谷焼 食器\n              Otani Tableware'),
    ('茶道具\n              Tea Ceremony Ware', '花器・壺\n              Vases &amp; Urns'),
    ('一点もの\n              One-of-a-kind Pieces', '轆轤体験\n              Pottery Experience'),
    ('受注制作\n              Custom Orders', '受注制作\n              Custom Orders'),
    # 簡易
    ('Everyday Ceramics', 'Otani Tableware'),
    ('Tea Ceremony Ware', 'Vases &amp; Urns'),
    ('One-of-a-kind Pieces', 'Pottery Experience'),
    # コンタクト
    ('器との\n              出会いを、\n              ここから。', '大谷焼との\n              出会いを、\n              ここから。'),
    ('ご購入のご相談、展示会のご案内、\n              受注制作のお問い合わせなど、\n              お気軽にご連絡ください。',
     'ご購入のご相談、体験のご予約、\n              受注制作のお問い合わせなど、\n              お気軽にご連絡ください。'),
    # フッター
    ('© 2025 Yamada Pottery. All rights reserved.', '© 2025 森陶器. All rights reserved.'),
]

# ─────────────────────────────────────────────
# 4. WAZAN — yamada-pottery テンプレ
# ─────────────────────────────────────────────
wazan_replacements = [
    ('<title>山田陶芸</title>', '<title>和山 WAZAN — 波佐見焼</title>'),
    ('山田陶芸', '和山'),
    ('Yamada Pottery — Kyoto, Japan', 'WAZAN — Hasami, Nagasaki'),
    ('土から生まれる、\n              静かな器', '現代の食卓に、\n              波佐見の美'),
    ('土から生まれる、 静かな器', '現代の食卓に、 波佐見の美'),
    ('Born from earth. Made by hand. Meant to last.', 'Hasami Ware. Modern design. Everyday beauty.'),
    ('山田陶芸 ◦ Yamada Pottery ◦ 京都 ◦ Handmade Ceramics ◦ Since 1987',
     '和山 ◦ WAZAN ◦ 波佐見 ◦ 波佐見焼 ◦ Hasami Ware'),
    ('手の記憶が、\n              かたちになる。\n              それが器です。',
     '日常の食卓を、\n              少しだけ豊かに。\n              それが波佐見焼です。'),
    ('手の記憶が、 かたちになる。 それが器です。', '日常の食卓を、 少しだけ豊かに。 それが波佐見焼です。'),
    ('京都の山あいで、山田太郎は土と向き合い続けています。\n              釉薬の偶然性、炎の揺らぎ、冷ます時間の長さ。\n              ひとつひとつの器に、繰り返しのない一瞬が宿っています。',
     '長崎県波佐見町に、和山の窯元があります。\n              400年の歴史を持つ波佐見焼の伝統を受け継ぎながら、\n              カフェやレストランのような食卓を家庭で実現するデザインを追求。\n              マットな質感、シンプルなフォルム、使いやすいサイズ感——\n              毎日使うからこそ、美しくあってほしいという思いが込められています。'),
    ('Yamada Studio, Kyoto', 'WAZAN Studio, Hasami'),
    ('"使うたびに手に馴染み、\n              時間が経つほど深みを増す。\n              それが、真の道具だと思っています。"',
     '"毎日使う器だからこそ、\n              飽きのこないデザインが大切です。\n              波佐見焼の伝統と現代の感覚を、一枚に込めています。"'),
    ('— 山田 太郎', '— 和山 デザインチーム'),
    ('日常の器\n              Everyday Ceramics', 'Modern Matte\n              モダンマット'),
    ('茶道具\n              Tea Ceremony Ware', 'En-Poire\n              アンポワール'),
    ('一点もの\n              One-of-a-kind Pieces', 'RONDE\n              ロンド'),
    ('受注制作\n              Custom Orders', 'Wabi Cup\n              わびカップ'),
    ('Everyday Ceramics', 'Modern Matte'),
    ('Tea Ceremony Ware', 'En-Poire'),
    ('One-of-a-kind Pieces', 'RONDE'),
    ('器との\n              出会いを、\n              ここから。', '波佐見焼との\n              出会いを、\n              ここから。'),
    ('ご購入のご相談、展示会のご案内、\n              受注制作のお問い合わせなど、\n              お気軽にご連絡ください。',
     'ご購入・卸のご相談、展示会のご案内、\n              コラボレーションのお問い合わせなど、\n              お気軽にご連絡ください。'),
    ('© 2025 Yamada Pottery. All rights reserved.', '© 2025 和山 WAZAN. All rights reserved.'),
]

# ─────────────────────────────────────────────
# 5. 京七宝ヒロミ・アート — senshoku テンプレ
# ─────────────────────────────────────────────
hiromi_replacements = [
    ('<title>山田染色工房 — Yamada Dye Studio</title>', '<title>京七宝ヒロミ・アート — Hiromi Art</title>'),
    ('山田染色工房 — Yamada Dye Studio', '京七宝ヒロミ・アート — Hiromi Art'),
    ('山田染色工房', '京七宝ヒロミ・アート'),
    ('Yamada Dye Studio — Kyoto, Since 1934', 'Hiromi Art — Higashiyama, Kyoto'),
    ('藍 と 紅 が、\n           布に宿る。', '炎と七色が、\n           金属に宿る。'),
    ('藍 と 紅 が、 布に宿る。', '炎と七色が、 金属に宿る。'),
    ('Where ancient pigments meet living cloth.', 'Where fire and glass fuse into eternal colour.'),
    ('天然の藍と紅花だけで染める、山田染色工房。\n              90年の歴史が積み重なった色は、\n              化学染料には出せない深みを持っています。',
     '京都・東山で七宝焼の技を受け継ぐ、ヒロミ・アート。\n              七宝とは、金属の上にガラス質の釉薬を焼き付ける工芸です。\n              千年以上の歴史が育んだ色の深みは、他の素材では出せません。'),
    ('天然の藍と紅花だけで染める、山田染色工房。', '京都・東山で七宝焼の技を受け継ぐ、ヒロミ・アート。'),
    ('90年の歴史が積み重なった色は、', '七宝とは、金属の上にガラス質の釉薬を焼き付ける工芸です。'),
    ('化学染料には出せない深みを持っています。', '千年以上の歴史が育んだ色の深みは、他の素材では出せません。'),
    ('藍染め作品', '七宝作品'),
    ('紅染め作品', '体験教室'),
    ('土から生まれた色が、\n           千年後も残る。', '炎が宿した色は、\n           千年後も残る。'),
    ('土から生まれた色が、 千年後も残る。', '炎が宿した色は、 千年後も残る。'),
    ('京都・西陣の路地奥に、山田染色工房があります。\n              初代・山田清次郎が1934年に開いたこの工房では、\n              今も化学染料を一切使いません。\n              藍は阿波から。紅花は山形から。\n              季節と天候によって、色は毎年微妙に違います。\n              それが、山田の布に宿る「生きた色」の正体です。',
     '京都・東山のギャラリーショップで、ヒロミ・アートは七宝を作り続けています。\n              七宝焼とは、銅や銀の台地にガラス質の釉薬を重ね、炉で焼き固める工芸。\n              1970年から続くこの工房では、制作・販売・体験教室をすべて行っています。\n              外国人観光客にも人気の七宝体験は、英語でも受け付けています。\n              作品はCreema・東山店で購入可能。免税対応（Tax Free）もあります。'),
    ('How We Dye', 'How We Create'),
    ('素材選び', '台地づくり'),
    ('絹・麻・木綿。\n                染まりやすさと\n                色の出方は\n                素材で全て変わる。',
     '銅・銀などの金属板を\n                切り抜き、成形する。\n                土台の精度が\n                仕上がりを左右する。'),
    ('灰汁引き', '釉薬置き'),
    ('染料を定着させる\n                ための下処理。\n                ここを丁寧にすると\n                色が長持ちする。',
     '色ガラスの粉末釉薬を\n                細いヘラで台地に置く。\n                繊細な作業が\n                美しい配色を生む。'),
    ('染め', '焼成'),
    ('Dyeing', 'Firing'),
    ('藍は発酵桶で。\n                紅は煮汁で。\n                温度と時間が、\n                色の深さを決める。',
     '800〜900℃の炉で\n                ガラス質を焼き固める。\n                温度と時間が\n                色の発色を決める。'),
    ('水洗い', '仕上げ磨き'),
    ('Washing', 'Polishing'),
    ('京都の伏流水で\n                丁寧に洗う。\n                色が落ち着き、\n                本来の表情が出る。',
     '表面を丁寧に磨き上げ、\n                ガラスの透明感を引き出す。\n                光を当てると宝石のように\n                輝く表情が現れる。'),
    ('乾燥・張り・検品。\n                一反ずつ手で確認し、\n                問題がなければ\n                初めて完成となる。',
     '彫金・エナメル・金線など\n                細部を調整し完成。\n                一点一点手で確認し、\n                問題がなければ完成となる。'),
    ('「色は、自然からの\n                借り物です。\n                職人の仕事は、\n                その色を布に\n                お返しすること。」',
     '「七宝の色は、\n                炎との対話です。\n                同じ釉薬でも、\n                焼くたびに\n                違う表情が生まれます。」'),
    ('— 山田 三郎, 三代目', '— 京七宝ヒロミ・アート'),
    ('「色は、自然からの 借り物です。 職人の仕事は、 その色を布に お返しすること。」', '「七宝の色は、炎との対話です。同じ釉薬でも、焼くたびに違う表情が生まれます。」'),
    ('01</span>\n              藍染めストール\n              <em>Indigo Stole</em>', '01</span>\n              アクセサリー\n              <em>Cloisonné Jewelry</em>'),
    ('02</span>\n              絞り染め反物\n              <em>Shibori Cloth</em>', '02</span>\n              置物・額\n              <em>Art Pieces</em>'),
    ('03</span>\n              天然顔料\n              <em>Natural Pigments</em>', '03</span>\n              体験教室\n              <em>Workshop</em>'),
    ('04</span>\n              掛け作品\n              <em>Hanging Works</em>', '04</span>\n              素材・材料\n              <em>Enamel Materials</em>'),
    ('05</span>\n              型染め布\n              <em>Stencil Dyed</em>', '05</span>\n              特注品\n              <em>Custom Orders</em>'),
    ('藍染めストール', 'アクセサリー'),
    ('Indigo Stole', 'Cloisonné Jewelry'),
    ('絞り染め反物', '置物・額'),
    ('Shibori Cloth', 'Art Pieces'),
    ('天然顔料', '体験教室'),
    ('Natural Pigments', 'Workshop'),
    ('掛け作品', '素材・材料'),
    ('Hanging Works', 'Enamel Materials'),
    ('型染め布', '特注品'),
    ('Stencil Dyed', 'Custom Orders'),
    ('藍 と 紅 の布を、\n             あなたのもとへ。', '京七宝の輝きを、\n             あなたのもとへ。'),
    ('作品のご購入、受注染めのご依頼、\n              工房見学のご予約など、\n              お気軽にお問い合わせください。',
     '作品のご購入、体験教室のご予約、\n              受注制作のご依頼など、\n              お気軽にお問い合わせください。'),
    ('We also accept international orders. English inquiries are welcome.',
     'Tax Free available. English inquiries are welcome.'),
    ('© 2025 Yamada Dye Studio. Kyoto, Japan.', '© 2025 京七宝ヒロミ・アート. Higashiyama, Kyoto.'),
]

# ─────────────────────────────────────────────
# 生成実行
# ─────────────────────────────────────────────
jobs = [
    ('showen',   'senshoku',       showen_replacements,    '昇苑くみひも'),
    ('suzuemon', 'modern-wa',      suzuemon_replacements,  'SUZUEMON'),
    ('mori',     'yamada-pottery', mori_replacements,      '森陶器'),
    ('wazan',    'yamada-pottery', wazan_replacements,     'WAZAN'),
    ('hiromi',   'senshoku',       hiromi_replacements,    '京七宝ヒロミ・アート'),
]

for slug, template_key, replacements, label in jobs:
    template_path = TEMPLATES[template_key]
    output_path   = os.path.join(OUTPUT_DIR, f'{slug}-demo.html')

    print(f'[{label}] 読み込み中... ({template_key})', end='', flush=True)
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f' 置換中({len(replacements)}件)...', end='', flush=True)
    content = replace_all(content, replacements)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    size_kb = os.path.getsize(output_path) / 1024
    print(f' 完了 → {slug}-demo.html ({size_kb:.0f}KB)')

print('\n✅ 全5件 生成完了')
print(f'出力先: {OUTPUT_DIR}')
