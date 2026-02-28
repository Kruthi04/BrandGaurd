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
  { key: "claude",     color: "#a78bfa", label: "Claude"     },
  { key: "chatgpt",    color: "#60a5fa", label: "ChatGPT"    },
  { key: "perplexity", color: "#fbbf24", label: "Perplexity" },
  { key: "gemini",     color: "#f87171", label: "Gemini"     },
];

export default function AccuracyTrendChart({ data }: AccuracyTrendChartProps) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 5, right: 16, left: -16, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(215 28% 16%)" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: "hsl(215 20% 60%)" }} stroke="hsl(215 28% 20%)" />
        <YAxis domain={[50, 100]} tick={{ fontSize: 11, fill: "hsl(215 20% 60%)" }} unit="%" stroke="hsl(215 28% 20%)" />
        <Tooltip
          formatter={(value: number) => [`${value.toFixed(1)}%`, ""]}
          contentStyle={{
            fontSize: 12,
            backgroundColor: "hsl(222 47% 5%)",
            border: "1px solid hsl(215 28% 16%)",
            borderRadius: 8,
            color: "hsl(210 40% 96%)",
          }}
          labelStyle={{ color: "hsl(215 20% 60%)" }}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: "hsl(215 20% 60%)" }} />
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
  );
}
