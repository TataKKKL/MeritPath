import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight, CheckCircle, Star } from 'lucide-react';
import FeaturesSection from '@/components/FeaturesSection';
import Header from '@/components/Header';
import Hero from '@/components/Hero';
import Footer from '@/components/Footer';
import AnimationStyles from '@/components/AnimationStyles';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <Head>
        <title>MeritPath - Find Your Perfect Academic Recommenders</title>
        <meta name="description" content="MeritPath helps academics find and connect with the perfect recommenders for their career advancement." />
      </Head>

      {/* Navigation */}
      <Header />

      {/* Hero Section */}
      <Hero />

      {/* Features Section */}
      <div className="bg-[var(--loggia-main-background)]">
        <FeaturesSection />
      </div>

      {/* Testimonials */}
      <section id="testimonials" className="bg-gray-50 py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Loved by academics worldwide
            </h2>
            <p className="text-xl text-gray-600">
              See what researchers and professors are saying about MeritPath
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-xl shadow-sm">
              <div className="flex text-yellow-400 mb-4">
                <Star className="fill-current" />
                <Star className="fill-current" />
                <Star className="fill-current" />
                <Star className="fill-current" />
                <Star className="fill-current" />
              </div>
              <p className="text-gray-700 mb-6">&ldquo;MeritPath helped me find the perfect recommenders for my tenure application. I was able to secure letters from top researchers in my field.&rdquo;</p>
              <div className="flex items-center">
                <div className="w-10 h-10 bg-blue-100 rounded-full mr-3"></div>
                <div>
                  <p className="font-semibold">Dr. Sarah Johnson</p>
                  <p className="text-sm text-gray-500">Associate Professor, Stanford University</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-8 rounded-xl shadow-sm">
              <div className="flex text-yellow-400 mb-4">
                <Star className="fill-current" />
                <Star className="fill-current" />
                <Star className="fill-current" />
                <Star className="fill-current" />
                <Star className="fill-current" />
              </div>
              <p className="text-gray-700 mb-6">&ldquo;The connection insights feature helped me discover mutual connections with potential recommenders, making it easier to reach out and get positive responses.&rdquo;</p>
              <div className="flex items-center">
                <div className="w-10 h-10 bg-blue-100 rounded-full mr-3"></div>
                <div>
                  <p className="font-semibold">Prof. Michael Chen</p>
                  <p className="text-sm text-gray-500">Full Professor, MIT</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-8 rounded-xl shadow-sm">
              <div className="flex text-yellow-400 mb-4">
                <Star className="fill-current" />
                <Star className="fill-current" />
                <Star className="fill-current" />
                <Star className="fill-current" />
                <Star className="fill-current" />
              </div>
              <p className="text-gray-700 mb-6">&ldquo;As a junior faculty member, I was struggling to find the right recommenders. MeritPath made the process so much easier and less stressful.&rdquo;</p>
              <div className="flex items-center">
                <div className="w-10 h-10 bg-blue-100 rounded-full mr-3"></div>
                <div>
                  <p className="font-semibold">Dr. Emily Rodriguez</p>
                  <p className="text-sm text-gray-500">Assistant Professor, UC Berkeley</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Simple, transparent pricing
          </h2>
          <p className="text-xl text-gray-600">
            Choose the plan that&apos;s right for your academic career stage
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-xl font-semibold mb-2">Basic</h3>
            <p className="text-gray-600 mb-6">For early-career researchers</p>
            <div className="mb-6">
              <span className="text-4xl font-bold">$0</span>
              <span className="text-gray-600">/month</span>
            </div>
            <ul className="space-y-3 mb-8">
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Up to 10 potential recommenders</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Basic recommender insights</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Email templates</span>
              </li>
            </ul>
            <Link href="/login">
              <Button variant="outline" className="w-full">Get started</Button>
            </Link>
          </div>
          
          <div className="bg-blue-50 p-8 rounded-xl shadow-sm border border-blue-200 relative">
            <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-bl-lg rounded-tr-lg">
              POPULAR
            </div>
            <h3 className="text-xl font-semibold mb-2">Pro</h3>
            <p className="text-gray-600 mb-6">For tenure-track faculty</p>
            <div className="mb-6">
              <span className="text-4xl font-bold">$29</span>
              <span className="text-gray-600">/month</span>
            </div>
            <ul className="space-y-3 mb-8">
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Unlimited potential recommenders</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Advanced recommender insights</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Mutual connection discovery</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Personalized email templates</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Recommendation tracking</span>
              </li>
            </ul>
            <Link href="/login">
              <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">Get started</Button>
            </Link>
          </div>
          
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-xl font-semibold mb-2">Enterprise</h3>
            <p className="text-gray-600 mb-6">For departments & institutions</p>
            <div className="mb-6">
              <span className="text-4xl font-bold">Custom</span>
            </div>
            <ul className="space-y-3 mb-8">
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Everything in Pro</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Department-wide analytics</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Admin dashboard</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Priority support</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                <span>Custom integration</span>
              </li>
            </ul>
            <Button variant="outline" className="w-full">Contact sales</Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6 max-w-3xl mx-auto">
            Ready to find your perfect academic recommenders?
          </h2>
          <p className="text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
            Join thousands of academics who have advanced their careers with MeritPath
          </p>
          <Link href="/login">
            <Button className="bg-white text-blue-600 hover:bg-blue-50 text-lg px-8 py-6 h-auto">
              Get started for free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer />

      {/* Global Animations */}
      <AnimationStyles />
    </div>
  );
}
