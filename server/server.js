const express = require("express");
const mongoose = require("mongoose");
const dotenv = require("dotenv");
const cookieParser = require("cookie-parser");
const morgan = require("morgan");
const cors = require("cors");

dotenv.config();

const app = express();
app.use(morgan("dev"));
app.use(cookieParser());
app.use(express.json());

// Allow all origins for testing; restrict in production
app.use(
  cors({
    origin: function (origin, callback) {
      // Allow requests with no origin (like mobile apps, curl, etc.)
      if (!origin) return callback(null, true);
      // Allow localhost and configured frontend URLs
      const allowedOrigins = [
        process.env.FRONTEND_URL,
        process.env.FRONTEND_URL_PROD,
        "http://localhost:3000",
        "http://localhost:5173",
      ];
      if (allowedOrigins.includes(origin)) {
        return callback(null, true);
      }
      return callback(new Error("Not allowed by CORS"));
    },
    credentials: true,
  })
);

const PORT = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGO_URI;

mongoose
  .connect(MONGO_URI)
  .then(() => console.log("MongoDB connected"))
  .catch((err) => console.error("MongoDB connection error:", err));

// Example route
app.get("/api/v1", (req, res) => {
  res.send("Hello World!");
});

app.use("/api/v1/auth", require("./routes/auth"));
app.use("/api/v1/users", require("./routes/user"));
app.use("/api/v1/databases", require("./routes/database"));
app.use("/api/v1/sessions", require("./routes/querySession"));
app.use("/api/v1/messages", require("./routes/queryMessage"));
app.use("/api/v1/pdf", require("./routes/pdf"));

app.use("/uploads", express.static("uploads"));

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
