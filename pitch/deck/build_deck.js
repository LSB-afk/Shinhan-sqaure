// 팀 GA · DropZero IR 피치덱 생성기 (15장: 공모전 사업소개서 15매 제한)
// 3D 렌더(render3d.py → post3d.py) 후 실행: node build_deck.js → DropZero_IR_팀GA.pptx
// 구성·UI는 수상작 레퍼런스의 체계를 따른다:
//   큰 장 번호(01) + 왼쪽 굵은 막대 + 작은 섹션 라벨 + 가로 구분선, 오른쪽 위 로고, 가운데 저작권 꼬리말
//   레이아웃 3종: 흰 바탕 / 위쪽 짙은 띠 / 왼쪽 회색 패널(2줄 헤드라인 + 제품 렌더)
//   부품: 굵기를 섞은 제목, 짙은 알약 라벨, 검은 번호 원, 둥근 회색 카드, 검은 머리줄 표, 해시태그
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const JSZip = require("jszip"); // pptxgenjs 의존성

// pptxgenjs가 못 하는 마무리를 저장 후 XML에서 한다.
// - 테마 색 구성표를 THEME 색으로
// - 테마의 동아시아(한글) 글꼴을 Pretendard로 (비어 있으면 맑은 고딕으로 대체됨)
// - 모든 문단에 eaLnBrk="0": 한글 단어가 중간에서 잘리지 않게(어절 단위 줄바꿈)
// - 차트 글자에도 한글 글꼴 지정
async function applyTheme(file, theme) {
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const edit = async (name, fn) => zip.file(name, fn(await zip.file(name).async("string")));
  const keys = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink"];
  const scheme = `<a:clrScheme name="${theme.name}">` + keys.map(k => `<a:${k}><a:srgbClr val="${theme.colors[k]}"/></a:${k}>`).join("") + "</a:clrScheme>";
  await edit("ppt/theme/theme1.xml", x => x
    .replace(/<a:clrScheme[\s\S]*?<\/a:clrScheme>/, scheme)
    .replace(/<a:ea typeface=""\/>/g, `<a:ea typeface="${theme.bodyFontFace}"/>`)
    .replace(/<a:font script="Hang" typeface="[^"]*"\/>/g, `<a:font script="Hang" typeface="${theme.bodyFontFace}"/>`));
  for (const name of Object.keys(zip.files)) {
    if (/^ppt\/(slides|slideLayouts|slideMasters)\/[^/]+\.xml$/.test(name)) {
      await edit(name, x => x
        .replace(/<a:pPr(?![^>]*eaLnBrk)/g, '<a:pPr eaLnBrk="0"')
        .replace(/<a:p>(?!<a:pPr)/g, '<a:p><a:pPr eaLnBrk="0"/>')
        .replace(/lang="en-US"/g, 'lang="ko-KR"'));
    } else if (/^ppt\/charts\/chart[^/]*\.xml$/.test(name)) {
      await edit(name, x => x.replace(/<a:latin typeface="(\+mn-lt|Arial)"\/>(?!<a:ea)/g, '<a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/>'));
    }
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

const A = f => path.join(__dirname, "assets", f);
const OUT = path.join(__dirname, "DropZero_IR_팀GA.pptx");

const THEME = {
  name: "DropZero",
  headFontFace: "Pretendard",
  bodyFontFace: "Pretendard",
  colors: {
    dk1: "1B1D21", lt1: "FFFFFF", dk2: "2E2F31", lt2: "F2F3F4",
    accent1: "FF5A1F", accent2: "8A9099", accent3: "4A4F57", accent4: "D2D4D7", accent5: "2B2F35", accent6: "E5E7EA",
    hlink: "FF5A1F", folHlink: "8A9099",
  },
};
const LIGHT_FONT = "Pretendard Light";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "DropZero IR 피치덱";
pres.author = "팀 GA (이승보, 이성재, 장재홍)";
const C = pres.SchemeColor;
const K = {
  ink: C.text1, band: C.text2, white: C.background1, paper: C.background2, orange: C.accent1,
  g5: C.accent2, g7: C.accent3, rule: C.accent4, g8: C.accent5, g2: C.accent6,
};
const HEX = THEME.colors;
const W = 13.333, L = 0.9, R = 12.43, BAND = 2.6, PANEL = 4.7;
const COPY = "Copyright © 2026 Team GA. All Rights Reserved.";

// ---------------------------------------------------------------- 레이아웃 (장 번호·섹션 라벨·제목은 자리표시자)
const footer = (c) => ({ text: { text: COPY, options: { x: 0, y: 7.08, w: W, h: 0.25, fontSize: 8.5, color: c, align: "center", margin: 0 } } });
const logo = (c) => ({ text: { text: "DropZero", options: { x: 10.9, y: 0.3, w: 1.9, h: 0.32, fontSize: 13, bold: true, color: c, align: "right", margin: 0, charSpacing: 1 } } });
const num = (c) => ({ placeholder: { options: { name: "num", type: "body", x: 0.5, y: 0.2, w: 0.85, h: 0.5, fontSize: 26, bold: true, color: c, margin: 0, align: "left", valign: "bottom" }, text: "" } });
const label = (c, x = 1.55, w = 8) => ({ placeholder: { options: { name: "label", type: "body", x, y: 0.43, w, h: 0.28, fontSize: 12, color: c, margin: 0, align: "left", valign: "bottom" }, text: "" } });
const bar = (c) => ({ rect: { x: 0, y: 0.74, w: 1.35, h: 0.07, fill: { color: c }, line: { color: c, width: 0 } } });
const rule = (x) => ({ line: { x, y: 0.775, w: W - x, h: 0, line: { color: K.rule, width: 0.75 } } });
const slideNo = (c) => ({ x: 12.35, y: 7.08, w: 0.5, h: 0.25, fontSize: 8.5, color: c, align: "right" });

pres.defineSlideMaster({
  title: "LIGHT", background: { color: K.white },
  objects: [bar(K.ink), rule(1.35), logo(K.g5), footer(K.g5), num(K.ink), label(K.g7),
    { placeholder: { options: { name: "title", type: "title", x: 1.55, y: 1.0, w: 11, h: 0.7, fontSize: 28, color: K.ink, margin: 0, align: "left", valign: "top" }, text: "" } }],
  slideNumber: slideNo(K.g5),
});
pres.defineSlideMaster({
  title: "BAND", background: { color: K.white },
  objects: [{ rect: { x: 0, y: 0, w: W, h: BAND, fill: { color: K.band }, line: { color: K.band, width: 0 } } },
    bar(K.white), logo(K.rule), footer(K.g5), num(K.white), label(K.rule),
    { placeholder: { options: { name: "title", type: "title", x: 1.55, y: 0.95, w: 11, h: 0.7, fontSize: 28, color: K.white, margin: 0, align: "left", valign: "top" }, text: "" } },
    { placeholder: { options: { name: "desc", type: "body", x: 1.55, y: 1.7, w: 10.5, h: 0.65, fontSize: 12.5, color: K.rule, margin: 0, align: "left", valign: "top", lineSpacingMultiple: 1.2 }, text: "" } }],
  slideNumber: slideNo(K.g5),
});
pres.defineSlideMaster({
  title: "PANEL", background: { color: K.white },
  objects: [{ rect: { x: 0, y: 0, w: PANEL, h: 7.5, fill: { color: K.paper }, line: { color: K.paper, width: 0 } } },
    bar(K.ink), rule(PANEL), logo(K.g5), footer(K.g5), num(K.ink), label(K.g7, 1.55, 3.0),
    { placeholder: { options: { name: "headline", type: "title", x: 0.55, y: 1.2, w: 3.9, h: 1.55, fontSize: 32, color: K.ink, margin: 0, align: "left", valign: "top", lineSpacingMultiple: 1.05 }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: 0.58, y: 2.85, w: 3.8, h: 0.3, fontSize: 12, color: K.g5, margin: 0, align: "left" }, text: "" } }],
  slideNumber: slideNo(K.g5),
});
pres.defineSlideMaster({ title: "DARK", background: { color: "1E2023" }, objects: [footer(K.g7)] });

// ---------------------------------------------------------------- 부품
// "**굵게**" 표시가 있는 문장을 가는 글씨 + 굵은 강조어 런으로 바꾼다
function mixed(text, o = {}) {
  return text.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map(t => t.startsWith("**")
    ? { text: t.slice(2, -2), options: { bold: true, fontFace: "Pretendard", ...o } }
    : { text: t, options: { fontFace: LIGHT_FONT, ...o } });
}
function slide(master, section, n, lbl, title, extra = {}) {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  s.addText(n, { placeholder: "num" });
  s.addText(lbl, { placeholder: "label" });
  if (master === "PANEL") {
    s.addText([{ text: title[0], options: { bold: true, fontFace: "Pretendard", breakLine: true } }, { text: title[1], options: { fontFace: LIGHT_FONT } }], { placeholder: "headline" });
    if (extra.sub) s.addText(extra.sub, { placeholder: "sub" });
  } else {
    s.addText(mixed(title), { placeholder: "title" });
    if (extra.desc) s.addText(extra.desc, { placeholder: "desc" });
  }
  return s;
}
const T = (s, text, o) => s.addText(text, { isTextBox: true, margin: 0, color: K.ink, fontSize: 13, valign: "top", ...o });
const source = (s, text, y = 6.78) => T(s, text, { x: L, y, w: R - L, h: 0.25, fontSize: 8.5, color: K.g5 });
const rect = (s, x, y, w, h, fill, o = {}) => s.addShape(o.round ? pres.ShapeType.roundRect : pres.ShapeType.rect,
  { x, y, w, h, fill: { color: fill }, line: o.line || { color: fill, width: 0 }, ...(o.round ? { rectRadius: o.round } : {}) });
const card = (s, x, y, w, h) => rect(s, x, y, w, h, K.paper, { round: 0.12, line: { color: K.g2, width: 0.75 } });
const dot = (s, x, y, d, color) => s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color }, line: { color, width: 0 } });
function pill(s, x, y, w, text, o = {}) {
  const h = o.h || 0.32, fill = o.fill || K.ink;
  rect(s, x, y, w, h, fill, { round: h / 2, line: o.line });
  T(s, text, { x, y, w, h, fontSize: o.fs || 11, bold: true, color: o.color || K.white, align: "center", valign: "middle" });
}
function numCircle(s, x, y, n, d = 0.36, fill = K.ink) {
  dot(s, x, y, d, fill);
  T(s, String(n), { x, y, w: d, h: d, fontSize: 12, bold: true, color: K.white, align: "center", valign: "middle" });
}
function arrow(s, x1, y1, x2, y2, color = K.g7, o = {}) {
  s.addShape(pres.ShapeType.line, {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1,
    line: { color, width: o.width || 1.25, endArrowType: "triangle", dashType: o.dash ? "dash" : "solid" },
  });
}
// 검은 머리줄 표 (레퍼런스의 사양표 형식)
function table(s, x, y, colW, head, rows, o = {}) {
  const none = { type: "none" }, line = { type: "solid", pt: 0.75, color: HEX.accent4 };
  const hd = head.map(h => ({ text: h, options: { bold: true, color: HEX.lt1, fill: { color: HEX.dk1 }, align: "center", valign: "middle", fontSize: o.hfs || 12, border: [none, none, none, none] } }));
  const body = rows.map(r => r.map((c, j) => ({ text: c, options: { bold: j === 0, color: j === 0 ? HEX.dk1 : HEX.accent3, align: j === 0 ? "center" : "left", valign: "middle", fontSize: o.fs || 11.5, border: [none, none, line, none] } })));
  s.addTable([hd, ...body], { x, y, w: colW.reduce((a, b) => a + b, 0), colW, rowH: o.rowH || 0.5, margin: [0.04, 0.12, 0.04, 0.12], valign: "middle" });
}

// ---------------------------------------------------------------- 1. 표지
pres.addSection({ title: "표지" });
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "표지" });
  s.addImage({ path: A("cover-3d.png"), x: 0, y: 0, w: W, h: 7.5 });
  T(s, "건설현장 낙하물 사고 예방을 위한", { x: 0.75, y: 0.95, w: 6, h: 0.3, fontSize: 13, color: K.rule });
  T(s, [{ text: "AI 낙하물 안전 관제", options: { fontSize: 40, bold: true, breakLine: true } }, { text: "DropZero", options: { fontSize: 58, bold: true } }],
    { x: 0.75, y: 1.3, w: 7, h: 1.9, color: K.white, lineSpacingMultiple: 1.0 });
  T(s, [{ text: "건설현장 낙하물 사고, ", options: { color: K.white } }, { text: " 맞기 전에 ", options: { color: K.white, highlight: HEX.accent1, bold: true } }, { text: " 막습니다", options: { color: K.white } }],
    { x: 0.75, y: 5.75, w: 6.5, h: 0.35, fontSize: 15 });
  T(s, [{ text: "팀 GA   ", options: { bold: true, color: K.white } }, { text: "이승보 · 이성재 · 장재홍", options: { color: K.rule } }], { x: 0.75, y: 6.22, w: 6.5, h: 0.3, fontSize: 12 });
  T(s, "2026 신한 스퀘어브릿지 대학생 창업 공모전 HERO IR", { x: 0.75, y: 6.6, w: 6.5, h: 0.28, fontSize: 10.5, color: K.g5 });
}

// ---------------------------------------------------------------- 01 시장·사업성 검토
const S1 = "01 시장·사업성 검토";
pres.addSection({ title: S1 });
{ // 2. 문제
  const s = slide("BAND", S1, "01", "시장·사업성 검토", "지난해 건설 현장에서 **286명**이 일하다 숨졌습니다",
    { desc: "2025년 산업현장 사고사망자 605명 중 47%가 건설업에서 나왔습니다.\n날아오거나 떨어진 물체에 맞은 사고(물체에 맞음)는 사망 원인 2위입니다." });
  const y = 3.0, h = 3.55;
  T(s, "건설업 사고사망", { x: L, y, w: 3.4, h: 0.35, fontSize: 16, bold: true });
  T(s, ": 전 산업의 절반 가까이", { x: L, y: y + 0.36, w: 3.4, h: 0.28, fontSize: 11.5, color: K.g7 });
  card(s, L, y + 0.8, 3.4, h - 0.8);
  T(s, [{ text: "286", options: { fontSize: 60, bold: true } }, { text: "명", options: { fontSize: 24, bold: true } }], { x: L + 0.35, y: y + 1.15, w: 2.9, h: 1.0 });
  T(s, "2025년 건설업 재해조사 대상 사고사망자", { x: L + 0.35, y: y + 2.2, w: 2.9, h: 0.3, fontSize: 11.5, color: K.g7 });
  T(s, "전년 대비 +3.6% · 전 산업 605명 중 47%", { x: L + 0.35, y: y + 2.55, w: 2.9, h: 0.3, fontSize: 11.5, bold: true, color: K.ink });

  T(s, "사고사망 발생 형태", { x: 4.65, y, w: 4.6, h: 0.35, fontSize: 16, bold: true });
  T(s, ": 물체에 맞음 72명, 떨어짐 다음으로 많습니다", { x: 4.65, y: y + 0.36, w: 4.6, h: 0.28, fontSize: 11.5, color: K.g7 });
  card(s, 4.65, y + 0.8, 4.6, h - 0.8);
  const cats = ["무너짐", "부딪힘", "물체에 맞음", "떨어짐"];
  s.addChart(pres.ChartType.bar, [
    { name: "물체에 맞음", labels: cats, values: [0, 0, 72, 0] },
    { name: "그 외", labels: cats, values: [38, 62, 0, 249] },
  ], {
    x: 4.8, y: y + 0.95, w: 4.3, h: h - 1.1, barDir: "bar", barGrouping: "stacked", barGapWidthPct: 55,
    chartColors: [HEX.accent1, HEX.accent2], showLegend: false,
    showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: "#,##0;;;", dataLabelFontSize: 12, dataLabelColor: HEX.lt1, dataLabelFontFace: "+mn-lt", dataLabelFontBold: true,
    catAxisLabelColor: HEX.accent3, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", catAxisLineShow: false,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  });
  arrow(s, 9.45, y + 2.2, 9.85, y + 2.2, K.g7);
  pill(s, 10.0, y + 0.85, 2.43, "KEY IMPLICATIONS");
  [["물체에 맞음 72명", "사망 원인 2위 (전 산업)"], ["낙하물 전담 솔루션 부재", "기존 AI CCTV는 안전모·침입 위주"]].forEach(([a, b], i) => {
    rect(s, 10.0, y + 1.35 + i * 1.12, 2.43, 1.0, K.paper);
    T(s, a, { x: 10.1, y: y + 1.5 + i * 1.12, w: 2.23, h: 0.3, fontSize: 12.5, bold: true, align: "center" });
    T(s, b, { x: 10.1, y: y + 1.85 + i * 1.12, w: 2.23, h: 0.3, fontSize: 10.5, color: K.g7, align: "center" });
  });
  source(s, "출처: 고용노동부 「2025년 재해조사 대상 사망사고 발생 현황」(2026. 3.), 연합뉴스 2026. 3. 31. 보도 재인용");
}
{ // 3. 2.47초
  const s = slide("LIGHT", S1, "01", "시장·사업성 검토 · 현장의 한계", "30m에서 떨어진 공구는 **2.47초** 만에 바닥에 닿습니다");
  const fx = L, fy = 1.95, fw = 3.9, fh = 4.333;
  s.addImage({ path: A("fall-3d.png"), x: fx, y: fy, w: fw, h: fh });
  const FP = JSON.parse(fs.readFileSync(A("fall-3d.json")));
  for (const [k, lbl, hl] of [["t2", "1.0초", 0], ["t3", "1.5초", 0], ["t4", "2.0초", 0], ["t5", "2.47초 · 바닥", 1]]) {
    const [px, py] = FP[k];
    T(s, lbl, { x: fx + px * fw + 0.05, y: fy + py * fh - 0.13, w: 1.4, h: 0.26, fontSize: 11.5, bold: true, color: hl ? K.orange : K.g8 });
  }
  const pts = [
    ["보고 피하기엔 짧습니다", "경보를 듣고 판단해 1~2m 피하는 데 1.5~2.5초가 걸립니다. 17m보다 낮은 곳에서 떨어지면 경보만으로는 막을 수 없습니다."],
    ["누가 아래에 있는지 모릅니다", "인양 중 하부 출입 통제는 신호수 한 사람의 눈에 달려 있습니다. 크레인이 움직이면 위험한 자리도 같이 바뀝니다."],
    ["다치지 않으면 기록이 없습니다", "사람이 맞지 않은 낙하는 보고되지 않습니다. 어느 현장이 위험한지 미리 가려낼 데이터가 쌓이지 않습니다."],
  ];
  pts.forEach(([h, b], i) => {
    const y = 2.1 + i * 1.38;
    numCircle(s, 5.4, y, i + 1);
    T(s, h, { x: 5.95, y: y - 0.02, w: 6.4, h: 0.4, fontSize: 18, bold: true });
    T(s, b, { x: 5.95, y: y + 0.42, w: 6.4, h: 0.85, fontSize: 13, color: K.g7, lineSpacingMultiple: 1.2 });
  });
  pill(s, 5.4, 6.18, 0.9, "POINT", { fill: K.orange, h: 0.3, fs: 10.5 });
  T(s, "경보보다 먼저, 떨어질 물건 아래에 사람이 없게 해야 합니다.", { x: 6.45, y: 6.18, w: 6, h: 0.3, fontSize: 12, bold: true, valign: "middle" });
}
{ // 4. 시장 규모
  const s = slide("BAND", S1, "01", "시장·사업성 검토 · 시장 규모", "국내 스마트 안전장비 예산 한도는 연 **7,430억 원**입니다",
    { desc: "건설사는 산업안전보건관리비의 20%까지 스마트 안전장비에 쓸 수 있습니다.\n해외 건설현장 안전 모니터링 시장은 2025년 3.7조 원에서 2030년 6.4조 원으로 커질 전망입니다." });
  const y = 3.0, h = 3.55;
  T(s, "국내 시장", { x: L, y, w: 4.3, h: 0.35, fontSize: 16, bold: true });
  T(s, ": TAM · SAM · SOM", { x: L, y: y + 0.36, w: 4.3, h: 0.28, fontSize: 11.5, color: K.g7 });
  card(s, L, y + 0.8, 4.3, h - 0.8);
  const cx = L + 1.35, base = y + h - 0.2;
  const ring = (d, fill, line) => s.addShape(pres.ShapeType.ellipse, { x: cx - d / 2, y: base - d, w: d, h: d, fill: { color: fill }, line: { color: line, width: 0.75 } });
  ring(2.45, K.white, K.rule); ring(1.6, K.g2, K.rule); ring(0.7, K.orange, K.orange);
  T(s, "TAM", { x: cx - 0.5, y: base - 2.33, w: 1, h: 0.2, fontSize: 9, bold: true, color: K.g5, align: "center" });
  T(s, "SAM", { x: cx - 0.5, y: base - 1.5, w: 1, h: 0.2, fontSize: 9, bold: true, color: K.g7, align: "center" });
  T(s, "SOM", { x: cx - 0.5, y: base - 0.45, w: 1, h: 0.2, fontSize: 8.5, bold: true, color: K.white, align: "center" });
  [["3.7조 원", "글로벌 건설현장 안전 모니터링 (2025)"], ["7,430억 원", "국내 산안비 중 스마트 장비 한도 (연)"], ["60억 원", "5년 차 목표 · 200개 현장 × 월 250만 원"]].forEach(([v, d], i) => {
    const yy = y + 1.0 + i * 0.78;
    T(s, v, { x: L + 2.75, y: yy, w: 1.5, h: 0.32, fontSize: 15, bold: true, color: i === 2 ? K.orange : K.ink });
    T(s, d, { x: L + 2.75, y: yy + 0.32, w: 1.5, h: 0.42, fontSize: 9, color: K.g7 });
  });

  T(s, "글로벌 시장", { x: 5.5, y, w: 4.0, h: 0.35, fontSize: 16, bold: true });
  T(s, ": 단위 조 원, 2024~25년 → 2030년", { x: 5.5, y: y + 0.36, w: 4.0, h: 0.28, fontSize: 11.5, color: K.g7 });
  card(s, 5.5, y + 0.8, 4.0, h - 0.8);
  s.addChart(pres.ChartType.bar, [
    { name: "2024~25년", labels: ["안전 모니터링", "건설 AI", "건설 드론"], values: [3.73, 6.84, 6.35] },
    { name: "2030년", labels: ["안전 모니터링", "건설 AI", "건설 드론"], values: [6.37, 20.3, 9.8] },
  ], {
    x: 5.6, y: y + 0.9, w: 3.8, h: h - 1.0, barDir: "col", barGrouping: "clustered", barGapWidthPct: 60,
    chartColors: [HEX.accent4, HEX.accent1], showLegend: true, legendPos: "t", legendFontSize: 10, legendFontFace: "+mn-lt", legendColor: HEX.accent3,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelFontSize: 10, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt", dataLabelFontBold: true,
    catAxisLabelColor: HEX.accent3, catAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  });
  arrow(s, 9.68, y + 2.2, 9.95, y + 2.2, K.g7);
  pill(s, 10.08, y + 0.85, 2.35, "KEY IMPLICATIONS");
  [["단가는 산안비 한도 안", "300억 원 현장 한도 월 약 330만 원"], ["싱가포르 영상감시 의무화", "S$500만 이상 현장 · 2024. 6."], ["미국 struck-by 사망 2위", "건설 4대 위험 · 2023년 154명"]].forEach(([a, b], i) => {
    rect(s, 10.08, y + 1.3 + i * 0.75, 2.35, 0.66, K.paper);
    T(s, a, { x: 10.15, y: y + 1.36 + i * 0.75, w: 2.2, h: 0.26, fontSize: 11, bold: true, align: "center" });
    T(s, b, { x: 10.15, y: y + 1.63 + i * 0.75, w: 2.2, h: 0.24, fontSize: 9, color: K.g7, align: "center" });
  });
  source(s, "출처: 건설산업연구원(2026. 4.), 고용노동부고시 제2024-53호·제2025-11호, Research and Markets·Mordor Intelligence(2025), MOM, CPWR · SAM = 건설수주 221.1조 × 70% × 요율 2.4% × 20%");
}

// ---------------------------------------------------------------- 02 규제·제도 요건 분석
const S2 = "02 규제·제도 요건 분석";
pres.addSection({ title: S2 });
{ // 5. 제도 요건
  const s = slide("LIGHT", S2, "02", "규제·제도 요건 분석", "법과 예산이 **스마트 안전장비** 도입을 밀어주고 있습니다");
  const rows = [
    ["기회", "건설업 산업안전보건관리비\n계상·사용기준 (고시 제2024-53호 등)", "스마트 안전장비 구입·임대비 2026년부터 100% 인정, 사용한도 산안비의 20%. 요율 평균 19% 인상", "구독·렌탈 비용을 산안비로 처리하는 가격 구조"],
    ["기회", "건설기술 진흥법 시행규칙", "16층 이상 공동주택 공사장 CCTV 설치 의무 (2020. 12.~)", "기존 CCTV에 분석을 얹어 도입비 절감"],
    ["기회", "중대재해 처벌 등에 관한 법률", "2024년부터 5인 이상 사업장 전면 적용, 안전보건관리체계 구축·이행 의무", "이벤트·조치 기록으로 이행 증빙 자동 생성"],
    ["준수", "항공안전법 (드론)", "관제권·비행금지구역 비행승인, 야간·가시권 밖 비행은 특별비행승인", "작업자 없는 시간대 정기 순찰, 승인 절차를 운영 매뉴얼에 포함"],
    ["준수", "개인정보 보호법", "영상정보처리기기 설치 목적·장소 고지, 목적 외 이용 제한", "얼굴 비식별화, 보존기간 제한, 촬영 고지"],
    ["준수", "전파법 (KC 적합성평가)", "무선 기기 적합성평가 필요", "초기엔 KC 인증 기성 모듈, 자체 하드웨어는 2단계에서 인증"],
  ];
  table(s, L, 1.95, [0.9, 3.2, 4.25, 3.18], ["구분", "근거", "핵심 내용", "DropZero 대응"], rows, { rowH: [0.45, 0.72, 0.62, 0.66, 0.66, 0.6, 0.6], fs: 11 });
  pill(s, L, 6.4, 0.9, "POINT", { fill: K.orange, h: 0.3, fs: 10.5 });
  T(s, "기회 요인 세 가지는 가격과 영업 근거로, 준수 요인 세 가지는 운영 수칙으로 반영했습니다.", { x: L + 1.05, y: 6.4, w: 10, h: 0.3, fontSize: 12.5, bold: true, valign: "middle" });
}

// ---------------------------------------------------------------- 03 제품·기술 실행방안
const S3 = "03 제품·기술 실행방안";
pres.addSection({ title: S3 });
{ // 6. 솔루션 개요
  const s = slide("LIGHT", S3, "03", "제품·기술 실행방안 · 솔루션", "떨어질 물건 아래에 **사람이 서 있지 않게** 합니다");
  const ix = L, iy = 1.95, iw = 7.6, ih = 4.275;
  s.addImage({ path: A("solution-3d.png"), x: ix, y: iy, w: iw, h: ih });
  const SP = JSON.parse(fs.readFileSync(A("solution-3d.json")));
  [["zone", 1], ["fall", 2], ["drone", 3]].forEach(([key, n]) => numCircle(s, ix + SP[key][0] * iw + 0.1, iy + SP[key][1] * ih - 0.46, n));
  [["예방", "Dynamic Zone", "인양물 아래 위험구역이 크레인을 따라 움직이고, 사람이 들어오면 바로 경보가 울립니다."],
   ["대응", "Fall Detection", "물체가 떨어지는 순간을 감지해 0.35초 안에 착지 예상 지점 주변에 대피 경보를 보냅니다."],
   ["학습", "Near-miss Data", "드론 순찰 결과와 모든 낙하 기록을 쌓아 위험한 현장과 시간대를 미리 가려냅니다."]].forEach(([h, en, b], i) => {
    const y = 2.0 + i * 1.42;
    numCircle(s, 8.85, y, i + 1);
    T(s, [{ text: h + "  ", options: { bold: true, fontSize: 18 } }, { text: en, options: { fontSize: 11, color: K.g5 } }], { x: 9.35, y: y - 0.02, w: 3.1, h: 0.4 });
    T(s, b, { x: 9.35, y: y + 0.42, w: 3.08, h: 0.95, fontSize: 12, color: K.g7, lineSpacingMultiple: 1.2 });
  });
}
{ // 7. 예방
  const s = slide("PANEL", S3, "03", "핵심 기능 ① 예방", ["움직이는,", "위험구역"], { sub: "Dynamic Exclusion Zone" });
  [["인양물 위치 계산", "후크 카메라와 선회각·반경 데이터로 매달린 자재 위치를 잡습니다."],
   ["위험구역 생성", "떨어질 수 있는 바닥 범위에 안전 여유를 더하고, 크레인이 움직일 때마다 다시 그립니다."],
   ["진입 즉시 경보", "경광등, 안전모 진동, 신호수 단말이 동시에 울립니다."]].forEach(([h, b], i) => {
    const y = 3.55 + i * 1.08;
    numCircle(s, 0.58, y, i + 1, 0.32);
    T(s, h, { x: 1.05, y: y - 0.02, w: 3.3, h: 0.32, fontSize: 14, bold: true });
    T(s, b, { x: 1.05, y: y + 0.32, w: 3.35, h: 0.62, fontSize: 11, color: K.g7, lineSpacingMultiple: 1.15 });
  });
  s.addImage({ path: A("zone-3d.png"), x: R - 6.25, y: 1.15, w: 6.25, h: 5.0 });
  pill(s, R - 6.25, 6.38, 0.9, "POINT", { fill: K.orange, h: 0.3, fs: 10.5 });
  T(s, "높이와 상관없이 작동해, 경보로 피할 시간이 없는 저층 인양도 막습니다.", { x: R - 6.25 + 1.05, y: 6.38, w: 5.3, h: 0.3, fontSize: 11, bold: true, valign: "middle" });
}
{ // 8. 대응
  const s = slide("LIGHT", S3, "03", "핵심 기능 ② 대응", "떨어지는 순간을 **0.35초** 안에 잡아 경보를 울립니다");
  const x0 = L, x1 = R, sc = (x1 - x0) / 2.47;
  T(s, "30m 높이에서 떨어진 물체가 바닥에 닿기까지 2.47초", { x: x0, y: 2.0, w: 8, h: 0.3, fontSize: 13, color: K.g7 });
  rect(s, x0, 2.42, 0.35 * sc, 0.6, K.orange);
  rect(s, x0 + 0.35 * sc, 2.42, (2.47 - 0.35) * sc, 0.6, K.g8);
  T(s, "감지 · 경보  0.35초", { x: x0 + 0.12, y: 2.42, w: 2.2, h: 0.6, fontSize: 12.5, bold: true, color: K.white, valign: "middle" });
  T(s, "대피할 수 있는 시간  약 2.1초", { x: x0 + 0.35 * sc + 0.25, y: 2.42, w: 5, h: 0.6, fontSize: 14, bold: true, color: K.white, valign: "middle" });
  for (const t of [0, 0.5, 1.0, 1.5, 2.0, 2.47]) {
    const x = x0 + t * sc;
    s.addShape(pres.ShapeType.line, { x, y: 3.05, w: 0, h: 0.1, line: { color: K.g5, width: 0.75 } });
    T(s, t === 0 ? "0초" : `${t}초`, { x: x - 0.4, y: 3.18, w: 0.8, h: 0.22, fontSize: 10, color: K.g5, align: "center" });
  }
  const steps = ["움직임 후보", "소형 객체 검출", "궤적 추적", "중력 궤적 검증", "착지점 예측", "경보"];
  const sw = (R - L + 0.2) / 6;
  steps.forEach((st, i) => {
    const hl = i === 3, x = x0 + i * (sw - 0.04);
    s.addShape(i === 0 ? pres.ShapeType.homePlate : pres.ShapeType.chevron, { x, y: 3.85, w: sw, h: 0.6, fill: { color: hl ? K.ink : K.paper }, line: { color: hl ? K.ink : K.g2, width: 0.75 } });
    T(s, st, { x: x + 0.22, y: 3.85, w: sw - 0.45, h: 0.6, fontSize: 12, bold: true, align: "center", valign: "middle", color: hl ? K.white : K.ink });
  });
  [["오경보 거르기", "움직임이 중력가속도(9.8m/s²)에 맞게 빨라지는지 확인합니다. 새, 비닐, 흔들리는 와이어는 여기서 걸러집니다."],
   ["현장에서 바로 판단", "엣지 박스가 직접 경광등을 울립니다. 현장 통신이 끊겨도 경보는 나갑니다."]].forEach(([h, b], i) => {
    const x = x0 + i * 5.93;
    card(s, x, 4.85, 5.6, 1.6);
    numCircle(s, x + 0.3, 5.1, i + 1, 0.32);
    T(s, h, { x: x + 0.75, y: 5.08, w: 4.6, h: 0.36, fontSize: 15, bold: true });
    T(s, b, { x: x + 0.75, y: 5.5, w: 4.65, h: 0.85, fontSize: 12, color: K.g7, lineSpacingMultiple: 1.2 });
  });
}
{ // 9. 학습
  const s = slide("PANEL", S3, "03", "핵심 기능 ③ 학습", ["다치지 않은", "낙하까지 기록"], { sub: "Near-miss Data · Drone Patrol" });
  T(s, "작업 전 · 점심 · 작업 종료 후 드론 순찰", { x: 0.58, y: 3.5, w: 3.9, h: 0.32, fontSize: 13.5, bold: true });
  T(s, "단부 자재 적치, 낙하물방지망 파손, 개구부 덮개 누락을 찾아 아침 TBM 전에 알려줍니다.", { x: 0.58, y: 3.85, w: 3.85, h: 0.65, fontSize: 11, color: K.g7, lineSpacingMultiple: 1.15 });
  s.addImage({ path: A("drone-3d.png"), x: 0.2, y: 4.45, w: 4.3, h: 2.676 });
  const cx = 5.3, cy = 1.25, cw = 7.13, ch = 5.2;
  rect(s, cx, cy, cw, ch, K.white, { round: 0.06, line: { color: K.g2, width: 1 } });
  T(s, "현장 안전 리포트", { x: cx + 0.4, y: cy + 0.3, w: 3, h: 0.35, fontSize: 15, bold: true });
  pill(s, cx + cw - 1.45, cy + 0.32, 1.05, "화면 예시", { fill: K.paper, color: K.g7, h: 0.28, fs: 9.5 });
  [["12", "오늘 이벤트", K.ink], ["3", "아차사고", K.orange], ["100%", "조치 완료", K.ink]].forEach(([n, l, c], i) => {
    const x = cx + 0.4 + i * 2.15;
    rect(s, x, cy + 0.85, 2.0, 1.2, K.paper, { round: 0.08 });
    T(s, n, { x: x + 0.22, y: cy + 0.95, w: 1.6, h: 0.55, fontSize: 26, bold: true, color: c });
    T(s, l, { x: x + 0.22, y: cy + 1.55, w: 1.6, h: 0.3, fontSize: 10.5, color: K.g5 });
  });
  table(s, cx + 0.4, cy + 2.3, [1.0, 3.95, 1.38], ["시각", "이벤트", "상태"],
    [["14:02", "낙하 감지 · 12층 동측", "아차사고"], ["10:15", "위험구역 진입 · 크레인 1호", "경보"], ["07:12", "드론 순찰 · 9층 방지망 파손", "조치 완료"]], { rowH: 0.42, fs: 11, hfs: 11 });
  rect(s, cx + 0.4, cy + ch - 0.72, cw - 0.8, 0.45, K.paper, { round: 0.1 });
  T(s, "위험성평가 개선 이력 · 점검일지 자동 생성  →  중대재해처벌법 대응 증빙", { x: cx + 0.6, y: cy + ch - 0.72, w: cw - 1.2, h: 0.45, fontSize: 11.5, color: K.g8, valign: "middle" });
}
{ // 10. 합성 데이터
  const s = slide("LIGHT", S3, "03", "기술 구현 · 학습 데이터", "사고 영상이 없어도 **학습 데이터**를 직접 만듭니다");
  [["sim-3d.png", "3D 물리 시뮬레이션", "높이, 물체, 조명, 날씨를 바꿔가며 낙하 장면을 대량으로 만듭니다."],
   ["cctv-3d.png", "실제 현장 영상에 합성", "현장 CCTV 배경 위에 렌더링한 낙하물을 모션 블러까지 입혀 붙입니다."],
   ["drop-3d.png", "실측 낙하 시험으로 검증", "더미 물체를 떨어뜨린 실제 영상은 평가에만 써서 실력을 확인합니다."]].forEach(([img, h, b], i) => {
    const x = L + i * 3.92, w = 3.69;
    s.addImage({ path: A(img), x, y: 1.95, w, h: w / 1.444 });
    numCircle(s, x, 4.75, i + 1, 0.34);
    T(s, h, { x: x + 0.47, y: 4.74, w: 3.2, h: 0.36, fontSize: 16, bold: true });
    T(s, b, { x: x + 0.47, y: 5.15, w: 3.2, h: 0.8, fontSize: 12, color: K.g7, lineSpacingMultiple: 1.2 });
    if (i < 2) arrow(s, x + w + 0.03, 3.23, x + w + 0.2, 3.23, K.g5);
  });
  pill(s, L, 6.2, 0.9, "POINT", { fill: K.orange, h: 0.3, fs: 10.5 });
  T(s, "공개 낙하물 영상 데이터셋 FADE(영상 2,611개)로 사전학습하고, 실제 사고 영상의 공백은 합성 데이터로 채웁니다.", { x: L + 1.05, y: 6.2, w: 10.4, h: 0.3, fontSize: 12, bold: true, valign: "middle" });
}
{ // 11. KIT 구성
  const s = slide("PANEL", S3, "03", "제품 구성", ["현장에 바로,", "DropZero KIT"], { sub: "Hardware Kit · 계획 사양" });
  s.addImage({ path: A("kit-3d.png"), x: 0.15, y: 3.35, w: 4.5, h: 3.375 });
  table(s, 5.25, 1.3, [2.25, 4.93], ["구성품", "주요 사양 · 역할"], [
    ["엣지 AI 박스", "Jetson Orin급 · IP66 함체 · LTE 이중화, 클라우드 없이 현장에서 경보 판단"],
    ["상층부 전용 카메라", "60fps, 낙하 감지 구간 전용 (나머지는 기존 CCTV 재활용)"],
    ["크레인 후크 카메라·센서", "인양물 위치 · 선회각 · 반경 수집 → 동적 위험구역 계산"],
    ["경광등 · 다국어 스피커", "구역 경보, 엣지 박스와 유선 · 전용 RF 연결"],
    ["스마트 안전모 BLE 태그", "작업자 위치 확인 · 진동 경보"],
    ["점검 드론", "작업 전 · 점심 · 종료 후 정기 순찰, 고소부 위험요소 촬영"],
  ], { rowH: [0.45, 0.62, 0.62, 0.62, 0.62, 0.55, 0.62], fs: 11.5 });
  ["#기존CCTV재활용", "#엣지단독경보", "#공사기간렌탈"].forEach((t, i) => pill(s, 5.25 + i * 1.75, 5.85, 1.6, t, { fill: K.paper, color: K.g8, h: 0.32, fs: 10.5 }));
  pill(s, 5.25, 6.4, 0.9, "POINT", { fill: K.orange, h: 0.3, fs: 10.5 });
  T(s, "센서 구성은 현장마다 달라도, 판단은 엣지 박스 한 곳에서 합니다.", { x: 6.3, y: 6.4, w: 6, h: 0.3, fontSize: 11.5, bold: true, valign: "middle" });
}
{ // 12. 차별성
  const s = slide("LIGHT", S3, "03", "시장 경쟁력 및 차별성", "기존 AI CCTV가 놓치는 **떨어지는 물체**까지 봅니다");
  const mx = L + 0.55, my = 2.15, mw = 5.4, mh = 3.95, cxm = mx + mw / 2, cym = my + mh / 2;
  arrow(s, mx, cym, mx + mw, cym, K.g5, { width: 1 }); arrow(s, mx + mw, cym, mx, cym, K.g5, { width: 1 });
  arrow(s, cxm, my + mh, cxm, my, K.g5, { width: 1 }); arrow(s, cxm, my, cxm, my + mh, K.g5, { width: 1 });
  T(s, "낙하물 특화", { x: cxm - 1, y: my - 0.32, w: 2, h: 0.26, fontSize: 10.5, color: K.g7, align: "center" });
  T(s, "범용 감지", { x: cxm - 1, y: my + mh + 0.06, w: 2, h: 0.26, fontSize: 10.5, color: K.g7, align: "center" });
  T(s, "사후\n기록", { x: mx - 0.55, y: cym - 0.25, w: 0.5, h: 0.5, fontSize: 10.5, color: K.g7, align: "center" });
  T(s, "사전\n예방", { x: mx + mw + 0.05, y: cym - 0.25, w: 0.5, h: 0.5, fontSize: 10.5, color: K.g7, align: "center" });
  const pos = (px, py, w, text, hl) => pill(s, mx + px * mw - w / 2, my + py * mh - 0.18, w, text, hl ? { h: 0.42, fs: 13 } : { fill: K.white, color: K.g7, line: { color: K.rule, width: 0.75 }, h: 0.36, fs: 10.5 });
  pos(0.24, 0.8, 1.75, "현장 CCTV 녹화 · 관제");
  pos(0.6, 0.64, 1.5, "범용 AI CCTV");
  pos(0.8, 0.86, 1.45, "BLE 접근 경보");
  pos(0.78, 0.2, 1.7, "DropZero", true);
  [["낙하물 사고의 전 과정", "위험요소 점검부터 하부 노출 차단, 낙하 감지, 기록까지 한 시스템이 맡습니다."],
   ["크레인을 따라 움직이는 구역", "출입금지 구역을 고정하지 않고 인양물 위치에 맞춰 계속 다시 그립니다."],
   ["물리 기반 판별", "중력 궤적 검증으로 오경보를 줄여, 현장이 경보를 꺼버리지 않게 합니다."],
   ["엣지 단독 경보", "통신이 끊겨도 현장 엣지 박스가 경보를 울립니다."]].forEach(([h, b], i) => {
    const x = 7.4 + (i % 2) * 2.55, y = 2.0 + Math.floor(i / 2) * 2.2;
    card(s, x, y, 2.43, 2.0);
    T(s, String(i + 1).padStart(2, "0"), { x: x + 0.22, y: y + 0.2, w: 1, h: 0.4, fontSize: 18, bold: true, color: K.orange });
    T(s, h, { x: x + 0.22, y: y + 0.62, w: 2.05, h: 0.5, fontSize: 12.5, bold: true, lineSpacingMultiple: 1.1 });
    T(s, b, { x: x + 0.22, y: y + 1.14, w: 2.05, h: 0.78, fontSize: 10, color: K.g7, lineSpacingMultiple: 1.15 });
  });
  source(s, "범용 AI CCTV 예: 카스웍스, 알체라, SAIGE 등 (각사 공개 자료 기준). 위치는 기능 범위를 비교한 개념도입니다.");
}

// ---------------------------------------------------------------- 04 사업화 전략
const S4 = "04 사업화 전략";
pres.addSection({ title: S4 });
{ // 13. 비즈니스 모델
  const s = slide("LIGHT", S4, "04", "사업화 전략 · 비즈니스 모델", "현장마다 받는 월 구독료는 **산안비**에서 나옵니다");
  const node = (x, y, w, h, t, sub, o = {}) => {
    rect(s, x, y, w, h, o.fill || K.paper, { round: 0.1, line: o.line || { color: K.g2, width: 0.75, dashType: o.dash ? "dash" : "solid" } });
    T(s, t, { x: x + 0.15, y: y + (sub ? 0.2 : 0), w: w - 0.3, h: sub ? 0.38 : h, fontSize: o.fs || 15, bold: true, align: "center", valign: sub ? "top" : "middle", color: o.color || K.ink });
    if (sub) T(s, sub, { x: x + 0.15, y: y + 0.6, w: w - 0.3, h: h - 0.65, fontSize: 10.5, align: "center", color: o.subColor || K.g5 });
  };
  node(L, 3.3, 2.6, 1.15, "건설사 · 현장", "중견 건설사 고층 현장");
  node(5.37, 3.3, 2.6, 1.15, "DropZero", "팀 GA", { fill: K.ink, line: { color: K.ink, width: 0 }, color: K.white, subColor: K.rule, fs: 19 });
  node(9.83, 3.3, 2.6, 1.15, "보험사 · 금융기관", "확장 단계", { fill: K.white, dash: true });
  node(L, 1.95, 2.6, 0.75, "발주자 · 산업안전보건관리비", null, { fs: 12 });
  node(5.37, 1.95, 2.6, 0.75, "국토부 중소현장 장비 지원", null, { fs: 12 });
  arrow(s, 5.37, 3.6, 3.5, 3.6, K.ink); T(s, "장비 + AI 관제 서비스", { x: 3.5, y: 3.24, w: 1.87, h: 0.28, fontSize: 10.5, align: "center", color: K.g7 });
  arrow(s, 3.5, 4.15, 5.37, 4.15, K.orange, { width: 2 }); T(s, "현장당 월 구독료", { x: 3.5, y: 4.22, w: 1.87, h: 0.28, fontSize: 10.5, bold: true, align: "center", color: K.orange });
  arrow(s, 7.97, 3.6, 9.83, 3.6, K.ink, { dash: true }); T(s, "현장 위험 점수", { x: 7.97, y: 3.24, w: 1.86, h: 0.28, fontSize: 10.5, align: "center", color: K.g7 });
  arrow(s, 9.83, 4.15, 7.97, 4.15, K.orange, { width: 2, dash: true }); T(s, "데이터 이용료", { x: 7.97, y: 4.22, w: 1.86, h: 0.28, fontSize: 10.5, bold: true, align: "center", color: K.orange });
  arrow(s, L + 1.3, 2.7, L + 1.3, 3.3, K.g7); T(s, "구입·임대비 100% 인정 (산안비의 20%까지)", { x: L + 1.42, y: 2.86, w: 3.5, h: 0.26, fontSize: 10, color: K.g7 });
  arrow(s, 6.67, 2.7, 6.67, 3.3, K.g7); T(s, "300억 미만 현장 무상 대여 · 임대 공급사로 참여", { x: 6.79, y: 2.86, w: 3.8, h: 0.26, fontSize: 10, color: K.g7 });
  table(s, L, 4.85, [2.4, 6.13, 3.0], ["수익원", "내용", "가격"], [
    ["① 장비 렌탈", "엣지 박스 · 전용 카메라 · 경광등을 공사 기간 동안 빌려줍니다.", "구독료에 포함"],
    ["② AI 관제 구독", "현장당 월 과금. 공사비 300억 원 현장의 스마트 장비 한도(월 약 330만 원) 안", "월 250만 원 내외 (가정)"],
    ["③ 위험 데이터 (확장)", "보험 요율 · PF 리스크 평가에 쓰는 현장 위험 점수", "건별 · 연간 계약"],
  ], { rowH: 0.42, fs: 11 });
}
{ // 14. 로드맵
  const s = slide("LIGHT", S4, "04", "사업화 전략 · 개발 및 사업 로드맵", "내년 파일럿 현장 한 곳에서 **오경보율과 지연**을 잽니다");
  table(s, L, 1.95, [1.6, 2.48, 2.48, 2.48, 2.49], ["구분", "2026. 11", "2027 상반기", "2027 하반기", "2028~"], [
    ["단계", "PoC 시연", "파일럿 현장 1곳", "제품화", "확장"],
    ["핵심 과제", "더미 낙하 → 엣지 감지 → 경광등 점등\n합성 데이터 1차 학습", "인양 위험구역 · 낙하 기록 실증\n오경보율 · 종단 지연 실측", "스마트 안전장비 지원사업 공급 등록\n하드웨어 KC 인증", "대형 건설사 API 공급\n싱가포르 등 해외 · 보험 연계"],
  ], { rowH: [0.42, 0.45, 0.85], fs: 11 });
  const ty = 4.55;
  s.addShape(pres.ShapeType.line, { x: L, y: ty, w: R - L, h: 0, line: { color: K.rule, width: 1.5 } });
  ["PoC", "파일럿", "제품화", "확장"].forEach((t, i) => {
    const x = L + 1.6 + 2.48 * i + 1.24;
    dot(s, x - 0.09, ty - 0.09, 0.18, i === 0 ? K.orange : K.ink);
    T(s, t, { x: x - 0.8, y: ty + 0.18, w: 1.6, h: 0.28, fontSize: 11.5, bold: true, align: "center", color: i === 0 ? K.orange : K.ink });
  });
  T(s, "타겟", { x: L, y: 5.3, w: 0.8, h: 0.32, fontSize: 13, bold: true, valign: "middle" });
  ["#중견건설사", "#고층공동주택", "#타워크레인현장"].forEach((t, i) => pill(s, L + 0.75 + i * 1.75, 5.3, 1.6, t, { fill: K.paper, color: K.g8, h: 0.32, fs: 10.5 }));
  card(s, L, 5.85, R - L, 0.7);
  T(s, [{ text: "파일럿 목표   ", options: { bold: true, color: K.orange } }, { text: "카메라당 오경보 시간당 0.1건 이하  ·  감지에서 경보까지 0.35초 이내  ·  위험구역 진입 경보 누락 0건" }], { x: L + 0.3, y: 5.85, w: R - L - 0.6, h: 0.7, fontSize: 13, valign: "middle" });
}

// ---------------------------------------------------------------- 15. 감사합니다 (팀)
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: S4 });
  T(s, "감사합니다.", { x: 0.9, y: 1.4, w: 7, h: 1.0, fontSize: 44, bold: true, color: K.white });
  T(s, "Q&A", { x: 0.95, y: 2.45, w: 3, h: 0.6, fontSize: 26, color: K.rule });
  T(s, [{ text: "팀 GA", options: { bold: true, fontSize: 16, color: K.white, breakLine: true } }, { text: "이승보 · 이성재 · 장재홍", options: { fontSize: 13, color: K.rule } }], { x: 0.95, y: 4.55, w: 6, h: 0.8, lineSpacingMultiple: 1.3 });
  T(s, "DropZero  ·  건설현장 낙하물 사고, 맞기 전에 막습니다", { x: 0.95, y: 5.55, w: 7, h: 0.3, fontSize: 12, color: K.g5 });
  rect(s, 8.5, 1.4, 3.93, 4.45, "2A2C30", { round: 0.08 });
  T(s, "함께하고 싶은 것", { x: 8.85, y: 1.7, w: 3.3, h: 0.4, fontSize: 16, bold: true, color: K.white });
  ["파일럿 현장 1곳\n(고층 건축 · 타워크레인 운용)", "실측 낙하 시험 장소", "건설 안전 실무 자문"].forEach((a, i) => {
    numCircle(s, 8.85, 2.4 + i * 1.05, i + 1, 0.3, K.orange);
    T(s, a, { x: 9.3, y: 2.37 + i * 1.05, w: 2.9, h: 0.85, fontSize: 12.5, color: K.rule, lineSpacingMultiple: 1.15 });
  });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
