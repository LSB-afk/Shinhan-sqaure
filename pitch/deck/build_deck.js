// 팀 GA · DropZero IR 피치덱 생성기 (15장: 공모전 사업소개서 15매 제한)
// node art.js && node build_deck.js → DropZero_IR_팀GA.pptx
// 글꼴은 Pretendard 하나만 쓴다(테마 제목/본문 글꼴).
const path = require("path");
const pptxgen = require("pptxgenjs");
const fs = require("fs");
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

const MARKET = require("./market.js");

const A = f => path.join(__dirname, "assets", f);
const OUT = path.join(__dirname, "DropZero_IR_팀GA.pptx");

const THEME = {
  name: "DropZero",
  headFontFace: "Pretendard",
  bodyFontFace: "Pretendard",
  colors: {
    dk1: "1B1D21", lt1: "FFFFFF", dk2: "16181B", lt2: "F3F4F6",
    accent1: "FF5A1F", accent2: "8A9099", accent3: "4A4F57", accent4: "C9CDD3", accent5: "2B2F35", accent6: "E3E5E8",
    hlink: "FF5A1F", folHlink: "8A9099",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "DropZero IR 피치덱";
pres.author = "팀 GA (이승보, 이성재, 장재홍)";
const C = pres.SchemeColor;
const K = {
  ink: C.text1, dark: C.text2, white: C.background1, paper: C.background2, orange: C.accent1,
  g5: C.accent2, g7: C.accent3, g3: C.accent4, g8: C.accent5, g2: C.accent6,
};
const HEX = THEME.colors;
const W = 13.333, M = 0.6;

// ---------------------------------------------------------------- 레이아웃
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: K.white },
  objects: [
    { text: { text: "DropZero  ·  팀 GA", options: { x: M, y: 7.0, w: 4, h: 0.3, fontSize: 9, color: K.g5, margin: 0 } } },
    { placeholder: { options: { name: "label", type: "body", x: M, y: 0.42, w: 9, h: 0.3, fontSize: 12, bold: true, color: K.orange, margin: 0, align: "left" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.74, w: 12.1, h: 0.95, fontSize: 28, bold: true, color: K.ink, margin: 0, valign: "top", align: "left" }, text: "" } },
  ],
  slideNumber: { x: 12.23, y: 7.0, w: 0.5, h: 0.3, fontSize: 9, color: K.g5, align: "right" },
});
pres.defineSlideMaster({ title: "DARK", background: { color: K.dark }, objects: [] });

function content(section, label, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(label, { placeholder: "label" });
  s.addText(title, { placeholder: "title" });
  return s;
}

const T = (s, text, o) => s.addText(text, { isTextBox: true, margin: 0, color: K.ink, fontSize: 15, valign: "top", ...o });
const source = (s, text) => T(s, text, { x: M, y: 6.62, w: 12.1, h: 0.28, fontSize: 9, color: K.g5 });
const dot = (s, x, y, d, color) => s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color }, line: { color, width: 0 } });
const rect = (s, x, y, w, h, fill, o = {}) => s.addShape(o.round ? pres.ShapeType.roundRect : pres.ShapeType.rect,
  { x, y, w, h, fill: { color: fill }, line: o.line || { color: fill, width: 0 }, ...(o.round ? { rectRadius: o.round } : {}), objectName: o.name });
function arrow(s, x1, y1, x2, y2, color = K.g7, o = {}) {
  s.addShape(pres.ShapeType.line, {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    flipH: x2 < x1, flipV: y2 < y1,
    line: { color, width: o.width || 1.5, endArrowType: "triangle", dashType: o.dash ? "dash" : "solid" },
  });
}
function badge(s, x, y, n, d = 0.38) {
  dot(s, x, y, d, K.orange);
  T(s, String(n), { x, y, w: d, h: d, fontSize: 13, bold: true, color: K.white, align: "center", valign: "middle" });
}
// 덱 모티프: 같은 시간 간격의 자유낙하 점(아래로 갈수록 간격이 벌어짐)
function fallMotif(s, x, y0, len, n = 6, d = 0.07, color = K.g5) {
  for (let i = 1; i <= n; i++) {
    const t = i / n, last = i === n;
    const dd = last ? d * 1.9 : d;
    dot(s, x - dd / 2, y0 + len * t * t - dd / 2, dd, last ? K.orange : color);
  }
}

// ---------------------------------------------------------------- 1. 표지
pres.addSection({ title: "표지" });
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "표지" });
  s.addImage({ path: A("cover-3d.png"), x: 0, y: 0, w: W, h: 7.5 });
  T(s, "2026 신한 스퀘어브릿지 대학생 창업 공모전  HERO IR", { x: 0.7, y: 0.7, w: 8, h: 0.3, fontSize: 12, color: K.g5 });
  T(s, "DropZero", { x: 0.7, y: 1.35, w: 7, h: 1.1, fontSize: 64, bold: true, color: K.white });
  T(s, "건설현장 낙하물 사고,\n맞기 전에 막습니다", { x: 0.7, y: 2.6, w: 5, h: 1.2, fontSize: 24, color: K.g3, lineSpacingMultiple: 1.15 });
  fallMotif(s, 0.82, 4.35, 1.5, 6, 0.08, K.g7);
  T(s, "팀 GA   이승보 · 이성재 · 장재홍", { x: 0.7, y: 6.6, w: 5, h: 0.35, fontSize: 13, color: K.g3 });
}

// ---------------------------------------------------------------- 2. 문제
pres.addSection({ title: "문제" });
{
  const s = content("문제", "문제", "지난해 건설 현장에서 286명이 일하다 숨졌습니다");
  T(s, [{ text: "286", options: { fontSize: 72, bold: true } }, { text: "명", options: { fontSize: 30, bold: true } }], { x: M, y: 2.0, w: 4.8, h: 1.1 });
  T(s, "2025년 건설업 사고사망자", { x: M, y: 3.15, w: 4.8, h: 0.35, fontSize: 16, bold: true, color: K.g7 });
  T(s, "전 산업 사고사망 605명 중 47%", { x: M, y: 3.52, w: 4.8, h: 0.3, fontSize: 13, color: K.g5 });
  T(s, [{ text: "72", options: { fontSize: 72, bold: true, color: K.orange } }, { text: "명", options: { fontSize: 30, bold: true, color: K.orange } }], { x: M, y: 4.25, w: 4.8, h: 1.1 });
  T(s, "‘물체에 맞음’ 사망자, 사고 유형 2위", { x: M, y: 5.4, w: 4.8, h: 0.35, fontSize: 16, bold: true, color: K.g7 });
  T(s, "날아오거나 떨어진 물체에 맞은 사고 (전 산업)", { x: M, y: 5.77, w: 4.8, h: 0.3, fontSize: 13, color: K.g5 });

  s.addChart(pres.ChartType.bar, [
    { name: "물체에 맞음", labels: ["무너짐", "부딪힘", "물체에 맞음", "떨어짐"], values: [0, 0, 72, 0] },
    { name: "그 외", labels: ["무너짐", "부딪힘", "물체에 맞음", "떨어짐"], values: [38, 62, 0, 249] },
  ], {
    x: 6.0, y: 1.95, w: 6.7, h: 4.5, barDir: "bar", barGrouping: "stacked", barGapWidthPct: 55,
    chartColors: [HEX.accent1, HEX.accent4], showLegend: false,
    showTitle: true, title: "2025년 사고사망 발생 형태 (전 산업, 명)", titleFontSize: 13, titleColor: HEX.accent3, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: "#,##0;;;", dataLabelFontSize: 13, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt", dataLabelFontBold: true,
    catAxisLabelColor: HEX.accent3, catAxisLabelFontSize: 13, catAxisLabelFontFace: "+mn-lt", catAxisLineShow: false,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  });
  source(s, "출처: 고용노동부 「2025년 재해조사 대상 사망사고 발생 현황」(2026. 3.), 연합뉴스 2026. 3. 31. 보도 재인용");
}

// ---------------------------------------------------------------- 3. 왜 어려운가
{
  const s = content("문제", "문제", "30m에서 떨어진 공구는 2.47초 만에 바닥에 닿습니다");
  const fw = 4.0, fh = 4.444, fy = 1.9;
  s.addImage({ path: A("fall-3d.png"), x: M, y: fy, w: fw, h: fh });
  const FP = JSON.parse(fs.readFileSync(A("fall-3d.json")));
  for (const [k, label, hl] of [["t2", "1.0초", 0], ["t3", "1.5초", 0], ["t4", "2.0초", 0], ["t5", "2.47초 · 바닥", 1]]) {
    const [px, py] = FP[k];
    T(s, label, { x: M + px * fw + 0.05, y: fy + py * fh - 0.13, w: 1.4, h: 0.26, fontSize: 12, bold: true, color: hl ? K.orange : K.g8 });
  }
  const pts = [
    ["보고 피하기엔 짧습니다", "경보를 듣고 판단해 1~2m 피하는 데 1.5~2.5초가 걸립니다. 17m보다 낮은 곳에서 떨어지면 경보만으로는 막을 수 없습니다."],
    ["누가 아래에 있는지 모릅니다", "인양 중 하부 출입 통제는 신호수 한 사람의 눈에 달려 있습니다. 크레인이 움직이면 위험한 자리도 같이 바뀝니다."],
    ["다치지 않으면 기록이 없습니다", "사람이 맞지 않은 낙하는 보고되지 않습니다. 어느 현장이 위험한지 미리 가려낼 데이터가 쌓이지 않습니다."],
  ];
  pts.forEach(([h, b], i) => {
    const y = 2.05 + i * 1.5;
    T(s, String(i + 1).padStart(2, "0"), { x: 5.6, y, w: 0.6, h: 0.35, fontSize: 15, bold: true, color: K.orange });
    T(s, h, { x: 6.25, y, w: 6.4, h: 0.4, fontSize: 20, bold: true });
    T(s, b, { x: 6.25, y: y + 0.45, w: 6.4, h: 0.85, fontSize: 14, color: K.g7, lineSpacingMultiple: 1.2 });
  });
}

// ---------------------------------------------------------------- 4. 왜 지금
pres.addSection({ title: "기회" });
{
  const s = content("기회", "왜 지금인가", "올해부터 스마트 안전장비 비용을 산안비로 전액 처리합니다");
  const cols = [
    ["100%", "스마트 안전장비 비용, 산안비로 전액 인정", "2026년부터 AI CCTV·접근 경보 장비의 구입·임대비를 산업안전보건관리비로 100% 씁니다. 사용 한도도 산안비의 20%로 늘었습니다."],
    ["19%↑", "산안비 요율 11년 만에 인상", "2025년 계약분부터 요율이 평균 19% 올랐습니다. 공사비 50억 원 이상 건축공사는 2.37%입니다."],
    ["16층+", "고층 현장엔 CCTV가 이미 있습니다", "16층 이상 공동주택 공사장은 CCTV 설치가 의무입니다. 카메라를 새로 달지 않고 분석만 얹으면 됩니다."],
    ["5인 이상", "중대재해처벌법 전면 적용", "2024년부터 5인 이상 사업장 전체로 넓어졌습니다. 안전보건관리체계를 실제로 운영한 기록이 필요합니다."],
  ];
  cols.forEach(([n, h, b], i) => {
    const x = M + i * 3.07, w = 2.85;
    rect(s, x, 2.0, w, 4.3, K.paper, { round: 0.08 });
    T(s, n, { x: x + 0.28, y: 2.28, w: w - 0.5, h: 0.9, fontSize: 44, bold: true, color: K.orange });
    T(s, h, { x: x + 0.28, y: 3.3, w: w - 0.5, h: 0.8, fontSize: 16, bold: true, lineSpacingMultiple: 1.15 });
    T(s, b, { x: x + 0.28, y: 4.2, w: w - 0.5, h: 1.95, fontSize: 13, color: K.g7, lineSpacingMultiple: 1.25 });
  });
  source(s, "근거: 고용노동부고시 제2024-53호·제2025-11호(건설업 산업안전보건관리비 계상 및 사용기준), 건설기술 진흥법 시행규칙(2020. 12. 10. 시행), 중대재해 처벌 등에 관한 법률");
}

// ---------------------------------------------------------------- 5. 솔루션
pres.addSection({ title: "솔루션" });
{
  const s = content("솔루션", "솔루션 · DropZero", "떨어질 물건 아래에 사람이 서 있지 않게 합니다");
  const ix = 0.45, iy = 2.0, iw = 8.0, ih = 4.5;
  s.addImage({ path: A("solution-3d.png"), x: ix, y: iy, w: iw, h: ih });
  const SP = JSON.parse(fs.readFileSync(A("solution-3d.json")));
  [["zone", 1], ["fall", 2], ["drone", 3]].forEach(([key, n]) => badge(s, ix + SP[key][0] * iw + 0.12, iy + SP[key][1] * ih - 0.5, n));
  const items = [
    ["예방", "인양물 아래 위험구역이 크레인을 따라 움직이고, 사람이 들어오면 바로 경보가 울립니다."],
    ["대응", "물체가 떨어지는 순간을 감지해 0.35초 안에 착지 예상 지점 주변에 대피 경보를 보냅니다."],
    ["학습", "드론 순찰 결과와 모든 낙하 기록을 쌓아 위험한 현장과 시간대를 미리 가려냅니다."],
  ];
  items.forEach(([h, b], i) => {
    const y = 2.1 + i * 1.5;
    badge(s, 8.95, y, i + 1);
    T(s, h, { x: 9.5, y: y - 0.02, w: 3.2, h: 0.4, fontSize: 20, bold: true });
    T(s, b, { x: 9.5, y: y + 0.42, w: 3.25, h: 1.0, fontSize: 14, color: K.g7, lineSpacingMultiple: 1.2 });
  });
}

// ---------------------------------------------------------------- 6. 기능 ① 예방
{
  const s = content("솔루션", "핵심 기능 ①  예방", "인양물이 움직이면 위험구역도 같이 움직입니다");
  s.addImage({ path: A("zone-3d.png"), x: 0.45, y: 1.85, w: 6.1, h: 4.88 });
  const steps = [
    ["인양물 위치 계산", "크레인 후크 카메라와 선회각·반경 데이터로 매달린 자재의 위치를 잡습니다."],
    ["위험구역 생성", "자재가 떨어질 수 있는 바닥 범위에 안전 여유를 더해 구역을 만들고, 크레인이 움직일 때마다 다시 그립니다."],
    ["진입 즉시 경보", "구역 안에 작업자가 들어오면 경광등, 안전모 진동, 신호수 단말이 동시에 울립니다."],
  ];
  steps.forEach(([h, b], i) => {
    const y = 2.0 + i * 1.22;
    T(s, String(i + 1), { x: 7.0, y, w: 0.4, h: 0.4, fontSize: 20, bold: true, color: K.orange });
    T(s, h, { x: 7.45, y, w: 5.2, h: 0.4, fontSize: 19, bold: true });
    T(s, b, { x: 7.45, y: y + 0.42, w: 5.2, h: 0.75, fontSize: 14, color: K.g7, lineSpacingMultiple: 1.2 });
  });
  rect(s, 7.0, 5.75, 5.7, 0.8, K.paper, { round: 0.06 });
  T(s, "낙하 높이와 상관없이 작동해서, 경보로 피할 시간이 없는 저층 인양도 이 단계에서 막습니다.", { x: 7.25, y: 5.87, w: 5.3, h: 0.6, fontSize: 13, color: K.g8, valign: "middle", lineSpacingMultiple: 1.15 });
}

// ---------------------------------------------------------------- 7. 기능 ② 대응
{
  const s = content("솔루션", "핵심 기능 ②  대응", "떨어지는 순간을 0.35초 안에 잡아 경보를 울립니다");
  const x0 = M, x1 = 12.7, scale = (x1 - x0) / 2.47;
  T(s, "30m 높이에서 떨어진 물체가 바닥에 닿기까지 2.47초", { x: x0, y: 2.1, w: 8, h: 0.3, fontSize: 14, color: K.g7 });
  rect(s, x0, 2.55, 0.35 * scale, 0.62, K.orange);
  rect(s, x0 + 0.35 * scale, 2.55, (2.47 - 0.35) * scale, 0.62, K.g8);
  T(s, "감지 · 경보  0.35초", { x: x0 + 0.12, y: 2.55, w: 2.3, h: 0.62, fontSize: 13, bold: true, color: K.white, valign: "middle" });
  T(s, "대피할 수 있는 시간  약 2.1초", { x: x0 + 0.35 * scale + 0.25, y: 2.55, w: 5, h: 0.62, fontSize: 15, bold: true, color: K.white, valign: "middle" });
  for (const t of [0, 0.5, 1.0, 1.5, 2.0, 2.47]) {
    const x = x0 + t * scale;
    s.addShape(pres.ShapeType.line, { x, y: 3.2, w: 0, h: 0.12, line: { color: K.g5, width: 1 } });
    T(s, t === 0 ? "0초" : `${t}초`, { x: x - 0.4, y: 3.35, w: 0.8, h: 0.25, fontSize: 11, color: K.g5, align: "center" });
  }
  const steps = ["움직임 후보", "소형 객체 검출", "궤적 추적", "중력 궤적 검증", "착지점 예측", "경보"];
  const sw = 2.02;
  steps.forEach((st, i) => {
    const hl = i === 3;
    s.addShape(i === 0 ? pres.ShapeType.homePlate : pres.ShapeType.chevron, {
      x: x0 + i * (sw - 0.04), y: 4.2, w: sw, h: 0.62,
      fill: { color: hl ? K.orange : K.paper }, line: { color: hl ? K.orange : K.g2, width: 0.75 },
    });
    T(s, st, { x: x0 + i * (sw - 0.04) + 0.22, y: 4.2, w: sw - 0.45, h: 0.62, fontSize: 13, bold: true, align: "center", valign: "middle", color: hl ? K.white : K.ink });
  });
  const notes = [
    ["오경보 거르기", "움직임이 중력가속도(9.8m/s²)에 맞게 빨라지는지 확인합니다. 새, 비닐, 흔들리는 와이어는 여기서 걸러집니다."],
    ["현장에서 바로 판단", "엣지 박스가 직접 경광등을 울립니다. 현장 통신이 끊겨도 경보는 나갑니다."],
  ];
  notes.forEach(([h, b], i) => {
    const x = x0 + i * 6.15;
    T(s, h, { x, y: 5.3, w: 5.8, h: 0.4, fontSize: 18, bold: true });
    T(s, b, { x, y: 5.75, w: 5.8, h: 0.9, fontSize: 14, color: K.g7, lineSpacingMultiple: 1.2 });
  });
}

// ---------------------------------------------------------------- 8. 기능 ③ 학습
{
  const s = content("솔루션", "핵심 기능 ③  학습", "사람이 다치지 않은 낙하까지 모두 기록합니다");
  s.addImage({ path: A("drone-3d.png"), x: 0.5, y: 2.0, w: 5.4, h: 3.36 });
  T(s, "작업 전 · 점심 · 작업 종료 후 드론 순찰", { x: 0.7, y: 5.45, w: 5.2, h: 0.35, fontSize: 16, bold: true });
  T(s, "단부 자재 적치, 낙하물방지망 파손, 개구부 덮개 누락을 찾아 아침 TBM 전에 알려줍니다.", { x: 0.7, y: 5.85, w: 5.2, h: 0.7, fontSize: 13, color: K.g7, lineSpacingMultiple: 1.2 });

  const cx = 6.6, cy = 1.95, cw = 6.1, ch = 4.55;
  rect(s, cx, cy, cw, ch, K.white, { round: 0.06, line: { color: K.g2, width: 1 } });
  T(s, "현장 안전 리포트", { x: cx + 0.35, y: cy + 0.28, w: 3, h: 0.35, fontSize: 15, bold: true });
  T(s, "화면 예시", { x: cx + cw - 1.6, y: cy + 0.3, w: 1.25, h: 0.3, fontSize: 10, color: K.g5, align: "right" });
  [["12", "오늘 이벤트", K.ink], ["3", "아차사고", K.orange], ["100%", "조치 완료", K.ink]].forEach(([n, l, c], i) => {
    const x = cx + 0.35 + i * 1.86;
    rect(s, x, cy + 0.8, 1.7, 1.15, K.paper, { round: 0.06 });
    T(s, n, { x: x + 0.18, y: cy + 0.9, w: 1.4, h: 0.55, fontSize: 26, bold: true, color: c });
    T(s, l, { x: x + 0.18, y: cy + 1.5, w: 1.4, h: 0.3, fontSize: 11, color: K.g5 });
  });
  const rows = [["14:02", "낙하 감지 · 12층 동측", "아차사고", K.orange], ["10:15", "위험구역 진입 · 크레인 1호", "경보", K.g8], ["07:12", "드론 순찰 · 9층 방지망 파손", "조치 완료", K.g5]];
  rows.forEach(([t, d, tag, c], i) => {
    const y = cy + 2.2 + i * 0.52;
    T(s, t, { x: cx + 0.35, y, w: 0.8, h: 0.36, fontSize: 12, color: K.g5, valign: "middle" });
    T(s, d, { x: cx + 1.15, y, w: 3.3, h: 0.36, fontSize: 13, valign: "middle" });
    rect(s, cx + cw - 1.55, y + 0.03, 1.2, 0.3, c, { round: 0.15 });
    T(s, tag, { x: cx + cw - 1.55, y: y + 0.03, w: 1.2, h: 0.3, fontSize: 10, bold: true, color: K.white, align: "center", valign: "middle" });
  });
  rect(s, cx + 0.35, cy + ch - 0.72, cw - 0.7, 0.45, K.paper, { round: 0.08 });
  T(s, "위험성평가 개선 이력 · 점검일지 자동 생성  →  중대재해처벌법 대응 증빙", { x: cx + 0.55, y: cy + ch - 0.72, w: cw - 1.0, h: 0.45, fontSize: 12, color: K.g8, valign: "middle" });
}

// ---------------------------------------------------------------- 9. 기술
pres.addSection({ title: "기술" });
{
  const s = content("기술", "기술", "사고 영상이 없어도 학습할 수 있도록 데이터를 직접 만듭니다");
  const cards = [
    ["sim-3d.png", "3D 물리 시뮬레이션", "높이, 물체, 조명, 날씨를 바꿔가며 낙하 장면을 대량으로 만듭니다."],
    ["cctv-3d.png", "실제 현장 영상에 합성", "현장 CCTV 배경 위에 렌더링한 낙하물을 모션 블러까지 입혀 붙입니다."],
    ["drop-3d.png", "실측 낙하 시험으로 검증", "더미 물체를 떨어뜨린 실제 영상은 평가에만 써서 실력을 확인합니다."],
  ];
  cards.forEach(([img, h, b], i) => {
    const x = M + i * 4.12;
    s.addImage({ path: A(img), x, y: 1.95, w: 3.86, h: 2.672 });
    T(s, String(i + 1), { x, y: 4.85, w: 0.4, h: 0.4, fontSize: 18, bold: true, color: K.orange });
    T(s, h, { x: x + 0.38, y: 4.85, w: 3.5, h: 0.4, fontSize: 18, bold: true });
    T(s, b, { x: x + 0.38, y: 5.3, w: 3.45, h: 0.8, fontSize: 13, color: K.g7, lineSpacingMultiple: 1.2 });
    if (i < 2) arrow(s, x + 3.9, 3.29, x + 4.08, 3.29, K.g5, { width: 1.5 });
  });
  source(s, "사전학습: 공개 낙하물 영상 데이터셋 FADE(영상 2,611개, arXiv:2408.05750)  ·  실제 낙하 사고 영상은 거의 없어 합성 데이터가 필수입니다");
}

// ---------------------------------------------------------------- 10. 시장
pres.addSection({ title: "시장" });
MARKET.slide(pres, { content, T, rect, dot, source, K, HEX, M });

// ---------------------------------------------------------------- 11. 비즈니스 모델
pres.addSection({ title: "비즈니스 모델" });
{
  const s = content("비즈니스 모델", "비즈니스 모델", "현장마다 받는 월 구독료는 산안비에서 나옵니다");
  const node = (x, y, w, h, title, sub, o = {}) => {
    rect(s, x, y, w, h, o.fill || K.white, { round: 0.08, line: o.line || { color: K.g3, width: 1.25, dashType: o.dash ? "dash" : "solid" } });
    T(s, title, { x: x + 0.15, y: y + (sub ? 0.18 : 0), w: w - 0.3, h: sub ? 0.4 : h, fontSize: o.fs || 16, bold: true, align: "center", valign: sub ? "top" : "middle", color: o.color || K.ink });
    if (sub) T(s, sub, { x: x + 0.15, y: y + 0.58, w: w - 0.3, h: h - 0.65, fontSize: 11.5, align: "center", color: o.subColor || K.g5 });
  };
  node(0.6, 3.3, 2.6, 1.15, "건설사 · 현장", "중견 건설사 고층 현장");
  node(5.6, 3.3, 2.6, 1.15, "DropZero", "팀 GA", { fill: K.dark, line: { color: K.dark, width: 0 }, color: K.white, subColor: K.g3, fs: 20 });
  node(10.1, 3.3, 2.6, 1.15, "보험사 · 금융기관", "확장 단계", { dash: true });
  node(0.6, 1.85, 2.6, 0.8, "발주자 · 산업안전보건관리비", null, { fs: 13 });
  node(5.6, 1.85, 2.6, 0.8, "국토부 중소현장 장비 지원", null, { fs: 13 });

  arrow(s, 5.6, 3.6, 3.2, 3.6, K.ink); T(s, "장비 + AI 관제 서비스", { x: 3.25, y: 3.22, w: 2.3, h: 0.3, fontSize: 12, align: "center", color: K.g7 });
  arrow(s, 3.2, 4.15, 5.6, 4.15, K.orange, { width: 2 }); T(s, "현장당 월 구독료", { x: 3.25, y: 4.22, w: 2.3, h: 0.3, fontSize: 12, bold: true, align: "center", color: K.orange });
  arrow(s, 8.2, 3.6, 10.1, 3.6, K.ink, { dash: true }); T(s, "현장 위험 점수", { x: 8.2, y: 3.22, w: 1.9, h: 0.3, fontSize: 12, align: "center", color: K.g7 });
  arrow(s, 10.1, 4.15, 8.2, 4.15, K.orange, { width: 2, dash: true }); T(s, "데이터 이용료", { x: 8.2, y: 4.22, w: 1.9, h: 0.3, fontSize: 12, bold: true, align: "center", color: K.orange });
  arrow(s, 1.9, 2.65, 1.9, 3.3, K.g7); T(s, "구입·임대비 100% 인정\n(산안비의 20%까지)", { x: 2.02, y: 2.72, w: 2.4, h: 0.5, fontSize: 11, color: K.g7 });
  arrow(s, 6.9, 2.65, 6.9, 3.3, K.g7); T(s, "300억 미만 현장 무상 대여\n임대 공급사로 참여", { x: 7.02, y: 2.72, w: 2.6, h: 0.5, fontSize: 11, color: K.g7 });

  const rev = [
    ["① 장비 렌탈", "엣지 박스 · 전용 카메라 · 경광등을 공사 기간 동안 빌려줍니다."],
    ["② AI 관제 구독", "현장당 월 250만 원 내외(가정). 공사비 300억 원 현장의 스마트 장비 한도(월 약 330만 원) 안입니다."],
    ["③ 위험 데이터 (확장)", "보험 요율 · PF 리스크 평가에 쓰는 현장 위험 점수를 제공합니다."],
  ];
  rev.forEach(([h, b], i) => {
    const x = M + i * 4.12;
    rect(s, x, 5.0, 3.86, 1.45, K.paper, { round: 0.06 });
    T(s, h, { x: x + 0.25, y: 5.13, w: 3.4, h: 0.35, fontSize: 15, bold: true, color: i === 1 ? K.orange : K.ink });
    T(s, b, { x: x + 0.25, y: 5.52, w: 3.4, h: 0.85, fontSize: 12, color: K.g7, lineSpacingMultiple: 1.15 });
  });
}

// ---------------------------------------------------------------- 12. 경쟁
pres.addSection({ title: "경쟁" });
{
  const s = content("경쟁", "경쟁 구도", "기존 AI CCTV가 놓치는 떨어지는 물체까지 봅니다");
  const bx = 1.45, by = 1.95, bw = 6.2, bh = 4.1;
  rect(s, bx, by, bw, bh, K.white, { line: { color: K.g2, width: 1 } });
  s.addShape(pres.ShapeType.line, { x: bx + bw / 2, y: by, w: 0, h: bh, line: { color: K.g2, width: 1 } });
  s.addShape(pres.ShapeType.line, { x: bx, y: by + bh / 2, w: bw, h: 0, line: { color: K.g2, width: 1 } });
  T(s, "사후 기록", { x: bx, y: by + bh + 0.08, w: 2, h: 0.28, fontSize: 11, color: K.g5 });
  T(s, "사전 예방", { x: bx + bw - 2, y: by + bh + 0.08, w: 2, h: 0.28, fontSize: 11, color: K.g5, align: "right" });
  T(s, "낙하물\n특화", { x: M, y: by, w: 0.8, h: 0.6, fontSize: 11, color: K.g5 });
  T(s, "범용\n감지", { x: M, y: by + bh - 0.6, w: 0.8, h: 0.6, fontSize: 11, color: K.g5, valign: "bottom" });
  const bub = (x, y, d, label, hl) => {
    dot(s, x - d / 2, y - d / 2, d, hl ? K.orange : K.g2);
    T(s, label, { x: x - 1.3, y: y + d / 2 + 0.05, w: 2.6, h: 0.5, fontSize: hl ? 15 : 12, bold: hl, align: "center", color: hl ? K.ink : K.g7 });
  };
  bub(bx + 1.3, by + 3.05, 0.45, "현장 CCTV 녹화 · 관제");
  bub(bx + 3.55, by + 2.5, 0.6, "범용 AI CCTV\n(안전모 · 침입 · 화재)");
  bub(bx + 5.15, by + 3.05, 0.45, "BLE 접근 경보\n웨어러블");
  bub(bx + 4.75, by + 0.85, 0.75, "DropZero", true);
  const diff = [
    ["낙하물 사고의 전 과정", "위험요소 점검부터 하부 노출 차단, 낙하 감지, 기록까지 한 시스템이 맡습니다."],
    ["크레인을 따라 움직이는 위험구역", "출입금지 구역을 고정하지 않고 인양물 위치에 맞춰 계속 다시 그립니다."],
    ["물리 기반 판별", "중력 궤적 검증으로 오경보를 줄여, 현장이 경보를 꺼버리지 않게 합니다."],
  ];
  diff.forEach(([h, b], i) => {
    const y = 2.05 + i * 1.42;
    T(s, h, { x: 8.2, y, w: 4.5, h: 0.4, fontSize: 17, bold: true });
    T(s, b, { x: 8.2, y: y + 0.43, w: 4.5, h: 0.85, fontSize: 13, color: K.g7, lineSpacingMultiple: 1.2 });
  });
  source(s, "범용 AI CCTV 예: 카스웍스, 알체라, SAIGE 등 (각사 공개 자료 기준). 위치는 기능 범위를 비교한 개념도입니다.");
}

// ---------------------------------------------------------------- 13. 실행 계획
pres.addSection({ title: "실행 계획" });
{
  const s = content("실행 계획", "실행 계획", "내년 파일럿 현장 한 곳에서 오경보율과 지연을 잽니다");
  const ms = [
    ["2026. 11", "PoC 시연", ["더미 낙하 → 엣지 감지 → 경광등 점등", "합성 데이터로 1차 학습"]],
    ["2027 상반기", "파일럿 현장 1곳", ["인양 위험구역과 낙하 기록 실증", "오경보율 · 종단 지연 실측"]],
    ["2027 하반기", "제품화", ["스마트 안전장비 지원사업 공급 등록", "하드웨어 KC 인증"]],
    ["2028~", "확장", ["대형 건설사 API 공급", "싱가포르 등 해외 · 보험 연계"]],
  ];
  s.addShape(pres.ShapeType.line, { x: 0.9, y: 3.0, w: 11.6, h: 0, line: { color: K.g3, width: 2 } });
  ms.forEach(([d, h, bs], i) => {
    const x = 0.9 + i * 3.05;
    dot(s, x - 0.13, 2.87, 0.26, i === 0 ? K.orange : K.g8);
    T(s, d, { x, y: 2.15, w: 2.8, h: 0.4, fontSize: 15, bold: true, color: i === 0 ? K.orange : K.g7 });
    T(s, h, { x, y: 3.35, w: 2.8, h: 0.45, fontSize: 20, bold: true });
    T(s, bs.map((b, j) => ({ text: b, options: { bullet: true, breakLine: j < bs.length - 1 } })), { x, y: 3.9, w: 2.85, h: 1.2, fontSize: 13, color: K.g7, paraSpaceAfter: 6 });
  });
  rect(s, M, 5.45, 12.1, 0.9, K.paper, { round: 0.06 });
  T(s, [{ text: "파일럿 목표   ", options: { bold: true, color: K.orange } }, { text: "카메라당 오경보 시간당 0.1건 이하  ·  감지에서 경보까지 0.35초 이내  ·  위험구역 진입 경보 누락 0건" }], { x: M + 0.35, y: 5.45, w: 11.5, h: 0.9, fontSize: 15, valign: "middle" });
}

// ---------------------------------------------------------------- 14. 팀 · 요청
pres.addSection({ title: "팀" });
{
  const s = content("팀", "팀 GA", "현장만 정해지면 바로 실증에 들어갈 세 사람입니다");
  ["이승보", "이성재", "장재홍"].forEach((n, i) => {
    const x = M + i * 2.62;
    rect(s, x, 2.0, 2.42, 3.9, K.paper, { round: 0.06 });
    fallMotif(s, x + 0.45, 2.35, 0.9, 5, 0.07, K.g3);
    T(s, n, { x: x + 0.3, y: 3.65, w: 1.9, h: 0.45, fontSize: 22, bold: true });
    T(s, "역할 입력", { x: x + 0.3, y: 4.15, w: 1.9, h: 0.35, fontSize: 14, bold: true, color: K.orange });
    T(s, "전공 · 경험 입력", { x: x + 0.3, y: 4.55, w: 1.9, h: 1.1, fontSize: 12, color: K.g5 });
  });
  rect(s, 8.75, 2.0, 3.95, 3.9, K.dark, { round: 0.06 });
  T(s, "맞기 전에 막겠습니다.", { x: M, y: 6.15, w: 9, h: 0.4, fontSize: 16, bold: true, color: K.ink });
  T(s, "필요한 것", { x: 9.1, y: 2.3, w: 3.3, h: 0.4, fontSize: 18, bold: true, color: K.white });
  const asks = ["파일럿 현장 1곳\n(고층 건축 · 타워크레인 운용)", "실측 낙하 시험 장소", "건설 안전 실무 자문"];
  asks.forEach((a, i) => {
    T(s, a, { x: 9.1, y: 2.95 + i * 0.95, w: 3.3, h: 0.85, fontSize: 14, color: K.g3, lineSpacingMultiple: 1.15 });
  });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
