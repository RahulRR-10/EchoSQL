import React, { useEffect } from "react";

const WaveAnimation = () => {
  const bars = Array.from({ length: 12 });

  useEffect(() => {
    const style = document.createElement("style");
    style.innerHTML = `
      @keyframes moveUp {
        0%, 100% { height: 30%; transform: translateY(0); }
        50% { height: 90%; transform: translateY(-8px); }
      }

      @keyframes moveDown {
        0%, 100% { height: 30%; transform: translateY(0); }
        50% { height: 90%; transform: translateY(8px); }
      }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  const getAnimationStyle = (index) => {
    const isMovingUp = index % 2 === 0;
    const animation = isMovingUp ? "moveUp" : "moveDown";

    let baseHeight;
    if (index % 6 === 0 || index % 6 === 5) baseHeight = "30%";
    else if (index % 6 === 1 || index % 6 === 4) baseHeight = "40%";
    else baseHeight = "55%";

    return {
      animation: `${animation} 1.3s infinite ease-in-out`,
      animationDelay: `${index * 0.1}s`,
      height: baseHeight,
    };
  };

  const getBarColor = (index) => {
    const colors = [
      "var(--accent-secondary)", // emerald/green
      "#fbbf24", // yellow
      "#f472b6", // pink
      "#f87171", // red
      "#60a5fa", // blue
      "#a78bfa", // indigo
    ];
    return colors[index % colors.length];
  };

  return (
    <div 
      className="flex items-center justify-center h-40 w-full px-12 rounded-lg"
      style={{ background: "var(--bg-primary)" }}
    >
      {bars.map((_, index) => {
        const color = getBarColor(index);
        return (
          <div
            key={index}
            className="w-1.5 rounded-full mx-1"
            style={{
              ...getAnimationStyle(index),
              background: `linear-gradient(to bottom, ${color}, var(--accent-primary))`,
            }}
          />
        );
      })}
    </div>
  );
};

export default WaveAnimation;
