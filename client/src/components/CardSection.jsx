import { motion } from "framer-motion";
import { Link } from "react-router-dom";

function CardSection() {
  return (
    <motion.div
      className="p-6 flex flex-col md:flex-row justify-center items-center w-full max-w-7xl mx-auto mt-12 space-y-8 md:space-y-0 md:space-x-8 mb-16 rounded-3xl overflow-hidden"
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.5, duration: 0.8 }}
    >
      <div className="w-full md:w-2/3 space-y-6 px-6 text-center md:text-left">
        <h2 className="font-poppins text-3xl sm:text-4xl lg:text-5xl tracking-wide font-bold leading-tight" style={{ color: 'var(--text-primary)' }}>
          Experience the Power of
          <br />
          <span className="text-gradient-purple">
            Voice-Driven
          </span>{" "}
          Visualization
        </h2>
        <p className="font-inter md:w-4/5 w-full text-base sm:text-lg leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          Transform complex ideas, pitches, or data into clear, compelling
          visuals — just by speaking. Whether you're brainstorming, presenting,
          or strategizing, see how fast your voice can turn into impact.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 mt-6">
          <Link
            to="/auth/signup"
            className="btn-primary text-base font-jetbrains px-8 py-4 rounded-2xl animate-scale-in"
          >
            Try Now!
          </Link>
          <Link
            to="/auth/login"
            className="btn-ghost text-base font-jetbrains px-8 py-4 rounded-2xl animate-scale-in"
          >
            Learn More
          </Link>
        </div>
      </div>

      <div className="w-full md:w-1/3 flex justify-center">
        <div className="relative">
          <img
            src="/hero.png"
            alt="Visualization Illustration"
            className="w-64 sm:w-80 md:w-96 h-auto rounded-3xl hidden md:block animate-float shadow-glow"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/20 to-green-400/20 rounded-3xl animate-pulse"></div>
        </div>
      </div>
    </motion.div>
  );
}

export default CardSection;
