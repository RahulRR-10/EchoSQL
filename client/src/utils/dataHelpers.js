// utils/dataHelpers.js

export const getNumericFields = (data) => {
  if (!Array.isArray(data) || data.length === 0) return [];
  const sample = data[0];
  return Object.keys(sample).filter((key) => {
    const value = sample[key];
    // Include numbers, numeric strings, and parseable values
    return typeof value === "number" || 
           (!isNaN(parseFloat(value)) && isFinite(value)) ||
           (typeof value === "string" && /^\d+(\.\d+)?$/.test(value.trim()));
  });
};

export const getCategoricalFields = (data) => {
  if (!Array.isArray(data) || data.length === 0) return [];
  const sample = data[0];
  return Object.keys(sample).filter((key) => {
    const value = sample[key];
    // Include strings, dates, and non-numeric values
    return typeof value === "string" || 
           value instanceof Date ||
           (value !== null && value !== undefined && typeof value !== "number");
  });
};

export const getAllFields = (data) => {
  if (!Array.isArray(data) || data.length === 0) return [];
  return Object.keys(data[0]);
};

export const convertToNumeric = (data, field) => {
  return data.map(row => ({
    ...row,
    [field]: parseFloat(row[field]) || 0
  }));
};

export const canVisualize = (data) => {
  if (!Array.isArray(data) || data.length === 0) return false;
  const fields = getAllFields(data);
  return fields.length > 0; // Can always try to visualize if we have fields
};
