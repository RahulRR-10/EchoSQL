// eslint-disable-next-line
import { motion } from "framer-motion";
import SQLCard from "./SQLCard";
import { formatDistanceToNow } from "date-fns";
import { AiOutlineUser, AiOutlineRobot } from "react-icons/ai"; // Icon imports
import { useState, useEffect } from "react";
import { getGraphRecommendations } from "../utils/service";
import DataVisualization from "./DataVisualization";

const ChatMessage = ({ message }) => {
  const [visualizationData, setVisualizationData] = useState(null);
  const [isLoadingViz, setIsLoadingViz] = useState(false);
  const [vizError, setVizError] = useState(null);
  const [canVisualize, setCanVisualize] = useState(null); // null = unknown, true/false = known
  const [isAutoValidating, setIsAutoValidating] = useState(false);

  // Safety check for message object
  if (!message) {
    return null;
  }

  const isUser = message.user && message.user.username;

  const handleVisualize = async () => {
    if (!message.sqlResponse) return;

    setIsLoadingViz(true);
    setVizError(null);

    try {
      const data = await getGraphRecommendations(
        message.sqlResponse,
        message.requestQuery || "",
        message.sqlQuery || message.cypherQuery || ""
      );

      // If the validator says no visualization, hide the button (don't show large explanation)
      if (data.should_visualize === false) {
        setCanVisualize(false);
        setVisualizationData(null);
      } else {
        setCanVisualize(true);
        setVisualizationData(data);
      }
    } catch (err) {
      setVizError("Failed to generate visualization");
      console.error("Visualization error:", err);
    } finally {
      setIsLoadingViz(false);
    }
  };

  // Auto-validate visualization suitability when a SQL response is present
  useEffect(() => {
    let cancelled = false;

    const autoValidate = async () => {
      if (!message.sqlResponse || !Array.isArray(message.sqlResponse) || message.sqlResponse.length === 0) {
        setCanVisualize(false);
        return;
      }

      // If we've already validated this message, skip
      if (canVisualize !== null) return;

      setIsAutoValidating(true);
      try {
        const res = await getGraphRecommendations(
          message.sqlResponse,
          message.requestQuery || "",
          message.sqlQuery || message.cypherQuery || ""
        );

        if (cancelled) return;

        if (res && res.should_visualize === false) {
          // Hide the button silently
          setCanVisualize(false);
        } else if (res && res.should_visualize === true) {
          setCanVisualize(true);
          // store recommended graphs so user can click visualize later
          setVisualizationData(res);
        } else {
          // Fallback: allow visualize button but no recommendation yet
          setCanVisualize(true);
        }
      } catch (err) {
        // On error, be permissive: allow user to attempt visualization
        console.error('Auto-validate visualization failed:', err);
        setCanVisualize(true);
      } finally {
        setIsAutoValidating(false);
      }
    };

    autoValidate();

    return () => {
      cancelled = true;
    };
  }, [message, canVisualize]);

  // Render SQLCard if it's a response message (SQL or Neo4j)
  const hasQueryResponse =
    (message.sqlQuery && message.sqlResponse) ||
    (message.cypherQuery && message.graphResult);

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

        {/* Only show visualization button for successful queries with array data and when validator allows it */}
        {message.sqlResponse &&
          Array.isArray(message.sqlResponse) &&
          message.sqlResponse.length > 0 &&
          (canVisualize === null || canVisualize === true) && (
            <motion.button
              onClick={handleVisualize}
              disabled={isLoadingViz}
              className="mt-2 px-4 py-2 bg-[#1a2a2a] border border-cyan-500/30 
              rounded-lg text-sm text-cyan-400 hover:bg-[#2a3a3a] 
              transition-all duration-200 disabled:opacity-50"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isLoadingViz ? "Generating..." : "Visualize Data"}
            </motion.button>
          )}

        {/* Only show explicit errors or messages (don't show validator's "no viz" reason) */}
        {vizError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-2 px-4 py-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-sm text-yellow-400"
          >
            💡 {vizError}
          </motion.div>
        )}

        {/* Visualization Component */}
        {visualizationData &&
          message.sqlResponse &&
          Array.isArray(message.sqlResponse) && (
            <DataVisualization
              visualizationData={{
                data: message.sqlResponse,
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
