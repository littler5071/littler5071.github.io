# -*- coding: utf-8 -*-
"""敏感字串掃描：檢查頁面是否出現憑證／帳號／email／id／本機路徑等模式。

每個模式都會印出「命中次數 + 上下文」，並自動排除已知的假陽性：
  - `s:/` 這種來自 https:// 的誤判
  - CSS 的 @media / @supports / @keyframes 等 at-rule
  - CSS 常見長字（webkit-overflow-scrolling、repeating-linear-gradient 等）

用法：
  python _scan_sensitive.py <檔案...>
  python _scan_sensitive.py --url <URL...>
"""
import re, sys, subprocess

CSS_AT = re.compile(r"^@(media|supports|keyframes|font-face|import|charset|page)\b")
CSS_LONG = {"webkit-overflow-scrolling", "repeating-linear-gradient", "linear-gradient",
            "background-image", "border-bottom-left-radius", "animation-timing-function"}

PATTERNS = [
    ("本機路徑(磁碟)", re.compile(r"[A-Za-z]:[\\/]")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("@ 字元", re.compile(r"@")),
    ("token 字樣", re.compile(r"(?i)\btoken\b")),
    ("password/密碼欄位", re.compile(r"(?i)\b(password|passwd|pwd)\b\s*[:=]")),
    ("chat/user id 字樣", re.compile(r"(?i)\b(chat[_-]?id|user[_-]?id|channel[_-]?id)\b")),
    ("金鑰前綴", re.compile(r"(?i)\b(sk-|ghp_|gho_|xox[baprs]-|AIza|ya29\.)")),
    ("長英數字串(>=24)", re.compile(r"[A-Za-z0-9_\-]{24,}")),
    ("長數字串(>=9)", re.compile(r"\d{9,}")),
    ("telegram/discord 連結", re.compile(r"(?i)(t\.me/|discord\.gg/)")),
    ("阿拉伯文", re.compile(r"[\u0600-\u06FF]")),
]


def real_hits(label, text):
    out = []
    for m in PATTERNS_RAW[label].finditer(text):
        s = m.group(0)
        if label == "本機路徑(磁碟)" and text[max(0, m.start() - 4):m.start()].lower().endswith("http"):
            continue                      # https:// 的 s:/ 誤判
        if label == "@ 字元" and CSS_AT.match(text[m.start():m.start() + 12]):
            continue                      # CSS at-rule
        if label.startswith("長英數") and s in CSS_LONG:
            continue
        ctx = text[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
        out.append((s, ctx))
    return out


PATTERNS_RAW = {label: pat for label, pat in PATTERNS}


def scan(name, text):
    print(f"--- {name} ({len(text)} chars) ---")
    total = 0
    for label, _ in PATTERNS:
        hits = real_hits(label, text)
        if not hits:
            continue
        total += len(hits)
        print(f"   [命中] {label}: {len(hits)} 次")
        for s, ctx in hits[:4]:
            print(f"        {s!r}  …{ctx}…")
    if total == 0:
        print("   乾淨：沒有命中任何敏感模式")
    return total


def main():
    args = sys.argv[1:]
    grand = 0
    if args and args[0] == "--url":
        for u in args[1:]:
            r = subprocess.run(["curl", "-s", "-A", "Mozilla/5.0", u], capture_output=True,
                               text=True, errors="ignore")
            grand += scan(u, r.stdout)
    else:
        for p in args:
            grand += scan(p, open(p, encoding="utf-8").read())
    print(f"\n總命中數（扣除已知假陽性後）：{grand}")


if __name__ == "__main__":
    main()
