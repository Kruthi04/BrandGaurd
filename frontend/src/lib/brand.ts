import { useSyncExternalStore } from "react";

const BRAND_KEY = "brandguard_active_brand";
const DEFAULT_BRAND = "yutori";

const listeners = new Set<() => void>();

export function getActiveBrand(): string {
  return localStorage.getItem(BRAND_KEY) || DEFAULT_BRAND;
}

export function setActiveBrand(id: string): void {
  localStorage.setItem(BRAND_KEY, id);
  listeners.forEach((l) => l());
}

export function useActiveBrand(): string {
  return useSyncExternalStore(
    (cb) => { listeners.add(cb); return () => listeners.delete(cb); },
    getActiveBrand,
  );
}
