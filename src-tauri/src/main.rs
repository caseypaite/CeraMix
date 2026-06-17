// Prevents an additional console window on Windows in release builds.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    // WebKitGTK's DMA-BUF renderer crashes on Arch Linux and other distros with
    // newer Mesa/kernel combos: WebKit returns a NULL GObject, then immediately
    // faults when trying to attach a signal to it, hanging the process.
    #[cfg(target_os = "linux")]
    {
        std::env::set_var("WEBKIT_DISABLE_DMABUF_RENDERER", "1");
    }

    ceramix_lib::run();
}
