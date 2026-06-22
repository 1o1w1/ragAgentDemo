import { useState, useEffect, useCallback } from "react";
import type { AppConfig } from "../types";
import { configApi } from "../services/api";

export function useConfig() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadConfig = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await configApi.getConfig();
      setConfig(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load config");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  const updateConfig = useCallback(async (updates: Record<string, unknown>) => {
    setError(null);
    try {
      const data = await configApi.updateConfig(updates);
      setConfig(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update config");
    }
  }, []);

  const reloadConfig = useCallback(async () => {
    setError(null);
    try {
      const data = await configApi.reloadConfig();
      setConfig(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reload config");
    }
  }, []);

  return { config, loading, error, updateConfig, reloadConfig };
}
