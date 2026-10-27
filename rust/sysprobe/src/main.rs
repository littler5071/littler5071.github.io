//! sysprobe — 同一個 Rust 原始碼，在 GitHub Actions 的三種作業系統上編譯。
//!
//! 用途：驗證「一份程式碼、多平台產出」的實際結果，並把編譯當時的環境寫進二進位檔，
//! 讓下載到 Windows / macOS / Linux 的人一眼看出這個檔案是誰、在哪裡、用什麼工具鏈編出來的。

use std::env;

const APP: &str = env!("CARGO_PKG_NAME");
const VERSION: &str = env!("CARGO_PKG_VERSION");

/// 編譯當下的資訊（`option_env!` 在 CI 有設才會是 Some）
fn build_info() -> Vec<(&'static str, String)> {
    let opt = |v: Option<&'static str>| v.unwrap_or("(未設定)").to_string();
    vec![
        ("built_on_os", opt(option_env!("BUILD_OS"))),
        ("built_on_arch", opt(option_env!("BUILD_ARCH"))),
        ("built_at", opt(option_env!("BUILD_TIME"))),
        ("rustc", opt(option_env!("BUILD_RUSTC"))),
        ("target", opt(option_env!("BUILD_TARGET"))),
        ("commit", opt(option_env!("BUILD_COMMIT"))),
    ]
}

/// 執行當下的平台資訊
fn runtime_info() -> Vec<(&'static str, String)> {
    vec![
        ("os", env::consts::OS.to_string()),
        ("arch", env::consts::ARCH.to_string()),
        ("family", env::consts::FAMILY.to_string()),
        ("pointer_bits", (std::mem::size_of::<usize>() * 8).to_string()),
        ("exe", env::current_exe().map(|p| p.display().to_string())
            .unwrap_or_else(|_| "(未知)".into())),
        ("args", env::args().skip(1).collect::<Vec<_>>().join(" ")),
    ]
}

fn json_escape(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"").replace('\n', " ")
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    let as_json = args.iter().any(|a| a == "--json");

    let mut rows: Vec<(&'static str, String)> = Vec::new();
    rows.extend(build_info());
    rows.extend(runtime_info());

    if as_json {
        let body = rows
            .iter()
            .map(|(k, v)| format!("  \"{}\": \"{}\"", k, json_escape(v)))
            .collect::<Vec<_>>()
            .join(",\n");
        println!("{{\n  \"app\": \"{}\",\n  \"version\": \"{}\",\n{}\n}}", APP, VERSION, body);
        return;
    }

    let width = rows.iter().map(|(k, _)| k.len()).max().unwrap_or(10);
    println!("{} {}", APP, VERSION);
    println!("{}", "-".repeat(width + 46));
    for (k, v) in &rows {
        println!("{:<width$} : {}", k, v, width = width);
    }
    println!("{}", "-".repeat(width + 46));
    println!("同一個檔案格式、同一份原始碼，走到哪裡都跑得動。");
}
