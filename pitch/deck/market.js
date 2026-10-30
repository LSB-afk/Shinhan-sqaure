// 시장 슬라이드 2장 (국내 TAM/SAM/SOM, 해외 성장·규제). 수치·출처는 2026-10-30 조사 기준.
const USD = 1380; // 원/달러 환산 기준

function slide(pres, { content, T, rect, dot, source, K, HEX, M }) {
  // ---------------------------------------------------------------- 10. 국내 시장
  {
    const s = content("시장", "시장 규모 · 국내", "국내 스마트 안전장비 예산 한도는 연 7,430억 원입니다");
    // 동심원: TAM ⊃ SAM ⊃ SOM (아래 기준선 정렬)
    const cx = 3.35, base = 6.35;
    const ring = (d, fill, line) => s.addShape(pres.ShapeType.ellipse, { x: cx - d / 2, y: base - d, w: d, h: d, fill: { color: fill }, line: { color: line, width: 1 } });
    ring(4.3, K.paper, K.g2);
    ring(2.75, K.g2, K.g3);
    ring(1.1, K.orange, K.orange);
    T(s, "TAM", { x: cx - 1, y: base - 4.05, w: 2, h: 0.3, fontSize: 12, bold: true, color: K.g5, align: "center" });
    T(s, "3.7조 원", { x: cx - 1.2, y: base - 3.75, w: 2.4, h: 0.45, fontSize: 22, bold: true, align: "center" });
    T(s, "SAM", { x: cx - 1, y: base - 2.5, w: 2, h: 0.3, fontSize: 12, bold: true, color: K.g7, align: "center" });
    T(s, "7,430억 원", { x: cx - 1.2, y: base - 2.2, w: 2.4, h: 0.45, fontSize: 22, bold: true, align: "center" });
    T(s, "SOM", { x: cx - 0.5, y: base - 0.82, w: 1, h: 0.25, fontSize: 10, bold: true, color: K.white, align: "center" });
    T(s, "60억", { x: cx - 0.55, y: base - 0.58, w: 1.1, h: 0.35, fontSize: 15, bold: true, color: K.white, align: "center" });

    const rows = [
      ["TAM", "글로벌 건설현장 안전 모니터링 시장", "27.1억 달러 (2025) → 2030년 6.4조 원, 연 11.3% 성장"],
      ["SAM", "국내 산안비 중 스마트 안전장비 사용 한도 (연)", "건설수주 221.1조 원 × 70% × 요율 2.4% = 산안비 약 3.7조 원\n× 스마트 장비 사용한도 20% = 약 7,430억 원 (규정상 최대치)"],
      ["SOM", "5년 차 목표 매출", "200개 현장 × 월 250만 원 × 12개월 = 60억 원 (SAM의 0.8%)"],
    ];
    rows.forEach(([k, h, b], i) => {
      const y = 2.0 + i * 1.45;
      T(s, k, { x: 6.55, y, w: 0.8, h: 0.35, fontSize: 14, bold: true, color: i === 2 ? K.orange : K.g5 });
      T(s, h, { x: 7.35, y, w: 5.35, h: 0.38, fontSize: 17, bold: true });
      T(s, b, { x: 7.35, y: y + 0.42, w: 5.35, h: 0.9, fontSize: 12.5, color: K.g7, lineSpacingMultiple: 1.2 });
    });
    rect(s, 6.55, 5.85, 6.15, 0.62, K.paper, { round: 0.08 });
    T(s, "단가 점검 · 공사비 300억 원 현장의 스마트 장비 한도는 월 약 330만 원, 구독료 월 250만 원은 그 안에 들어갑니다.", { x: 6.75, y: 5.85, w: 5.8, h: 0.62, fontSize: 11.5, color: K.g8, valign: "middle" });
    source(s, `출처: 건설산업연구원 건설동향브리핑 1055호(2026. 4.), 고용노동부고시 제2024-53호·제2025-11호, Research and Markets(Knowledge Sourcing, 2025. 2.). 환율 ${USD.toLocaleString()}원/달러. 대상 70%·요율 2.4%·현장 수·단가는 가정`);
  }

  // ---------------------------------------------------------------- 11. 해외 시장
  {
    const s = content("시장", "시장 규모 · 해외", "해외 건설현장 안전 모니터링 시장은 2030년 6.4조 원으로 커집니다");
    s.addChart(pres.ChartType.bar, [
      { name: "2024~25년", labels: ["건설현장 안전 모니터링", "건설 AI", "건설 드론"], values: [3.73, 6.84, 6.35] },
      { name: "2030년", labels: ["건설현장 안전 모니터링", "건설 AI", "건설 드론"], values: [6.37, 20.3, 9.8] },
    ], {
      x: M, y: 1.95, w: 6.9, h: 4.45, barDir: "col", barGrouping: "clustered", barGapWidthPct: 70,
      chartColors: [HEX.accent4, HEX.accent1],
      showTitle: true, title: "글로벌 시장 규모 (조 원)", titleFontSize: 13, titleColor: HEX.accent3, titleFontFace: "+mn-lt",
      showLegend: true, legendPos: "t", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.accent3,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelFontSize: 12, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt", dataLabelFontBold: true,
      catAxisLabelColor: HEX.accent3, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    });
    const drivers = [
      ["싱가포르", "2024년 6월부터 계약금액 S$500만 이상 현장의 고위험 작업 구역에 영상감시 설치 의무화", "MOM, 2024. 5."],
      ["미국", "‘물체에 맞음(Struck-by)’은 건설 4대 위험 중 사망 2위. 2023년 154명", "CPWR, 2025. 4."],
      ["한국 건설사 해외 현장", "국내에서 검증한 패키지를 한국 건설사가 해외 현장에 나갈 때 같이 가져갑니다", "진출 전략"],
    ];
    drivers.forEach(([h, b, src], i) => {
      const y = 2.0 + i * 1.45;
      rect(s, 7.95, y, 4.75, 1.25, K.paper, { round: 0.06 });
      T(s, h, { x: 8.2, y: y + 0.15, w: 3.0, h: 0.35, fontSize: 16, bold: true });
      T(s, src, { x: 10.9, y: y + 0.17, w: 1.6, h: 0.3, fontSize: 10, color: K.g5, align: "right" });
      T(s, b, { x: 8.2, y: y + 0.55, w: 4.3, h: 0.65, fontSize: 12.5, color: K.g7, lineSpacingMultiple: 1.15 });
    });
    source(s, `출처: Research and Markets(Knowledge Sourcing 2025. 2. / GSBR 2025. 9.), Mordor Intelligence(건설 AI, 2025→2030). 건설 드론은 2024년 기준. 환율 ${USD.toLocaleString()}원/달러`);
  }
}

module.exports = { slide };
