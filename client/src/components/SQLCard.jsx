// eslint-disable-next-line
import { motion } from "framer-motion";
import { useState } from "react";
import { formatDistanceToNow } from "date-fns";

const SQLCard = ({
  query,
  sqlQuery,
  sqlResponse,
  summary,
  thoughtProcess,
  executionTime,
  timestamp,
  title,
  databaseType,
}) => {
  const [showThoughtProcess, setShowThoughtProcess] = useState(false);

  // Determine if this is a Neo4j/Cypher query
  const isNeo4j =
    databaseType === "neo4j" ||
    (sqlQuery &&
      (sqlQuery.toLowerCase().includes("match") ||
        sqlQuery.toLowerCase().includes("return") ||
        sqlQuery.toLowerCase().includes("create") ||
        sqlQuery.toLowerCase().includes("merge")));

  // Labels based on database type
  const queryLabel = isNeo4j ? "Cypher Query" : "SQL Query";
  const responseLabel = isNeo4j ? "Graph Results" : "Query Results";

  // Check if sqlResponse is valid and is an array
  const isValidResponse =
    sqlResponse && Array.isArray(sqlResponse) && sqlResponse.length > 0;
  const hasError =
    typeof sqlResponse === "string" || (!isValidResponse && sqlResponse);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="w-full md:max-w-4xl bg-[#1a2a2a] border border-gray-700 rounded-xl shadow-lg p-4 space-y-4"
    >
      {/* User Query */}
      <div className="text-gray-400 text-sm">
        <p className="font-medium mb-1">User Query:</p>
        <p className="text-white">{query}</p>
      </div>

      {/* Title (if provided) */}
      {title && (
        <div className="text-cyan-400 text-lg font-semibold">{title}</div>
      )}

      {/* SQL/Cypher Query */}
      <div className="bg-[#0a1a1a] rounded-lg p-3">
        <p className="text-gray-400 text-xs mb-2 font-medium">{queryLabel}:</p>
        <pre className="text-cyan-400 text-xs md:text-sm overflow-x-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
          <code className="whitespace-pre-wrap break-words">{sqlQuery}</code>
        </pre>
      </div>

      {/* SQL Response - Error Case */}
      {hasError && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
          <p className="text-red-300 text-sm font-medium mb-2">Query Error:</p>
          <p className="text-red-200 text-sm">
            {typeof sqlResponse === "string"
              ? sqlResponse
              : "Invalid query result"}
          </p>
        </div>
      )}

      {/* Query Response - Success Case */}
      {isValidResponse && (
        <div className="overflow-x-auto">
          <p className="text-gray-400 text-xs mb-2 font-medium">
            {responseLabel}:
          </p>
          <table className="min-w-full divide-y divide-gray-700 text-sm text-left">
            <thead className="bg-[#2a3a3a] text-gray-300 uppercase text-xs">
              <tr>
                {sqlResponse[0] &&
                  Object.keys(sqlResponse[0]).map((key, index) => (
                    <th key={index} className="px-3 py-2">
                      {key.replace(/_/g, " ")}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {sqlResponse.map((row, i) => (
                <tr key={i} className="hover:bg-[#2a3a3a]">
                  {Object.values(row).map((val, j) => (
                    <td key={j} className="px-3 py-2 text-gray-300">
                      {typeof val === "object" && val !== null
                        ? JSON.stringify(val)
                        : val}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* No Data Case */}
      {!hasError && !isValidResponse && (
        <div className="bg-gray-800/50 border border-gray-600 rounded-lg p-4 text-center">
          <p className="text-gray-400 text-sm">No data returned from query</p>
        </div>
      )}

      {/* Enhanced Summary Section */}
      {summary && (
        <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-1">
              <div className="w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center">
                <span className="text-blue-400 text-xs font-bold">✨</span>
              </div>
            </div>
            <div className="flex-1">
              <h4 className="text-blue-300 font-medium text-sm mb-2">
                EchoSQL Summary
              </h4>
              <p className="text-gray-200 text-sm leading-relaxed">{summary}</p>
            </div>
          </div>
        </div>
      )}

      {/* Footer Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-gray-500">
        <span>Execution time: {(executionTime / 1000).toFixed(2)}s</span>
        <button
          onClick={() => setShowThoughtProcess(!showThoughtProcess)}
          className="text-cyan-400 hover:text-cyan-300"
        >
          {showThoughtProcess ? "Hide" : "Show"} thought process
        </button>
        <span>
          {formatDistanceToNow(new Date(timestamp), { addSuffix: true })}
        </span>
      </div>

      {/* Thought Process Toggle Section */}
      {showThoughtProcess && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="bg-[#0a1a1a] rounded-lg p-3"
        >
          <pre className="text-gray-400 text-xs md:text-sm whitespace-pre-wrap break-words">
            {thoughtProcess}
          </pre>
        </motion.div>
      )}
    </motion.div>
  );
};

export default SQLCard;
