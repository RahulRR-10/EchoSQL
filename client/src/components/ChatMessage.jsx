// eslint-disable-next-line
import { motion } from "framer-motion";
import SQLCard from "./SQLCard";
import { formatDistanceToNow } from "date-fns";
import { AiOutlineUser, AiOutlineRobot } from "react-icons/ai"; // Icon imports
import { useState } from "react";
import { getGraphRecommendations } from "../utils/service";
import DataVisualization from "./DataVisualization";

const ChatMessage = ({ message }) => {
  const [visualizationData, setVisualizationData] = useState(null);
  const [isLoadingViz, setIsLoadingViz] = useState(false);
  const [vizError, setVizError] = useState(null);
  const [showVisualization, setShowVisualization] = useState(false);

  // Safety check for message object
  if (!message) {
    return null;
  }

  const isUser = message.user && message.user.username;

  const handleToggleVisualization = async () => {
    // If already showing, just hide it
    if (showVisualization) {
      setShowVisualization(false);
      return;
    }

    // If we already have viz data, just show it
    if (visualizationData) {
      setShowVisualization(true);
      return;
    }

    // Get the actual data (SQL or Neo4j)
    const responseData = message.sqlResponse || message.graphResult;
    if (!responseData) return;

    setIsLoadingViz(true);
    setVizError(null);

    try {
      const data = await getGraphRecommendations(
        responseData,
        message.requestQuery || "",
        message.sqlQuery || message.cypherQuery || ""
      );

      // Only show if visualization is recommended
      if (data.should_visualize === false) {
        setVizError(data.reason || "This data is not suitable for visualization");
        setVisualizationData(null);
        setShowVisualization(false);
      } else {
        setVisualizationData(data);
        setShowVisualization(true);
        setVizError(null);
      }
    } catch (err) {
      setVizError("Failed to generate visualization");
      console.error("Visualization error:", err);
    } finally {
      setIsLoadingViz(false);
    }
  };

  // Render SQLCard if it's a response message (SQL or Neo4j)
  const hasQueryResponse =
    (message.sqlQuery && message.sqlResponse) ||
    (message.cypherQuery && message.graphResult);

  // Check if this is a Neo4j graph result (nodes with properties)
  const isNeo4jGraphResult = message.graphResult && 
    Array.isArray(message.graphResult) && 
    message.graphResult.length > 0 &&
    message.graphResult[0] && 
    typeof message.graphResult[0] === 'object' &&
    Object.values(message.graphResult[0]).some(val => 
      val && typeof val === 'object' && (val.type || val.properties)
    );

  // Only show visualize button for:
  // 1. SQL results (always)
  // 2. Neo4j results that are NOT graph nodes (i.e., aggregated data like COUNT, SUM)
  const canShowVisualization = message.sqlResponse || 
    (message.graphResult && !isNeo4jGraphResult);

  if (hasQueryResponse) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="w-full flex flex-col items-center px-4 my-4"
      >
        <SQLCard
          query={message.requestQuery}
          sqlQuery={message.sqlQuery || message.cypherQuery}
          sqlResponse={message.sqlResponse || message.graphResult}
          summary={message.summary}
          title={message.title}
          databaseType={
            message.databaseType || (message.cypherQuery ? "neo4j" : "sql")
          }
          thoughtProcess={message.thoughtProcess}
          executionTime={message.executionTime}
          timestamp={message.createdAt}
        />

        {/* Visualization button - only for SQL or Neo4j aggregated results, NOT graph nodes */}
        {canShowVisualization && (
            <div className="flex flex-col items-center gap-2 mt-3">
              <motion.button
                onClick={handleToggleVisualization}
                disabled={isLoadingViz}
                className={`px-6 py-2 rounded-lg text-sm font-medium
                  transition-all duration-200 disabled:opacity-50
                  ${showVisualization 
                    ? 'bg-cyan-500/20 border border-cyan-500 text-cyan-400 hover:bg-cyan-500/30' 
                    : 'bg-[#1a2a2a] border border-gray-600 text-gray-300 hover:bg-[#2a3a3a] hover:border-cyan-500/50'
                  }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {isLoadingViz 
                  ? "Analyzing..." 
                  : showVisualization 
                    ? "Hide Visualization" 
                    : "📊 Visualize Data"}
              </motion.button>
              
              {vizError && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="px-4 py-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-xs text-yellow-400 max-w-md text-center"
                >
                  {vizError}
                </motion.div>
              )}
            </div>
          )}

        {/* Visualization Component - works for both SQL and Neo4j */}
        {showVisualization &&
          visualizationData &&
          (message.sqlResponse || message.graphResult) &&
          Array.isArray(message.sqlResponse || message.graphResult) && (
            <DataVisualization
              visualizationData={{
                data: message.sqlResponse || message.graphResult,
                recommended_graphs: visualizationData.recommended_graphs,
              }}
            />
          )}
      </motion.div>
    );
  }

  // Regular user/AI messages
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`w-full px-4 my-4 flex ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div className="max-w-[70%] flex flex-col gap-1">
        <div className="flex items-center gap-2">
          {isUser ? (
            <AiOutlineUser className="text-green-400 w-5 h-5" />
          ) : (
            <AiOutlineRobot className="text-blue-400 w-5 h-5" />
          )}
          {isUser && (
            <span className="text-xs text-gray-400 px-2">
              {message.user.username}
            </span>
          )}
        </div>

        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? "bg-gradient-to-r from-green-400 to-cyan-400 text-black"
              : "text-white bg-transparent border border-gray-700"
          }`}
        >
          {message.requestQuery || message.content}
        </div>

        {/* Thought process section */}
        {message.thoughtProcess && (
          <div className="bg-gray-800 p-3 rounded-xl mt-2">
            <span className="text-xs text-gray-400">Thought Process:</span>
            <p className="text-sm text-white">{message.thoughtProcess}</p>
          </div>
        )}

        <div className="flex justify-between items-center mt-2">
          <span className="text-xs text-gray-500 px-2">
            {formatDistanceToNow(new Date(message.createdAt), {
              addSuffix: true,
            })}
          </span>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatMessage;
