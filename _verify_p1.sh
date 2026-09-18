#!/bin/bash
P="https://littler5071.github.io/toeic/p1-full/"
echo "== Part 1 頁面 =="
echo "HTTP: $(curl -s -o /dev/null -w '%{http_code}' "$P")"
HTML=$(curl -s "$P")
echo "大小: $(printf '%s' "$HTML" | wc -c) bytes"
echo "含 Part 1: $(printf '%s' "$HTML" | grep -c 'Part 1')"
echo "照片數(img): $(printf '%s' "$HTML" | grep -o 'img/[^"]*\.\(jpg\|jpeg\|png\|webp\)' | sort -u | wc -l)"
echo "音檔數: $(printf '%s' "$HTML" | grep -o 'audio/[^"]*\.mp3' | sort -u | wc -l)"
echo "quiz.js: $(printf '%s' "$HTML" | grep -c 'quiz.js')"
echo "原創聲明: $(printf '%s' "$HTML" | grep -c '原創')"
echo "授權/來源註明: $(printf '%s' "$HTML" | grep -c 'CC0\|公眾領域')"
echo "== 資源抽測 =="
for f in $(printf '%s' "$HTML" | grep -o 'img/[^"]*\.\(jpg\|jpeg\|png\|webp\)' | sort -u | head -2); do
  echo "  $f → $(curl -s -o /dev/null -w '%{http_code}' "$P$f")"
done
for f in $(printf '%s' "$HTML" | grep -o 'audio/[^"]*\.mp3' | sort -u); do
  echo "  $f → $(curl -s -o /dev/null -w '%{http_code}' "$P$f")"
done
echo "== 卡片與加密頁 =="
echo "/toeic/ 含 Part 1: $(curl -s https://littler5071.github.io/toeic/ | grep -c 'Part 1')"
echo "首頁含 p1-full: $(curl -s https://littler5071.github.io/ | grep -c 'p1-full')"
echo "/ai/hdd-ai/ 明文外洩: $(curl -s https://littler5071.github.io/ai/hdd-ai/ | grep -c '可行性評估')（應 0）"
echo "/ai/hdd-ai/ 加密痕跡: $(curl -s https://littler5071.github.io/ai/hdd-ai/ | grep -c -i staticrypt)（應 >0）"
