import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

const MultiLanguageVoice = ({ onTranscript, onLanguageDetect }) => {
  const [isListening, setIsListening] = useState(false);
  const [detectedLanguage, setDetectedLanguage] = useState("en");
  const [confidence, setConfidence] = useState(0);
  const [transcript, setTranscript] = useState("");

  const languages = {
    en: "🇺🇸 English",
    es: "🇪🇸 Spanish",
    fr: "🇫🇷 French",
    de: "🇩🇪 German",
    it: "🇮🇹 Italian",
    pt: "🇵🇹 Portuguese",
    zh: "🇨🇳 Chinese",
    ja: "🇯🇵 Japanese",
    ko: "🇰🇷 Korean",
    hi: "🇮🇳 Hindi",
    ar: "🇸🇦 Arabic",
  };

  useEffect(() => {
    if (
      !("webkitSpeechRecognition" in window) &&
      !("SpeechRecognition" in window)
    ) {
      console.warn("Speech recognition not supported");
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);

    recognition.onresult = async (event) => {
      const result = event.results[event.results.length - 1];
      const transcriptText = result[0].transcript;
      const confidenceScore = result[0].confidence || 0.8;

      setTranscript(transcriptText);
      setConfidence(confidenceScore);

      // Detect language using AI
      try {
        const langDetection = await detectLanguage(transcriptText);
        setDetectedLanguage(langDetection.language);
        onLanguageDetect?.(langDetection);
      } catch (error) {
        console.error("Language detection failed:", error);
      }

      if (result.isFinal) {
        onTranscript?.(transcriptText, detectedLanguage, confidenceScore);
      }
    };

    const startListening = () => {
      recognition.start();
    };

    const stopListening = () => {
      recognition.stop();
    };

    // Expose methods
    window.speechRecognition = { startListening, stopListening };

    return () => {
      recognition.stop();
    };
  }, [detectedLanguage, onTranscript, onLanguageDetect]);

  const detectLanguage = async (text) => {
    try {
      const response = await fetch("/api/v1/detect-language", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      return await response.json();
    } catch (error) {
      return { language: "en", confidence: 0.5 };
    }
  };

  const toggleListening = () => {
    if (isListening) {
      window.speechRecognition?.stopListening();
    } else {
      window.speechRecognition?.startListening();
    }
  };

  return (
    <motion.div className="multi-language-voice bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-4 text-white">
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-bold text-lg">🌍 Multi-Language Voice</h4>
        <div className="flex items-center space-x-2">
          <span className="text-sm">
            {languages[detectedLanguage] || "🌐 Auto"}
          </span>
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <motion.button
          onClick={toggleListening}
          className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl transition-all duration-300 ${
            isListening
              ? "bg-red-500 hover:bg-red-600 animate-pulse"
              : "bg-green-500 hover:bg-green-600"
          }`}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          {isListening ? "⏹️" : "🎤"}
        </motion.button>

        <div className="flex-1">
          <div className="bg-black/20 rounded-lg p-3 min-h-[60px]">
            {transcript ? (
              <div>
                <p className="text-sm opacity-80 mb-1">
                  {languages[detectedLanguage]} (Confidence:{" "}
                  {Math.round(confidence * 100)}%)
                </p>
                <p className="text-white">{transcript}</p>
              </div>
            ) : (
              <p className="text-white/60 italic">
                {isListening
                  ? "Listening... speak in any language"
                  : "Click microphone to start"}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Language confidence indicator */}
      <div className="mt-3">
        <div className="flex justify-between text-xs mb-1">
          <span>Language Detection Confidence</span>
          <span>{Math.round(confidence * 100)}%</span>
        </div>
        <div className="w-full bg-black/20 rounded-full h-2">
          <motion.div
            className="bg-gradient-to-r from-green-400 to-cyan-400 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${confidence * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>
    </motion.div>
  );
};

export default MultiLanguageVoice;
