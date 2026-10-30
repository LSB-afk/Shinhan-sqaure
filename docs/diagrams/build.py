"""DropZero 도면 생성기: python3 docs/diagrams/build.py → 같은 폴더에 SVG 3장 + PNG 3장(2x).

문구·좌표를 바꾸려면 이 파일만 고치고 다시 실행한다.
"""
import math
import pathlib
import subprocess
from html import escape

OUT = pathlib.Path(__file__).parent
FONT = "Pretendard, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

INK, MUTED = "#0F172A", "#64748B"
COLORS = {"gray": "#4B5563", "red": "#DC2626", "blue": "#2563EB", "green": "#16A34A", "amber": "#D97706"}
STYLES = {  # fill, stroke, title, sub
    "blue": ("#FFFFFF", "#3B6FE0", "#1E3A8A", MUTED),
    "redlane": ("#FFFFFF", "#E26D6D", "#7F1D1D", MUTED),
    "greenlane": ("#FFFFFF", "#3FA866", "#14532D", MUTED),
    "alert": ("#E53935", "#B71C1C", "#FFFFFF", "#FFE4E4"),
    "gray": ("#F3F4F6", "#9CA3AF", "#374151", MUTED),
    "amber": ("#FFF7E0", "#F59E0B", "#92400E", "#A16207"),
    "dark": ("#1E3A8A", "#1E3A8A", "#FFFFFF", "#C7D2FE"),
}


def t(x, y, s, size=14, weight=400, fill=INK, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def box(x, y, w, h, title, sub=None, kind="blue", dashed=False, rx=10):
    fill, stroke, tc, sc = STYLES[kind]
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    cx, cy = x + w / 2, y + h / 2
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"{dash}/>']
    if sub:
        out += [t(cx, cy - 3, title, 14.5, 700, tc, "middle"), t(cx, cy + 15, sub, 12, 400, sc, "middle")]
    else:
        out.append(t(cx, cy + 5, title, 14, 700, tc, "middle"))
    return "".join(out)


def diamond(cx, cy, l1, l2, w=150, h=76):
    pts = f"{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}"
    return (f'<polygon points="{pts}" fill="#FFF8E1" stroke="#F59E0B" stroke-width="2"/>'
            + t(cx, cy - 3, l1, 14, 700, "#92400E", "middle") + t(cx, cy + 15, l2, 14, 700, "#92400E", "middle"))


def arrow(pts, color="gray", dashed=False, width=2):
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    p = " ".join(f"{x},{y}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{COLORS[color]}" stroke-width="{width}"{dash} '
            f'stroke-linejoin="round" marker-end="url(#ah-{color})"/>')


def svg(w, h, body):
    markers = "".join(
        f'<marker id="ah-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" '
        f'markerWidth="11" markerHeight="11" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{v}"/></marker>'
        for k, v in COLORS.items())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}"><defs>{markers}</defs><rect width="{w}" height="{h}" fill="#FFFFFF"/>'
            + "".join(body) + "</svg>")


def badge(x, y, n):
    return f'<circle cx="{x}" cy="{y}" r="12" fill="{INK}"/>' + t(x, y + 5, str(n), 13, 700, "#FFFFFF", "middle")


def worker(x, y, helmet="#F59E0B", ring=None):
    """y = 발 위치."""
    s = "#374151"
    out = [
        f'<line x1="{x}" y1="{y - 14}" x2="{x - 6}" y2="{y}" stroke="{s}" stroke-width="3" stroke-linecap="round"/>',
        f'<line x1="{x}" y1="{y - 14}" x2="{x + 6}" y2="{y}" stroke="{s}" stroke-width="3" stroke-linecap="round"/>',
        f'<line x1="{x}" y1="{y - 14}" x2="{x}" y2="{y - 28}" stroke="{s}" stroke-width="4" stroke-linecap="round"/>',
        f'<line x1="{x - 8}" y1="{y - 22}" x2="{x + 8}" y2="{y - 22}" stroke="{s}" stroke-width="3" stroke-linecap="round"/>',
        f'<circle cx="{x}" cy="{y - 33}" r="5" fill="#F1C7A5"/>',
        f'<path d="M{x - 7},{y - 35} A7,7 0 0 1 {x + 7},{y - 35} Z" fill="{helmet}"/>',
    ]
    if ring:
        out.append(f'<circle cx="{x}" cy="{y - 18}" r="26" fill="none" stroke="{ring}" stroke-width="2.5" stroke-dasharray="5 4"/>')
    return "".join(out)


# ---------------------------------------------------------------- 1. 현장 배치도
def site_layout():
    W, H, G = 1500, 815, 680  # G = 지면 y
    b = [t(40, 46, "현장 배치도 (측면도)", 26, 800),
         t(40, 72, "건설현장 낙하물 사고 예방·경보 시스템 DropZero — 장비 배치 예시", 15, 400, MUTED),
         f'<rect x="30" y="92" width="1145" height="{G - 92}" rx="14" fill="#F5F9FF"/>',
         f'<rect x="30" y="{G}" width="1145" height="72" fill="#EADFCC"/>',
         f'<line x1="30" y1="{G}" x2="1175" y2="{G}" stroke="#8B7355" stroke-width="3"/>']

    # 건물 (9개 층, 상부 골조 공사 중)
    b.append(f'<rect x="120" y="212" width="300" height="{G - 212}" fill="#E3E8EF" stroke="#7B8794" stroke-width="2"/>')
    for k in range(0, 6):
        top = G - 52 * (k + 1)
        for bx in (120, 220, 320):
            b.append(f'<rect x="{bx + 12}" y="{top + 11}" width="76" height="28" rx="2" fill="#C9D6E6"/>')
    for k in range(1, 10):
        y = G - 52 * k
        b.append(f'<line x1="112" y1="{y}" x2="428" y2="{y}" stroke="#6B7684" stroke-width="5"/>')
    for x in (120, 220, 320, 420):
        b.append(f'<line x1="{x}" y1="164" x2="{x}" y2="{G}" stroke="#7B8794" stroke-width="3"/>')
    b.append('<rect x="222" y="176" width="96" height="36" fill="#D9B98C" stroke="#A0784A"/>')  # 거푸집
    b.append('<line x1="112" y1="190" x2="428" y2="190" stroke="#F59E0B" stroke-width="2.5"/>')  # 안전난간
    for y in (472, 316):  # 낙하물방지망 (좌측 외벽)
        b.append(f'<polygon points="120,{y} 62,{y - 26} 62,{y - 21} 120,{y + 5}" fill="#A5D6A7" stroke="#2E7D32" stroke-width="2"/>')
    b.append(t(40, 438, "낙하물방지망", 12, 600, "#2E7D32"))
    b.append(worker(392, 212))

    # 낙하 궤적 (자유낙하: 수평 이동량 ∝ √낙하거리)
    traj = [(432 + 38 * math.sqrt((y - 206) / (G - 206)), y) for y in range(206, G + 1, 6)]
    b.append('<polyline points="' + " ".join(f"{x:.1f},{y}" for x, y in traj)
             + '" fill="none" stroke="#F97316" stroke-width="2.5" stroke-dasharray="2 7" stroke-linecap="round"/>')
    for y in (262, 322, 392):
        x = 432 + 38 * math.sqrt((y - 206) / (G - 206))
        b.append(f'<circle cx="{x:.1f}" cy="{y}" r="5" fill="#FFFFFF" stroke="#F97316" stroke-width="2"/>')
    ox = 432 + 38 * math.sqrt((462 - 206) / (G - 206))
    b.append(f'<rect x="{ox - 4:.1f}" y="452" width="8" height="20" rx="2" fill="#374151" transform="rotate(25 {ox:.1f} 462)"/>')
    for dx in (-5, 0, 5):
        b.append(f'<line x1="{ox + dx:.1f}" y1="430" x2="{ox + dx:.1f}" y2="446" stroke="#94A3B8" stroke-width="1.5"/>')
    b.append(t(484, 300, "낙하물 궤적 추적", 13, 700, "#C2410C"))
    b.append(t(484, 318, "중력가속도 일치 검증", 13, 400, "#C2410C"))
    b.append(f'<ellipse cx="470" cy="{G}" rx="46" ry="9" fill="#FB923C" fill-opacity=".35" stroke="#F97316" stroke-width="2" stroke-dasharray="5 4"/>')
    b.append(t(470, 712, "낙하 착지점 예측", 14, 700, "#C2410C", "middle"))
    b.append(t(470, 731, "+ 비산 반경", 12, 400, "#C2410C", "middle"))
    b.append(worker(535, G, ring="#F97316"))

    # 경광등·스피커 (건물 출입 동선)
    b.append(f'<line x1="600" y1="556" x2="600" y2="{G}" stroke="#6B7280" stroke-width="4"/>')
    b.append('<rect x="590" y="538" width="20" height="18" rx="4" fill="#EF4444"/>')
    for a in (-60, -30, 0, 30, 60):
        r = math.radians(a - 90)
        b.append(f'<line x1="{600 + 16 * math.cos(r):.1f}" y1="{547 + 16 * math.sin(r):.1f}" '
                 f'x2="{600 + 25 * math.cos(r):.1f}" y2="{547 + 25 * math.sin(r):.1f}" stroke="#EF4444" stroke-width="2"/>')

    # 현장사무실 + 엣지 박스
    b.append(f'<rect x="625" y="628" width="120" height="52" rx="3" fill="#1E3A8A"/>')
    b.append('<line x1="735" y1="628" x2="735" y2="606" stroke="#1E3A8A" stroke-width="2"/>')
    b.append('<path d="M727,604 A10,10 0 0 1 743,604 M722,598 A16,16 0 0 1 748,598" fill="none" stroke="#1E3A8A" stroke-width="2"/>')
    b.append(t(685, 650, "현장사무실", 12, 400, "#C7D2FE", "middle"))
    b.append(t(685, 668, "엣지 AI 박스", 13, 700, "#FFFFFF", "middle"))

    # 타워크레인
    b.append(f'<rect x="760" y="120" width="20" height="{G - 120}" fill="none" stroke="#D97706" stroke-width="2.5"/>')
    b.append('<polyline points="' + " ".join(f"{760 if i % 2 else 780},{120 + 20 * i}" for i in range((G - 120) // 20 + 1))
             + '" fill="none" stroke="#D97706" stroke-width="1.5"/>')
    b.append(f'<rect x="748" y="{G - 8}" width="44" height="10" fill="#6B7280"/>')
    b.append('<rect x="650" y="112" width="500" height="14" fill="none" stroke="#D97706" stroke-width="2.5"/>')
    b.append('<polyline points="' + " ".join(f"{650 + 14 * i},{126 if i % 2 else 112}" for i in range(36))
             + '" fill="none" stroke="#D97706" stroke-width="1.5"/>')
    b.append('<polygon points="760,112 770,66 780,112" fill="none" stroke="#D97706" stroke-width="2.5"/>')
    b.append('<line x1="770" y1="66" x2="1150" y2="112" stroke="#D97706" stroke-width="1"/>')
    b.append('<line x1="770" y1="66" x2="650" y2="112" stroke="#D97706" stroke-width="1"/>')
    b.append('<rect x="655" y="126" width="34" height="26" fill="#9CA3AF"/>')
    b.append('<rect x="782" y="128" width="26" height="22" rx="2" fill="#FBBF24" stroke="#D97706"/>')
    b.append('<line x1="770" y1="66" x2="770" y2="52" stroke="#374151" stroke-width="2"/>')  # 풍속계
    b.append('<circle cx="763" cy="50" r="4" fill="#374151"/><circle cx="777" cy="50" r="4" fill="#374151"/>')
    b.append('<rect x="990" y="126" width="20" height="9" fill="#374151"/>')  # 트롤리
    b.append('<line x1="1000" y1="135" x2="1000" y2="392" stroke="#374151" stroke-width="1.5"/>')
    b.append('<polygon points="1000,148 978,404 1022,404" fill="#3B82F6" fill-opacity=".08"/>')  # 후크캠 시야
    b.append('<rect x="994" y="137" width="12" height="9" rx="2" fill="#2563EB"/>')
    b.append('<line x1="1000" y1="392" x2="966" y2="404" stroke="#374151"/><line x1="1000" y1="392" x2="1034" y2="404" stroke="#374151"/>')
    b.append('<rect x="962" y="404" width="76" height="22" fill="#8D99AE" stroke="#4B5563"/>')
    for y in (410, 415, 420):
        b.append(f'<line x1="964" y1="{y}" x2="1036" y2="{y}" stroke="#4B5563" stroke-width="1"/>')

    # 인양물 동적 위험구역
    b.append(f'<polygon points="962,426 1038,426 1072,{G} 928,{G}" fill="#EF4444" fill-opacity=".08" stroke="#EF4444" stroke-dasharray="5 5"/>')
    b.append(f'<ellipse cx="1000" cy="{G}" rx="72" ry="10" fill="#EF4444" fill-opacity=".35" stroke="#DC2626" stroke-width="2"/>')
    b.append(t(1000, 712, "인양물 동적 위험구역", 14, 700, "#B91C1C", "middle"))
    b.append(t(1000, 731, "투영 + 안전반경 · 인양 중 실시간 갱신", 12, 400, "#B91C1C", "middle"))
    b.append(worker(1050, G, ring="#DC2626"))
    b.append(t(1050, 618, "진입 경보", 12, 700, "#B91C1C", "middle"))

    # 상층부 전용 카메라 (크레인 마스트) + 시야
    b.append('<polygon points="738,329 430,150 430,470" fill="#3B82F6" fill-opacity=".07" stroke="#3B82F6" stroke-opacity=".35" stroke-dasharray="4 4"/>')
    b.append('<rect x="736" y="322" width="22" height="14" rx="3" fill="#2563EB"/>')

    # 지상 CCTV 폴 + 경광등
    b.append(f'<line x1="1140" y1="470" x2="1140" y2="{G}" stroke="#6B7280" stroke-width="4"/>')
    b.append(f'<polygon points="1112,474 930,{G} 1090,{G}" fill="#3B82F6" fill-opacity=".07" stroke="#3B82F6" stroke-opacity=".35" stroke-dasharray="4 4"/>')
    b.append('<rect x="1110" y="463" width="30" height="15" rx="3" fill="#2563EB"/>')
    b.append('<rect x="1144" y="512" width="14" height="13" rx="3" fill="#EF4444"/>')

    # 드론 + 순찰 경로
    b.append('<ellipse cx="270" cy="150" rx="205" ry="30" fill="none" stroke="#6366F1" stroke-width="2" stroke-dasharray="7 6"/>')
    b.append('<rect x="279" y="105" width="14" height="8" rx="2" fill="#4338CA"/>')
    for dx in (-12, 12):
        b.append(f'<line x1="286" y1="109" x2="{286 + dx}" y2="103" stroke="#4338CA" stroke-width="2"/>')
        b.append(f'<ellipse cx="{286 + dx}" cy="101" rx="9" ry="2.5" fill="#818CF8"/>')
    b.append(t(306, 112, "작업자 없는 시간대 순찰", 12, 600, "#4338CA"))

    for x, y, n in ((1030, 150, 1), (747, 356, 2), (1140, 446, 3), (262, 106, 4),
                    (628, 612, 5), (578, 540, 6), (1082, 640, 7), (792, 52, 8)):
        b.append(badge(x, y, n))

    # 범례
    b.append('<rect x="1195" y="92" width="275" height="660" rx="14" fill="#F8FAFC" stroke="#E2E8F0"/>')
    b.append(t(1215, 126, "장비 구성", 17, 800))
    items = [("크레인 후크캠", "인양물 위치 추적"), ("상층부 전용 카메라", "60fps · 낙하 감지"),
             ("지상 CCTV", "기존 재활용 · 작업자·구역"), ("점검 드론", "하루 2~3회 정기순찰"),
             ("엣지 AI 박스", "현장 내 판단·경보"), ("경광등·다국어 스피커", "구역 경보"),
             ("스마트 안전모·BLE 태그", "진동 경보 · 위치"), ("풍속계", "강풍 시 인양 중지")]
    for i, (name, desc) in enumerate(items):
        y = 160 + i * 56
        b += [badge(1224, y - 5, i + 1), t(1246, y, name, 15, 700), t(1246, y + 19, desc, 12.5, 400, MUTED)]
    b.append('<line x1="1215" y1="608" x2="1450" y2="608" stroke="#E2E8F0"/>')
    b.append('<ellipse cx="1232" cy="636" rx="16" ry="5" fill="#EF4444" fill-opacity=".35" stroke="#DC2626"/>' + t(1258, 641, "인양물 동적 위험구역", 13))
    b.append('<ellipse cx="1232" cy="664" rx="16" ry="5" fill="#FB923C" fill-opacity=".35" stroke="#F97316"/>' + t(1258, 669, "낙하 착지점 예측 반경", 13))
    b.append('<polygon points="1218,692 1248,684 1248,700" fill="#3B82F6" fill-opacity=".15" stroke="#3B82F6" stroke-opacity=".5"/>' + t(1258, 697, "카메라 시야", 13))
    b.append('<line x1="1216" y1="720" x2="1248" y2="720" stroke="#6366F1" stroke-width="2" stroke-dasharray="7 6"/>' + t(1258, 725, "드론 순찰 경로", 13))
    b.append(t(40, 800, "※ 개념도 — 실제 장비 위치·수량은 현장 구조와 크레인 배치에 따라 설계. 모든 센서는 엣지 AI 박스로 연결(유선/무선).", 12, 400, MUTED))
    return svg(W, H, b)


# ---------------------------------------------------------------- 2. 시스템 구성도
def architecture():
    W, H = 1440, 810
    b = [t(40, 46, "시스템 구성도", 26, 800),
         t(40, 72, "센서 → 현장 엣지(판단·경보) → 클라우드(관제·학습)", 15, 400, MUTED)]

    def pill(x, w, label, y=104):
        return f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="13" fill="{INK}"/>' + t(x + w / 2, y + 18, label, 13.5, 700, "#FFFFFF", "middle")

    b += [pill(40, 250, "① 현장 센서"), pill(340, 420, "② 현장 엣지 AI 박스"), pill(860, 540, "④ 클라우드 (관제·학습)")]

    sensors = [("상층부 전용 카메라", "60fps · 낙하 감지"), ("기존 현장 CCTV", "RTSP 재활용 · 작업자·구역"),
               ("크레인 후크캠·센서", "인양물 위치·선회각"), ("스마트 안전모 BLE 태그", "작업자 위치"),
               ("풍속계", "순간풍속"), ("점검 드론", "정기순찰 영상 · 사후 업로드")]
    for i, (n, d) in enumerate(sensors):
        y = 140 + i * 76
        drone = i == 5
        b.append(box(40, y, 250, 62, n, d, "blue", dashed=drone))
        b.append(arrow([(290, y + 31), (338, y + 31)], "gray", dashed=drone))

    # 엣지 박스
    b.append('<rect x="340" y="140" width="420" height="442" rx="16" fill="#F1F5FF" stroke="#1D4ED8" stroke-width="2"/>')
    b.append(t(550, 166, "Jetson Orin급 · IP66 함체 · LTE 이중화 · 단독 동작", 12.5, 600, "#1E3A8A", "middle"))
    b.append('<rect x="358" y="180" width="384" height="162" rx="10" fill="#FFFFFF" stroke="#93C5FD"/>')
    b.append(t(372, 202, "낙하 감지 파이프라인", 14, 700, "#1D4ED8"))
    for x, label in ((368, "움직임 후보"), (490, "소형객체 검출"), (612, "궤적 추적")):
        b.append(box(x, 216, 112, 40, label, kind="gray", rx=8))
    b += [arrow([(480, 236), (488, 236)]), arrow([(602, 236), (610, 236)]), arrow([(668, 256), (668, 280)])]
    b.append(box(612, 282, 120, 44, "물리 일관성 필터", kind="amber", rx=8))
    b.append(box(490, 282, 112, 44, "착지점 예측", kind="gray", rx=8))
    b.append(arrow([(612, 304), (604, 304)]))
    b.append(t(372, 299, "탄도 궤적 아니면 폐기", 11.5, 600, "#92400E"))
    b.append(t(372, 316, "(새·비닐·와이어)", 11.5, 400, MUTED))
    b.append('<rect x="358" y="352" width="384" height="72" rx="10" fill="#FFFFFF" stroke="#93C5FD"/>')
    b += [t(372, 374, "위험구역 엔진", 14, 700, "#1D4ED8"),
          t(372, 394, "인양물 투영 + 안전반경 → 동적 위험구역", 12.5, 400, "#334155"),
          t(372, 412, "상하 동시작업 감지 · 강풍 시 인양 중지", 12.5, 400, "#334155")]
    b.append('<rect x="358" y="434" width="384" height="56" rx="10" fill="#FFFFFF" stroke="#93C5FD"/>')
    b += [t(372, 456, "작업자 위치 융합", 14, 700, "#1D4ED8"), t(372, 476, "영상 사람 검출 + BLE 태그 위치", 12.5, 400, "#334155")]
    b.append('<rect x="358" y="502" width="384" height="64" rx="10" fill="#FEE2E2" stroke="#EF4444" stroke-width="2"/>')
    b += [t(372, 526, "경보 판단·등급", 14, 700, "#B91C1C"),
          t(372, 548, "(착지 반경 ∪ 위험구역) ∩ 작업자 → 등급별 경보", 12.5, 400, "#7F1D1D")]
    for y in (261, 388, 462):
        b.append(f'<line x1="742" y1="{y}" x2="752" y2="{y}" stroke="{COLORS["gray"]}" stroke-width="2"/>')
    b.append(f'<line x1="752" y1="261" x2="752" y2="534" stroke="{COLORS["gray"]}" stroke-width="2"/>')
    b.append(arrow([(752, 534), (744, 534)]))
    b.append(t(340, 606, "감지 → 경광등 종단 지연 목표 0.2~0.35초", 13.5, 700, "#B91C1C"))

    # 엣지 ↔ 클라우드
    b += [arrow([(760, 232), (858, 232)], "blue", dashed=True), t(810, 223, "이벤트·클립", 11.5, 600, "#1D4ED8", "middle"),
          t(810, 248, "(LTE)", 11.5, 400, "#1D4ED8", "middle"),
          arrow([(860, 372), (762, 372)], "green", dashed=True), t(810, 363, "모델 배포", 11.5, 600, "#15803D", "middle"),
          t(810, 389, "(OTA)", 11.5, 400, "#15803D", "middle")]

    # 클라우드
    b.append('<rect x="860" y="140" width="540" height="280" rx="16" fill="#F8FAFC" stroke="#64748B" stroke-width="2"/>')
    chips = [("이벤트 DB", "영상 클립·궤적·위치"), ("드론 영상 분석", "고소부 위험요소 리포트"),
             ("관제 대시보드", "웹 · 관리자 모바일 앱"), ("위험 히트맵", "공종·협력사·시간대 위험지수"),
             ("법정 증빙 자동화", "위험성평가·점검일지"), ("(확장) 금융 연계", "보험·PF 위험점수 API")]
    for i, (n, d) in enumerate(chips):
        x, y = (878, 1137)[i % 2], 156 + (i // 2) * 54
        b.append(box(x, y, 245, 46, n, d, "blue", dashed=i == 5, rx=8))
    b.append('<rect x="878" y="322" width="504" height="82" rx="8" fill="#FFF7E0" stroke="#F59E0B" stroke-width="2"/>')
    b.append(t(1130, 352, "학습 파이프라인", 14.5, 700, "#92400E", "middle"))
    b.append(t(1130, 378, "오탐·미탐 샘플 → 합성 데이터 보강 → 재학습·실측 평가 → 엣지 배포", 12.5, 400, "#92400E", "middle"))

    # 현장 경보 / 사용자
    b.append(t(860, 466, "③ 현장 경보 (엣지 직결)", 15, 800))
    for i, (n, d) in enumerate([("경광등·다국어 스피커", "구역 경보"), ("스마트 안전모 진동", "개인 경보"),
                                ("신호수·크레인 운전원", "인양 중지 알림")]):
        b.append(box(860, 478 + i * 58, 230, 50, n, d, "alert"))
    b.append(f'<line x1="760" y1="534" x2="822" y2="534" stroke="{COLORS["red"]}" stroke-width="3"/>')
    b.append(f'<line x1="822" y1="503" x2="822" y2="619" stroke="{COLORS["red"]}" stroke-width="3"/>')
    for y in (503, 561, 619):
        b.append(arrow([(822, y), (858, y)], "red", width=3))
    b.append(t(791, 526, "실시간", 12, 700, "#B91C1C", "middle"))

    b.append(t(1130, 466, "⑤ 사용자", 15, 800))
    b.append(arrow([(1265, 420), (1265, 450)], "blue"))
    for i, (n, d) in enumerate([("현장 안전관리자", "모바일 앱 · 조치·종결"), ("본사 안전팀", "다현장 통합관제"),
                                ("(확장) 보험사·금융기관", "위험점수 API")]):
        b.append(box(1130, 478 + i * 58, 270, 50, n, d, "blue", dashed=i == 2))

    # 범례 + 설계 원칙
    leg = [("gray", False, "센서 데이터"), ("red", False, "실시간 경보 (엣지 → 현장)"),
           ("blue", True, "클라우드 동기화"), ("green", True, "모델 배포 (OTA)")]
    for i, (c, d, label) in enumerate(leg):
        x, y = 40 + (i % 2) * 300, 712 + (i // 2) * 40
        b += [arrow([(x, y - 5), (x + 44, y - 5)], c, dashed=d, width=2.5), t(x + 56, y, label, 13.5)]
    b.append('<rect x="700" y="672" width="700" height="118" rx="14" fill="#0F172A"/>')
    b += [t(724, 702, "설계 원칙", 15, 800, "#FFFFFF"),
          t(724, 728, "1. 경보 판단은 엣지에서 — 통신이 끊겨도 경보는 울린다", 13.5, 400, "#E2E8F0"),
          t(724, 752, "2. 기존 CCTV 재활용 — 낙하 감지 구간만 전용 카메라 추가", 13.5, 400, "#E2E8F0"),
          t(724, 776, "3. 모든 이벤트(아차사고 포함)는 증빙·학습 데이터로 축적", 13.5, 400, "#E2E8F0")]
    return svg(W, H, b)


# ---------------------------------------------------------------- 3. 프로세스
def process():
    W, H = 1500, 905
    b = [t(40, 44, "운영 프로세스 — 3단 방어", 26, 800),
         t(40, 70, "예방(노출 차단) → 대응(실시간 경보) → 학습(기록·증빙·재학습)", 15, 400, MUTED)]
    # 범례
    b += ['<rect x="1080" y="38" width="26" height="18" rx="4" fill="#E53935"/>', t(1114, 52, "경보", 13),
          '<polygon points="1182,38 1196,47 1182,56 1168,47" fill="#FFF8E1" stroke="#F59E0B" stroke-width="2"/>', t(1204, 52, "판단", 13),
          '<rect x="1256" y="38" width="26" height="18" rx="4" fill="#FFFFFF" stroke="#64748B" stroke-width="2" stroke-dasharray="4 3"/>',
          t(1290, 52, "확장·피드백", 13)]

    def lane(y, h, fill, side, color, n, name, desc):
        cy = y + h / 2
        return (f'<rect x="30" y="{y}" width="1440" height="{h}" rx="14" fill="{fill}"/>'
                f'<rect x="30" y="{y}" width="170" height="{h}" rx="14" fill="{side}"/>'
                + t(115, cy - 16, n, 26, 800, color, "middle") + t(115, cy + 14, name, 20, 800, color, "middle")
                + t(115, cy + 38, desc, 13, 400, MUTED, "middle"))

    # 1단 예방
    b.append(lane(92, 255, "#EEF4FF", "#DCE7FF", "#1D4ED8", "1단", "예방", "노출 차단 · 작업 전/중"))
    for i, (n, d) in enumerate([("드론 정기순찰", "작업 전·점심·종료 후"), ("고소부 위험요소 탐지", "단부 자재·방지망·개구부"),
                                ("TBM 위험 리포트", "작업 전 공유·지시"), ("조치·사진 증빙", "관리자 앱으로 종결")]):
        b.append(box(230 + 200 * i, 130, 170, 56, n, d))
        if i:
            b.append(arrow([(200 + 200 * i, 158), (228 + 200 * i, 158)]))
    b.append(box(230, 242, 170, 56, "크레인 인양 시작", "후크캠·선회각 수신"))
    b.append(arrow([(400, 270), (428, 270)]))
    b.append(box(430, 242, 170, 56, "동적 위험구역 생성", "인양물 투영 + 안전반경"))
    b.append(arrow([(600, 270), (628, 270)]))
    b.append(diamond(705, 270, "구역 내", "작업자?"))
    b.append(arrow([(780, 270), (828, 270)], "red"))
    b.append(t(804, 262, "예", 12.5, 700, "#B91C1C", "middle"))
    b.append(box(830, 242, 170, 56, "구역 경보", "경광등·안전모 진동·신호수", "alert"))
    b.append(arrow([(705, 308), (705, 324), (515, 324), (515, 300)]))
    b.append(t(610, 340, "아니오 → 인양 중 계속 갱신", 12, 600, MUTED, "middle"))
    b.append(box(1060, 130, 390, 56, "상시 · 상하 동시작업 감지", "같은 수직선 위·아래 작업자 → 작업 조정 알림"))
    b.append(box(1060, 242, 390, 56, "상시 · 풍속계 강풍 감지", "인양 중지 · 고소 자재 결속 알림"))

    # 2단 대응
    b.append(lane(360, 295, "#FFF1F1", "#FFDEDE", "#C62828", "2단", "대응", "낙하 순간"))
    cy = 450
    for x, n, d in ((230, "움직임 후보", "배경차분"), (400, "소형객체 검출", "움직임 어텐션"), (570, "궤적 추적", "칼만·ByteTrack")):
        b.append(box(x, cy - 28, 150, 56, n, d, "redlane"))
    b += [arrow([(380, cy), (398, cy)]), arrow([(550, cy), (568, cy)]), arrow([(720, cy), (738, cy)])]
    b.append(diamond(815, cy, "중력 궤적", "일치?"))
    b += [arrow([(890, cy), (918, cy)]), t(904, cy - 8, "예", 12.5, 700, "#B91C1C", "middle")]
    b.append(box(920, cy - 28, 150, 56, "착지점 예측", "호모그래피+비산반경", "redlane"))
    b.append(arrow([(1070, cy), (1088, cy)]))
    b.append(diamond(1165, cy, "반경 내", "작업자?"))
    b += [arrow([(1240, cy), (1268, cy)], "red"), t(1254, cy - 8, "예", 12.5, 700, "#B91C1C", "middle")]
    b.append(box(1270, cy - 28, 180, 56, "즉시 대피 경보", "지정 방향 · 다국어 음성", "alert"))
    for x, n, d in ((815, "폐기", "새·비닐·와이어"), (1165, "아차사고 기록", "맞은 사람 없음 → 3단")):
        b += [arrow([(x, cy + 38), (x, 528)]), t(x + 8, 514, "아니오", 12, 600, MUTED),
              box(x - 75, 530, 150, 46, n, d, "gray", rx=8)]
    for x, s in ((305, "t ≈ 33ms"), (645, "t ≈ 133ms"), (995, "t ≈ 143ms"), (1360, "t ≈ 350ms 경광등 점등")):
        b.append(t(x, 498, s, 12, 600, "#9F1239", "middle"))
    b.append('<rect x="1270" y="530" width="180" height="80" rx="10" fill="#FFFFFF" stroke="#FCA5A5" stroke-width="2"/>')
    b += [t(1360, 554, "종단 지연 목표", 13, 700, "#B91C1C", "middle"), t(1360, 580, "0.2~0.35초", 20, 800, "#B91C1C", "middle"),
          t(1360, 600, "30m 낙하 = 2.47초", 12, 400, MUTED, "middle")]

    # 3단 학습
    b.append(lane(670, 222, "#EEF8F1", "#D6F0DE", "#1E7B45", "3단", "학습", "기록·증빙·재학습"))
    top = [("이벤트 기록", "1·2단 전 이벤트·영상"), ("관리자 확인·조치", "모바일 앱 → 종결"), ("위험 히트맵·지수", "공종·협력사·시간대"),
           ("법정 증빙 자동화", "위험성평가·점검일지"), ("(확장) 금융 연계", "보험·PF 위험점수")]
    for i, (n, d) in enumerate(top):
        b.append(box(230 + 200 * i, 697, 170, 56, n, d, "greenlane", dashed=i == 4))
        if i:
            b.append(arrow([(200 + 200 * i, 725), (228 + 200 * i, 725)], "gray", dashed=i == 4))
    b.append(arrow([(515, 753), (515, 780), (1115, 780), (1115, 795)], "green", dashed=True))
    b.append(t(815, 773, "오탐·미탐 표시", 12, 700, "#15803D", "middle"))
    bottom = [("엣지 배포", "OTA 업데이트"), ("실측 평가", "더미 낙하 평가세트"), ("재학습", "시나리오 랜덤화"),
              ("합성 데이터 보강", "3D 시뮬 + 실영상 합성"), ("오탐·미탐 샘플", "관리자 피드백")]
    for i, (n, d) in enumerate(bottom):
        b.append(box(230 + 200 * i, 797, 170, 56, n, d, "amber"))
        if i:
            b.append(arrow([(230 + 200 * i, 825), (402 + 200 * (i - 1), 825)], "green"))
    b.append(arrow([(230, 825), (212, 825), (212, cy), (228, cy)], "green", dashed=True, width=2.5))
    b.append(t(240, 600, "모델 갱신", 12, 700, "#15803D", "middle", 'transform="rotate(-90 240 600)"'))
    return svg(W, H, b)


if __name__ == "__main__":
    for name, fn in (("01-site-layout", site_layout), ("02-architecture", architecture), ("03-process", process)):
        path = OUT / f"{name}.svg"
        content = fn()
        path.write_text(content, encoding="utf-8")
        w, h = content.split('width="')[1].split('"')[0], content.split('height="')[1].split('"')[0]
        subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=2",
                        f"--window-size={w},{h}", f"--screenshot={OUT / (name + '.png')}", path.as_uri()],
                       check=True, capture_output=True)
        print("wrote", path.name, "+ png")
