# sysprobe — 一份 Rust 原始碼，四個平台產出

用 GitHub Actions 的**免費額度**，同一個 commit 同時編出：

| 產出 | Runner | 目標 triple | 格式 |
|---|---|---|---|
| `sysprobe-linux-x64.tar.gz` | `ubuntu-latest` | `x86_64-unknown-linux-gnu` | tar.gz |
| `sysprobe-windows-x64.zip` | `windows-latest` | `x86_64-pc-windows-msvc` | zip（內含 `.exe`） |
| `sysprobe-macos-x64.app.zip` | `macos-15-intel` | `x86_64-apple-darwin` | `.app` bundle |
| `sysprobe-macos-arm64.app.zip` | `macos-14` | `aarch64-apple-darwin` | `.app` bundle |

每個 artifact 都含 `SHA256SUMS.txt`，保留 14 天。

## 它做什麼

執行後印出「編譯當時」與「執行當時」兩組資訊：

```
sysprobe 0.1.0
-----------------------------------------------------------
built_on_os   : Linux
built_on_arch : X64
built_at      : 2026-10-27T…
rustc         : rustc 1.99.1 (58cf8f9c3 2026-10-13)
target        : x86_64-unknown-linux-gnu
commit        : <sha>
os            : linux
arch          : x86_64
family        : unix
pointer_bits  : 64
```

`built_*` 由 CI 在編譯時注入（`option_env!` 編進二進位），`os/arch/family` 是執行時由 `std::env::consts` 取得 —
所以把 `sysprobe-macos-arm64.zip` 解開、在 M 系列 Mac 上跑，會同時看到「編譯環境」與「執行環境」，可以直接證明是同一份原始碼跨平台編譯。

加上 `--json` 可輸出 JSON。

## 本機開發

```bash
cargo run --release
cargo run --release -- --json
```

零外部 crate（只依賴 std），`cargo build --release` 約 3 秒。

## 免費額度怎麼算

- **公開 repo**：標準 runner 不計分鐘，等於免費。
- **私有 repo**（GitHub Free）：每月 2,000 分鐘、artifact 500 MB、cache 10 GB。
- 計費倍率（對照 Linux 2-core $0.006/分）：Windows 2-core $0.010/分、macOS $0.062/分 ≈ **10 倍**。

換句話說：這個矩陣的「四平台」成本幾乎都花在 macOS 那兩個 job 上。

## 授權

MIT
