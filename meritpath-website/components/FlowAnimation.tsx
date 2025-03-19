import React from 'react';

const FlowAnimation = () => {
  return (
    <div className="flex items-center justify-center h-32 w-full mb-2">
      <div className="relative group cursor-pointer w-32 h-full flex items-center justify-center">
        <svg
          viewBox="0 0 120 200"
          className="w-24 h-32 transform transition-all duration-1000 ease-out group-hover:scale-110"
          style={{
            filter: 'drop-shadow(0 0 8px rgba(37, 99, 235, 0.2))'
          }}
        >
          {/* Background Glow */}
          <path
            d="M30 40 C60 80, 40 120, 70 160 S30 200, 60 220"
            fill="transparent"
            stroke="rgba(59, 130, 246, 0.2)" /* blue-500 at 20% opacity */
            strokeWidth="10"
            strokeLinecap="round"
            className="transition-all duration-700"
          />

          {/* Primary Flow Path */}
          <path
            d="M30 40 C60 80, 40 120, 70 160 S30 200, 60 220"
            fill="transparent"
            stroke="#2563eb" /* blue-600 */
            strokeWidth="3"
            strokeLinecap="round"
            className="transition-all duration-1000 group-hover:stroke-blue-400"
            strokeDasharray="240"
            strokeDashoffset="240"
            style={{
              animation: 'flowDash 3s linear forwards infinite paused',
              animationPlayState: 'var(--play-state, paused)'
            }}
          />
          
          {/* Secondary Flow Path for layered effect */}
          <path
            d="M30 40 C60 80, 40 120, 70 160 S30 200, 60 220"
            fill="transparent"
            stroke="#60a5fa" /* blue-400 */
            strokeWidth="1.5"
            strokeLinecap="round"
            className="transition-opacity duration-1000 opacity-0 group-hover:opacity-80"
            strokeDasharray="240"
            strokeDashoffset="240"
            style={{
              animation: 'flowDash 3s linear forwards infinite paused',
              animationPlayState: 'var(--play-state, paused)',
              animationDelay: '0.5s'
            }}
          />
          
          {/* Connection Nodes */}
          <circle cx="30" cy="40" r="5" fill="transparent" stroke="#2563eb" strokeWidth="2" 
            className="group-hover:fill-blue-100 transition-all duration-500" />
          <circle cx="70" cy="160" r="5" fill="transparent" stroke="#2563eb" strokeWidth="2" 
            className="group-hover:fill-blue-100 transition-all duration-700 delay-300" />
          <circle cx="60" cy="220" r="5" fill="transparent" stroke="#2563eb" strokeWidth="2" 
            className="group-hover:fill-blue-100 transition-all duration-900 delay-500" />
          
          {/* Flow Particles - First Group (Fast) */}
          {[0, 1, 2, 3].map((i) => (
            <circle 
              key={`particle-fast-${i}`}
              cx="0" cy="0" r="2.5" 
              fill="#93c5fd" /* blue-300 */
              className="opacity-0 group-hover:opacity-100"
            >
              <animateMotion
                path="M30 40 C60 80, 40 120, 70 160 S30 200, 60 220"
                dur="2s"
                repeatCount="indefinite"
                begin={`${i * 0.5}s`}
                keyPoints="0;1"
                keyTimes="0;1"
                calcMode="linear"
              />
              <animate
                attributeName="opacity"
                values="0;0.9;0.9;0"
                keyTimes="0;0.1;0.9;1"
                dur="2s"
                repeatCount="indefinite"
                begin={`${i * 0.5}s`}
              />
              <animate
                attributeName="r"
                values="1.5;2.5;1.5"
                keyTimes="0;0.5;1"
                dur="2s"
                repeatCount="indefinite"
                begin={`${i * 0.5}s`}
              />
            </circle>
          ))}
          
          {/* Flow Particles - Second Group (Slower, larger) */}
          {[0, 1].map((i) => (
            <circle 
              key={`particle-slow-${i}`}
              cx="0" cy="0" r="3.5" 
              fill="#3b82f6" /* blue-500 */
              className="opacity-0 group-hover:opacity-100"
            >
              <animateMotion
                path="M30 40 C60 80, 40 120, 70 160 S30 200, 60 220"
                dur="3s"
                repeatCount="indefinite"
                begin={`${i * 1.5}s`}
                keyPoints="0;1"
                keyTimes="0;1"
                calcMode="linear"
              />
              <animate
                attributeName="opacity"
                values="0;0.8;0.8;0"
                keyTimes="0;0.1;0.9;1"
                dur="3s"
                repeatCount="indefinite"
                begin={`${i * 1.5}s`}
              />
              <animate
                attributeName="r"
                values="2;3.5;2"
                keyTimes="0;0.5;1"
                dur="3s"
                repeatCount="indefinite"
                begin={`${i * 1.5}s`}
              />
            </circle>
          ))}
          
          {/* Pulsing Source/Origin Glow */}
          <circle
            cx="30" cy="40" r="8"
            className="opacity-0 group-hover:opacity-90 transition-opacity duration-300"
            style={{
              animation: 'pulse 2s ease-in-out infinite paused',
              animationPlayState: 'var(--play-state, paused)'
            }}
            fill="url(#startGlow)"
          />
          
          {/* Pulsing Destination Glow */}
          <circle
            cx="60" cy="220" r="10"
            className="opacity-0 group-hover:opacity-90 transition-opacity duration-300"
            style={{
              animation: 'pulse 2s ease-in-out infinite paused',
              animationPlayState: 'var(--play-state, paused)',
              animationDelay: '0.7s'
            }}
            fill="url(#endGlow)"
          />
          
          {/* Gradients */}
          <defs>
            <radialGradient id="startGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#3b82f6" /* blue-500 */ />
              <stop offset="70%" stopColor="rgba(59, 130, 246, 0.3)" />
              <stop offset="100%" stopColor="rgba(59, 130, 246, 0)" />
            </radialGradient>
            
            <radialGradient id="endGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#3b82f6" /* blue-500 */ />
              <stop offset="70%" stopColor="rgba(59, 130, 246, 0.3)" />
              <stop offset="100%" stopColor="rgba(59, 130, 246, 0)" />
            </radialGradient>
          </defs>
        </svg>
        
        {/* Small floating particles around the path for added dimension */}
        <div className="absolute top-0 left-0 w-full h-full opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none">
          {[...Array(5)].map((_, i) => (
            <div
              key={`float-particle-${i}`}
              className="absolute rounded-full bg-blue-200 w-1 h-1"
              style={{
                top: `${20 + i * 15}%`,
                left: `${30 + (i % 3) * 15}%`,
                animation: `floatParticle ${2 + i * 0.5}s ease-in-out infinite`,
                animationDelay: `${i * 0.2}s`,
                opacity: 0.7
              }}
            />
          ))}
        </div>
      </div>
      
      {/* Add global keyframes */}
      <style jsx global>{`
        @keyframes flowDash {
          to {
            stroke-dashoffset: 0;
          }
        }
        
        @keyframes pulse {
          0% {
            transform: scale(0.95);
            opacity: 0.7;
          }
          50% {
            transform: scale(1.05);
            opacity: 0.9;
          }
          100% {
            transform: scale(0.95);
            opacity: 0.7;
          }
        }
        
        @keyframes floatParticle {
          0%, 100% {
            transform: translateY(0) translateX(0);
            opacity: 0.3;
          }
          50% {
            transform: translateY(-10px) translateX(5px);
            opacity: 0.7;
          }
        }
        
        .group:hover svg {
          --play-state: running;
        }
      `}</style>
    </div>
  );
};

export default FlowAnimation;