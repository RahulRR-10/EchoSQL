import React from "react";
import BarChartComponent from "./charts/BarChartComponent";
import LineChartComponent from "./charts/LineChartComponent";
import PieChartComponent from "./charts/PieChartComponent";
import AreaChartComponent from "./charts/AreaChartComponent";
import ScatterChartComponent from "./charts/ScatterChartComponent";
import HeatmapChartComponent from "./charts/HeatmapChartComponent";
import { getNumericFields, getCategoricalFields, getAllFields, convertToNumeric, canVisualize } from "../utils/dataHelpers";

// ChartRenderer: Aggressively attempts to visualize any data with appropriate charts
// Only returns "cannot visualize" if truly impossible
const ChartRenderer = ({ data, recommendedGraphs = [] }) => {
  if (!data || data.length === 0) {
    return <p className="text-red-500">No data to display</p>;
  }

  if (!canVisualize(data)) {
    return (
      <div className="text-yellow-400 text-center p-4">
        This response cannot be visualized.
      </div>
    );
  }

  const allFields = getAllFields(data);
  let numericFields = getNumericFields(data);
  let categoricalFields = getCategoricalFields(data);
  const chartsToRender = [];

  // If no numeric fields, try to convert some categorical fields to numeric
  if (numericFields.length === 0) {
    for (const field of categoricalFields) {
      const firstValue = data[0][field];
      if (!isNaN(parseFloat(firstValue)) && isFinite(firstValue)) {
        data = convertToNumeric(data, field);
        numericFields = getNumericFields(data);
        categoricalFields = getCategoricalFields(data);
        break;
      }
    }
  }

  // If still no numeric fields, use row count or create an index
  if (numericFields.length === 0 && categoricalFields.length > 0) {
    // Add a count field for visualization
    const countData = {};
    data.forEach(row => {
      const key = row[categoricalFields[0]];
      countData[key] = (countData[key] || 0) + 1;
    });
    
    data = Object.entries(countData).map(([key, count]) => ({
      [categoricalFields[0]]: key,
      count: count
    }));
    
    numericFields = ['count'];
    categoricalFields = [categoricalFields[0]];
  }

  // Helper functions to check if charts can be rendered
  const canRenderBar = numericFields.length > 0 && (categoricalFields.length > 0 || allFields.length > 1);
  const canRenderLine = numericFields.length > 0 && (categoricalFields.length > 0 || allFields.length > 1);
  const canRenderPie = numericFields.length > 0 && categoricalFields.length > 0;
  const canRenderArea = numericFields.length > 0 && (categoricalFields.length > 0 || allFields.length > 1);
  const canRenderScatter = numericFields.length >= 2;
  const canRenderHeatmap = numericFields.length > 0 && categoricalFields.length >= 2;

  // Prioritize recommended charts first
  if (recommendedGraphs.includes("bar") && canRenderBar) {
    chartsToRender.push(
      <BarChartComponent
        key="bar"
        data={data}
        xKey={categoricalFields[0] || allFields[0]}
        yKey={numericFields[0]}
      />
    );
  }
  
  if (recommendedGraphs.includes("line") && canRenderLine) {
    chartsToRender.push(
      <LineChartComponent
        key="line"
        data={data}
        xKey={categoricalFields[0] || allFields[0]}
        yKey={numericFields[0]}
      />
    );
  }
  
  if (recommendedGraphs.includes("pie") && canRenderPie) {
    chartsToRender.push(
      <PieChartComponent
        key="pie"
        data={data}
        nameKey={categoricalFields[0]}
        valueKey={numericFields[0]}
      />
    );
  }
  
  if (recommendedGraphs.includes("area") && canRenderArea) {
    chartsToRender.push(
      <AreaChartComponent
        key="area"
        data={data}
        xKey={categoricalFields[0] || allFields[0]}
        yKey={numericFields[0]}
      />
    );
  }
  
  if (recommendedGraphs.includes("scatter") && canRenderScatter) {
    chartsToRender.push(
      <ScatterChartComponent
        key="scatter"
        data={data}
        xKey={numericFields[0]}
        yKey={numericFields[1]}
      />
    );
  }
  
  if (recommendedGraphs.includes("heatmap") && canRenderHeatmap) {
    chartsToRender.push(
      <HeatmapChartComponent
        key="heatmap"
        data={data}
        xKey={categoricalFields[0]}
        yKey={categoricalFields[1]}
        valueKey={numericFields[0]}
      />
    );
  }

  // If no recommended charts worked, aggressively try defaults
  if (chartsToRender.length === 0) {
    if (canRenderBar) {
      chartsToRender.push(
        <BarChartComponent
          key="default-bar"
          data={data}
          xKey={categoricalFields[0] || allFields[0]}
          yKey={numericFields[0]}
        />
      );
    } else if (canRenderPie && data.length <= 20) { // Pie charts work well with smaller datasets
      chartsToRender.push(
        <PieChartComponent
          key="default-pie"
          data={data}
          nameKey={categoricalFields[0]}
          valueKey={numericFields[0]}
        />
      );
    } else if (canRenderScatter) {
      chartsToRender.push(
        <ScatterChartComponent
          key="default-scatter"
          data={data}
          xKey={numericFields[0]}
          yKey={numericFields[1]}
        />
      );
    } else if (canRenderLine) {
      chartsToRender.push(
        <LineChartComponent
          key="default-line"
          data={data}
          xKey={categoricalFields[0] || allFields[0]}
          yKey={numericFields[0]}
        />
      );
    }
  }

  // Last resort: if we have any fields at all, create a simple bar chart
  if (chartsToRender.length === 0 && allFields.length > 0) {
    // Create a simple count visualization
    const simpleData = data.map((row, index) => ({
      index: `Row ${index + 1}`,
      value: Object.values(row).find(v => !isNaN(parseFloat(v))) || 1
    }));
    
    chartsToRender.push(
      <BarChartComponent
        key="last-resort-bar"
        data={simpleData}
        xKey="index"
        yKey="value"
      />
    );
  }

  // Only return "cannot visualize" if absolutely nothing worked
  if (chartsToRender.length === 0) {
    return (
      <div className="text-yellow-400 text-center p-4">
        This response cannot be visualized.
      </div>
    );
  }

  return <div className="space-y-8">{chartsToRender}</div>;
};

export default ChartRenderer;
