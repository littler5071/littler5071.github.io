# sysprobe ＋ hid_probe — 一份 Rust 原始碼，Windows 與 macOS x64 各自原生編譯

用 GitHub Actions 的**免費額度**，同一個 commit 同時編出：

- **`sysprobe-windows-x64.zip`** — `windows-latest`（4 核／16 GB）→ `x86_64-pc-windows-msvc`，內含 `sysprobe.exe`、`hid_probe.exe`
- **`sysprobe-macos-x64.app.zip`** — `macos-15-intel`（Intel）→ `x86_64-apple-darwin`，內含 `SysProbe.app`、`hid_probe`

每個 artifact 都含 `SHA256SUMS.txt` 與 `HID-SMOKE.txt`（CI 實機列舉結果），保留 14 天。

## 兩支程式

**`sysprobe`** — 把「編譯當時」的環境用 `option_env!` 編進二進位，執行時再印出「執行當時」的環境，用來證明同一份原始碼跨平台編譯。

**`hid_probe`** — Rust 的 HID（Human Interface Device）通訊範例：

```bash
hid_probe list                       # 列出所有 HID 裝置（VID:PID、名稱、路徑）
hid_probe info <vid:pid>             # 廠商／產品／序號／report descriptor 長度
hid_probe read <vid:pid> [秒數]       # 讀 input report（16 進位）
hid_probe send <vid:pid> <hex...>    # 送 output report
hid_probe get  <vid:pid> <report-id> # 讀 feature report
hid_probe set  <vid:pid> <hex...>    # 寫 feature report
```

底層是 `hidapi` crate（Rust 包裝 hidapi C 函式庫），各平台打自己的系統 API：

- **Windows**：`hid.dll` ＋ SetupAPI（系統內建 HID 驅動，不需另裝驅動）
- **macOS**：IOKit / IOHIDManager
- **Linux**：`/dev/hidraw`（本機開發測試用，不是 CI 目標）

## CI 會做什麼

1. 安裝 Rust（指定 target）
2. `cargo build --release --locked`，同時產出 `sysprobe` 與 `hid_probe`
3. **煙霧測試**：在 runner 上實際執行 `hid_probe list`，裝置數 < 1 就讓 job 失敗（避免「編得過但跑不動」的假成功）
4. macOS 另包成 `.app` 並 ad-hoc 簽章
5. 產生 `SHA256SUMS.txt`，上傳 artifact

## 本機開發

```bash
cargo run --release                        # sysprobe
cargo run --release --bin hid_probe -- list
```

Linux 上自行編譯需要 `libudev` 開發檔與 `pkg-config`（本機採 `linux-static-hidraw` 特性，直接從原始碼編 hidapi）。

## 免費額度（重點）

- 公開 repo：標準 runner **不計分鐘**；Windows 4 核 16 GB、macOS 3 核 M1 7 GB
- 私有 repo（Free）：每月 2,000 分鐘、artifact 500 MB、快取 10 GB；Windows 約 Linux 的 1.7 倍、macOS 約 **10 倍**
- Free 方案並行上限 20 個 job，其中 macOS 最多 5 個

## 授權

MIT
