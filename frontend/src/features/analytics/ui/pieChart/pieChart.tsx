import { lazy } from "react";

export const PieChartComponent = lazy(async () => {
  const recharts = await import("recharts");
  return {
    default: ({
      categoryChartData,
    }: {
      categoryChartData: Array<{
        name: string;
        value: number;
        color: string;
      }>;
    }) => {
      const { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } = recharts;
      return (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={categoryChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => {
                return `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`;
              }}
              outerRadius={90}
              fill="#8884d8"
              dataKey="value"
            >
              {categoryChartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={
                    entry.color === "purple-500"
                      ? "#8b5cf6"
                      : entry.color === "blue-500"
                      ? "#3b82f6"
                      : entry.color === "pink-500"
                      ? "#ec4899"
                      : entry.color === "green-500"
                      ? "#10b981"
                      : entry.color === "orange-500"
                      ? "#f59e0b"
                      : "#6b7280"
                  }
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "12px",
                padding: "8px",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      );
    },
  };
});
