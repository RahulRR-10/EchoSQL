const express = require("express");
const router = express.Router();
const { protect } = require("../middlewares/auth");
const {
  generateSessionPDF,
  generateSessionReport,
} = require("../controllers/pdfController");

// @route   GET /api/v1/pdf/session/:sessionId
// @desc    Download PDF report for a session
// @access  Private
router.get("/session/:sessionId", protect, generateSessionPDF);

// @route   GET /api/v1/pdf/report/:sessionId
// @desc    Get session report data (for preview before PDF generation)
// @access  Private
router.get("/report/:sessionId", protect, generateSessionReport);

// @route   GET /api/v1/pdf/test
// @desc    Test endpoint to verify PDF routes are working
// @access  Public
router.get("/test", (req, res) => {
  res.json({
    message: "PDF routes are working!",
    timestamp: new Date().toISOString(),
  });
});

module.exports = router;
