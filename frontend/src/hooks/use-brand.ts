import { useState } from "react";
import type { Brand } from "@/types";

/** Hook to manage the currently selected brand context */
export function useBrand() {
  const [activeBrand, setActiveBrand] = useState<Brand | null>(null);

  return {
    activeBrand,
    setActiveBrand,
    brandId: activeBrand?.id ?? null,
  };
}
