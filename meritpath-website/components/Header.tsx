import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

const Header = () => {
  return (
    <nav className="container mx-auto px-4 py-6 flex justify-between items-center">
      <div className="flex items-center">
        <h1 className="text-2xl font-bold text-blue-600">MeritPath</h1>
      </div>
      <div className="hidden md:flex space-x-8 items-center">
        <a href="#features" className="text-gray-600 hover:text-blue-600">Features</a>
        <a href="#testimonials" className="text-gray-600 hover:text-blue-600">Testimonials</a>
        <a href="#pricing" className="text-gray-600 hover:text-blue-600">Pricing</a>
        <Link href="https://meritpath-app.pathon.ai/login">
          <Button variant="outline" className="border-blue-600 text-blue-600 hover:bg-blue-50">
            Log in
          </Button>
        </Link>
        <Link href="https://meritpath-app.pathon.ai/login">
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
  );
};

export default Header; 