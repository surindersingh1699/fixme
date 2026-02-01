import { invoke } from "@tauri-apps/api/core";

export function useSidecar() {
  const call = async (method, params = {}) => {
    try {
      const result = await invoke("sidecar_call", { method, params });
      return result;
    } catch (err) {
      console.error(`[Sidecar] ${method} failed:`, err);
      throw err;
    }
  };

  return { call };
}
