import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface CostCurveChartProps {
  costCurve: Record<string, number>;
}

export function CostCurveChart({ costCurve }: CostCurveChartProps) {
  // Ensure all costs 0-10 are represented
  const data = [];
  for (let i = 0; i <= 10; i++) {
    const key = String(i);
    data.push({
      cost: key,
      count: costCurve[key] || 0,
    });
  }
  // Add 10+ if exists
  if (costCurve["10+"]) {
    data[10].count += costCurve["10+"];
  }

  const maxCount = Math.max(...data.map((d) => d.count), 1);

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <XAxis
            dataKey="cost"
            tick={{ fill: "#888", fontSize: 12 }}
            axisLine={{ stroke: "#333" }}
            tickLine={{ stroke: "#333" }}
          />
          <YAxis
            tick={{ fill: "#888", fontSize: 12 }}
            axisLine={{ stroke: "#333" }}
            tickLine={{ stroke: "#333" }}
            allowDecimals={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1a1a24",
              border: "1px solid #2a2a3a",
              borderRadius: "8px",
            }}
            labelStyle={{ color: "#999" }}
            formatter={(value: number) => [`${value} cards`, "Count"]}
            labelFormatter={(label) => `Cost: ${label}`}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={`rgba(99, 102, 241, ${0.3 + (entry.count / maxCount) * 0.7})`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
