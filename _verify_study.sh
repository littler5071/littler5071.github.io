#!/usr/bin/env bash
# 驗證 /study/ 頁面與 8 個 PDF 上線
BASE="https://littler5071.github.io"
PAGES=("/study/" "/study/pdf/g2-guowen.pdf" "/study/pdf/g2-history.pdf" "/study/pdf/g2-geography.pdf" \
       "/study/pdf/g2-civics.pdf" "/study/pdf/g2-science.pdf" "/study/pdf/g2-math.pdf" \
       "/study/pdf/chengyu-117.pdf" "/study/pdf/guowen-jueju-lvshi.pdf")
for try in 1 2 3 4 5 6; do
  ok=0; total=0
  for p in "${PAGES[@]}"; do
    total=$((total+1))
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 25 -L "$BASE$p?v=$try")
    [ "$code" = "200" ] && ok=$((ok+1))
  done
  echo "第 ${try} 輪：$ok/$total 個 200"
  if [ "$ok" = "$total" ]; then echo "  ✓ 全部上線"; break; fi
  sleep 30
done
echo
echo "=== 逐項狀態 ==="
for p in "${PAGES[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 25 -L "$BASE$p")
  size=$(curl -s -o /dev/null -w "%{size_download}" --max-time 25 -L "$BASE$p")
  printf "  %-38s %s  %s bytes\n" "$p" "$code" "$size"
done
echo
echo "=== 遠端 nav.js 有沒有「段考複習」 ==="
curl -s --max-time 25 "$BASE/nav.js" | grep -c "段考複習" | sed 's/^/  出現次數: /'
echo
echo "=== /study/ 頁面內容抽查 ==="
BODY=$(curl -s --max-time 25 -L "$BASE/study/")
for k in "段考複習講義" "絕句 與 律詩" "chengyu-117.pdf" "guowen-jueju-lvshi.pdf" 'class="hnav"' ; do
  printf "  %-24s %s 次\n" "$k" "$(echo "$BODY" | grep -c -- "$k")"
done
