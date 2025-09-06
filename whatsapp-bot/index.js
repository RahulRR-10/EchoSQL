import express from "express";
import bodyParser from "body-parser";
import axios from "axios";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL;

// Middleware
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

// Health check endpoint
app.get("/", (req, res) => {
  res.json({ 
    status: "WhatsApp Bot is running!",
    port: PORT,
    backendUrl: BACKEND_URL 
  });
});

// WhatsApp webhook route
app.post("/whatsapp", async (req, res) => {
  try {
    console.log("📩 Full Incoming Request Body:", JSON.stringify(req.body, null, 2));
    
    const incomingMsg = req.body.Body;
    console.log("📱 Incoming WhatsApp Message:", incomingMsg);
    
    if (!incomingMsg) {
      console.log("⚠️ No message body found in request");
      res.set("Content-Type", "text/xml");
      res.send(`
        <Response>
          <Message>Sorry, I didn't receive any message.</Message>
        </Response>
      `);
      return;
    }

    if (!BACKEND_URL) {
      console.error("❌ BACKEND_URL not configured");
      res.set("Content-Type", "text/xml");
      res.send(`
        <Response>
          <Message>Sorry, backend service is not configured.</Message>
        </Response>
      `);
      return;
    }

    // Forward message to backend
    console.log(`🔄 Processing message: ${incomingMsg}`);
    
    // For WhatsApp, we'll use a default database configuration
    // Users send natural language queries, we handle the database config internally
    const requestPayload = {
      database_config: {
        dbtype: process.env.DEFAULT_DB_TYPE || "mysql",
        host: process.env.DEFAULT_DB_HOST || "localhost", 
        user: process.env.DEFAULT_DB_USER || "root",
        password: process.env.DEFAULT_DB_PASSWORD || "password",
        dbname: process.env.DEFAULT_DB_NAME || ""  // Empty string for default database
      },
      query_request: {
        query: incomingMsg
      }
    };
    
    console.log(`🔄 Using /chat endpoint with default database config`);
    const backendResponse = await axios.post(`${BACKEND_URL}/chat`, requestPayload, {
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' }
    });

    // Process the backend response
    console.log("✅ Backend response received");

    const result = backendResponse.data;
    let answer;
    
    // Format the response to match webapp experience
    if (result.error) {
      answer = `❌ ${result.error}`;
    } else if (result.summary) {
      // Successful database query response - clean format like webapp
      answer = result.summary;
      
      // If there are results, add a sample
      if (result.sql_result && Array.isArray(result.sql_result) && result.sql_result.length > 0) {
        const sampleSize = Math.min(2, result.sql_result.length);
        answer += `\n\n📋 Sample results:`;
        for (let i = 0; i < sampleSize; i++) {
          const row = result.sql_result[i];
          const rowStr = Object.entries(row)
            .map(([key, value]) => `${key}: ${value}`)
            .join(', ');
          answer += `\n• ${rowStr}`;
        }
        if (result.sql_result.length > sampleSize) {
          answer += `\n... and ${result.sql_result.length - sampleSize} more`;
        }
      }
    } else {
      // Fallback
      answer = result.answer || "Query completed successfully";
    }
    
    console.log("📤 Formatted response:", answer);

    // Send TwiML response back to WhatsApp
    res.set("Content-Type", "text/xml");
    res.send(`
      <Response>
        <Message>${answer}</Message>
      </Response>
    `);

    console.log("📤 Sent response to WhatsApp user");

  } catch (error) {
    console.error("❌ Error processing WhatsApp message:", error.message);
    
    // Log more details for debugging
    if (error.response) {
      console.error("Backend Error Response:", {
        status: error.response.status,
        data: error.response.data
      });
    }

    // Send error response to user
    res.set("Content-Type", "text/xml");
    res.send(`
      <Response>
        <Message>Sorry, something went wrong.</Message>
      </Response>
    `);
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error("❌ Unhandled error:", error);
  res.status(500).json({ error: "Internal server error" });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 WhatsApp Bot server running on port ${PORT}`);
  console.log(`🔗 Backend URL: ${BACKEND_URL || 'Not configured'}`);
  console.log(`📱 Webhook endpoint: http://localhost:${PORT}/whatsapp`);
});
