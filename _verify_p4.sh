#!/bin/bash
# 驗證 Part 4 頁面與加密頁是否都正確
P="https://littler5071.github.io/toeic/p4-full/"
echo "== Part 4 頁面 =="
echo "HTTP: $(curl -s -o /dev/null -w '%{http_code}' "$P")"
HTML=$(curl -s "$P")
echo "頁面大小: $(printf '%s' "$HTML" | wc -c) bytes"
echo "含 Part 4 字樣: $(printf '%s' "$HTML" | grep -c 'Part 4')"
echo "含原創聲明: $(printf '%s' "$HTML" | grep -c '原創')"
echo "quiz.js 引用: $(printf '%s' "$HTML" | grep -c 'quiz.js')"
echo "音檔引用數: $(printf '%s' "$HTML" | grep -o 'audio/[^"]*\.mp3' | sort -u | wc -l)"
echo "== 音檔抽測 =="
for f in toeic_p4_full.mp3 toeic_p4_full_explain.mp3; do
  SZ=$(curl -s -o /dev/null -w '%{http_code} %{size_download}' -r 0-1 "$P/audio/$f")
  echo "  $f → $SZ (只抓前 2 bytes)"
done
echo "== 分類頁卡片 =="
echo "/toeic/ 含 Part 4: $(curl -s https://littler5071.github.io/toeic/ | grep -c 'Part 4')"
echo "首頁含 p4-full: $(curl -s https://littler5071.github.io/ | grep -c 'p4-full')"
echo "== 加密頁是否仍受保護 =="
echo "/ai/hdd-ai/ 明文外洩: $(curl -s https://littler5071.github.io/ai/hdd-ai/ | grep -c '可行性評估') (應為 0)"
echo "/ai/hdd-ai/ 加密痕跡: $(curl -s https://littler5071.github.io/ai/hdd-ai/ | grep -c -i staticrypt) (應 >0)"
echo "/toeic/ 是否有導覽注入到加密頁: $(curl -s https://littler5071.github.io/ai/hdd-ai/ | grep -c 'hermesnav') (應為 0)"
