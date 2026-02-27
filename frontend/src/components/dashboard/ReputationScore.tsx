import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ReputationScoreProps {
  score?: number;
  brandName?: string;
}

export default function ReputationScore({ score, brandName }: ReputationScoreProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Reputation Score</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center">
          <div className="text-4xl font-bold">{score ?? "--"}</div>
          <p className="text-sm text-muted-foreground mt-1">
            {brandName ?? "No brand selected"}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
