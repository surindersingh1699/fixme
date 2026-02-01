mod sidecar;

use sidecar::Sidecar;
use std::path::PathBuf;
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

/// Find the project root containing sidecar/main.py.
/// Checks multiple locations:
/// 1. Bundled resources inside .app (production)
/// 2. Walk up from app directory (dev mode)
/// 3. Well-known paths (~/Developer/fixme)
fn find_project_root(resource_dir: &std::path::Path) -> Option<PathBuf> {
    // 1. Check if sidecar is bundled in resource dir (production .app)
    if resource_dir.join("sidecar").join("main.py").exists() {
        return Some(resource_dir.to_path_buf());
    }

    // 2. Walk up from resource dir (dev mode — src-tauri is under desktop/)
    let mut dir = resource_dir.to_path_buf();
    for _ in 0..6 {
        if dir.join("sidecar").join("main.py").exists() {
            return Some(dir);
        }
        match dir.parent() {
            Some(parent) => dir = parent.to_path_buf(),
            None => break,
        }
    }

    // 3. Check well-known paths
    if let Some(home) = dirs::home_dir() {
        let candidates = [
            home.join("Developer").join("fixme"),
            home.join("projects").join("fixme"),
            home.join("fixme"),
        ];
        for candidate in &candidates {
            if candidate.join("sidecar").join("main.py").exists() {
                return Some(candidate.clone());
            }
        }
    }

    None
}

/// Find a Python interpreter with the required dependencies.
/// Checks venv in project root, then well-known venv locations, then system python3.
fn find_python(project_root: &std::path::Path) -> String {
    // Check venv in project root (dev mode)
    let venv_python_mac = project_root.join("venv").join("bin").join("python3");
    if venv_python_mac.exists() {
        return venv_python_mac.to_string_lossy().to_string();
    }
    let venv_python_win = project_root.join("venv").join("Scripts").join("python.exe");
    if venv_python_win.exists() {
        return venv_python_win.to_string_lossy().to_string();
    }

    // Check well-known venv locations (production — venv not bundled)
    if let Some(home) = dirs::home_dir() {
        let candidates = [
            home.join("Developer").join("fixme").join("venv").join("bin").join("python3"),
            home.join("projects").join("fixme").join("venv").join("bin").join("python3"),
            home.join("fixme").join("venv").join("bin").join("python3"),
            home.join(".fixme").join("venv").join("bin").join("python3"),
        ];
        for candidate in &candidates {
            if candidate.exists() {
                return candidate.to_string_lossy().to_string();
            }
        }
    }

    "python3".to_string()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            let sidecar = Arc::new(Sidecar::new());

            let resource_dir = app.path().resource_dir().unwrap_or_default();

            let project_root = find_project_root(&resource_dir)
                .unwrap_or_else(|| resource_dir.clone());

            let sidecar_script = project_root.join("sidecar").join("main.py");
            let python_path = find_python(&project_root);

            println!("[FixMe] Resource dir: {}", resource_dir.display());
            println!("[FixMe] Project root: {}", project_root.display());
            println!("[FixMe] Python: {}", python_path);
            println!("[FixMe] Sidecar: {}", sidecar_script.display());

            if sidecar_script.exists() {
                if let Err(e) = sidecar.spawn(&python_path, &sidecar_script.to_string_lossy()) {
                    eprintln!("[FixMe] Failed to start sidecar: {}", e);
                }
            } else {
                eprintln!("[FixMe] Sidecar script not found at: {}", sidecar_script.display());
            }

            app.manage(sidecar);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![sidecar_call])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
