import React from 'react';

const AnimationStyles = () => {
  return (
    <style jsx global>{`
      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      
      .animate-fadeInUp {
        animation: fadeInUp 0.8s ease-out;
      }
      
      @keyframes floatParticle {
        0% {
          transform: translateY(0) translateX(0) scale(0);
          opacity: 0;
        }
        20% {
          transform: translateY(-5px) translateX(5px) scale(1);
          opacity: 0.4;
        }
        80% {
          transform: translateY(-15px) translateX(10px) scale(1);
          opacity: 0.4;
        }
        100% {
          transform: translateY(-20px) translateX(15px) scale(0);
          opacity: 0;
        }
      }
    `}</style>
  );
};

export default AnimationStyles; 