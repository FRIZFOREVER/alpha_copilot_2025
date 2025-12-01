import { lazy } from "react";

export const ActivityChart = lazy(async () => {
  const recharts = await import("recharts");
  return {
    default: ({
      data,
      showMonthOnly = false,
    }: {
      data: Array<{ month: string; value: number }>;
      showMonthOnly?: boolean;
    }) => {
      const { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } =
        recharts;

      // Для месячного периода показываем только одну метку по центру
      const getXAxisTickFormatter = (value: any, index: number) => {
        if (showMonthOnly) {
          // Находим средний индекс и название месяца
          const middleIndex = Math.floor(data.length / 2);
          const monthName = data.find((item) => item.month)?.month || "";
          // Показываем название месяца только для средней метки
          if (index === middleIndex) {
            return monthName;
          }
          return "";
        }
        return value;
      };

      return (
        <ResponsiveContainer width="100%" height={250}>
          <BarChart
            data={data}
            margin={{ top: 15, right: 30, left: 0, bottom: 0 }}
          >
            <XAxis
              dataKey="month"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#6b7280", fontSize: 12 }}
              tickFormatter={getXAxisTickFormatter}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#6b7280", fontSize: 12 }}
              domain={[0, 400]}
              ticks={[100, 200, 300, 400]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
                padding: "8px",
              }}
            />
            <Bar dataKey="value" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      );
    },
  };
});
