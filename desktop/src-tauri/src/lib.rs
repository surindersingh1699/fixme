mod sidecar;

use sidecar::Sidecar;
use std::sync::Arc;
use tauri::Manager;

#[tauri::command]
async fn sidecar_call(
    method: String,
    params: serde_json::Value,
    state: tauri::State<'_, Arc<Sidecar>>,
) -> Result<serde_json::Value, String> {
    state.call(&method, params).await
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            let sidecar = Arc::new(Sidecar::new());

            // Determine paths for the Python sidecar
            let resource_dir = app.path().resource_dir().unwrap_or_default();
            let app_dir = resource_dir.parent().unwrap_or(&resource_dir);

            // In development, use the venv python and sidecar script from project root
            // Walk up from the resource dir to find the project root
            let mut project_root = app_dir.to_path_buf();
            // In dev mode, try to find sidecar relative to the desktop dir
            for _ in 0..5 {
                if project_root.join("sidecar").join("main.py").exists() {
                    break;
                }
                if let Some(parent) = project_root.parent() {
                    project_root = parent.to_path_buf();
                } else {
                    break;
                }
            }

            let sidecar_script = project_root.join("sidecar").join("main.py");

            // Try venv python first, then system python3
            let python_path = if project_root.join("venv").join("bin").join("python3").exists() {
                project_root.join("venv").join("bin").join("python3").to_string_lossy().to_string()
            } else if project_root.join("venv").join("Scripts").join("python.exe").exists() {
                project_root.join("venv").join("Scripts").join("python.exe").to_string_lossy().to_string()
            } else {
                "python3".to_string()
            };

            println!("[FixMe] Python: {}", python_path);
            println!("[FixMe] Sidecar: {}", sidecar_script.display());

            if let Err(e) = sidecar.spawn(&python_path, &sidecar_script.to_string_lossy()) {
                eprintln!("[FixMe] Failed to start sidecar: {}", e);
            }

            app.manage(sidecar);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![sidecar_call])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
