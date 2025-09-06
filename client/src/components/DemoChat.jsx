import { useState } from "react";
import { motion } from "framer-motion";
import WaveAnimation from "./WaveAnimation";
import { AiOutlineStock } from "react-icons/ai";
import AutoChatDemo from "./AutoChatDemo";

function DemoChat() {
  const [activeChat, setActiveChat] = useState(0); // 0 for IPL, 1 for Sales

  return (
    <div className="min-h-screen px-4 pt-4" style={{ background: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      <motion.div
        className="text-center"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <WaveAnimation />
        <div className="ml-10 mb-4 overflow-hidden max-w-full">
          <h1 className="typewriter text-3xl sm:text-5xl font-semibold tracking-wide text-transparent bg-gradient-to-r from-green-400 via-cyan-400 to-blue-500 bg-clip-text">
            Query.Clarity.Action
          </h1>
        </div>

        <p className="mt-2 mb-6 text-sm sm:text-base tracking-wider" style={{ color: 'var(--text-muted)' }}>
          Where voice meets visualization through cutting-edge AI.
        </p>
      </motion.div>

      <motion.div
        className="w-full max-w-6xl rounded-xl flex flex-col h-[26rem] overflow-hidden mx-auto mt-16"
        style={{ 
          background: 'var(--bg-card)', 
          border: '1px solid var(--border-accent)',
          boxShadow: '0 0 8px var(--shadow-glow), 0 0 12px var(--shadow-glow), 0 0 16px var(--shadow-glow)'
        }}
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
      >
        <div className="p-4 border-b flex justify-between items-center" style={{ borderColor: 'var(--border-primary)' }}>
          <h2 className="text-xl font-semibold text-gradient">
            Chat Demo
          </h2>
          <div className="flex gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`px-3 py-1 rounded-md text-sm font-medium h-10 flex items-center gap-2 cursor-pointer ${
                activeChat === 0
                  ? "text-black"
                  : "border"
              }`}
              style={{
                background: activeChat === 0 ? 'var(--accent-primary)' : 'var(--bg-glass)',
                color: activeChat === 0 ? 'var(--text-primary)' : 'var(--text-primary)',
                borderColor: activeChat === 0 ? 'transparent' : 'var(--border-primary)'
              }}
            >
              IPL
              <img src="./ipl.png" alt="IPL" className="w-8 h-8" />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`px-3 py-1 rounded-md text-sm font-medium h-10 flex items-center gap-2 cursor-pointer ${
                activeChat === 1
                  ? "text-black"
                  : "border"
              }`}
              style={{
                background: activeChat === 1 ? 'var(--accent-secondary)' : 'var(--bg-glass)',
                color: activeChat === 1 ? 'var(--text-primary)' : 'var(--text-primary)',
                borderColor: activeChat === 1 ? 'transparent' : 'var(--border-primary)'
              }}
            >
              Sales
              <AiOutlineStock size={24} />
            </motion.button>
          </div>
        </div>

        <div className="flex-1 overflow-hidden px-4 py-3">
          <AutoChatDemo setActiveChat={setActiveChat} />
        </div>
      </motion.div>
    </div>
  );
}

export default DemoChat;
