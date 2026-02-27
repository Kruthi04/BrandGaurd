import AppLayout from "@/components/layout/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Threats() {
  // TODO: Fetch threats from API
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Threat Monitor</h1>
          <p className="text-muted-foreground">
            Track and respond to reputation threats.
          </p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Threat Feed</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">No threats detected. Your brand is safe.</p>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
