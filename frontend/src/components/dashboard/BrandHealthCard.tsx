import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface BrandHealthCardProps {
  score: number;
  brandName: string;
  totalMentions: number;
}

function CircularScore({ score }: { score: number }) {
  const r = 52;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? "#16a34a" : score >= 60 ? "#ca8a04" : "#dc2626";

  return (
    <svg width="136" height="136" viewBox="0 0 136 136">
      <circle cx="68" cy="68" r={r} fill="none" stroke="#e5e7eb" strokeWidth="12" />
      <circle
        cx="68" cy="68" r={r}
        fill="none"
        stroke={color}
        strokeWidth="12"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform="rotate(-90 68 68)"
        style={{ transition: "stroke-dashoffset 0.8s ease" }}
      />
      <text x="68" y="63" textAnchor="middle" fontSize="30" fontWeight="bold" fill={color}>
        {score}
      </text>
      <text x="68" y="82" textAnchor="middle" fontSize="11" fill="#9ca3af">
        / 100
      </text>
    </svg>
  );
}

export default function BrandHealthCard({ score, brandName, totalMentions }: BrandHealthCardProps) {
  const label = score >= 80 ? "Healthy" : score >= 60 ? "At Risk" : "Critical";
  const labelColor = score >= 80 ? "text-green-600" : score >= 60 ? "text-yellow-600" : "text-red-600";

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Brand Health Score</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-3">
        <CircularScore score={score} />
        <div className="text-center">
          <p className={`font-semibold text-sm ${labelColor}`}>{label}</p>
          <p className="text-xs text-muted-foreground">{brandName}</p>
          <p className="text-xs text-muted-foreground mt-1">{totalMentions} total mentions</p>
        </div>
      </CardContent>
    </Card>
  );
}
