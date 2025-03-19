import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

const Hero = () => {
  return (
    <section className="container mx-auto px-4 py-20 md:py-32 overflow-hidden relative">
      {/* Background animation elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-10 -right-10 w-64 h-64 bg-blue-100 rounded-full opacity-20 blur-3xl"></div>
        <div className="absolute top-1/2 -left-20 w-72 h-72 bg-blue-200 rounded-full opacity-10 blur-3xl"></div>
        <div className="absolute -bottom-20 right-1/4 w-80 h-80 bg-blue-50 rounded-full opacity-20 blur-3xl"></div>
        
        {/* Floating particles similar to FlowAnimation */}
        {[...Array(8)].map((_, i) => (
          <div
            key={`hero-particle-${i}`}
            className="absolute rounded-full bg-blue-200 w-2 h-2"
            style={{
              top: `${15 + (i % 5) * 15}%`,
              left: `${10 + (i % 7) * 12}%`,
              animation: `floatParticle ${3 + i * 0.7}s ease-in-out infinite`,
              animationDelay: `${i * 0.3}s`,
              opacity: 0.4,
              transform: 'scale(0)'
            }}
          />
        ))}
      </div>

      <div className="max-w-4xl mx-auto text-center relative z-10">
        <h1 
          className="text-4xl md:text-6xl font-bold tracking-tight text-gray-900 mb-6 opacity-0 animate-fadeInUp"
          style={{ animationDelay: '0.2s', animationFillMode: 'forwards' }}
        >
          Find the perfect academic recommenders for your career advancement
        </h1>
        <p 
          className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto opacity-0 animate-fadeInUp"
          style={{ animationDelay: '0.5s', animationFillMode: 'forwards' }}
        >
          MeritPath helps academics identify, connect with, and secure the most impactful recommenders for their tenure, promotion, and grant applications.
        </p>
        <div 
          className="flex flex-col sm:flex-row justify-center gap-4 opacity-0 animate-fadeInUp"
          style={{ animationDelay: '0.8s', animationFillMode: 'forwards' }}
        >
          <Link href="/login">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white text-lg px-8 py-6 h-auto group transition-all duration-300">
              Get started for free
              <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
            </Button>
          </Link>
          <Button 
            variant="outline" 
            className="border-gray-300 text-gray-700 hover:bg-gray-50 text-lg px-8 py-6 h-auto transition-all duration-300 hover:border-blue-300"
          >
            Book a demo
          </Button>
        </div>
      </div>
    </section>
  );
};

export default Hero; 