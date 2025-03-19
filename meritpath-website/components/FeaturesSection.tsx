import React from "react";
import FlowAnimation from './FlowAnimation';
import { Card } from "@/components/ui/card";

interface Feature {
  title: string;
  description: string;
  extraContent?: React.ReactNode;
}

const features: Feature[] = [
  {
    title: "01. Smart Recommender Generation",
    description:
      "Generate the list of potential recommenders for your VISA and job application.",
    extraContent: <FlowAnimation />
  },
  {
    title: "02. Recommendation Management",
    description:
      "Track and manage your recommendation requests and follow-ups in one place.",
    extraContent: <FlowAnimation />
  },
  {
    title: "03. Connection Insights",
    description:
      "Discover mutual connections and collaboration opportunities with potential recommenders.",
    extraContent: <FlowAnimation />,
  },
];

export function FeaturesSection() {
  return (
    <section className="relative py-24 bg-gradient-to-b from-white to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-16 mb-16">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 leading-tight">
              Find recommenders who will champion your work
            </h2>
          </div>
          <div className="self-center">
            <p className="text-lg md:text-xl leading-relaxed text-gray-700">
              MeritPath uses advanced algorithms to identify the most relevant and influential 
              recommenders in your field.
            </p>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="group relative p-6 md:p-8 transition-all duration-300 ease-out 
                         hover:bg-blue-50 hover:border-blue-200 hover:translate-y-[-4px] 
                         hover:shadow-lg cursor-pointer overflow-hidden"
            >
              {/* Extra Content (animations) */}
              {feature.extraContent && (
                <div className="mb-6 transform transition-transform duration-300 group-hover:scale-105">
                  {feature.extraContent}
                </div>
              )}
              
              {/* Card content */}
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-base md:text-lg text-gray-600">
                {feature.description}
              </p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FeaturesSection;