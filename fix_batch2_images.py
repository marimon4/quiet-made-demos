#!/usr/bin/env python3
"""base64埋め込み画像を外部URLに差し替える"""
import re, os

BASE = '/Users/marika/Desktop/quietmade/'

# 各工房の商品画像URL（5枚）
PRODUCT_IMAGES = {
    'shinkukan-demo.html': [
        'https://img14.shop-pro.jp/PA01080/748/product/85609078_th.jpg',
        'https://img14.shop-pro.jp/PA01080/748/product/15975615_th.jpg',
        'https://img14.shop-pro.jp/PA01080/748/product/15975622_th.jpg',
        'https://img14.shop-pro.jp/PA01080/748/product/15699475_th.jpg',
        'https://img14.shop-pro.jp/PA01080/748/product/85609078_th.jpg',
    ],
    'rampuya-demo.html': [
        'https://rampuya.com/wp-content/uploads/2017/04/top-img.jpg',
        'https://rampuya.com/wp-content/uploads/2017/03/jinbe-samue-300x300.jpg',
        'https://rampuya.com/wp-content/uploads/2017/03/shirt-tops-2-300x300.jpg',
        'https://rampuya.com/wp-content/uploads/2017/03/noren-300x300.jpg',
        'https://rampuya.com/wp-content/uploads/2022/11/IZM_8736-1-300x300.jpg',
    ],
    'futaai-demo.html': [
        'https://cdn.goope.jp/184721/230306151803rbkb_l.png',
        'https://cdn.goope.jp/184721/211202150533q56c_l.jpg',
        'https://cdn.goope.jp/184721/211213140239jdv9_l.jpg',
        'https://cdn.goope.jp/184721/211213140255dhkh_l.jpg',
        'https://cdn.goope.jp/184721/211213140308jyhh_l.jpg',
    ],
    'yano-demo.html': [
        'https://cdn.goope.jp/184721/230306151803rbkb_l.png',  # placeholder
        'https://cdn.goope.jp/184721/211202150533q56c_l.jpg',
        'https://cdn.goope.jp/184721/211213140239jdv9_l.jpg',
        'https://cdn.goope.jp/184721/211213140255dhkh_l.jpg',
        'https://cdn.goope.jp/184721/211213140308jyhh_l.jpg',
    ],
}

# ヒーロー背景URL（showen/tsujiwaベース用）
HERO_IMAGES = {
    'shinkukan-demo.html': 'https://img14.shop-pro.jp/PA01080/748/product/85609078_th.jpg',
    'rampuya-demo.html': 'https://rampuya.com/wp-content/uploads/2017/04/top-img2.jpg',
    'futaai-demo.html': 'https://cdn.goope.jp/184721/230306151803rbkb_l.png',
    'yano-demo.html':   'https://cdn.goope.jp/184721/211202150533q56c_l.jpg',
}

for filename, img_urls in PRODUCT_IMAGES.items():
    path = BASE + filename
    with open(path, 'r') as f:
        c = f.read()

    # ── 商品グリッドのbase64 imgを外部URLに差し替え ──
    # col-itemのimgタグのbase64srcを順番に置換
    count = 0
    def replace_colitem_img(m):
        global count
        if count < len(img_urls):
            url = img_urls[count]
            count += 1
            return f'<img src="{url}"'
        return m.group(0)

    # col-item内のimgタグを特定して置換
    def replace_imgs(content, urls):
        result = []
        idx = 0
        img_count = 0
        pattern = re.compile(r'(<div class="col-item[^"]*"[^>]*>[\s\S]*?)<img src="data:image[^"]*"', re.DOTALL)
        last = 0
        for m in pattern.finditer(content):
            result.append(content[last:m.start()])
            if img_count < len(urls):
                result.append(m.group(1) + f'<img src="{urls[img_count]}"')
                img_count += 1
            else:
                result.append(m.group(0))
            last = m.end()
        result.append(content[last:])
        return ''.join(result)

    c = replace_imgs(c, img_urls)

    # ── tsujiwaベースのファイルは辻和金網の画像も残ってるので差し替え ──
    if filename in ('futaai-demo.html', 'yano-demo.html'):
        makeshop_imgs = re.findall(r'https://gigaplus\.makeshop\.jp/tujiwa/images/item/[^\s"\']+', c)
        for i, old_url in enumerate(makeshop_imgs):
            if i < len(img_urls):
                c = c.replace(old_url, img_urls[i], 1)

        # ヒーロー背景（HERO01.jpgなど）を削除してCSSのみに
        hero_url = HERO_IMAGES.get(filename, '')
        if hero_url:
            # tsujiwa heroのbackground-image URLを差し替え
            c = c.replace(
                "background-image: url('HERO01.jpg'), url('HERO02jpg.jpg'), url('HeRO03.jpg')",
                f"background-image: url('{hero_url}')"
            )
            # story.jpgも差し替え
            c = c.replace('src="story.jpg"', f'src="{img_urls[1] if len(img_urls)>1 else img_urls[0]}"')

    with open(path, 'w') as f:
        f.write(c)
    print(f'✅ {filename} 画像差し替え完了')

print('\n🎉 全ファイル修正完了')
