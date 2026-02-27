/** Active brand ID — stored in localStorage so it persists across sessions. */

const STORAGE_KEY = "brandguard_active_brand";
const DEFAULT_BRAND = "acme-corp";

export function getActiveBrand(): string {
  return localStorage.getItem(STORAGE_KEY) || DEFAULT_BRAND;
}

export function setActiveBrand(brandId: string) {
  localStorage.setItem(STORAGE_KEY, brandId);
}
