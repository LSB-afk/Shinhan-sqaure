# DropZero IR 피치덱 (팀 GA)

- `DropZero_IR_팀GA.pptx`: 편집용 (PowerPoint, 글꼴 Pretendard). 이미지는 모두 Blender 3D 렌더

## 다시 만들기

```bash
npm install            # 처음 한 번 (pptxgenjs, sharp)
for s in drone sim cctv droptest solution cover zone fall kit; do
  /Applications/Blender.app/Contents/MacOS/Blender -b -P render3d.py -- $s renders/$s.png 160
done
python3 post3d.py      # 렌더 후처리 → assets/*-3d.png
node build_deck.js     # PPTX 생성
./export_pdf.sh        # (필요할 때만) PowerPoint로 PDF 내보내기
```

| 파일 | 내용 |
|------|------|
| `build_deck.js` | 슬라이드 구성·문구·UI (수상작 레퍼런스 체계: 장 번호 헤더, 짙은 띠·회색 패널 레이아웃, 검은 머리줄 표) |
| `render3d.py` | Blender 장면: 드론, 시뮬레이션·CCTV·낙하 시험, 현장 전경(표지·솔루션), 위험구역, 낙하 다중 노출, KIT 제품 컷. 모델은 모두 기본 도형으로 직접 만듦 |
| `post3d.py` | CCTV 화면 표시·검출 박스, 카드용 둥근 모서리, 배지·시간 라벨 좌표(json) 복사 |

PPTX를 PowerPoint에서 직접 고쳐도 된다. 다시 생성하면 직접 고친 내용은 덮어쓰이니, 큰 수정은 스크립트에서 한다.
