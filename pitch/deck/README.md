# DropZero IR 피치덱 (팀 GA)

- `DropZero_IR_팀GA.pptx`: 편집용 (PowerPoint, 글꼴 Pretendard)
- `DropZero_IR_팀GA.pdf`: 제출용 (PowerPoint에서 내보냄, 15장)

## 다시 만들기

```bash
npm install            # 처음 한 번 (pptxgenjs, sharp)
node art.js            # assets/ 일러스트 생성
node build_deck.js     # PPTX 생성
./export_pdf.sh        # PowerPoint로 PDF 내보내기
```

| 파일 | 내용 |
|------|------|
| `build_deck.js` | 슬라이드 구성·문구 (시장 2장은 `market.js`) |
| `art.js` | 드론·크레인·현장 일러스트. 그림 안에 글자 없음, 라벨은 PPT 텍스트 |

PPTX를 PowerPoint에서 직접 고쳐도 된다. 다시 생성하면 직접 고친 내용은 덮어쓰이니, 큰 수정은 스크립트에서 한다.
