import React, { useState } from "react";
import { motion } from "framer-motion";
import { HiDownload, HiDocumentText, HiEye } from "react-icons/hi";

// API base URL - remove /api/v1 from the end and ensure no trailing slash
const API_BASE_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:5000/api/v1"
)
  .replace("/api/v1", "")
  .replace(/\/$/, ""); // Remove trailing slash if present

const PDFDownloadButton = ({
  sessionId,
  sessionTitle,
  className = "",
  buttonStyle = "full", // "full", "icon", "compact"
  iconSize = 16,
  onDownloadStart,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [reportData, setReportData] = useState(null);

  const downloadPDF = async () => {
    try {
      setIsGenerating(true);

      // Call the callback if provided
      if (onDownloadStart) {
        onDownloadStart();
      }

      const apiUrl = `${API_BASE_URL}/api/v1/pdf/session/${sessionId}`;
      console.log("PDF Download URL:", apiUrl);
      console.log("API_BASE_URL:", API_BASE_URL);

      const response = await fetch(apiUrl, {
        method: "GET",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("PDF download failed - Response:", errorText);
        throw new Error(
          `HTTP error! status: ${response.status} - ${errorText}`
        );
      }

      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/pdf")) {
        const text = await response.text();
        console.error("PDF download failed - Expected PDF but got:", text);
        throw new Error("Server returned non-PDF response");
      }

      // Get the blob
      const blob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      // Generate filename
      const timestamp = new Date().toISOString().split("T")[0];
      const filename = `chat_${sessionId}_${timestamp}.pdf`;
      link.download = filename;

      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Cleanup
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("PDF download failed:", error);
      alert("Failed to download PDF: " + error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const previewReport = async () => {
    try {
      const apiUrl = `${API_BASE_URL}/api/v1/pdf/report/${sessionId}`;
      console.log("Preview Report URL:", apiUrl);
      console.log("API_BASE_URL:", API_BASE_URL);

      const response = await fetch(apiUrl, {
        method: "GET",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Preview failed - Response:", errorText);
        throw new Error(
          `HTTP error! status: ${response.status} - ${errorText}`
        );
      }

      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await response.text();
        console.error("Preview failed - Expected JSON but got:", text);
        throw new Error("Server returned non-JSON response");
      }

      const data = await response.json();
      setReportData(data);
      setShowPreview(true);
    } catch (error) {
      console.error("Preview failed:", error);
      alert("Failed to load preview: " + error.message);
    }
  };

  return (
    <>
      {buttonStyle === "icon" ? (
        // Icon-only mode for context menus
        <motion.button
          onClick={downloadPDF}
          disabled={isGenerating}
          className={className}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          title="Download PDF"
        >
          {isGenerating ? (
            <div
              className={`border-2 border-current border-t-transparent rounded-full animate-spin`}
              style={{ width: iconSize, height: iconSize }}
            />
          ) : (
            <HiDownload size={iconSize} />
          )}
        </motion.button>
      ) : (
        // Full or compact mode
        <div className={`flex items-center space-x-2 ${className}`}>
          {/* Preview Button */}
          <motion.button
            onClick={previewReport}
            className="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white rounded-lg transition-all duration-200"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <HiEye className="w-4 h-4" />
            <span className="text-sm">Preview</span>
          </motion.button>

          {/* Download PDF Button */}
          <motion.button
            onClick={downloadPDF}
            disabled={isGenerating}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-600 disabled:to-gray-700 text-white rounded-lg transition-all duration-200 shadow-lg"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isGenerating ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span className="text-sm">Generating...</span>
              </>
            ) : (
              <>
                <HiDownload className="w-4 h-4" />
                <span className="text-sm font-medium">Download PDF</span>
              </>
            )}
          </motion.button>
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && reportData && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowPreview(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-xl shadow-2xl max-w-4xl max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold flex items-center">
                    <HiDocumentText className="w-6 h-6 mr-2" />
                    Report Preview
                  </h2>
                  <p className="text-blue-100 mt-1">
                    {reportData.session.title}
                  </p>
                </div>
                <button
                  onClick={() => setShowPreview(false)}
                  className="text-white hover:text-blue-200 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              {/* Session Metadata */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">
                  Session Details
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-600">Created:</span>
                    <p className="text-gray-800">
                      {new Date(
                        reportData.session.createdAt
                      ).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">User:</span>
                    <p className="text-gray-800">
                      {reportData.session.user.email}
                    </p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Database:</span>
                    <p className="text-gray-800">
                      {reportData.session.database?.database || "N/A"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Statistics */}
              <div className="bg-blue-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">
                  Session Statistics
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      {reportData.statistics.totalMessages}
                    </p>
                    <p className="text-gray-600">Total Messages</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {reportData.statistics.totalQueries}
                    </p>
                    <p className="text-gray-600">SQL Queries</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">
                      {reportData.statistics.successfulQueries}
                    </p>
                    <p className="text-gray-600">Successful</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-orange-600">
                      {reportData.statistics.sessionDuration}m
                    </p>
                    <p className="text-gray-600">Duration</p>
                  </div>
                </div>
              </div>

              {/* Sample Messages */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">
                  Sample Messages (First 3)
                </h3>
                <div className="space-y-3">
                  {reportData.messages.slice(0, 3).map((message, index) => (
                    <div
                      key={index}
                      className="border border-gray-200 rounded-lg p-3"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-sm text-gray-600">
                          {message.user ? "👤 User" : "🤖 Assistant"}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(message.createdAt).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-gray-800 text-sm">
                        {message.requestQuery ||
                          message.content ||
                          "No content"}
                      </p>
                      {message.sqlQuery && (
                        <div className="mt-2 p-2 bg-gray-100 rounded text-xs font-mono">
                          {message.sqlQuery}
                        </div>
                      )}
                    </div>
                  ))}
                  {reportData.messages.length > 3 && (
                    <p className="text-gray-500 text-sm text-center italic">
                      ...and {reportData.messages.length - 3} more messages
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="bg-gray-50 px-6 py-4 flex justify-between items-center">
              <span className="text-gray-600 text-sm">
                Full report will include all messages and visualizations
              </span>
              <motion.button
                onClick={downloadPDF}
                disabled={isGenerating}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span className="text-sm">Generating...</span>
                  </>
                ) : (
                  <>
                    <HiDownload className="w-4 h-4" />
                    <span className="text-sm">Download Full PDF</span>
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </>
  );
};

export default PDFDownloadButton;
