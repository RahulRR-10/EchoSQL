import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

const COLORS = ["#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#F97316", "#EC4899"];

const PieChartComponent = ({ data, nameKey, valueKey }) => {
  // Use provided keys or auto-detect from data
  const keys = Object.keys(data[0] || {});
  const actualNameKey = nameKey || keys.find((k) => typeof data[0][k] === "string") || keys[0];
  const actualValueKey = valueKey || keys.find((k) => typeof data[0][k] === "number") || keys[1];

  // Convert valueKey values to numbers if they're strings
  const processedData = data.map(item => ({
    ...item,
    [actualValueKey]: typeof item[actualValueKey] === 'string' ? parseFloat(item[actualValueKey]) || 0 : item[actualValueKey]
  }));

  return (
    <div className="text-white">
      <h3 className="mb-2 font-semibold">Pie Chart</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Tooltip 
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#F9FAFB'
            }}
          />
          <Pie
            data={processedData}
            dataKey={actualValueKey}
            nameKey={actualNameKey}
            cx="50%"
            cy="50%"
            outerRadius={100}
            fill="#06B6D4"
            label={({ name, value }) => `${name}: ${value}`}
          >
            {processedData.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PieChartComponent;
