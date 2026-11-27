"""把豆包生成的猫咪图处理成带透明背景的界面素材（一次性构建脚本）。

需要 Pillow（仅构建时用）：
    py -m pip install pillow
    py tools/prepare_cats.py

源图来自 Downloads 里的「豆包 (1/2/3).png」，处理步骤：
    1. 从四边泛洪，抠掉接近纯白的背景（猫身内部白色由描边隔着，不会被误抠）；
    2. 抹掉右下角「豆包 AI 生成」水印；
    3. 按内容裁边，缩放到界面基准显示尺寸的 3 倍（运行时按 DPI subsample）。

输出：assets/cat_focus.png（正面坐）、cat_wait.png（抬头看）、cat_rest.png（趴着）。
"""

import os
from collections import deque

from PIL import Image, ImageDraw  # noqa: E402

SRC_DIR = os.path.expanduser(r"~\Downloads")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# 源文件 -> (输出名, 最大高度, 最大宽度)，均为基准显示尺寸的 3 倍，
# 运行时按实际 DPI 用 subsample 取整缩放（避免高缩放下裁切）
JOBS = [
    ("豆包 (1).png", "cat_focus.png", 360, 330),
    ("豆包 (2).png", "cat_rest.png", 300, 480),
    ("豆包 (3).png", "cat_wait.png", 375, 345),
]

TOL = 34  # 与纯白的最大通道差，超过即视为猫的笔画


def cut_background(im):
    rgb = im.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    bg = bytearray(w * h)
    queue = deque()

    def near_white(c):
        return max(255 - c[0], 255 - c[1], 255 - c[2]) <= TOL

    def seed(x, y):
        i = y * w + x
        if not bg[i] and near_white(px[x, y]):
            bg[i] = 1
            queue.append(i)

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)

    while queue:
        i = queue.popleft()
        y, x = divmod(i, w)
        if x > 0:
            seed(x - 1, y)
        if x < w - 1:
            seed(x + 1, y)
        if y > 0:
            seed(x, y - 1)
        if y < h - 1:
            seed(x, y + 1)

    alpha = Image.frombytes("L", (w, h), bytes(0 if b else 255 for b in bg))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def prepare(src_name, out_name, max_h, max_w):
    im = Image.open(os.path.join(SRC_DIR, src_name))
    out = cut_background(im)
    w, h = out.size

    # 右下角水印
    ImageDraw.Draw(out).rectangle((1240, 1430, w, h), fill=(0, 0, 0, 0))

    box = out.getbbox()
    out = out.crop(box)
    w, h = out.size
    scale = min(max_h / h, max_w / w)
    out = out.resize((round(w * scale), round(h * scale)), Image.LANCZOS)

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, out_name)
    out.save(path)
    print(out_name, out.size, "<-", src_name, box)


def main():
    for job in JOBS:
        prepare(*job)


if __name__ == "__main__":
    main()
