#!/bin/zsh
# PowerPoint로 PPTX → PDF (Pretendard가 그대로 들어간다).
# PowerPoint는 샌드박스라 자기 컨테이너 폴더에만 쓸 수 있어서, 거기서 저장한 뒤 옮긴다.
set -e
cd "$(dirname "$0")"
NAME="DropZero_IR_팀GA"
C="$HOME/Library/Containers/com.microsoft.Powerpoint/Data/tmp"
mkdir -p "$C"
rm -f "$C/deck.pdf"
cp "$NAME.pptx" "$C/deck.pptx"
osascript <<EOF
tell application "Microsoft PowerPoint"
  try
    close every presentation saving no
  end try
  open POSIX file "$C/deck.pptx"
  repeat 40 times
    if (count of presentations) > 0 then exit repeat
    delay 0.5
  end repeat
  save presentation 1 in ((POSIX file "$C/deck.pdf") as string) as save as PDF
  close every presentation saving no
end tell
EOF
mv "$C/deck.pdf" "$NAME.pdf"
echo "wrote $NAME.pdf"
