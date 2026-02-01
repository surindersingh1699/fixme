use std::io::{BufRead, BufReader, Write};
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use tokio::sync::oneshot;

type PendingMap = Arc<Mutex<HashMap<u64, oneshot::Sender<serde_json::Value>>>>;

pub struct Sidecar {
    child: Mutex<Option<Child>>,
    stdin: Mutex<Option<std::process::ChildStdin>>,
    pending: PendingMap,
    next_id: AtomicU64,
}

impl Sidecar {
    pub fn new() -> Self {
        Self {
            child: Mutex::new(None),
            stdin: Mutex::new(None),
            pending: Arc::new(Mutex::new(HashMap::new())),
            next_id: AtomicU64::new(1),
        }
    }

    pub fn spawn(&self, python_path: &str, sidecar_script: &str) -> Result<(), String> {
        let mut child = Command::new(python_path)
            .arg(sidecar_script)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

        let stdin = child.stdin.take().ok_or("Failed to get sidecar stdin")?;
        let stdout = child.stdout.take().ok_or("Failed to get sidecar stdout")?;

        *self.stdin.lock().unwrap() = Some(stdin);
        *self.child.lock().unwrap() = Some(child);

        let pending = Arc::clone(&self.pending);
        std::thread::spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                if let Ok(line) = line {
                    if let Ok(resp) = serde_json::from_str::<serde_json::Value>(&line) {
                        if let Some(id) = resp.get("id").and_then(|v| v.as_u64()) {
                            let result = resp.get("result").cloned()
                                .or_else(|| resp.get("error").cloned())
                                .unwrap_or(serde_json::Value::Null);
                            if let Some(sender) = pending.lock().unwrap().remove(&id) {
                                let _ = sender.send(result);
                            }
                        }
                    }
                }
            }
        });

        Ok(())
    }

    pub async fn call(&self, method: &str, params: serde_json::Value) -> Result<serde_json::Value, String> {
        let id = self.next_id.fetch_add(1, Ordering::SeqCst);
        let request = serde_json::json!({
            "jsonrpc": "2.0",
            "id": id,
            "method": method,
            "params": params
        });

        let (tx, rx) = oneshot::channel();
        self.pending.lock().unwrap().insert(id, tx);

        {
            let mut stdin_guard = self.stdin.lock().unwrap();
            let stdin = stdin_guard.as_mut().ok_or("Sidecar not running")?;
            let msg = serde_json::to_string(&request).map_err(|e| e.to_string())?;
            writeln!(stdin, "{}", msg).map_err(|e| format!("Failed to write to sidecar: {}", e))?;
            stdin.flush().map_err(|e| format!("Failed to flush sidecar stdin: {}", e))?;
        }

        rx.await.map_err(|_| "Sidecar response channel closed".to_string())
    }

    pub fn kill(&self) {
        if let Some(mut child) = self.child.lock().unwrap().take() {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

impl Drop for Sidecar {
    fn drop(&mut self) {
        self.kill();
    }
}
