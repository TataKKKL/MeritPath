import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight, CheckCircle, Star } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <Head>
        <title>MeritPath - Find Your Perfect Academic Recommenders</title>
        <meta name="description" content="MeritPath helps academics find and connect with the perfect recommenders for their career advancement." />
      </Head>

      {/* Navigation */}
      <nav className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center">
          <h1 className="text-2xl font-bold text-blue-600">MeritPath</h1>
        </div>
        <div className="hidden md:flex space-x-8 items-center">
          <a href="#features" className="text-gray-600 hover:text-blue-600">Features</a>
          <a href="#testimonials" className="text-gray-600 hover:text-blue-600">Testimonials</a>
          <a href="#pricing" className="text-gray-600 hover:text-blue-600">Pricing</a>
          <Link href="/login">
            <Button variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50">
              Log in
            </Button>
          </Link>
          <Link href="/login">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
              Sign up
            </Button>
          </Link>
        </div>
        <div className="md:hidden">
          <Button variant="ghost" size="sm">
            <span className="sr-only">Open menu</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 md:py-32">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-gray-900 mb-6">
            Find the perfect academic recommenders for your career advancement
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto">
            MeritPath helps academics identify, connect with, and secure the most impactful recommenders for their tenure, promotion, and grant applications.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link href="/login">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white text-lg px-8 py-6 h-auto">
                Get started for free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Button variant="outline" className="border-gray-300 text-gray-700 hover:bg-gray-50 text-lg px-8 py-6 h-auto">
              Book a demo
            </Button>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      {/* <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <p className="text-center text-gray-600 mb-10">Trusted by academics at leading institutions</p>
          <div className="flex flex-wrap justify-center gap-12 opacity-70">
            <div className="w-32 h-12 flex items-center justify-center">
              <span className="text-xl font-bold text-gray-500">Stanford</span>
            </div>
            <div className="w-32 h-12 flex items-center justify-center">
              <span className="text-xl font-bold text-gray-500">MIT</span>
            </div>
            <div className="w-32 h-12 flex items-center justify-center">
              <span className="text-xl font-bold text-gray-500">Harvard</span>
            </div>
            <div className="w-32 h-12 flex items-center justify-center">
              <span className="text-xl font-bold text-gray-500">Oxford</span>
            </div>
            <div className="w-32 h-12 flex items-center justify-center">
              <span className="text-xl font-bold text-gray-500">Cambridge</span>
            </div>
          </div>
        </div>
      </section> */}

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Find recommenders who will champion your work
          </h2>
          <p className="text-xl text-gray-600">
            MeritPath uses advanced algorithms to identify the most relevant and influential recommenders in your field.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600"><path d="M17 6.1H3"/><path d="M21 12.1H3"/><path d="M15.1 18H3"/></svg>
            </div>
            <h3 className="text-xl font-semibold mb-3">Smart Recommender Matching</h3>
            <p className="text-gray-600">Identify academics who have cited your work and are most likely to provide strong recommendations.</p>
          </div>
          
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <h3 className="text-xl font-semibold mb-3">Connection Insights</h3>
            <p className="text-gray-600">Discover mutual connections and collaboration opportunities with potential recommenders.</p>
          </div>
          
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
            </div>
            <h3 className="text-xl font-semibold mb-3">Recommendation Management</h3>
            <p className="text-gray-600">Track and manage your recommendation requests and follow-ups in one place.</p>
          </div>
        </div>
      </section>

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
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-white text-lg font-semibold mb-4">MeritPath</h3>
              <p className="mb-4">Helping academics find the perfect recommenders for career advancement.</p>
              <div className="flex space-x-4">
                <a href="#" className="hover:text-white">
                  <span className="sr-only">Twitter</span>
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
                <a href="#" className="hover:text-white">
                  <span className="sr-only">LinkedIn</span>
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                  </svg>
                </a>
              </div>
            </div>
            <div>
              <h3 className="text-white text-lg font-semibold mb-4">Product</h3>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">Testimonials</a></li>
                <li><a href="#" className="hover:text-white">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white text-lg font-semibold mb-4">Company</h3>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white text-lg font-semibold mb-4">Legal</h3>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white">Cookie Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-12 pt-8 text-center">
            <p>© 2023 MeritPath. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
