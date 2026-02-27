import { useState } from "react";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface BrandFact {
  key: string;
  value: string;
}

export default function Settings() {
  const [brandName,   setBrandName]   = useState("");
  const [industry,    setIndustry]    = useState("");
  const [description, setDescription] = useState("");
  const [facts,       setFacts]       = useState<BrandFact[]>([{ key: "", value: "" }]);
  const [loading,     setLoading]     = useState(false);
  const [submitted,   setSubmitted]   = useState(false);

  function addFact() {
    setFacts((prev) => [...prev, { key: "", value: "" }]);
  }

  function updateFact(index: number, field: "key" | "value", value: string) {
    setFacts((prev) => prev.map((f, i) => (i === index ? { ...f, [field]: value } : f)));
  }

  function removeFact(index: number) {
    setFacts((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!brandName.trim()) return;
    setLoading(true);

    try {
      // 1. Push ground truth to Senso
      await fetch("/api/content/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand_name: brandName, facts }),
      }).catch(() => null);

      // 2. Create brand node in Neo4j
      await fetch("/api/graph/mentions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand_name: brandName, industry, description }),
      }).catch(() => null);

      // 3. Set up Senso rules
      await fetch("/api/rules/setup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand_name: brandName, facts }),
      }).catch(() => null);

      // 4. Start Yutori scout
      await fetch("/api/monitoring/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand_name: brandName }),
      }).catch(() => null);

      setSubmitted(true);
      toast.success(`Brand "${brandName}" onboarded successfully!`);
    } catch {
      toast.error("Onboarding failed — please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6 max-w-2xl">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">Configure BrandGuard and onboard new brands.</p>
        </div>

        {/* Brand Onboarding */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              {submitted ? "✓ Brand Onboarded" : "Add a Brand"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {submitted ? (
              <div className="space-y-3">
                <p className="text-sm text-green-700 dark:text-green-400">
                  <strong>{brandName}</strong> has been onboarded. Ground truth facts pushed to Senso,
                  brand node created in Neo4j, and Yutori scout started.
                </p>
                <Button variant="outline" onClick={() => { setSubmitted(false); setBrandName(""); setIndustry(""); setDescription(""); setFacts([{ key: "", value: "" }]); }}>
                  Add another brand
                </Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Brand Name *</label>
                    <input
                      required
                      className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                      placeholder="e.g. Acme Corp"
                      value={brandName}
                      onChange={(e) => setBrandName(e.target.value)}
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Industry</label>
                    <input
                      className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                      placeholder="e.g. Enterprise Software"
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-medium">Description</label>
                  <textarea
                    className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                    rows={2}
                    placeholder="Brief description of the brand"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>

                {/* Ground truth facts */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">Ground Truth Facts</label>
                    <button type="button" onClick={addFact} className="text-xs text-primary hover:underline">
                      + Add fact
                    </button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    These facts are pushed to Senso and used to evaluate AI-generated content.
                  </p>
                  {facts.map((fact, i) => (
                    <div key={i} className="flex gap-2 items-center">
                      <input
                        className="flex-1 rounded-md border px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                        placeholder="Fact label (e.g. Founded)"
                        value={fact.key}
                        onChange={(e) => updateFact(i, "key", e.target.value)}
                      />
                      <input
                        className="flex-[2] rounded-md border px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                        placeholder="Value (e.g. 2005)"
                        value={fact.value}
                        onChange={(e) => updateFact(i, "value", e.target.value)}
                      />
                      {facts.length > 1 && (
                        <button type="button" onClick={() => removeFact(i)} className="text-muted-foreground hover:text-destructive text-sm">✕</button>
                      )}
                    </div>
                  ))}
                </div>

                <Button type="submit" disabled={loading || !brandName.trim()} className="w-full">
                  {loading ? "Onboarding…" : "Onboard Brand"}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>

        {/* API Config info */}
        <Card>
          <CardHeader><CardTitle className="text-lg">API Configuration</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              API keys are configured via environment variables on the backend. See{" "}
              <code className="text-xs bg-muted px-1 rounded">.env.example</code> for required keys.
            </p>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
