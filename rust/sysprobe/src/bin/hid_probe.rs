//! hid_probe — Rust 的 HID（Human Interface Device）通訊範例
//!
//! 一支程式同時支援 Windows / macOS / Linux，底層由 `hidapi` crate 包住三個平台的系統 API：
//!   - Windows：`hid.dll` + SetupAPI（系統內建 HID 驅動，不需另裝驅動）
//!   - macOS：IOKit / IOHIDManager
//!   - Linux：/dev/hidraw（需要 udev 規則才能免 root）
//!
//! 用法：
//!   hid_probe list                          列出所有 HID 裝置
//!   hid_probe info <vid:pid>                印出該裝置的 report descriptor 長度等資訊
//!   hid_probe read <vid:pid> [秒數]          讀取 input report（16 進位）
//!   hid_probe send <vid:pid> <hex...>       送出 output report
//!   hid_probe get  <vid:pid> <report-id>    讀取 feature report
//!   hid_probe set  <vid:pid> <hex...>       寫入 feature report

use hidapi::{HidApi, HidDevice};
use std::time::{Duration, Instant};

fn parse_ids(s: &str) -> Result<(u16, u16), String> {
    let (v, p) = s.split_once(':').ok_or("格式要 VID:PID，例如 046d:c52b")?;
    Ok((
        u16::from_str_radix(v.trim_start_matches("0x"), 16).map_err(|e| e.to_string())?,
        u16::from_str_radix(p.trim_start_matches("0x"), 16).map_err(|e| e.to_string())?,
    ))
}

fn hex_to_bytes(parts: &[String]) -> Vec<u8> {
    parts
        .iter()
        .flat_map(|p| {
            let p = p.trim_start_matches("0x");
            let p = if p.len() % 2 == 1 { format!("0{}", p) } else { p.to_string() };
            (0..p.len() / 2)
                .map(|i| u8::from_str_radix(&p[i * 2..i * 2 + 2], 16).unwrap_or(0))
                .collect::<Vec<_>>()
        })
        .collect()
}

fn open(api: &HidApi, vid: u16, pid: u16) -> Result<HidDevice, String> {
    api.open(vid, pid).map_err(|e| format!("開啟失敗：{e}（可能被其他程式獨佔，或權限不足）"))
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let cmd = args.first().map(|s| s.as_str()).unwrap_or("list");

    let api = match HidApi::new() {
        Ok(a) => a,
        Err(e) => {
            eprintln!("初始化 hidapi 失敗：{e}");
            std::process::exit(1);
        }
    };

    match cmd {
        "list" => {
            println!("HID 裝置共 {} 個\n", api.device_list().count());
            for d in api.device_list() {
                println!(
                    "{:04x}:{:04x}  {:<38} {:<28} {}",
                    d.vendor_id(),
                    d.product_id(),
                    d.product_string().unwrap_or("(無名稱)"),
                    d.manufacturer_string().unwrap_or("(無廠商)"),
                    d.path().to_string_lossy()
                );
            }
        }
        "info" => {
            let (vid, pid) = parse_ids(args.get(1).map(|s| s.as_str()).unwrap_or(""))
                .unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(2) });
            let dev = open(&api, vid, pid).unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(1) });
            let m = dev.get_manufacturer_string().ok().flatten().unwrap_or_default();
            let p = dev.get_product_string().ok().flatten().unwrap_or_default();
            let s = dev.get_serial_number_string().ok().flatten().unwrap_or_default();
            println!("裝置 {vid:04x}:{pid:04x}");
            println!("  廠商：{m}");
            println!("  產品：{p}");
            println!("  序號：{s}");
            match dev.get_report_descriptor(&mut [0u8; 4096]) {
                Ok(n) => println!("  Report descriptor：{n} bytes"),
                Err(e) => println!("  Report descriptor：讀不到（{e}）"),
            }
        }
        "read" => {
            let (vid, pid) = parse_ids(args.get(1).map(|s| s.as_str()).unwrap_or(""))
                .unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(2) });
            let secs: u64 = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(5);
            let dev = open(&api, vid, pid).unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(1) });
            dev.set_blocking_mode(false).ok();
            let mut buf = [0u8; 64];
            let end = Instant::now() + Duration::from_secs(secs);
            println!("讀取 {secs} 秒（input report）…");
            while Instant::now() < end {
                match dev.read_timeout(&mut buf, 200) {
                    Ok(0) => {}
                    Ok(n) => {
                        let hex: Vec<String> = buf[..n].iter().map(|b| format!("{b:02x}")).collect();
                        println!("  [{} bytes] {}", n, hex.join(" "));
                    }
                    Err(e) => {
                        eprintln!("讀取錯誤：{e}");
                        break;
                    }
                }
            }
        }
        "send" => {
            let (vid, pid) = parse_ids(args.get(1).map(|s| s.as_str()).unwrap_or(""))
                .unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(2) });
            let bytes = hex_to_bytes(&args[2..]);
            let dev = open(&api, vid, pid).unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(1) });
            match dev.write(&bytes) {
                Ok(n) => println!("已送出 {n} bytes：{:02x?}", bytes),
                Err(e) => eprintln!("送出失敗：{e}"),
            }
        }
        "get" => {
            let (vid, pid) = parse_ids(args.get(1).map(|s| s.as_str()).unwrap_or(""))
                .unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(2) });
            let rid: u8 = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(0);
            let dev = open(&api, vid, pid).unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(1) });
            let mut buf = [0u8; 256];
            match dev.get_feature_report(&mut buf) {
                Ok(n) => println!("feature report {rid} → {} bytes: {:02x?}", n, &buf[..n]),
                Err(e) => eprintln!("讀取 feature report 失敗：{e}"),
            }
        }
        "set" => {
            let (vid, pid) = parse_ids(args.get(1).map(|s| s.as_str()).unwrap_or(""))
                .unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(2) });
            let bytes = hex_to_bytes(&args[2..]);
            let dev = open(&api, vid, pid).unwrap_or_else(|e| { eprintln!("{e}"); std::process::exit(1) });
            match dev.send_feature_report(&bytes) {
                Ok(_) => println!("feature report 已寫入 {} bytes：{:02x?}", bytes.len(), bytes),
                Err(e) => eprintln!("寫入 feature report 失敗：{e}"),
            }
        }
        other => {
            eprintln!("未知指令 {other}；可用：list / info / read / send / get / set");
            std::process::exit(2);
        }
    }
}
