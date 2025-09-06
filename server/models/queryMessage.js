const mongoose = require("mongoose");

const queryMessageSchema = new mongoose.Schema(
  {
    session: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "QuerySession",
      required: true,
    },
    user: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    requestQuery: { type: String, required: true },
    sqlQuery: { type: String },
    sqlResponse: { type: mongoose.Schema.Types.Mixed },
    cypherQuery: { type: String }, // For Neo4j queries
    graphResult: { type: mongoose.Schema.Types.Mixed }, // For Neo4j results
    summary: { type: String },
    thoughtProcess: { type: String },
    executionTime: { type: Number },
    title: { type: String }, // For response titles
    databaseType: { type: String }, // "sql" or "neo4j"
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model("QueryMessage", queryMessageSchema);
