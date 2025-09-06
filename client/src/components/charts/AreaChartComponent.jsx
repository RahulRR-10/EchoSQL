import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const AreaChartComponent = ({ data, xKey, yKey }) => {
  // Use provided keys or auto-detect from data
  const keys = Object.keys(data[0] || {});
  const actualXKey = xKey || keys.find((k) => typeof data[0][k] === "string") || keys[0];
  const actualYKey = yKey || keys.find((k) => typeof data[0][k] === "number") || keys[1];

  // Convert yKey values to numbers if they're strings
  const processedData = data.map(item => ({
    ...item,
    [actualYKey]: typeof item[actualYKey] === 'string' ? parseFloat(item[actualYKey]) || 0 : item[actualYKey]
  }));

  return (
    <div className="text-white">
      <h3 className="mb-2 font-semibold">Area Chart</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={processedData}>
          <defs>
            <linearGradient id="colorArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <XAxis dataKey={actualXKey} stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <Tooltip 
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#F9FAFB'
            }}
          />
          <Area
            type="monotone"
            dataKey={actualYKey}
            stroke="#06B6D4"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorArea)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AreaChartComponent;
