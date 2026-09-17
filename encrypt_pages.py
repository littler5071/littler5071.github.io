# -*- coding: utf-8 -*-
"""把指定頁面用 StatiCrypt 加密（全站共用一個密碼）。

用法：
    python encrypt_pages.py            # 依 protected.json 清單加密
    python encrypt_pages.py --list     # 只顯示清單與密碼檔狀態

流程：產生頁面（各 build_*.py）→ 跑這支 → git push。
密碼放在 repo 之外的 .private/site_password.txt（不進版控、不出現在網站）。
"""
import io, json, os, subprocess, sys, shutil, tempfile  # noqa

SITE = os.path.dirname(os.path.abspath(__file__))
PROTECTED = os.path.join(SITE, "protected.json")
PW_FILE = os.path.join(os.path.dirname(SITE), ".private", "site_password.txt")


def read_pw():
    if not os.path.exists(PW_FILE):
        print(f"❌ 找不到密碼檔：{PW_FILE}")
        print("   請先建立：printf '%s\\n' '<你的全站密碼(≥14字元)>' > "
              f"'{PW_FILE}'")
        sys.exit(1)
    pw = io.open(PW_FILE, encoding="utf-8").read().strip()
    if len(pw) < 14:
        print(f"❌ 密碼太短（{len(pw)} 字元）－StatiCrypt 建議 ≥14 字元，否則每次都要互動確認")
        sys.exit(1)
    return pw


def main():
    listing = [l.strip() for l in io.open(PROTECTED, encoding="utf-8").read().splitlines()
               if l.strip() and not l.strip().startswith("#")]
    print(f"要加密的頁面（{len(listing)} 筆）：")
    for p in listing:
        print("  -", p, "✓存在" if os.path.exists(os.path.join(SITE, p)) else "❌不存在")
    print(f"密碼檔：{PW_FILE} ({'存在' if os.path.exists(PW_FILE) else '不存在'})")
    if "--list" in sys.argv:
        return 0
    pw = read_pw()
    ok, fail = 0, []
    for rel in listing:
        src = os.path.join(SITE, rel)
        if not os.path.exists(src):
            fail.append(rel)
            continue
        tmpdir = os.path.join(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()), "Temp", "staticrypt_" + str(os.getpid()))
        src_dir = os.path.join(tmpdir, "src")       # 輸入與輸出必須分開放：
        out_dir = os.path.join(tmpdir, "out")       # staticrypt 的輸出檔名＝輸入檔名，同目錄會找不到成品
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(out_dir, exist_ok=True)
        tmp_src = os.path.join(src_dir, os.path.basename(rel))
        shutil.copy2(src, tmp_src)
        cmd = f'"{shutil.which("npx") or "npx"}" --yes staticrypt "{tmp_src}" -p "{pw}" -d "{out_dir}" --remember 30'
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors="ignore", timeout=600)
        produced = None
        for root, _dirs, files in os.walk(out_dir):
            for f in files:
                if f.lower().endswith(".html"):
                    produced = os.path.join(root, f)
        if produced:
            shutil.copy2(produced, src)          # 就地覆蓋成加密版
            size = os.path.getsize(src)
            print(f"  ✔ 已加密 {rel}（{size:,} bytes）")
            ok += 1
        else:
            print(f"  ❌ 加密失敗 {rel}")
            print("     ", (r.stdout or "")[-300:], (r.stderr or "")[-200:])
            fail.append(rel)
        shutil.rmtree(tmpdir, ignore_errors=True)
    print(f"\n完成：成功 {ok} 筆，失敗 {len(fail)} 筆 {fail if fail else ''}")
    print("提醒：加密後請 git add/commit/push，並等 50–60 秒再驗證線上。")
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
