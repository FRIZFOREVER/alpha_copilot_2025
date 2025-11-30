import { lazy } from "react";

export const EfficiencyMiniChart = lazy(async () => {
  const recharts = await import("recharts");
  return {
    default: () => {
      const { LineChart, Line, ResponsiveContainer } = recharts;
      const data = [
        { value: 70 },
        { value: 85 },
        { value: 72 },
        { value: 88 },
        { value: 75 },
        { value: 86 },
      ];
      return (
        <ResponsiveContainer width="100%" height={40}>
          <LineChart
            data={data}
            margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
          >
            <Line
              type="natural"
              dataKey="value"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      );
    },
  };
});

