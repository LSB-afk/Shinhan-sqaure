"""DropZero 도면 생성기: python3 docs/diagrams/build.py → 같은 폴더에 논문 스타일 그림 5장(SVG + PNG).

Fig. 1·3·4·5는 SVG를 직접 그려 Chrome으로 PNG 렌더링, Fig. 2는 matplotlib.
문구·좌표를 바꾸려면 이 파일만 고치고 다시 실행한다.
"""
import math
import pathlib
import re
import subprocess
from html import escape

OUT = pathlib.Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SERIF = "'Times New Roman', AppleMyungjo, serif"
K, GRAY = "#222222", "#555555"
MK = {"k": K, "v": "#D55E00", "b": "#0072B2"}  # 검정 · 주홍 · 파랑 (Okabe–Ito 색약 안전 팔레트)
PAL = {  # fill, stroke — CV 논문(FADE-Net 등)의 저채도 파스텔 모듈 색
    "pink": ("#F6E1EE", "#B07AA1"), "green": ("#D7EDD2", "#5E9E52"), "blue": ("#E0EAF6", "#6A8DB5"),
    "peach": ("#FBE7D8", "#C98B5E"), "lav": ("#E6E5F5", "#7D7AB8"), "gray": ("#EDEDED", "#8C8C8C"),
    "yellow": ("#FFF5D1", "#B8962E"), "white": ("#FFFFFF", "#333333"), "alert": ("#FBE3D6", "#C0602B"),
}
KDEFS = ("<defs>" + "".join(
    f'<marker id="kh-{k}" viewBox="0 0 10 10" refX="9.5" refY="5" markerUnits="userSpaceOnUse" markerWidth="8" '
    f'markerHeight="8" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="{c}"/></marker>' for k, c in MK.items())
    + '<pattern id="hatch-v" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)">'
      f'<line x1="0" y1="0" x2="0" y2="6" stroke="{MK["v"]}" stroke-width="1.2"/></pattern></defs>')
_TOK = re.compile(r"(\$[^$]+\$|_\{[^}]*\}|\^\{[^}]*\}|\*\*[^*]+\*\*)")


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{SERIF}"><rect width="{w}" height="{h}" fill="#FFFFFF"/>{KDEFS}' + "".join(body) + "</svg>")


def rich(x, y, s, size=14, anchor="middle", weight=400, fill=K, italic=False):
    """$x$ 이탤릭, _{..} 아래첨자, ^{..} 위첨자, **..** 굵게."""
    spans = []
    for p in _TOK.split(s):
        if not p:
            continue
        if p[0] == "$":
            spans.append(f'<tspan font-style="italic">{escape(p[1:-1])}</tspan>')
        elif p[:2] in ("_{", "^{"):
            inner, shift = p[2:-1], "sub" if p[0] == "_" else "super"
            it = ' font-style="italic"' if re.search("[A-Za-z]", inner) else ""
            spans.append(f'<tspan baseline-shift="{shift}" font-size="{size * .7:.1f}"{it}>{escape(inner)}</tspan>')
        elif p[:2] == "**":
            spans.append(f'<tspan font-weight="700">{escape(p[2:-2])}</tspan>')
        else:
            spans.append(escape(p))
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{st}>{"".join(spans)}</text>')


def mod(x, y, w, h, lines, pal="blue", size=14, dashed=False):
    fill, stroke = PAL[pal]
    dash = ' stroke-dasharray="5 3"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1.2"{dash}/>']
    lh = size * 1.4
    y0 = y + h / 2 - (len(lines) - 1) * lh / 2 + size * .35
    for i, s in enumerate(lines):
        out.append(rich(x + w / 2, y0 + i * lh, s, size if i == 0 else size - 1.5, weight=700 if i == 0 else 400))
    return "".join(out)


def karrow(pts, dashed=False, c="k", both=False, width=1.3):
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    start = f' marker-start="url(#kh-{c})"' if both else ""
    p = " ".join(f"{x},{y}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{MK[c]}" stroke-width="{width}"{dash} '
            f'stroke-linejoin="round" marker-end="url(#kh-{c})"{start}/>')


def group(x, y, w, h, title):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="#777" stroke-width="1.2" stroke-dasharray="6 4"/>'
            + rich(x + 12, y + 24, title, 15.5, "start", 700))


def cuboid(x, y, w, h, d):
    s = 'stroke="#8A6D1F" stroke-width="1"'
    return (f'<polygon points="{x},{y} {x + d},{y - d} {x + w + d},{y - d} {x + w},{y}" fill="#F8E3A6" {s}/>'
            f'<polygon points="{x + w},{y} {x + w + d},{y - d} {x + w + d},{y + h - d} {x + w},{y + h}" fill="#D8B04A" {s}/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F2CF6B" {s}/>')


def frame(x, y, w=104, h=92, sk=10, dot=False):
    out = [f'<polygon points="{x},{y + sk} {x + w},{y} {x + w},{y + h} {x},{y + h + sk}" fill="#DDE2E8" stroke="#555" stroke-width="1"/>']
    for i in range(1, 5):  # 건물 외벽 격자
        fx, top = x + w * i / 5, y + sk * (1 - i / 5)
        out.append(f'<line x1="{fx:.1f}" y1="{top:.1f}" x2="{fx:.1f}" y2="{top + h:.1f}" stroke="#A9B2BE" stroke-width=".8"/>')
    for j in range(1, 6):
        fy = h * j / 6
        out.append(f'<line x1="{x}" y1="{y + sk + fy:.1f}" x2="{x + w}" y2="{y + fy:.1f}" stroke="#A9B2BE" stroke-width=".8"/>')
    if dot:
        for i in range(4):
            out.append(f'<circle cx="{x + 72 + 3 * i}" cy="{y + 18 + 7 * i * i}" r="{1.6 if i < 3 else 2.8}" '
                       f'fill="{"#D55E00" if i == 3 else "none"}" stroke="#D55E00" stroke-width="1"/>')
    return "".join(out)


def person(x, y):
    """작업자 막대 그림. y = 발 위치."""
    s = f'stroke="{K}" stroke-width="1.4" stroke-linecap="round"'
    return (f'<line x1="{x}" y1="{y - 10}" x2="{x - 4}" y2="{y}" {s}/><line x1="{x}" y1="{y - 10}" x2="{x + 4}" y2="{y}" {s}/>'
            f'<line x1="{x}" y1="{y - 10}" x2="{x}" y2="{y - 21}" {s}/><line x1="{x - 6}" y1="{y - 17}" x2="{x + 6}" y2="{y - 17}" {s}/>'
            f'<circle cx="{x}" cy="{y - 25.5}" r="4.5" fill="#FFFFFF" {s}/>')


def camera(x, y, facing=-1):
    """카메라 기호. facing=-1 왼쪽, 1 오른쪽, 0 아래."""
    if facing == 0:
        return f'<rect x="{x - 6}" y="{y - 4}" width="12" height="9" fill="{MK["b"]}"/><polygon points="{x - 4},{y + 5} {x + 4},{y + 5} {x},{y + 10}" fill="{MK["b"]}"/>'
    bx = x if facing < 0 else x - 20
    tip = x - 6 if facing < 0 else x + 6
    return (f'<rect x="{bx}" y="{y - 6}" width="20" height="12" fill="{MK["b"]}"/>'
            f'<polygon points="{x},{y - 4} {x},{y + 4} {tip},{y}" fill="{MK["b"]}"/>')


def siren(x, y):
    v = MK["v"]
    rays = "".join(f'<line x1="{x + 9 * math.cos(math.radians(a)):.1f}" y1="{y + 9 * math.sin(math.radians(a)):.1f}" '
                   f'x2="{x + 14 * math.cos(math.radians(a)):.1f}" y2="{y + 14 * math.sin(math.radians(a)):.1f}" stroke="{v}" stroke-width="1.2"/>'
                   for a in (-150, -90, -30))
    return f'<path d="M{x - 6},{y + 4} A6,6 0 0 1 {x + 6},{y + 4} Z" fill="{v}"/>' + rays


def dim(x1, y1, x2, y2, label, lx, ly, rot=0, c="k"):
    """양방향 치수선 + 라벨."""
    tr = f' transform="rotate({rot} {lx} {ly})"' if rot else ""
    return karrow([(x1, y1), (x2, y2)], c=c, both=True, width=1) + rich(lx, ly, label, 13).replace("<text ", f"<text{tr} ", 1)


# ---------------------------------------------------------------- Fig. 3 — 장비 배치 개념도 (측면도)
def site_figure():
    W, H, G = 1500, 830, 680  # G = 지면 y, 축척 15 px/m
    b = []
    # 지면 (토질 해칭)
    b.append(f'<line x1="40" y1="{G}" x2="1165" y2="{G}" stroke="{K}" stroke-width="1.6"/>')
    for x in range(52, 1165, 14):
        b.append(f'<line x1="{x}" y1="{G}" x2="{x - 10}" y2="{G + 11}" stroke="{GRAY}" stroke-width=".8"/>')

    # 건물: 10개 층(층고 3 m), 최상부 골조 공사 중
    b.append(f'<rect x="150" y="230" width="270" height="{G - 230}" fill="#F4F4F4"/>')
    for x in (150, 240, 330, 420):
        b.append(f'<line x1="{x}" y1="230" x2="{x}" y2="{G}" stroke="{K}" stroke-width="1.3"/>')
        b.append(f'<line x1="{x}" y1="190" x2="{x}" y2="230" stroke="#777" stroke-width="1" stroke-dasharray="4 3"/>')
    for k in range(1, 11):
        b.append(f'<line x1="142" y1="{G - 45 * k}" x2="428" y2="{G - 45 * k}" stroke="{K}" stroke-width="2.2"/>')
    b.append(f'<line x1="142" y1="214" x2="428" y2="214" stroke="{GRAY}" stroke-width="1"/>')
    for y in (545, 365):  # 낙하물방지망
        b.append(f'<line x1="150" y1="{y}" x2="108" y2="{y - 17}" stroke="{GRAY}" stroke-width="1.6"/>')
    b += [rich(116, 570, "낙하물", 12), rich(116, 585, "방지망", 12)]
    b.append(f'<line x1="74" y1="230" x2="140" y2="230" stroke="#999" stroke-width=".8"/><line x1="74" y1="{G}" x2="140" y2="{G}" stroke="#999" stroke-width=".8"/>')
    b.append(dim(82, 232, 82, G - 2, "$H$ = 30 m", 74, 455, rot=-90))
    b.append(person(398, 230))

    # 자유낙하 궤적: y = 15 px/m × ½gt², 0.5 s 간격 표시
    pos = lambda tt: (424 + 10 * tt, 226 + 0.5 * 9.81 * tt * tt * 15)
    pts = [pos(i / 50 * 2.47) for i in range(51)]
    b.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
             + f'" fill="none" stroke="{MK["v"]}" stroke-width="1.4" stroke-dasharray="5 3"/>')
    for tt in (0, .5, 1, 1.5, 2, 2.47):
        x, y = pos(tt)
        y = min(y, G)
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{MK["v"] if tt == 2.47 else "#FFFFFF"}" stroke="{MK["v"]}" stroke-width="1.3"/>')
        if tt in (1, 1.5, 2):
            b.append(rich(x + 9, y + 4, f"{tt:.1f} s", 12, "start", fill="#A04000"))
    b += [rich(476, 338, "자유낙하 궤적", 13, "start", fill="#A04000", italic=True),
          rich(476, 355, "(Δ$t$ = 0.5 s 간격, 착지 2.47 s)", 12, "start", fill="#A04000")]
    b.append(dim(449, 664, 495, 664, "", 0, 0, c="v") + rich(472, 656, "$r$_{b}", 13, fill="#A04000"))
    b.append(person(530, G))

    # 경광등(건물 측), 현장사무실·엣지 박스
    b.append(f'<line x1="575" y1="595" x2="575" y2="{G}" stroke="{GRAY}" stroke-width="1.6"/>' + siren(575, 592) + rich(590, 592, "S", 13, "start", 700))
    b.append(f'<rect x="610" y="636" width="120" height="44" fill="#EEEEEE" stroke="{K}" stroke-width="1.2"/>')
    b.append(f'<line x1="720" y1="636" x2="720" y2="618" stroke="{K}" stroke-width="1.2"/><circle cx="720" cy="616" r="2.2" fill="{K}"/>')
    b += [rich(670, 655, "**E**", 13), rich(670, 672, "엣지 AI 박스", 12)]

    # 타워크레인 (선화)
    for x in (760, 780):
        b.append(f'<line x1="{x}" y1="152" x2="{x}" y2="{G}" stroke="{K}" stroke-width="1.3"/>')
    b.append('<polyline points="' + " ".join(f"{760 if i % 2 else 780},{152 + 20 * i}" for i in range(27))
             + f'" fill="none" stroke="{GRAY}" stroke-width=".8"/>')
    b.append(f'<rect x="750" y="{G - 4}" width="40" height="8" fill="{GRAY}"/>')
    for y in (140, 152):
        b.append(f'<line x1="640" y1="{y}" x2="1150" y2="{y}" stroke="{K}" stroke-width="1.3"/>')
    b.append('<polyline points="' + " ".join(f"{640 + 12 * i},{152 if i % 2 else 140}" for i in range(43))
             + f'" fill="none" stroke="{GRAY}" stroke-width=".8"/>')
    b.append(f'<polygon points="760,140 770,100 780,140" fill="none" stroke="{K}" stroke-width="1.3"/>')
    b.append(f'<line x1="770" y1="100" x2="1150" y2="140" stroke="#888" stroke-width=".8"/><line x1="770" y1="100" x2="640" y2="140" stroke="#888" stroke-width=".8"/>')
    b.append(f'<rect x="645" y="152" width="34" height="22" fill="#CCCCCC" stroke="{GRAY}"/>')
    b.append(f'<rect x="782" y="152" width="22" height="18" fill="#FFFFFF" stroke="{K}"/>')
    b.append(f'<line x1="770" y1="100" x2="770" y2="88" stroke="{K}"/><circle cx="764" cy="86" r="3" fill="none" stroke="{K}"/><circle cx="776" cy="86" r="3" fill="none" stroke="{K}"/>')
    b.append(rich(786, 90, "**A** 풍속계", 13, "start"))
    b.append(f'<rect x="990" y="152" width="20" height="6" fill="{GRAY}"/><line x1="1000" y1="158" x2="1000" y2="392" stroke="{K}"/>')
    b.append(f'<line x1="1000" y1="392" x2="966" y2="404" stroke="{K}"/><line x1="1000" y1="392" x2="1034" y2="404" stroke="{K}"/>')
    b.append(f'<rect x="962" y="404" width="76" height="20" fill="#DDDDDD" stroke="{K}" stroke-width="1.2"/>')
    b.append(camera(1000, 164, 0))
    b.append(f'<polyline points="972,404 1000,174 1028,404" fill="none" stroke="{MK["b"]}" stroke-width="1" stroke-dasharray="4 3"/>')
    b.append(rich(1012, 178, "**C2** 후크 카메라", 13, "start"))

    # 인양물 동적 위험구역 Z_t
    b.append(f'<line x1="962" y1="424" x2="928" y2="{G}" stroke="{MK["v"]}" stroke-width="1.1" stroke-dasharray="5 3"/>')
    b.append(f'<line x1="1038" y1="424" x2="1072" y2="{G}" stroke="{MK["v"]}" stroke-width="1.1" stroke-dasharray="5 3"/>')
    b.append(f'<rect x="928" y="{G - 9}" width="144" height="9" fill="url(#hatch-v)" stroke="{MK["v"]}" stroke-width="1"/>')
    b.append(dim(1038, 652, 1072, 652, "", 0, 0, c="v") + rich(1055, 645, "$r$_{s}", 13, fill="#A04000"))
    b.append(f'<line x1="1038" y1="424" x2="1038" y2="{G}" stroke="#AAA" stroke-width=".8" stroke-dasharray="2 3"/>')
    b.append(person(985, G - 9))
    b += [rich(1000, 708, "$Z$_{t} : 동적 위험구역 (투영 + $r$_{s})", 13, fill="#A04000"),
          rich(985, 626, "$W$_{t} ∈ $Z$_{t} → 경보", 12.5, fill="#A04000")]

    # 카메라 C1 (마스트), C3 (지상 폴) + 시야
    b.append(camera(758, 330, -1))
    b.append(f'<polyline points="424,178 752,330 424,474" fill="none" stroke="{MK["b"]}" stroke-width="1" stroke-dasharray="4 3"/>')
    b.append(rich(790, 334, "**C1** 상층부 카메라 (60 fps)", 13, "start"))
    b.append(f'<line x1="1140" y1="500" x2="1140" y2="{G}" stroke="{GRAY}" stroke-width="1.6"/>')
    b.append(camera(1120, 500, -1).replace(f'x="1120"', 'x="1120"'))
    b.append(f'<polyline points="928,{G - 10} 1114,500 1096,{G - 10}" fill="none" stroke="{MK["b"]}" stroke-width="1" stroke-dasharray="4 3"/>')
    b.append(rich(1130, 486, "**C3** 지상 CCTV", 13))
    b.append(siren(1152, 548) + rich(1152, 572, "S", 13, weight=700))

    # 점검 드론 D + 순찰 경로
    b.append(f'<ellipse cx="285" cy="176" rx="182" ry="22" fill="none" stroke="{GRAY}" stroke-width="1" stroke-dasharray="6 4"/>')
    b.append(f'<line x1="288" y1="116" x2="312" y2="116" stroke="{K}" stroke-width="1.4"/><rect x="295" y="112" width="10" height="8" fill="{K}"/>')
    for dx in (-12, 12):
        b.append(f'<ellipse cx="{300 + dx}" cy="110" rx="8" ry="2.2" fill="none" stroke="{K}"/><line x1="{300 + dx}" y1="110" x2="{300 + dx}" y2="116" stroke="{K}"/>')
    b.append(rich(324, 120, "**D** 점검 드론 (작업 전·후 정기 순찰)", 13, "start"))

    # 범례
    b.append('<rect x="1190" y="80" width="280" height="610" fill="none" stroke="#999" stroke-width="1"/>')
    b.append(rich(1206, 106, "기호", 15, "start", 700))
    items = [("C1", "상층부 카메라 (60 fps, 낙하 감지)"), ("C2", "크레인 후크 카메라"), ("C3", "지상 CCTV (기존 설비 활용)"),
             ("D", "점검 드론 (비실시간)"), ("E", "엣지 AI 박스 (판단 · 경보)"), ("S", "경광등 · 다국어 스피커"),
             ("A", "풍속계 (강풍 시 인양 중지)"), ("W", "작업자 (BLE 태그 착용)")]
    for i, (k, v) in enumerate(items):
        y = 140 + i * 38
        b += [rich(1206, y, k, 13.5, "start", 700), rich(1240, y, v, 13, "start")]
    ly = 460
    b.append(f'<line x1="1206" y1="{ly}" x2="1450" y2="{ly}" stroke="#CCC"/>')
    b.append(f'<line x1="1206" y1="{ly + 30}" x2="1236" y2="{ly + 30}" stroke="{MK["b"]}" stroke-dasharray="4 3"/>' + rich(1246, ly + 34, "카메라 시야", 13, "start"))
    b.append(f'<line x1="1206" y1="{ly + 64}" x2="1236" y2="{ly + 64}" stroke="{MK["v"]}" stroke-width="1.4" stroke-dasharray="5 3"/>' + rich(1246, ly + 68, "자유낙하 궤적", 13, "start"))
    b.append(f'<rect x="1206" y="{ly + 92}" width="30" height="10" fill="url(#hatch-v)" stroke="{MK["v"]}"/>' + rich(1246, ly + 102, "동적 위험구역 $Z$_{t}", 13, "start"))
    b.append(f'<line x1="1206" y1="{ly + 132}" x2="1236" y2="{ly + 132}" stroke="{GRAY}" stroke-dasharray="6 4"/>' + rich(1246, ly + 136, "드론 순찰 경로", 13, "start"))
    b.append(f'<line x1="1206" y1="{ly + 166}" x2="1236" y2="{ly + 166}" stroke="{K}" stroke-width="1"/>' + rich(1246, ly + 170, "치수선 ($H$, $r$_{b}, $r$_{s})", 13, "start"))

    b.append(rich(30, 772, "**Fig. 3.** 장비 배치 개념도(측면도). 높이 $H$ = 30 m(10개 층)에서의 자유낙하 궤적을 Δ$t$ = 0.5 s 간격으로 표시하였으며(착지까지 2.47 s), "
                  "등간격 시각에 대한 위치 간격이 증가하는", 16, "start"))
    b.append(rich(30, 798, "가속 운동을 확인할 수 있다. 착지 반경 $r$_{b}와 인양물 동적 위험구역 $Z$_{t}(투영 + 안전반경 $r$_{s})를 함께 나타낸다. 축척 및 장비 위치는 개념적 예시이다.", 16, "start"))
    return svg(W, H, b)


# ---------------------------------------------------------------- Fig. 4 — 시스템 계층 구조
def architecture_figure():
    W, H = 1500, 800
    rows = [("응용 계층", 40, 150), ("클라우드 계층", 170, 300), ("엣지 계층", 320, 520), ("장치 계층", 540, 700)]
    b = []
    for i, (name, y0, y1) in enumerate(rows):
        b.append(f'<rect x="30" y="{y0}" width="1220" height="{y1 - y0}" fill="{"#FAFAFA" if i % 2 else "#FFFFFF"}" stroke="#999" stroke-width="1"/>')
        b.append(f'<rect x="30" y="{y0}" width="44" height="{y1 - y0}" fill="#EFEFEF" stroke="#999" stroke-width="1"/>')
        cy = (y0 + y1) / 2
        b.append(rich(57, cy, name, 15, weight=700).replace("<text ", f'<text transform="rotate(-90 57 {cy})" ', 1))

    # 응용 계층
    apps = [(110, 250, ["현장 안전관리자 앱", "이벤트 확인 · 조치 · 종결"], False), (390, 250, ["본사 통합관제", "다현장 위험지수 비교"], False),
            (670, 250, ["법정 증빙 리포트", "위험성평가 · 점검일지 자동 생성"], False), (950, 270, ["(확장) 위험점수 API", "보험 · PF 리스크 연계"], True)]
    for x, w, lines, d in apps:
        b.append(mod(x, 70, w, 52, lines, "gray", 14, dashed=d))
    # 클라우드 계층
    clouds = [(110, 250, ["이벤트 DB · 영상 저장", "클립 · 궤적 · 위치 메타데이터"], "lav"), (390, 250, ["드론 영상 분석", "고소부 위험요소 탐지"], "lav"),
              (670, 250, ["위험 분석", "히트맵 · 현장 위험지수"], "lav"), (950, 270, ["학습 파이프라인", "합성 데이터 → 재학습 → 실측 평가"], "green")]
    for x, w, lines, pal in clouds:
        b.append(mod(x, 200, w, 64, lines, pal, 14))
    for x in (235, 515, 795):
        b.append(karrow([(x, 200), (x, 124)]))
    b.append(karrow([(900, 200), (900, 162), (1085, 162), (1085, 124)], dashed=True))

    # 엣지 계층
    b.append(f'<rect x="110" y="338" width="850" height="168" rx="6" fill="none" stroke="#777" stroke-width="1.2" stroke-dasharray="6 4"/>')
    b.append(rich(122, 360, "**엣지 AI 박스** (Jetson Orin급 · IP66 함체 · LTE 이중화)", 14, "start"))
    mods = [(130, 180, ["낙하 감지", "검출 · 추적 · 물리 검증"], "blue"), (330, 180, ["위험구역 엔진", "인양물 투영 + $r$_{s}"], "lav"),
            (530, 180, ["위치 융합", "영상 사람 검출 + BLE"], "blue"), (750, 190, ["경보 판단", "$R$_{t}, $L$_{t}"], "alert")]
    for x, w, lines, pal in mods:
        b.append(mod(x, 380, w, 60, lines, pal, 14))
    for x in (220, 420, 620):
        b.append(f'<line x1="{x}" y1="440" x2="{x}" y2="470" stroke="{K}" stroke-width="1.3"/>')
    b.append(f'<line x1="220" y1="470" x2="845" y2="470" stroke="{K}" stroke-width="1.3"/>')
    b.append(karrow([(845, 470), (845, 442)]))
    b += [karrow([(235, 338), (235, 266)], dashed=True), karrow([(515, 338), (515, 266)], dashed=True),
          karrow([(955, 266), (955, 336)], dashed=True), rich(963, 312, "$θ$* (OTA)", 13, "start")]
    b.append(karrow([(940, 410), (1130, 410), (1130, 554)], c="v", width=1.6))
    b.append(rich(1035, 400, "실시간 경보", 13, fill="#A04000", weight=700))

    # 장치 계층
    b.append(rich(110, 562, "센서", 13, "start", italic=True, fill=GRAY))
    sensors = [(["상층부 카메라", "60 fps · 낙하 감지"], False), (["기존 CCTV", "RTSP 재활용"], False), (["크레인 센서", "후크캠 · 선회각"], False),
               (["BLE 태그", "작업자 위치"], False), (["풍속계", "순간풍속"], False), (["점검 드론", "정기 순찰"], True)]
    for i, (lines, d) in enumerate(sensors):
        x = 110 + 150 * i
        b.append(mod(x, 574, 135, 54, lines, "white", 14, dashed=d))
        b.append(karrow([(x + 67, 574), (x + 67, 508)], dashed=d))
    b.append(f'<rect x="1020" y="556" width="220" height="134" rx="6" fill="none" stroke="#777" stroke-width="1.2" stroke-dasharray="6 4"/>')
    b.append(rich(1032, 576, "경보 장치", 13, "start", italic=True, fill=GRAY))
    for i, s in enumerate(("경광등 · 다국어 스피커", "웨어러블 진동", "신호수 · 크레인 운전원 단말")):
        b.append(mod(1035, 586 + 34 * i, 190, 28, [s], "alert", 13))

    # 통신 · 지연
    b.append(rich(1270, 30, "통신 / 지연 요구", 14, "start", 700))
    notes = [(160, "HTTPS · 푸시 알림", "일 단위 리포트"), (310, "LTE (MQTT · HTTPS)", "분 단위 · 비실시간"),
             (530, "유선 PoE · RS-485 · BLE", "실시간 ≤ 0.35 s")]
    for y, a, c in notes:
        b.append(f'<line x1="1250" y1="{y}" x2="1268" y2="{y}" stroke="#999"/>')
        b += [rich(1276, y - 3, a, 13.5, "start"), rich(1276, y + 16, c, 12.5, "start", italic=True, fill=GRAY)]

    b.append(rich(30, 742, "**Fig. 4.** 시스템 계층 구조. 경보 판단은 엣지 계층에서 완결되어 통신 장애 시에도 동작하며(실선), "
                  "클라우드 계층은 이벤트 저장 · 분석 · 재학습을 비실시간으로 수행한다(점선).", 16, "start"))
    b.append(rich(30, 768, "경보 장치는 엣지 계층의 판단 결과로 구동되며, 학습된 가중치 $θ$*는 OTA로 엣지에 배포된다.", 16, "start"))
    return svg(W, H, b)


# ---------------------------------------------------------------- Fig. 5 — 3단계 운영 프로세스
def process_figure():
    W, H = 1500, 935

    def lane(y, h, n, name, desc):
        cy = y + h / 2
        return (f'<rect x="30" y="{y}" width="1440" height="{h}" fill="#FFFFFF" stroke="#999" stroke-width="1"/>'
                f'<rect x="30" y="{y}" width="170" height="{h}" fill="#F0F0F0" stroke="#999" stroke-width="1"/>'
                + rich(115, cy - 12, n, 20, weight=700) + rich(115, cy + 14, name, 17, weight=700) + rich(115, cy + 36, desc, 13, fill=GRAY))

    def diamond(cx, cy, l1, l2):
        return (f'<polygon points="{cx},{cy - 38} {cx + 75},{cy} {cx},{cy + 38} {cx - 75},{cy}" fill="#FFFFFF" stroke="#333" stroke-width="1.2"/>'
                + rich(cx, cy - 3, l1, 13.5, weight=700) + rich(cx, cy + 15, l2, 13.5, weight=700))

    yes = lambda x, y: rich(x, y, "예", 12.5, italic=True)
    no = lambda x, y: rich(x, y, "아니오", 12.5, "start", italic=True)
    b = []
    # 1단계 예방
    b.append(lane(30, 255, "1단계", "예방", "(노출 차단)"))
    for i, lines in enumerate((["드론 정기 순찰", "작업 전 · 점심 · 종료 후"], ["고소부 위험요소 탐지", "단부 자재 · 방지망 · 개구부"],
                               ["TBM 위험 리포트", "작업 전 공유 · 지시"], ["조치 · 사진 증빙", "관리자 앱으로 종결"])):
        b.append(mod(230 + 200 * i, 68, 170, 56, lines, "white"))
        if i:
            b.append(karrow([(200 + 200 * i, 96), (228 + 200 * i, 96)]))
    b += [mod(230, 180, 170, 56, ["크레인 인양 시작", "후크캠 · 선회각 수신"], "white"), karrow([(400, 208), (428, 208)]),
          mod(430, 180, 170, 56, ["동적 위험구역 생성", "$Z$_{t} = $P$(load) ⊕ $r$_{s}"], "white"), karrow([(600, 208), (628, 208)]),
          diamond(705, 208, "구역 내", "작업자?"), karrow([(780, 208), (828, 208)]), yes(804, 200),
          mod(830, 180, 170, 56, ["구역 경보", "경광등 · 진동 · 신호수"], "alert"),
          karrow([(705, 246), (705, 262), (515, 262), (515, 238)]), rich(610, 278, "아니오 → 인양 중 계속 갱신", 12.5, italic=True),
          mod(1060, 68, 390, 56, ["상시 · 상하 동시작업 감지", "동일 연직선상 상 · 하부 작업자 → 작업 조정 알림"], "white"),
          mod(1060, 180, 390, 56, ["상시 · 강풍 감지", "풍속 임계 초과 → 인양 중지 · 고소 자재 결속 알림"], "white")]

    # 2단계 대응
    cy = 388
    b.append(lane(298, 295, "2단계", "대응", "(낙하 순간)"))
    for x, lines in ((230, ["움직임 후보", "배경차분 $M$_{t}"]), (400, ["소형 객체 검출", "움직임 어텐션"]), (570, ["궤적 추적", "Kalman 필터"])):
        b.append(mod(x, cy - 28, 150, 56, lines, "white"))
    b += [karrow([(380, cy), (398, cy)]), karrow([(550, cy), (568, cy)]), karrow([(720, cy), (738, cy)]),
          diamond(815, cy, "중력 궤적", "일치?"), karrow([(890, cy), (918, cy)]), yes(904, cy - 8),
          mod(920, cy - 28, 150, 56, ["착지점 추정", "$p̂$ = $H$ $x̂$, 반경 $r$_{b}"], "white"), karrow([(1070, cy), (1088, cy)]),
          diamond(1165, cy, "반경 내", "작업자?"), karrow([(1240, cy), (1268, cy)]), yes(1254, cy - 8),
          mod(1270, cy - 28, 180, 56, ["즉시 대피 경보", "지정 방향 · 다국어 음성"], "alert")]
    for x, lines in ((815, ["기각", "조류 · 비닐 · 와이어"]), (1165, ["아차사고 기록", "피해 없음 → 3단계로"])):
        b += [karrow([(x, cy + 38), (x, 466)]), no(x + 8, 452), mod(x - 75, 468, 150, 46, lines, "gray", 13.5)]
    for x, s in ((305, "$t$ ≈ 33 ms"), (645, "$t$ ≈ 133 ms"), (995, "$t$ ≈ 143 ms"), (1360, "$t$ ≈ 350 ms (경광등 점등)")):
        b.append(rich(x, 436, s, 12.5, italic=False, fill=GRAY))
    b.append('<rect x="1270" y="468" width="180" height="78" fill="#FFFFFF" stroke="#999" stroke-width="1"/>')
    b += [rich(1360, 492, "종단 지연 목표", 13, weight=700), rich(1360, 516, "0.2 – 0.35 s", 17, weight=700),
          rich(1360, 536, "(30 m 낙하: 2.47 s)", 12, fill=GRAY)]

    # 3단계 학습
    b.append(lane(608, 222, "3단계", "학습", "(기록 · 증빙 · 재학습)"))
    top = [["이벤트 기록", "1 · 2단계 전 이벤트 · 영상"], ["관리자 확인 · 조치", "모바일 앱 → 종결"], ["위험 분석", "히트맵 · 현장 위험지수"],
           ["법정 증빙 자동화", "위험성평가 · 점검일지"], ["(확장) 금융 연계", "보험 · PF 위험점수"]]
    for i, lines in enumerate(top):
        b.append(mod(230 + 200 * i, 635, 170, 56, lines, "white", dashed=i == 4))
        if i:
            b.append(karrow([(200 + 200 * i, 663), (228 + 200 * i, 663)], dashed=i == 4))
    b += [karrow([(515, 691), (515, 718), (1115, 718), (1115, 733)], dashed=True),
          rich(815, 712, "오탐 · 미탐 표시", 12.5, italic=True)]
    bottom = [["가중치 배포", "OTA → 엣지"], ["실측 평가", "더미 낙하 시험"], ["검출기 재학습", "$θ$ 갱신"],
              ["합성 데이터 보강", "3D 시뮬레이션 + 실영상 합성"], ["하드 샘플 수집", "오탐 · 미탐"]]
    for i, lines in enumerate(bottom):
        b.append(mod(230 + 200 * i, 735, 170, 56, lines, "green"))
        if i:
            b.append(karrow([(230 + 200 * i, 763), (402 + 200 * (i - 1), 763)]))
    b.append(karrow([(230, 763), (212, 763), (212, cy), (228, cy)], dashed=True))
    b.append(rich(238, 540, "모델 갱신", 12.5, italic=True).replace("<text ", '<text transform="rotate(-90 238 540)" ', 1))

    cap = ["**Fig. 5.** 3단계 운영 프로세스. 1단계(예방)는 낙하 위험요소와 인양물 하부 노출을 사전에 차단하고, 2단계(대응)는 낙하 발생 시 0.35 s 이내 경보를 목표로 하며,",
           "3단계(학습)는 모든 이벤트를 기록 · 증빙하고 오탐 · 미탐을 합성 데이터로 보강하여 검출 모델을 갱신한다. 음영 상자는 경보, 회색 상자는 기각 · 기록,",
           "마름모는 판단, 점선은 비실시간 · 확장 경로를 나타낸다. 각 단계의 $t$는 감지 시작부터의 누적 지연 목표치이다."]
    for i, s in enumerate(cap):
        b.append(rich(30, 866 + 26 * i, s, 16, "start"))
    return svg(W, H, b)


# ---------------------------------------------------------------- Fig. 1 — 프레임워크 개요
def framework_figure():
    W, H = 1620, 810
    b = []
    b += [group(30, 70, 205, 460, "(a) 센서 입력"), group(255, 70, 940, 460, "(b) 현장 엣지 추론 (Edge Inference)"),
          group(1215, 70, 360, 460, "(c) 위험도 판단 · 경보 · 관제"),
          group(255, 580, 1320, 140, "(d) 합성 데이터 기반 학습 루프 (오프라인)")]

    # (a) 센서 입력
    b.append(mod(45, 108, 175, 44, ["드론 순찰 영상", "(비실시간)"], "gray", 13.5, dashed=True))
    b += [frame(74, 170), frame(62, 180), frame(50, 190, dot=True)]
    b += [rich(125, 324, "입력 프레임", 13.5), rich(125, 343, "$I$_{t−k}, …, $I$_{t}", 13.5)]
    b.append('<rect x="45" y="362" width="175" height="46" fill="#FFFFFF" stroke="#888" stroke-width="1"/>')
    b.append('<polyline points="52,401 52,368 52,401 214,401" fill="none" stroke="#888" stroke-width=".8"/>')
    b.append('<polyline points="' + " ".join(f"{55 + i * 4},{384 - 11 * math.sin(i / 5):.1f}" for i in range(40))
             + '" fill="none" stroke="#0072B2" stroke-width="1.2"/>')
    b.append('<polyline points="' + " ".join(f"{55 + i * 4},{392 - 6 * math.sin(i / 11 + 1):.1f}" for i in range(40))
             + '" fill="none" stroke="#D55E00" stroke-width="1.2"/>')
    b.append(rich(132, 428, "크레인 텔레메트리 $θ$($t$), $r$($t$)", 12.5))
    b.append('<rect x="45" y="446" width="175" height="44" fill="#FFFFFF" stroke="#888" stroke-width="1"/>')
    for gx in range(60, 220, 20):
        b.append(f'<line x1="{gx}" y1="446" x2="{gx}" y2="490" stroke="#E3E3E3"/>')
    for gx, gy in ((78, 462), (121, 476), (157, 458), (190, 471)):
        b.append(f'<circle cx="{gx}" cy="{gy}" r="3.2" fill="#0072B2"/>')
    b.append(rich(132, 510, "BLE 태그 위치", 12.5))

    # (b-1) 낙하물 검출 분기
    b.append(rich(285, 150, "소형 객체 검출기 (움직임 어텐션, MA)", 13, "start", italic=True, fill="#444"))
    b += [cuboid(285, 172, 22, 100, 14), mod(330, 206, 45, 32, ["MA"], "green", 13),
          cuboid(397, 186, 26, 72, 12), mod(445, 206, 45, 32, ["MA"], "green", 13),
          cuboid(512, 200, 30, 44, 10), mod(565, 204, 72, 36, ["검출 헤드"], "gray", 13)]
    b += [karrow([(182, 222), (283, 222)]), karrow([(307, 222), (328, 222)]), karrow([(375, 222), (395, 222)]),
          karrow([(423, 222), (443, 222)]), karrow([(490, 222), (510, 222)]), karrow([(542, 222), (563, 222)])]
    b.append(mod(300, 300, 170, 38, ["움직임 마스크 $M$_{t} (MOG2)"], "pink", 13.5))
    b += [karrow([(182, 270), (243, 270), (243, 319), (298, 319)]),
          karrow([(352, 300), (352, 240)]), karrow([(467, 300), (467, 240)])]
    b.append(mod(660, 198, 100, 48, ["다중 객체 추적", "(Kalman)"], "blue", 13.5))
    b.append(karrow([(637, 222), (658, 222)]))
    # 물리 일관성 검증 (미니 플롯)
    b.append(f'<rect x="785" y="140" width="200" height="155" rx="2" fill="{PAL["peach"][0]}" stroke="{PAL["peach"][1]}" stroke-width="1.2"/>')
    b += [rich(885, 162, "물리 일관성 검증", 14, weight=700),
          rich(885, 182, "$ŷ$($t$) = $y$_{0} + $v$_{0}$t$ + ½$g$$t$^{2}", 13)]
    b.append('<polyline points="805,194 805,262 972,262" fill="none" stroke="#666" stroke-width=".9"/>')
    b.append('<polyline points="' + " ".join(f"{810 + 150 * i / 40:.1f},{198 + 60 * (i / 40) ** 2:.1f}" for i in range(41))
             + '" fill="none" stroke="#222" stroke-width="1"/>')
    for i in range(10):
        tt = i / 9
        b.append(f'<circle cx="{810 + 150 * tt:.1f}" cy="{198 + 60 * tt * tt + (1.5 if i % 2 else -1.5):.1f}" r="2.6" fill="#222"/>')
    for x, y in ((822, 236), (842, 224), (862, 233), (882, 218), (902, 229), (922, 214)):
        b.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#FFFFFF" stroke="#D55E00" stroke-width="1.2"/>')
    b += [rich(872, 257, "채택", 11, "start"), rich(930, 209, "기각", 11, "start", fill="#B34700"),
          rich(974, 274, "$t$", 11, "end"), rich(800, 202, "Δ$y$", 11, "end"),
          rich(885, 286, "|$ĝ$ − $g$| < $ε$ 이면 채택", 12.5)]
    b.append(karrow([(760, 222), (783, 222)]))
    # 착지점 추정
    b.append(f'<rect x="1010" y="167" width="170" height="110" rx="2" fill="{PAL["blue"][0]}" stroke="{PAL["blue"][1]}" stroke-width="1.2"/>')
    b += [rich(1095, 190, "착지점 추정", 14, weight=700), rich(1095, 210, "$p̂$ = $H$ $x̂$", 13)]
    b.append('<polygon points="1030,266 1160,266 1136,224 1054,224" fill="#F4F4F4" stroke="#777" stroke-width="1"/>')
    b.append('<ellipse cx="1096" cy="248" rx="25" ry="7" fill="none" stroke="#D55E00" stroke-width="1.2" stroke-dasharray="3 2"/>')
    b.append('<circle cx="1096" cy="248" r="3" fill="#D55E00"/>' + rich(1128, 244, "$r$_{b}", 11, "start"))
    b.append(karrow([(985, 222), (1008, 222)]))

    # (b-2) 위험구역 분기
    b.append(mod(300, 385, 170, 50, ["인양물 투영", "(후크캠 · 선회각 · 반경)"], "lav", 13.5))
    b.append(mod(500, 375, 200, 70, ["동적 위험구역", "$Z$_{t} = $P$(load) ⊕ $r$_{s}"], "lav", 14))
    b.append(mod(300, 465, 170, 50, ["작업자 위치 $W$_{t}", "(사람 검출 + BLE)"], "blue", 13.5))
    b += [karrow([(220, 385), (240, 385), (240, 410), (298, 410)]), karrow([(470, 410), (498, 410)]),
          karrow([(220, 468), (240, 468), (240, 490), (298, 490)])]

    # (c) 위험도 판단 · 경보
    b += [karrow([(1180, 222), (1230, 222)]), rich(1205, 214, "$p̂$, $r$_{b}", 12),
          karrow([(700, 410), (1230, 410)]), rich(1170, 402, "$Z$_{t}", 13),
          karrow([(470, 490), (1230, 490)]), rich(1170, 482, "$W$_{t}", 13)]
    b.append(f'<rect x="1232" y="180" width="173" height="335" rx="2" fill="{PAL["yellow"][0]}" stroke="{PAL["yellow"][1]}" stroke-width="1.2"/>')
    b += [rich(1318, 318, "위험도 판단", 15, weight=700),
          rich(1318, 352, "$R$_{t} = **1**[$A$_{t} ∩ $W$_{t} ≠ ∅]", 14),
          rich(1318, 380, "$A$_{t} = $B$($p̂$, $r$_{b}) ∪ $Z$_{t}", 14),
          rich(1318, 414, "경보 등급 $L$_{t} ∈ {0, 1, 2}", 14)]
    for y, lines, pal in ((180, ["관제 대시보드", "· 이벤트 로그"], "gray"), (305, ["현장 경보", "(경광등 · 스피커)"], "peach"),
                          (430, ["개인 경보", "(웨어러블 진동)"], "peach")):
        b.append(mod(1435, y, 125, 60 if y == 180 else 50, lines, pal, 13.5))
        b.append(karrow([(1405, y + (30 if y == 180 else 25)), (1433, y + (30 if y == 180 else 25))]))
    b.append(karrow([(180, 108), (180, 50), (1497, 50), (1497, 178)], dashed=True))
    b.append(rich(838, 42, "드론 정기 순찰 → 고소부 위험요소 점검 결과 (비실시간)", 13, italic=True, fill="#555"))

    # (d) 학습 루프 (오른쪽 → 왼쪽)
    b.append(karrow([(1560, 210), (1592, 210), (1592, 658), (1547, 658)], dashed=True))
    b.append(rich(1598, 434, "오탐 · 미탐 샘플", 12.5, italic=True, fill="#555").replace("<text ", '<text transform="rotate(90 1598 434)" '))
    stages = [(1400, 145, ["하드 샘플 수집", "(오탐 · 미탐)"], "gray"),
              (1120, 250, ["합성 데이터 생성", "(3D 물리 시뮬레이션 + 실영상 합성)"], "lav"),
              (880, 210, ["도메인 무작위화", "{$h$, 객체, 조명, 기상, 카메라}"], "lav"),
              (700, 150, ["검출기 학습", "($θ$ 갱신)"], "green"),
              (520, 150, ["실측 평가", "(더미 낙하 시험)"], "blue"),
              (300, 190, ["가중치 배포 $θ$*", "(OTA → 엣지)"], "green")]
    for i, (x, w, lines, pal) in enumerate(stages):
        b.append(mod(x, 628, w, 60, lines, pal, 14))
        if i:
            px = stages[i - 1][0]
            b.append(karrow([(px, 658), (x + w + 2, 658)]))
    b.append(karrow([(395, 628), (395, 533)], dashed=True))
    b.append(rich(405, 566, "검출기 가중치 갱신", 12.5, "start", italic=True, fill="#555"))

    # 캡션
    b.append(rich(30, 762, "**Fig. 1.** 제안하는 건설현장 낙하물 사고 예방·경보 프레임워크(DropZero)의 전체 구조. "
                  "(a) 영상·크레인 텔레메트리·BLE 다중 센서 입력, (b) 낙하물 검출과 동적 위험구역 추정을 수행하는 현장 엣지 추론,", 16, "start"))
    b.append(rich(30, 788, "(c) 위험도 판단에 따른 현장·개인 경보 및 관제, (d) 현장 하드 샘플과 합성 데이터를 이용한 오프라인 학습 루프. "
                  "실선은 실시간 경로, 점선은 비실시간 경로를 나타낸다.", 16, "start"))
    return svg(W, H, b)


# ---------------------------------------------------------------- Fig. 2 — 타당성 분석 (matplotlib)
def analysis_figure():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    plt.rcParams.update({
        "font.family": ["Nanum Myeongjo"], "font.size": 11,  # mathtext 본문 글꼴은 대체 글꼴이 없어 한글 포함 글꼴 하나로
        "mathtext.fontset": "custom", "mathtext.rm": "Nanum Myeongjo", "mathtext.it": "Times New Roman:italic",
        "mathtext.bf": "Times New Roman:bold", "mathtext.fallback": "stix",
        "axes.linewidth": .8, "xtick.direction": "in", "ytick.direction": "in", "axes.spines.top": False,
        "axes.spines.right": False, "legend.frameon": False, "axes.unicode_minus": False, "svg.fonttype": "path"})
    g, lat, VERM, GREEN = 9.81, .35, "#D55E00", "#009E73"
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.4), gridspec_kw={"width_ratios": [1.15, 1, 1]})
    fig.subplots_adjust(left=.05, right=.985, top=.97, bottom=.34, wspace=.27)

    # (a) 낙하 높이별 자유낙하 시간 vs 경보 후 회피 요구 시간
    ax = axs[0]
    h = np.linspace(0, 60, 400)
    lo, hi = lat + 1.5, lat + 2.5
    h_lo, h_hi = g * lo ** 2 / 2, g * hi ** 2 / 2
    ax.axvspan(0, h_lo, color=VERM, alpha=.07, lw=0)
    ax.axhspan(lo, hi, color="0.87", lw=0)
    ax.axhline(lat, color="0.35", ls="--", lw=.9)
    ax.plot(h, np.sqrt(2 * h / g), color="k", lw=1.6)
    for hv in (h_lo, h_hi):
        ax.axvline(hv, color=VERM, ls=":", lw=1.2)
        ax.text(hv + .8, .1, f"{hv:.1f} m", color="#A04000", fontsize=10)
    for hp in (10, 30):
        tp = np.sqrt(2 * hp / g)
        ax.plot(hp, tp, "o", ms=5.5, mfc="white", mec="k", mew=1.1)
        ax.annotate(f"{tp:.2f} s", (hp, tp), xytext=(7, -15), textcoords="offset points", fontsize=10)
    ax.text(h_lo / 2, 1.62, "회피 곤란", ha="center", fontsize=10.5, color="#A04000")
    ax.text(51, 1.25, "회피 가능", ha="center", fontsize=10.5, color="#00704F")
    ax.set(xlim=(0, 60), ylim=(0, 4.6), xlabel="낙하 높이 $h$ (m)", ylabel="낙하 시간 $t$ (s)")
    ax.legend(handles=[Line2D([], [], color="k", lw=1.6, label=r"자유낙하 시간 $t=\sqrt{2h/g}$"),
                       Patch(color="0.87", label="경보 후 회피 요구 시간 (지연 0.35 s + 반응 1.5–2.5 s)"),
                       Line2D([], [], color="0.35", ls="--", lw=.9, label="시스템 지연 목표 0.35 s"),
                       Line2D([], [], color=VERM, ls=":", lw=1.2, label="실시간 회피 가능 최소 높이")],
              loc="upper left", fontsize=9.5, handlelength=2.2, frameon=True, facecolor="white", edgecolor="none", framealpha=1)

    # (b) 감지 → 경보 종단 지연 예산
    ax = axs[1]
    comps = [("영상 획득 (2 frame, 60 fps)", 33, "0.25", ""), ("검출·추적 (5–6 frame)", 100, "0.55", ""),
             ("물리 검증·판단", 10, "0.8", ""), ("경보 전송 (유선/RF)", None, "white", "///")]
    for yi, tx in enumerate((50, 200)):
        left = 0
        for name, v, c, hatch in comps:
            v = tx if v is None else v
            ax.barh(yi, v, left=left, height=.5, color=c, edgecolor="k", lw=.8, hatch=hatch, label=None if yi else name)
            left += v
        ax.text(left + 13, yi, f"{left} ms", va="center", fontsize=10.5)
    ax.axvline(350, color=VERM, ls=":", lw=1.2)
    ax.text(345, -.4, "목표 상한 350 ms", ha="right", fontsize=10, color="#A04000")
    ax.set(yticks=[0, 1], yticklabels=["최소", "최대"], xlim=(0, 420), ylim=(3.0, -.6), xlabel="종단 지연 (ms)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, .02), fontsize=9.5, ncol=1)

    # (c) 물리 일관성 검증 (모의 데이터)
    ax = axs[2]
    rng = np.random.default_rng(7)
    t = np.arange(16) / 60
    tracks = [("낙하물", .5 * g * t ** 2 + .15 * t + rng.normal(0, .006, t.size), "o", "k", "k"),
              ("조류", .35 * t - 1.2 * t ** 2 + .02 * np.sin(2 * np.pi * 7 * t) + rng.normal(0, .006, t.size), "^", "#0072B2", "white"),
              ("와이어 흔들림", .05 * np.sin(2 * np.pi * 3 * t) + rng.normal(0, .004, t.size), "s", VERM, "white")]
    tf = np.linspace(0, t[-1], 100)
    for name, y, mk, c, fc in tracks:
        coef = np.polyfit(t, y, 2)
        ghat = 2 * coef[0]
        verdict = "채택" if abs(ghat - g) < 1.5 else "기각"
        ax.plot(t, y, mk, ms=5, mec=c, mfc=fc, mew=1.1, label=f"{name}: $\\hat{{g}}$ = {ghat:.1f} m/s$^2$ ({verdict})")
        ax.plot(tf, np.polyval(coef, tf), color=c, lw=1, alpha=.9)
    ax.text(.02, .97, "모의 데이터 · 60 fps, 16 frame", transform=ax.transAxes, va="top", fontsize=9.5, color="0.35")
    ax.set(xlim=(0, .26), xlabel="시간 $t$ (s)", ylabel=r"연직 하강 변위 $\Delta y$ (m)")
    ax.legend(loc="upper left", bbox_to_anchor=(0, .91), fontsize=9.5, handlelength=1.5)

    for ax, label in zip(axs, ("(a) 낙하 높이별 실시간 회피 가능성", "(b) 감지 → 경보 종단 지연 예산 (목표치)",
                               "(c) 중력가속도 적합에 의한 비낙하 객체 기각")):
        pos = ax.get_position()
        fig.text(pos.x0 + pos.width / 2, .175, label, ha="center", fontsize=12.5)
    cap = ["실시간 낙하 경보의 물리적 타당성 분석. (a) 자유낙하 시간과 경보 후 회피 요구 시간(시스템 지연 0.35 s + 인간 반응 1.5–2.5 s)의 비교:",
           "약 17 m 미만에서는 실시간 회피가 곤란하므로 예방(노출 차단) 계층이 필수적이다. (b) 감지에서 경보까지의 종단 지연 예산(목표치).",
           "(c) 궤적의 2차 적합으로 추정한 중력가속도 $\\hat{g}$를 이용한 비낙하 객체 기각 예시(|$\\hat{g}-g$| < 1.5 m/s$^2$ 채택, 카메라 보정 후 연직 변위, 모의 데이터)."]
    t1 = fig.text(.012, .105, "Fig. 2.", fontsize=12.5, fontweight="bold", fontfamily="Times New Roman")
    fig.canvas.draw()
    off = t1.get_window_extent().width / fig.bbox.width + .005
    fig.text(.012 + off, .105, cap[0], fontsize=12)
    fig.text(.012, .062, cap[1], fontsize=12)
    fig.text(.012, .019, cap[2], fontsize=12)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"fig2-analysis.{ext}", dpi=220)
    plt.close(fig)
    print("wrote fig2-analysis.svg + png")


if __name__ == "__main__":
    for name, fn in (("fig1-framework", framework_figure), ("fig3-site-layout", site_figure),
                     ("fig4-architecture", architecture_figure), ("fig5-process", process_figure)):
        path = OUT / f"{name}.svg"
        content = fn()
        path.write_text(content, encoding="utf-8")
        w, h = content.split('width="')[1].split('"')[0], content.split('height="')[1].split('"')[0]
        subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=2",
                        f"--window-size={w},{h}", f"--screenshot={OUT / (name + '.png')}", path.as_uri()],
                       check=True, capture_output=True)
        print("wrote", path.name, "+ png")
    analysis_figure()
