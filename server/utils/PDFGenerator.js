const puppeteer = require("puppeteer");
const fs = require("fs").promises;
const path = require("path");

class PDFGenerator {
  constructor() {
    this.browser = null;
  }

  async initBrowser() {
    if (!this.browser) {
      this.browser = await puppeteer.launch({
        headless: "new",
        args: ["--no-sandbox", "--disable-setuid-sandbox"],
      });
    }
    return this.browser;
  }

  async closeBrowser() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }

  generateChatHTML(sessionData, messages, visualizations = []) {
    const { title, createdAt, user, database } = sessionData;
    const formattedDate = new Date(createdAt).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

    const messagesHTML = messages
      .map((message, index) => {
        const isUser = message.user && message.user.username;
        const visualization = visualizations.find(
          (viz) => viz.messageIndex === index
        );

        return `
        <div class="message ${isUser ? "user-message" : "assistant-message"}">
          <div class="message-header">
            <div class="message-author">
              ${isUser ? "👤 " + message.user.username : "🤖 EchoSQL Assistant"}
            </div>
            <div class="message-time">
              ${new Date(message.createdAt).toLocaleTimeString()}
            </div>
          </div>
          
          <div class="message-content">
            ${message.requestQuery || message.content || ""}
          </div>
          
          ${
            message.sqlQuery
              ? `
            <div class="sql-section">
              <h4>🔍 Generated SQL Query:</h4>
              <pre class="sql-code">${message.sqlQuery}</pre>
            </div>
          `
              : ""
          }
          
          ${
            message.sqlResponse && Array.isArray(message.sqlResponse)
              ? `
            <div class="results-section">
              <h4>📊 Query Results:</h4>
              <div class="results-table">
                ${this.generateTableHTML(message.sqlResponse)}
              </div>
            </div>
          `
              : ""
          }
          
          ${
            message.summary
              ? `
            <div class="summary-section">
              <h4>📝 Summary:</h4>
              <p>${message.summary}</p>
            </div>
          `
              : ""
          }
          
          ${
            message.thoughtProcess
              ? `
            <div class="thought-process">
              <h4>💭 Thought Process:</h4>
              <p>${message.thoughtProcess}</p>
            </div>
          `
              : ""
          }
          
          ${
            visualization
              ? `
            <div class="visualization-section">
              <h4>📈 Data Visualization:</h4>
              <img src="${visualization.imageData}" alt="Chart visualization" class="chart-image" />
            </div>
          `
              : ""
          }
        </div>
      `;
      })
      .join("");

    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat Session Report - ${title}</title>
        <style>
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fff;
            padding: 40px;
          }
          
          .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #4F46E5;
          }
          
          .header h1 {
            color: #4F46E5;
            font-size: 2.5em;
            margin-bottom: 10px;
          }
          
          .header .subtitle {
            font-size: 1.2em;
            color: #6B7280;
            margin-bottom: 20px;
          }
          
          .metadata {
            background: #F3F4F6;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
          }
          
          .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
          }
          
          .metadata-item {
            display: flex;
            flex-direction: column;
          }
          
          .metadata-label {
            font-weight: bold;
            color: #374151;
            font-size: 0.9em;
            margin-bottom: 5px;
          }
          
          .metadata-value {
            color: #6B7280;
          }
          
          .messages-container {
            margin-bottom: 40px;
          }
          
          .message {
            margin-bottom: 30px;
            page-break-inside: avoid;
          }
          
          .user-message {
            background: linear-gradient(135deg, #EBF8FF 0%, #DBEAFE 100%);
            border-left: 4px solid #3B82F6;
            padding: 20px;
            border-radius: 8px;
          }
          
          .assistant-message {
            background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
            border-left: 4px solid #10B981;
            padding: 20px;
            border-radius: 8px;
          }
          
          .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #E5E7EB;
          }
          
          .message-author {
            font-weight: bold;
            font-size: 1.1em;
          }
          
          .message-time {
            color: #6B7280;
            font-size: 0.9em;
          }
          
          .message-content {
            font-size: 1.1em;
            margin-bottom: 15px;
            line-height: 1.8;
          }
          
          .sql-section, .results-section, .summary-section, .thought-process, .visualization-section {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 6px;
            border: 1px solid #E5E7EB;
          }
          
          .sql-section h4, .results-section h4, .summary-section h4, .thought-process h4, .visualization-section h4 {
            color: #374151;
            margin-bottom: 10px;
            font-size: 1em;
          }
          
          .sql-code {
            background: #1F2937;
            color: #10B981;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
          }
          
          .results-table {
            overflow-x: auto;
          }
          
          .results-table table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
          }
          
          .results-table th, .results-table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #E5E7EB;
          }
          
          .results-table th {
            background: #F9FAFB;
            font-weight: bold;
            color: #374151;
          }
          
          .chart-image {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            border: 1px solid #E5E7EB;
          }
          
          .summary {
            background: #FEF3C7;
            border: 1px solid #F59E0B;
            border-radius: 8px;
            padding: 20px;
            margin-top: 40px;
          }
          
          .summary h2 {
            color: #92400E;
            margin-bottom: 15px;
          }
          
          .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #E5E7EB;
            color: #6B7280;
            font-size: 0.9em;
          }
          
          @media print {
            body { padding: 20px; }
            .message { page-break-inside: avoid; }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>🎤 EchoSQL Chat Report</h1>
          <div class="subtitle">Voice-Powered Database Intelligence Session</div>
        </div>
        
        <div class="metadata">
          <div class="metadata-grid">
            <div class="metadata-item">
              <div class="metadata-label">Session Title</div>
              <div class="metadata-value">${title || "Untitled Session"}</div>
            </div>
            <div class="metadata-item">
              <div class="metadata-label">Created Date</div>
              <div class="metadata-value">${formattedDate}</div>
            </div>
            <div class="metadata-item">
              <div class="metadata-label">User</div>
              <div class="metadata-value">${user?.email || "Unknown User"}</div>
            </div>
            <div class="metadata-item">
              <div class="metadata-label">Database</div>
              <div class="metadata-value">${
                database?.database || "Unknown Database"
              }</div>
            </div>
            <div class="metadata-item">
              <div class="metadata-label">Total Messages</div>
              <div class="metadata-value">${messages.length}</div>
            </div>
            <div class="metadata-item">
              <div class="metadata-label">Generated On</div>
              <div class="metadata-value">${new Date().toLocaleDateString()}</div>
            </div>
          </div>
        </div>
        
        <div class="messages-container">
          <h2 style="color: #374151; margin-bottom: 20px; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px;">💬 Conversation History</h2>
          ${messagesHTML}
        </div>
        
        <div class="summary">
          <h2>📋 Session Summary</h2>
          <p><strong>Total Queries:</strong> ${
            messages.filter((m) => m.sqlQuery).length
          }</p>
          <p><strong>Successful Results:</strong> ${
            messages.filter(
              (m) => m.sqlResponse && Array.isArray(m.sqlResponse)
            ).length
          }</p>
          <p><strong>Key Topics:</strong> Database analysis, data exploration, and business insights</p>
          <p><strong>Session Duration:</strong> ${this.calculateSessionDuration(
            messages
          )}</p>
        </div>
        
        <div class="footer">
          <p>This report was generated automatically by EchoSQL - Voice-Powered Database Intelligence Platform</p>
          <p>Generated on ${new Date().toLocaleString()}</p>
        </div>
      </body>
      </html>
    `;
  }

  generateTableHTML(data) {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return "<p>No data to display</p>";
    }

    const headers = Object.keys(data[0]);
    const maxRows = 50; // Limit rows in PDF to prevent huge files
    const displayData = data.slice(0, maxRows);
    const hasMore = data.length > maxRows;

    return `
      <table>
        <thead>
          <tr>
            ${headers
              .map((header) => `<th>${header.replace(/_/g, " ")}</th>`)
              .join("")}
          </tr>
        </thead>
        <tbody>
          ${displayData
            .map(
              (row) => `
            <tr>
              ${headers
                .map(
                  (header) => `<td>${this.formatCellValue(row[header])}</td>`
                )
                .join("")}
            </tr>
          `
            )
            .join("")}
        </tbody>
      </table>
      ${
        hasMore
          ? `<p style="margin-top: 10px; font-style: italic; color: #6B7280;">Showing first ${maxRows} rows of ${data.length} total records...</p>`
          : ""
      }
    `;
  }

  formatCellValue(value) {
    if (value === null || value === undefined) return "-";
    if (typeof value === "string" && value.length > 100) {
      return value.substring(0, 100) + "...";
    }
    return String(value);
  }

  calculateSessionDuration(messages) {
    if (messages.length < 2) return "N/A";

    const firstMessage = new Date(messages[0].createdAt);
    const lastMessage = new Date(messages[messages.length - 1].createdAt);
    const diffMinutes = Math.round((lastMessage - firstMessage) / (1000 * 60));

    if (diffMinutes < 60) return `${diffMinutes} minutes`;
    const hours = Math.floor(diffMinutes / 60);
    const minutes = diffMinutes % 60;
    return `${hours}h ${minutes}m`;
  }

  async generatePDF(sessionData, messages, visualizations = []) {
    try {
      const browser = await this.initBrowser();
      const page = await browser.newPage();

      // Set page format
      await page.setViewport({ width: 1200, height: 800 });

      const htmlContent = this.generateChatHTML(
        sessionData,
        messages,
        visualizations
      );
      await page.setContent(htmlContent, { waitUntil: "networkidle0" });

      const pdfBuffer = await page.pdf({
        format: "A4",
        printBackground: true,
        margin: {
          top: "20mm",
          right: "15mm",
          bottom: "20mm",
          left: "15mm",
        },
      });

      await page.close();

      return pdfBuffer;
    } catch (error) {
      console.error("PDF generation error:", error);
      throw error;
    }
  }
}

module.exports = PDFGenerator;
