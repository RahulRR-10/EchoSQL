import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const ScatterChartComponent = ({ data, xKey, yKey }) => {
  // Use provided keys or auto-detect from data
  const keys = Object.keys(data[0] || {});
  const actualXKey = xKey || keys.find((k) => typeof data[0][k] === "number") || keys[0];
  const actualYKey = yKey || keys.find((k) => typeof data[0][k] === "number" && k !== actualXKey) || keys[1];

  // Convert values to numbers if they're strings
  const processedData = data.map(item => ({
    ...item,
    [actualXKey]: typeof item[actualXKey] === 'string' ? parseFloat(item[actualXKey]) || 0 : item[actualXKey],
    [actualYKey]: typeof item[actualYKey] === 'string' ? parseFloat(item[actualYKey]) || 0 : item[actualYKey]
  }));

  return (
    <div className="text-white">
      <h3 className="mb-2 font-semibold">Scatter Chart</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart>
          <CartesianGrid stroke="#374151" />
          <XAxis 
            dataKey={actualXKey} 
            name={actualXKey} 
            stroke="#9CA3AF"
            type="number"
          />
          <YAxis 
            dataKey={actualYKey} 
            name={actualYKey} 
            stroke="#9CA3AF"
            type="number"
          />
          <Tooltip 
            cursor={{ strokeDasharray: "3 3" }}
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#F9FAFB'
            }}
          />
          <Scatter 
            name="Data Points" 
            data={processedData} 
            fill="#10B981" 
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ScatterChartComponent;
