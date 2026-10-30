// 피치덱 일러스트 생성기: node art.js → assets/*.png
// 그림 안에는 글자를 넣지 않는다(라벨은 PPT 텍스트로 얹어 편집 가능하게).
// 드론은 산업용 점검 드론(DJI Matrice 350급) 정면 실루엣을 참고해 직접 그렸다.
const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const OUT = path.join(__dirname, "assets");
const ORANGE = "#FF5A1F";

// 밝은 배경 / 어두운 배경 팔레트
const LIGHT = { bg: "none", ink: "#2B2F35", mid: "#5C626B", soft: "#A3A9B1", pale: "#D9DCE0", wall: "#EEF0F2", glass: "#C9D1DA", ground: "#8A9099" };
const DARK = { bg: "none", ink: "#C9CDD3", mid: "#8D939B", soft: "#5E646C", pale: "#3A3F46", wall: "#262A2F", glass: "#31373E", ground: "#4A5058" };

const svg = (w, h, body) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`;

// 자유낙하 점 궤적: 같은 시간 간격 → 점 사이가 점점 벌어진다 (덱 전체의 모티프)
function fallDots(x, y0, y1, n, r, color, lastColor = ORANGE) {
  let s = "";
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const y = y0 + (y1 - y0) * t * t;
    const last = i === n;
    s += `<circle cx="${x + 6 * t}" cy="${y}" r="${last ? r * 1.7 : r}" fill="${last ? lastColor : color}"/>`;
  }
  return s;
}

function worker(x, y, p, vest = ORANGE, scale = 1) {
  // y = 발 위치. ISO 픽토그램 비율(머리 1 : 몸 3)
  const k = scale;
  return `<g transform="translate(${x},${y}) scale(${k})">
    <rect x="-6" y="-26" width="5" height="26" rx="2.5" fill="${p.ink}"/>
    <rect x="1" y="-26" width="5" height="26" rx="2.5" fill="${p.ink}"/>
    <rect x="-9" y="-52" width="18" height="28" rx="5" fill="${vest}"/>
    <rect x="-9" y="-41" width="18" height="3" fill="#FFFFFF" opacity=".8"/>
    <circle cx="0" cy="-60" r="7" fill="#E8C4A8"/>
    <path d="M-9,-61 A9,9 0 0 1 9,-61 L10,-59 L-10,-59 Z" fill="#FFFFFF" stroke="${p.mid}" stroke-width=".8"/>
  </g>`;
}

function building(x, ground, floors, fh, w, p, opts = {}) {
  const top = ground - floors * fh;
  let s = `<rect x="${x}" y="${top}" width="${w}" height="${floors * fh}" fill="${p.wall}"/>`;
  const bays = opts.bays || 4;
  const bw = w / bays;
  for (let f = 0; f < floors - 3; f++) {
    for (let b = 0; b < bays; b++) {
      s += `<rect x="${x + b * bw + 8}" y="${ground - (f + 1) * fh + 7}" width="${bw - 16}" height="${fh - 14}" fill="${p.glass}"/>`;
    }
  }
  for (let f = 0; f <= floors; f++) s += `<rect x="${x - 6}" y="${ground - f * fh - 3}" width="${w + 12}" height="6" fill="${p.mid}"/>`;
  for (let b = 0; b <= bays; b++) s += `<rect x="${x + b * bw - 3}" y="${top - fh * 0.9}" width="6" height="${floors * fh + fh * 0.9}" fill="${p.ink}"/>`;
  // 최상층 거푸집 + 안전난간
  s += `<rect x="${x + bw}" y="${top - fh * 0.75}" width="${bw * 1.2}" height="${fh * 0.75}" fill="#C79A63"/>`;
  s += `<rect x="${x - 6}" y="${top - fh * 0.45}" width="${w + 12}" height="2.5" fill="${ORANGE}"/>`;
  // 낙하물방지망 (좌측 외벽)
  for (const f of opts.nets || []) {
    const yy = ground - f * fh;
    s += `<polygon points="${x - 6},${yy} ${x - 46},${yy - 16} ${x - 46},${yy - 12} ${x - 6},${yy + 4}" fill="${p.soft}"/>`;
  }
  return s;
}

function crane(mx, ground, top, jibL, jibR, p) {
  // 플랫탑 타워크레인: 마스트, 지브, 카운터지브, 운전실
  let s = `<rect x="${mx - 11}" y="${top}" width="22" height="${ground - top}" fill="none" stroke="${p.ink}" stroke-width="3"/>`;
  for (let y = top; y + 22 <= ground; y += 22) {
    s += `<line x1="${mx - 11}" y1="${y}" x2="${mx + 11}" y2="${y + 22}" stroke="${p.ink}" stroke-width="1.6"/>`;
    s += `<line x1="${mx + 11}" y1="${y}" x2="${mx - 11}" y2="${y + 22}" stroke="${p.ink}" stroke-width="1.6"/>`;
  }
  const jy = top - 14;
  s += `<rect x="${mx - jibL}" y="${jy}" width="${jibL + jibR}" height="14" fill="none" stroke="${p.ink}" stroke-width="3"/>`;
  for (let x = mx - jibL; x < mx + jibR; x += 16) s += `<line x1="${x}" y1="${jy + 14}" x2="${x + 8}" y2="${jy}" stroke="${p.ink}" stroke-width="1.4"/><line x1="${x + 8}" y1="${jy}" x2="${x + 16}" y2="${jy + 14}" stroke="${p.ink}" stroke-width="1.4"/>`;
  s += `<rect x="${mx - jibL + 6}" y="${jy + 14}" width="44" height="30" fill="${p.mid}"/>`;
  s += `<rect x="${mx + 12}" y="${top - 2}" width="30" height="26" rx="3" fill="${p.mid}"/><rect x="${mx + 17}" y="${top + 3}" width="20" height="11" fill="${p.glass}"/>`;
  s += `<rect x="${mx - 20}" y="${ground - 8}" width="40" height="8" fill="${p.ink}"/>`;
  return { svg: s, jy };
}

function hookLoad(x, jy, loadY, p) {
  return `<rect x="${x - 12}" y="${jy + 14}" width="24" height="8" fill="${p.ink}"/>
    <line x1="${x}" y1="${jy + 22}" x2="${x}" y2="${loadY - 16}" stroke="${p.ink}" stroke-width="2"/>
    <path d="M${x - 4},${loadY - 18} q4,8 8,0" fill="none" stroke="${p.ink}" stroke-width="2.5"/>
    <line x1="${x}" y1="${loadY - 14}" x2="${x - 38}" y2="${loadY}" stroke="${p.ink}" stroke-width="1.6"/>
    <line x1="${x}" y1="${loadY - 14}" x2="${x + 38}" y2="${loadY}" stroke="${p.ink}" stroke-width="1.6"/>
    <rect x="${x - 44}" y="${loadY}" width="88" height="22" fill="${p.mid}"/>
    ${[0, 1, 2].map(i => `<line x1="${x - 44}" y1="${loadY + 6 + i * 6}" x2="${x + 44}" y2="${loadY + 6 + i * 6}" stroke="${p.ink}" stroke-width="1"/>`).join("")}`;
}

function zone(x, loadY, ground, half, margin, p) {
  // 인양물 투영 + 안전반경: 사다리꼴 음영 + 지면 띠
  return `<polygon points="${x - half},${loadY + 22} ${x + half},${loadY + 22} ${x + half + margin},${ground} ${x - half - margin},${ground}" fill="${ORANGE}" opacity=".10"/>
    <line x1="${x - half}" y1="${loadY + 22}" x2="${x - half - margin}" y2="${ground}" stroke="${ORANGE}" stroke-width="2" stroke-dasharray="7 6"/>
    <line x1="${x + half}" y1="${loadY + 22}" x2="${x + half + margin}" y2="${ground}" stroke="${ORANGE}" stroke-width="2" stroke-dasharray="7 6"/>
    <rect x="${x - half - margin}" y="${ground - 7}" width="${2 * (half + margin)}" height="7" fill="${ORANGE}" opacity=".85"/>`;
}

function cctv(x, y, dir, p) {
  // dir: -1 왼쪽을 바라봄
  const s = dir < 0 ? 1 : -1;
  return `<g transform="translate(${x},${y}) scale(${s},1)">
    <rect x="-34" y="-9" width="34" height="18" rx="4" fill="${p.ink}"/>
    <rect x="-40" y="-7" width="8" height="14" rx="2" fill="${p.mid}"/>
    <circle cx="-38" cy="0" r="3" fill="${ORANGE}"/>
    <rect x="-4" y="6" width="5" height="12" fill="${p.ink}"/></g>`;
}

function beacon(x, ground, h, p) {
  return `<rect x="${x - 2}" y="${ground - h}" width="4" height="${h}" fill="${p.mid}"/>
    <rect x="${x - 9}" y="${ground - h - 18}" width="18" height="18" rx="5" fill="${ORANGE}"/>
    ${[-50, -20, 20, 50].map(a => { const r = (a - 90) * Math.PI / 180; return `<line x1="${x + 15 * Math.cos(r)}" y1="${ground - h - 9 + 15 * Math.sin(r)}" x2="${x + 24 * Math.cos(r)}" y2="${ground - h - 9 + 24 * Math.sin(r)}" stroke="${ORANGE}" stroke-width="2.4" stroke-linecap="round"/>`; }).join("")}`;
}

function edgeBox(x, y, w, h, p) {
  // 방열핀이 있는 산업용 엣지 컴퓨터 함체
  let s = `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="${p.ink}"/>`;
  for (let i = 0; i < 6; i++) s += `<rect x="${x + 10 + i * (w - 20) / 6}" y="${y - 8}" width="${(w - 20) / 6 - 5}" height="10" rx="1.5" fill="${p.mid}"/>`;
  s += `<circle cx="${x + w - 16}" cy="${y + h - 14}" r="4" fill="${ORANGE}"/>`;
  s += `<rect x="${x + 12}" y="${y + h - 18}" width="${w * 0.35}" height="6" rx="3" fill="${p.mid}"/>`;
  s += `<rect x="${x + w * 0.7}" y="${y - 30}" width="3" height="24" fill="${p.mid}"/>`;
  return s;
}

function drone(cx, cy, k, p, spin = true) {
  // 정면 3/4 시점. 뒤쪽 암·로터는 흐리게, 앞쪽은 진하게
  const P = (x, y) => `${cx + x * k},${cy + y * k}`;
  const prop = (x, y, back) => spin
    ? `<ellipse cx="${cx + x * k}" cy="${cy + y * k}" rx="${62 * k}" ry="${5.5 * k}" fill="${back ? p.pale : p.soft}" opacity="${back ? .9 : .75}"/>`
    : `<line x1="${cx + (x - 60) * k}" y1="${cy + y * k}" x2="${cx + (x + 60) * k}" y2="${cy + y * k}" stroke="${p.mid}" stroke-width="${4 * k}"/>`;
  const motor = (x, y, back) => `<rect x="${cx + (x - 9) * k}" y="${cy + (y - 4) * k}" width="${18 * k}" height="${20 * k}" rx="${4 * k}" fill="${back ? p.mid : p.ink}"/>`;
  let s = "";
  // 뒤쪽 암(위쪽, 짧게)
  for (const sx of [-1, 1]) {
    const x = 118 * sx, y = -26;
    s += `<polygon points="${P(-20 * sx, -4)} ${P(x, y + 8)} ${P(x, y + 15)} ${P(-20 * sx, 8)}" fill="${p.mid}"/>` + motor(x, y, true) + prop(x, y - 6, true);
  }
  // 착륙 다리
  for (const sx of [-1, 1]) {
    s += `<polygon points="${P(14 * sx, 30)} ${P(64 * sx, 112)} ${P(72 * sx, 112)} ${P(24 * sx, 30)}" fill="${p.ink}"/>`;
    s += `<rect x="${cx + (sx > 0 ? 44 : -96) * k}" y="${cy + 110 * k}" width="${52 * k}" height="${7 * k}" rx="${3.5 * k}" fill="${p.ink}"/>`;
  }
  // 동체 + 배터리 블록 + 안테나
  s += `<rect x="${cx - 46 * k}" y="${cy - 22 * k}" width="${92 * k}" height="${54 * k}" rx="${10 * k}" fill="${p.ink}"/>`;
  s += `<rect x="${cx - 30 * k}" y="${cy - 46 * k}" width="${60 * k}" height="${26 * k}" rx="${5 * k}" fill="${p.mid}"/>`;
  s += `<rect x="${cx - 22 * k}" y="${cy - 40 * k}" width="${44 * k}" height="${4 * k}" rx="${2 * k}" fill="${p.soft}"/>`;
  for (const sx of [-1, 1]) s += `<rect x="${cx + (sx * 38 - 2) * k}" y="${cy - 40 * k}" width="${4 * k}" height="${20 * k}" rx="${2 * k}" fill="${p.mid}"/>`;
  s += `<rect x="${cx - 30 * k}" y="${cy - 8 * k}" width="${60 * k}" height="${10 * k}" rx="${3 * k}" fill="${p.mid}"/>`;
  // 앞쪽 암(아래로, 길게) + 모터 + 로터 + 항법등
  for (const sx of [-1, 1]) {
    const x = 168 * sx, y = 2;
    s += `<polygon points="${P(-34 * sx, 0)} ${P(x, y + 8)} ${P(x, y + 17)} ${P(-34 * sx, 16)}" fill="${p.ink}"/>` + motor(x, y, false) + prop(x, y - 6, false);
    s += `<circle cx="${cx + x * k}" cy="${cy + (y + 20) * k}" r="${3.5 * k}" fill="${ORANGE}"/>`;
  }
  // 짐벌 카메라
  s += `<rect x="${cx - 4 * k}" y="${cy + 30 * k}" width="${8 * k}" height="${12 * k}" fill="${p.mid}"/>`;
  s += `<rect x="${cx - 20 * k}" y="${cy + 40 * k}" width="${40 * k}" height="${30 * k}" rx="${8 * k}" fill="${p.ink}"/>`;
  s += `<circle cx="${cx}" cy="${cy + 55 * k}" r="${10 * k}" fill="${p.mid}"/><circle cx="${cx}" cy="${cy + 55 * k}" r="${6 * k}" fill="#111316"/><circle cx="${cx}" cy="${cy + 55 * k}" r="${10 * k}" fill="none" stroke="${ORANGE}" stroke-width="${2 * k}"/>`;
  return s;
}

// ---------------------------------------------------------------- 장면
function sceneSite(p, w = 1600, h = 900) {
  const G = 820;
  let s = `<rect x="0" y="${G}" width="${w}" height="${h - G}" fill="${p.pale}"/>`;
  s += building(170, G, 11, 56, 360, p, { nets: [4, 8] });
  const c = crane(1010, G, 170, 300, 520, p);
  s += c.svg;
  s += zone(1300, 420, G, 44, 38, p) + hookLoad(1300, c.jy, 420, p);
  s += fallDots(552, 214, G - 6, 7, 5.5, p.mid);
  s += cctv(998, 360, -1, p) + `<polygon points="960,360 560,250 560,520" fill="${ORANGE}" opacity=".06"/>`;
  s += beacon(1500, G, 150, p) + beacon(700, G, 110, p);
  s += edgeBox(760, G - 70, 120, 70, p);
  s += worker(1330, G, p) + worker(640, G, p) + worker(470, G - 616, p, ORANGE, .9);
  s += `<path d="M110,175 Q330,-20 590,175" fill="none" stroke="${p.soft}" stroke-width="2" stroke-dasharray="8 7"/>`;
  s += drone(345, 64, .6, p);
  return svg(w, h, s);
}

function sceneFall(p, w = 900, h = 1000) {
  const G = 940;
  let s = `<rect x="0" y="${G}" width="${w}" height="${h - G}" fill="${p.pale}"/>`;
  s += building(80, G, 10, 76, 320, p, { bays: 3, nets: [3, 7] });
  // 0.5 s 간격 위치: y = ½gt² × (픽셀/미터)
  const top = G - 760, ppm = 760 / 30.3;
  for (let i = 0; i <= 5; i++) {
    const t = Math.min(i * 0.5, 2.485);
    const y = top + 0.5 * 9.81 * t * t * ppm;
    const yy = Math.min(y, G - 9);
    s += `<line x1="430" y1="${yy}" x2="${i ? 470 : 470}" y2="${yy}" stroke="${p.soft}" stroke-width="1.5" stroke-dasharray="3 4"/>`;
    s += `<circle cx="${430 + i * 3}" cy="${yy}" r="${i === 5 ? 11 : 7}" fill="${i === 5 ? ORANGE : p.ink}"/>`;
  }
  s += `<polyline points="${Array.from({ length: 41 }, (_, i) => { const t = 2.485 * i / 40; return `${430 + t * 6},${Math.min(top + 0.5 * 9.81 * t * t * ppm, G - 9)}`; }).join(" ")}" fill="none" stroke="${p.soft}" stroke-width="2" stroke-dasharray="2 6"/>`;
  s += worker(380, G - 760, p, ORANGE, 1.1) + worker(800, G, p, ORANGE, 1.1);
  return svg(w, h, s);
}

function sceneZone(p, w = 1000, h = 800) {
  const G = 740;
  let s = `<rect x="0" y="${G}" width="${w}" height="${h - G}" fill="${p.pale}"/>`;
  const jy = 60;
  s += `<rect x="0" y="${jy}" width="${w}" height="16" fill="none" stroke="${p.ink}" stroke-width="3"/>`;
  for (let x = 0; x < w; x += 18) s += `<line x1="${x}" y1="${jy + 16}" x2="${x + 9}" y2="${jy}" stroke="${p.ink}" stroke-width="1.5"/><line x1="${x + 9}" y1="${jy}" x2="${x + 18}" y2="${jy + 16}" stroke="${p.ink}" stroke-width="1.5"/>`;
  // 이전 위치(희미하게) → 현재 위치
  s += `<g opacity=".28">${zone(330, 330, G, 60, 50, p)}${hookLoad(330, jy - 2, 330, p)}</g>`;
  s += zone(600, 330, G, 60, 50, p) + hookLoad(600, jy - 2, 330, p);
  s += `<path d="M390,300 L520,300" stroke="${p.mid}" stroke-width="3" marker-end="url(#a)"/>`;
  s = `<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="${p.mid}"/></marker></defs>` + s;
  s += worker(660, G, p, ORANGE, 1.25);
  s += `<circle cx="660" cy="${G - 42}" r="58" fill="none" stroke="${ORANGE}" stroke-width="3" stroke-dasharray="9 7"/>`;
  s += worker(860, G, p, ORANGE, 1.25) + beacon(930, G, 190, p);
  return svg(w, h, s);
}

function sceneDrone(p, w = 900, h = 560) {
  return svg(w, h, drone(450, 230, 1.9, p));
}


// 기술 슬라이드: 합성 데이터 3단계 (시뮬레이션 → 실영상 합성 → 실측 검증)
function synthSim(p, w = 520, h = 360) {
  let s = `<rect width="${w}" height="${h}" rx="14" fill="#1F2328"/>`;
  const L = "#6B7480";
  s += `<polygon points="120,90 220,60 320,90 220,120" fill="none" stroke="${L}" stroke-width="1.6"/>`;
  s += `<polyline points="120,90 120,300 220,330 220,120" fill="none" stroke="${L}" stroke-width="1.6"/>`;
  s += `<polyline points="220,330 320,300 320,90" fill="none" stroke="${L}" stroke-width="1.6"/>`;
  for (let i = 1; i < 7; i++) {
    const y = 90 + i * 30;
    s += `<line x1="120" y1="${y}" x2="220" y2="${y + 30}" stroke="${L}" stroke-opacity=".5"/><line x1="220" y1="${y + 30}" x2="320" y2="${y}" stroke="${L}" stroke-opacity=".5"/>`;
  }
  const tr = [[230, 96, 18], [262, 104, 34], [292, 110, 52], [318, 96, 74], [200, 88, -22]];
  tr.forEach(([x, y, dx], i) => {
    let d = "";
    for (let k = 0; k <= 8; k++) { const t = k / 8; d += `${x + dx * t},${y + (300 - y) * t * t} `; }
    s += `<polyline points="${d}" fill="none" stroke="${i === 2 ? ORANGE : "#C9CDD3"}" stroke-width="2" stroke-dasharray="2 6" stroke-linecap="round"/>`;
    s += `<rect x="${x + dx * .55 - 4}" y="${y + (300 - y) * .3}" width="8" height="14" rx="2" fill="${i === 2 ? ORANGE : "#C9CDD3"}"/>`;
  });
  s += `<line x1="60" y1="335" x2="460" y2="335" stroke="#3A4048" stroke-width="2"/>`;
  return svg(w, h, s);
}

function synthComposite(p, w = 520, h = 360) {
  let s = `<defs><clipPath id="cc"><rect width="${w}" height="${h}" rx="14"/></clipPath></defs><g clip-path="url(#cc)"><rect width="${w}" height="${h}" fill="#E9ECEF"/>`;
  s += `<rect x="40" y="60" width="200" height="300" fill="#CFD5DC"/><rect x="250" y="120" width="150" height="240" fill="#D9DEE3"/>`;
  for (let y = 80; y < 350; y += 30) for (let x = 55; x < 230; x += 45) s += `<rect x="${x}" y="${y}" width="32" height="18" fill="#BAC2CB"/>`;
  for (let y = 140; y < 350; y += 34) for (let x = 262; x < 390; x += 42) s += `<rect x="${x}" y="${y}" width="28" height="20" fill="#C6CDD5"/>`;
  s += `<rect x="415" y="40" width="70" height="320" fill="#DDE1E6"/>`;
  // 합성된 낙하물 + 모션 블러
  s += `<g transform="rotate(18 300 150)"><rect x="294" y="108" width="12" height="26" rx="2" fill="${ORANGE}" opacity=".25"/><rect x="294" y="122" width="12" height="26" rx="2" fill="${ORANGE}" opacity=".5"/><rect x="294" y="136" width="12" height="26" rx="2" fill="${ORANGE}"/></g>`;
  s += `<rect x="276" y="98" width="52" height="78" fill="none" stroke="${ORANGE}" stroke-width="2.5" stroke-dasharray="6 4"/>`;
  s += `<rect x="20" y="20" width="${w - 40}" height="${h - 40}" fill="none" stroke="#8A9099" stroke-width="2"/>`;
  for (const [x, y, dx, dy] of [[20, 20, 1, 1], [w - 20, 20, -1, 1], [20, h - 20, 1, -1], [w - 20, h - 20, -1, -1]])
    s += `<polyline points="${x},${y + 26 * dy} ${x},${y} ${x + 26 * dx},${y}" fill="none" stroke="#2B2F35" stroke-width="4"/>`;
  return svg(w, h, s + "</g>");
}

function synthTest(p, w = 520, h = 360) {
  let s = `<rect width="${w}" height="${h}" rx="14" fill="#F2F3F5"/>`;
  s += `<rect x="70" y="40" width="26" height="290" fill="#5C626B"/><rect x="70" y="40" width="150" height="16" fill="#5C626B"/>`;
  s += `<line x1="200" y1="56" x2="200" y2="80" stroke="#2B2F35" stroke-width="2"/><rect x="190" y="80" width="20" height="14" rx="3" fill="#2B2F35"/>`;
  s += fallDots(200, 104, 312, 6, 5, "#5C626B");
  for (let i = 0; i <= 6; i++) { const y = 70 + i * 40; s += `<line x1="250" y1="${y}" x2="${i % 2 ? 262 : 272}" y2="${y}" stroke="#8A9099" stroke-width="2"/>`; }
  s += `<line x1="250" y1="70" x2="250" y2="310" stroke="#8A9099" stroke-width="2"/>`;
  s += `<rect x="40" y="318" width="440" height="12" fill="#C9CED4"/>`;
  s += cctv(440, 120, -1, LIGHT) + `<rect x="436" y="138" width="5" height="180" fill="#5C626B"/>`;
  s += `<polygon points="400,120 230,80 230,300" fill="${ORANGE}" opacity=".08"/>`;
  return svg(w, h, s);
}

async function render(name, svgStr, scale = 2) {
  const file = path.join(OUT, name + ".png");
  await sharp(Buffer.from(svgStr), { density: 72 * scale }).png().toFile(file);
  fs.writeFileSync(path.join(OUT, name + ".svg"), svgStr);
  console.log("wrote", name);
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  await render("site-dark", sceneSite(DARK));
  await render("site-light", sceneSite(LIGHT));
  await render("fall", sceneFall(LIGHT));
  await render("zone", sceneZone(LIGHT));
  await render("drone", sceneDrone(LIGHT));
  await render("synth-sim", synthSim(LIGHT));
  await render("synth-composite", synthComposite(LIGHT));
  await render("synth-test", synthTest(LIGHT));
})();
