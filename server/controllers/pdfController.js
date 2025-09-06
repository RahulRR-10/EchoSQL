const PDFGenerator = require("../utils/PDFGenerator");
const QueryMessage = require("../models/queryMessage");
const QuerySession = require("../models/querySession");
const Database = require("../models/database");

const pdfGenerator = new PDFGenerator();

const generateSessionPDF = async (req, res) => {
  try {
    const { sessionId } = req.params;
    console.log(`PDF generation requested for session: ${sessionId}`);
    console.log(`User ID: ${req.user?._id}`);

    // Validate session exists and belongs to user
    const session = await QuerySession.findById(sessionId)
      .populate("user", "username email")
      .populate("database", "database dbType host");

    console.log(`Session found:`, session ? "Yes" : "No");

    if (!session) {
      console.log(`Session ${sessionId} not found`);
      return res.status(404).json({ error: "Session not found" });
    }

    // Check if user owns this session
    if (session.user._id.toString() !== req.user._id.toString()) {
      return res.status(403).json({ error: "Access denied" });
    }

    // Get all messages for this session
    const messages = await QueryMessage.find({ session: sessionId })
      .sort({ createdAt: 1 })
      .populate("user", "username email");

    if (!messages || messages.length === 0) {
      return res
        .status(404)
        .json({ error: "No messages found for this session" });
    }

    // Generate PDF
    const pdfBuffer = await pdfGenerator.generatePDF(session, messages);

    // Create filename
    const timestamp = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
    const filename = `chat_${sessionId}_${timestamp}.pdf`;

    // Set response headers
    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", `attachment; filename="${filename}"`);
    res.setHeader("Content-Length", pdfBuffer.length);

    // Send PDF
    res.send(pdfBuffer);
  } catch (error) {
    console.error("PDF generation error:", error);
    res.status(500).json({
      error: "Failed to generate PDF",
      details: error.message,
    });
  }
};

const generateSessionReport = async (req, res) => {
  try {
    const { sessionId } = req.params;
    console.log(`Report generation requested for session: ${sessionId}`);
    console.log(`User ID: ${req.user?._id}`);

    // Get session with metadata
    const session = await QuerySession.findById(sessionId)
      .populate("user", "username email")
      .populate("database", "database dbType host");

    console.log(`Session found for report:`, session ? "Yes" : "No");

    if (!session) {
      console.log(`Session ${sessionId} not found for report`);
      return res.status(404).json({ error: "Session not found" });
    }

    // Check access
    if (session.user._id.toString() !== req.user._id.toString()) {
      return res.status(403).json({ error: "Access denied" });
    }

    // Get messages with statistics
    const messages = await QueryMessage.find({ session: sessionId })
      .sort({ createdAt: 1 })
      .populate("user", "username email");

    // Calculate session statistics
    const stats = {
      totalMessages: messages.length,
      totalQueries: messages.filter((m) => m.sqlQuery).length,
      successfulQueries: messages.filter(
        (m) => m.sqlResponse && Array.isArray(m.sqlResponse)
      ).length,
      averageResponseTime:
        messages
          .filter((m) => m.executionTime)
          .reduce((sum, m) => sum + m.executionTime, 0) /
          messages.filter((m) => m.executionTime).length || 0,
      firstMessage: messages[0]?.createdAt,
      lastMessage: messages[messages.length - 1]?.createdAt,
      sessionDuration:
        messages.length > 1
          ? Math.round(
              (new Date(messages[messages.length - 1].createdAt) -
                new Date(messages[0].createdAt)) /
                (1000 * 60)
            )
          : 0,
    };

    res.json({
      session: {
        _id: session._id,
        title: session.title,
        description: session.description,
        createdAt: session.createdAt,
        user: session.user,
        database: session.database,
      },
      messages,
      statistics: stats,
    });
  } catch (error) {
    console.error("Session report error:", error);
    res.status(500).json({
      error: "Failed to generate session report",
      details: error.message,
    });
  }
};

// Cleanup function to close PDF generator browser
const cleanup = async () => {
  try {
    await pdfGenerator.closeBrowser();
  } catch (error) {
    console.error("Cleanup error:", error);
  }
};

// Handle graceful shutdown
process.on("SIGINT", cleanup);
process.on("SIGTERM", cleanup);

module.exports = {
  generateSessionPDF,
  generateSessionReport,
  cleanup,
};
