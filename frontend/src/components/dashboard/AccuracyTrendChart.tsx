import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer,
} from "recharts";

interface TrendDataPoint {
  date: string;
  chatgpt: number;
  claude: number;
  perplexity: number;
  gemini: number;
}

interface AccuracyTrendChartProps {
  data: TrendDataPoint[];
}

const LINES = [
  { key: "claude",     color: "#8b5cf6", label: "Claude"     },
  { key: "chatgpt",    color: "#3b82f6", label: "ChatGPT"    },
  { key: "perplexity", color: "#f59e0b", label: "Perplexity" },
  { key: "gemini",     color: "#ef4444", label: "Gemini"     },
];

export default function AccuracyTrendChart({ data }: AccuracyTrendChartProps) {
  return (
    <Card className="col-span-full md:col-span-2">
      <CardHeader>
        <CardTitle className="text-lg">7-Day Accuracy Trend</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data} margin={{ top: 5, right: 16, left: -16, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis domain={[50, 100]} tick={{ fontSize: 11 }} unit="%" />
            <Tooltip
              formatter={(value: number) => [`${value.toFixed(1)}%`, ""]}
              contentStyle={{ fontSize: 12 }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {LINES.map(({ key, color, label }) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                name={label}
                stroke={color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
