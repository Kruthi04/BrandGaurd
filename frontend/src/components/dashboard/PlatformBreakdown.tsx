import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface PlatformStat {
  accuracy: number;
  mentions: number;
  trend: "up" | "down" | "stable";
}

interface PlatformBreakdownProps {
  platforms: Record<string, PlatformStat>;
}

const PLATFORM_LABELS: Record<string, string> = {
  chatgpt:    "ChatGPT",
  claude:     "Claude",
  perplexity: "Perplexity",
  gemini:     "Gemini",
};

const TREND_ICON: Record<string, string> = {
  up:     "↑",
  down:   "↓",
  stable: "→",
};

const TREND_COLOR: Record<string, string> = {
  up:     "text-green-600",
  down:   "text-red-500",
  stable: "text-muted-foreground",
};

function barColor(accuracy: number) {
  if (accuracy >= 80) return "bg-green-500";
  if (accuracy >= 60) return "bg-yellow-500";
  return "bg-red-500";
}

export default function PlatformBreakdown({ platforms }: PlatformBreakdownProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Platform Breakdown</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {Object.entries(platforms).map(([key, stat]) => (
          <div key={key} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">{PLATFORM_LABELS[key] ?? key}</span>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-medium ${TREND_COLOR[stat.trend]}`}>
                  {TREND_ICON[stat.trend]}
                </span>
                <span className="font-semibold">{stat.accuracy.toFixed(1)}%</span>
              </div>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${barColor(stat.accuracy)}`}
                style={{ width: `${stat.accuracy}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">{stat.mentions} mentions</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
