"""3D 렌더 후처리: python3 post3d.py → assets/*-3d.png

- cctv: CCTV 화면처럼 보이게(채도·노이즈·비네팅) + 화면 표시(OSD) + 낙하물 검출 박스
- sim / cctv / droptest: 슬라이드 카드용으로 모서리를 둥글게
- drone: 배경 투명 그대로 복사, cover: 전면 배경용 그대로
- solution / fall: 렌더 때 저장한 화면 좌표(json)도 함께 복사 → 덱의 배지·시간 라벨 위치
"""
import json
import pathlib
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

D = pathlib.Path(__file__).parent
R, A = D / "renders", D / "assets"
MONO = "/System/Library/Fonts/Menlo.ttc"
SANS = str(pathlib.Path.home() / "Library/Fonts/Pretendard-Bold.ttf")
ORANGE = (255, 90, 31)


def rounded(im, radius=30):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], radius, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def dashed_rect(d, box, color, width=4, dash=14, gap=9):
    x0, y0, x1, y1 = box
    for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        length = max(abs(bx - ax), abs(by - ay))
        steps = int(length // (dash + gap)) + 1
        for i in range(steps):
            t0, t1 = i * (dash + gap) / length, min(1, (i * (dash + gap) + dash) / length)
            d.line([(ax + (bx - ax) * t0, ay + (by - ay) * t0), (ax + (bx - ax) * t1, ay + (by - ay) * t1)], fill=color, width=width)


def cctv():
    im = Image.open(R / "cctv.png").convert("RGB")
    w, h = im.size
    im = ImageEnhance.Color(im).enhance(0.82)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    # 센서 노이즈
    random.seed(3)
    noise = Image.effect_noise((w, h), 18).convert("RGB")
    im = Image.blend(im, noise, 0.06)
    # 비네팅
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-w * 0.25, -h * 0.3, w * 1.25, h * 1.3], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(160))
    im = Image.composite(im, Image.new("RGB", (w, h), (12, 14, 16)), vig)

    d = ImageDraw.Draw(im)
    mono = ImageFont.truetype(MONO, 30)
    sans = ImageFont.truetype(SANS, 26)
    d.text((44, 36), "CAM-03  NORTH FACADE  12F-8F", font=mono, fill=(240, 242, 244), stroke_width=2, stroke_fill=(20, 22, 24))
    d.text((w - 44, 36), "2026-10-29  14:02:11.433", font=mono, fill=(240, 242, 244), anchor="ra", stroke_width=2, stroke_fill=(20, 22, 24))
    d.ellipse([44, h - 74, 64, h - 54], fill=(230, 40, 40))
    d.text((76, h - 80), "REC   60 FPS", font=mono, fill=(240, 242, 244), stroke_width=2, stroke_fill=(20, 22, 24))
    # 낙하물 검출 박스 (렌더할 때 저장한 화면 좌표)
    b = json.loads((R / "cctv.json").read_text())["bbox"]
    pad = 22
    box = (b[0] * w - pad, b[1] * h - pad, b[2] * w + pad, b[3] * h + pad)
    dashed_rect(d, box, ORANGE)
    label = "낙하물  0.97"
    tw = d.textlength(label, font=sans)
    d.rectangle([box[0], box[1] - 44, box[0] + tw + 24, box[1] - 4], fill=ORANGE)
    d.text((box[0] + 12, box[1] - 40), label, font=sans, fill=(255, 255, 255))
    rounded(im).save(A / "cctv-3d.png")


def feather(im, margin=0.1):
    """투명 배경 렌더의 그림자가 이미지 가장자리에서 뚝 끊기지 않게 알파를 가장자리로 갈수록 줄인다."""
    im = im.convert("RGBA")
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rectangle([w * margin, h * margin, w * (1 - margin), h * (1 - margin)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * margin * 0.6))
    r, g, b, alpha = im.split()
    im.putalpha(Image.composite(alpha, Image.new("L", (w, h), 0), mask))
    return im


def card(name, out):
    rounded(Image.open(R / f"{name}.png").convert("RGB")).save(A / out)


if __name__ == "__main__":
    cctv()
    card("sim", "sim-3d.png")
    card("droptest", "drop-3d.png")
    feather(Image.open(R / "drone.png")).save(A / "drone-3d.png")
    Image.open(R / "cover.png").convert("RGB").save(A / "cover-3d.png")
    feather(Image.open(R / "kit.png")).save(A / "kit-3d.png")
    for name in ("solution", "zone", "fall"):
        card(name, f"{name}-3d.png")
    for name in ("solution", "fall"):   # 배지·라벨 위치(이미지 대비 비율 좌표)
        (A / f"{name}-3d.json").write_text((R / f"{name}.json").read_text())
    print("wrote assets/*-3d.png")
