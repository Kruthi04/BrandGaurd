import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { getActiveBrand } from "@/lib/brand";

interface StartMonitoringDialogProps {
  onClose: () => void;
  onCreated: () => void;
}

export default function StartMonitoringDialog({ onClose, onCreated }: StartMonitoringDialogProps) {
  const [brandName, setBrandName] = useState("");
  const [interval, setInterval] = useState("3600");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!brandName.trim()) return;
    setLoading(true);
    try {
      await api.post("/monitoring/start", {
        brand_id: getActiveBrand(),
        brand_name: brandName.trim(),
        interval: Number(interval),
      });
      onCreated();
      toast.success(`Scout created for "${brandName}"`);
      onClose();
    } catch {
      toast.error("Failed to create scout");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-lg">Start Monitoring</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">Brand Name</label>
              <input
                className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="e.g. Acme Corp"
                value={brandName}
                onChange={(e) => setBrandName(e.target.value)}
                required
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">Check Interval</label>
              <select
                className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                value={interval}
                onChange={(e) => setInterval(e.target.value)}
              >
                <option value="1800">Every 30 minutes</option>
                <option value="3600">Every hour</option>
                <option value="7200">Every 2 hours</option>
                <option value="86400">Daily</option>
              </select>
            </div>
            <div className="flex gap-2 justify-end pt-2">
              <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
              <Button type="submit" disabled={loading || !brandName.trim()}>
                {loading ? "Creating..." : "Start Scout"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
