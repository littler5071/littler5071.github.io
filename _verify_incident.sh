#!/usr/bin/env bash
# 線上驗證：AI 助理被攻擊事件文章（/ai/incident/）
set -u
BASE="https://littler5071.github.io"
Q="?v=$(date +%s)"

echo "== 1. 遠端檔案本體（權威，不受 CDN 影響） =="
git show origin/main:ai/incident/index.html | grep -c 'youtube.com/embed/W99welO4wwE' | sed 's/^/  iframe id 出現次數: /'
git show origin/main:ai/incident/index.html | grep -c 'class="hnav"' | sed 's/^/  導覽列: /'

echo
echo "== 2. 線上頁面 HTTP 狀態 =="
for p in "ai/incident/" "ai/" ""; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -A "Mozilla/5.0" "$BASE/$p$Q")
  size=$(curl -s -A "Mozilla/5.0" "$BASE/$p$Q" | wc -c)
  echo "  /$p -> HTTP $code ($size bytes)"
done

echo
echo "== 3. 文章頁內容檢查 =="
H=$(curl -s -A "Mozilla/5.0" "$BASE/ai/incident/$Q")
echo "$H" | grep -c 'W99welO4wwE' | sed 's/^/  影片 id: /'
echo "$H" | grep -o '<iframe src="[^"]*"' | sed 's/^/  iframe: /'
echo "$H" | grep -c 'aspect-ratio:16/9' | sed 's/^/  16:9 容器: /'
echo "$H" | grep -c 'class="hnav"' | sed 's/^/  導覽列: /'
echo "$H" | grep -c '不構成任何安全性保證' | sed 's/^/  免責句: /'
echo "$H" | grep -c '防的不是聰明，是授權邊界' | sed 's/^/  結論句: /'
echo "$H" | grep -c '>首頁<' | sed 's/^/  多餘的「首頁」按鈕(應為0): /'

echo
echo "== 4. 分類頁 / 首頁卡片 =="
curl -s -A "Mozilla/5.0" "$BASE/ai/$Q" | grep -c 'incident/' | sed 's|^|  分類頁出現 incident 連結: |'
curl -s -A "Mozilla/5.0" "$BASE/ai/$Q" | grep -o '<a class="btn" href="incident/">[^<]*</a>' | sed 's/^/  分類頁卡片: /'
curl -s -A "Mozilla/5.0" "$BASE/$Q" | grep -o 'href="ai/incident/">[^<]*</a>' | sed 's/^/  首頁卡片: /'
curl -s -A "Mozilla/5.0" "$BASE/$Q" | grep -o 'AI 助理被攻擊的那一晚[^<]*' | head -2 | sed 's/^/  首頁標題: /'
