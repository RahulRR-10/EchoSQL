const QueryMessage = require("../models/queryMessage");
const Database = require("../models/database");
const mongoose = require("mongoose");
const axios = require("axios");

const createQueryMessage = async (req, res) => {
  const startTime = Date.now();

  try {
    const database = await Database.findById(req.body.databaseId);
    if (!database) {
      return res
        .status(404)
        .json({ error: "Database configuration not found" });
    }

    let response;
    try {
      const apiRes = await axios.post("http://localhost:1111/chat", {
        query_request: {
          query: req.body.requestQuery,
        },
        database_config: {
          dbtype: database.dbType,
          host: database.host,
          user: database.username,
          password: database.password,
          dbname: database.database,
          uri: database.uri, // Add uri field for Neo4j connections
        },
      });

      response = apiRes.data;

      // Handle custom error response returned from FastAPI with status 200
      if (response.error) {
        return res.status(400).json({
          error: response.error,
          details: response.details || "No additional details provided",
        });
      }
    } catch (error) {
      if (error.response) {
        // FastAPI returned an HTTP error status
        const status = error.response.status;
        const errorData = error.response.data;

        return res.status(status).json({
          error: errorData.detail || "Chat service error",
          code: status,
        });
      } else if (error.request) {
        return res.status(503).json({
          error: "Unable to reach chat service. Please try again later.",
        });
      } else {
        return res
          .status(500)
          .json({ error: `Unexpected error: ${error.message}` });
      }
    }

    // Handle both SQL and Neo4j responses
    const {
      user_query,
      sql_query,
      sql_result,
      cypher_query,
      graph_result,
      summary,
      agent_thought_process,
      title,
      database_type,
    } = response;

    // Use appropriate fields based on database type
    const queryField = sql_query || cypher_query || null;
    const resultField = sql_result || graph_result || null;
    const isNeo4j = database_type === "neo4j" || cypher_query;

    const queryMessageData = {
      session: req.body.sessionId,
      user: req.user._id,
      requestQuery: user_query,
      summary,
      thoughtProcess: agent_thought_process,
      executionTime: Date.now() - startTime,
      title,
      databaseType: database_type,
    };

    // Add appropriate query and response fields based on database type
    if (isNeo4j) {
      queryMessageData.cypherQuery = queryField;
      queryMessageData.graphResult = resultField;
    } else {
      queryMessageData.sqlQuery = queryField;
      queryMessageData.sqlResponse = resultField;
    }

    const queryMessage = new QueryMessage(queryMessageData);

    const savedMessage = await queryMessage.save();

    if (title) {
      await mongoose
        .model("QuerySession")
        .findByIdAndUpdate(req.body.sessionId, { title });
    }

    return res.status(201).json(savedMessage);
  } catch (error) {
    console.error("Error creating query message:", error);
    return res.status(500).json({ error: error.message });
  }
};

// Get query messages by session ID
const getQueryMessagesBySession = async (req, res) => {
  try {
    if (!req.params.sessionId) {
      return res.status(400).json({ error: "Session ID is required" });
    }

    const messages = await QueryMessage.find({ session: req.params.sessionId })
      .sort({ createdAt: -1 })
      .populate("user", "username");

    if (!messages || messages.length === 0) {
      return res
        .status(404)
        .json({ message: "No messages found for this session" });
    }

    res.status(200).json(messages);
  } catch (error) {
    console.error("Error fetching query messages:", error);
    res.status(500).json({ error: "Failed to fetch query messages" });
  }
};

module.exports = {
  createQueryMessage,
  getQueryMessagesBySession,
};
