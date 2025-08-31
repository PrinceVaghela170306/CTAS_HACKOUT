'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getSession } from '../../lib/supabase';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { session } = await getSession();
        if (session?.access_token) {
          // User is logged in, redirect to dashboard
          localStorage.setItem('token', session.access_token);
          router.push('/dashboard');
        } else {
          // User is not logged in, redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          router.push('/login');
        }
      } catch (error) {
        // If there's an error checking session, redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        router.push('/login');
      }
    };

    checkAuth();
  }, [router]);

  // Show loading state while redirecting
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 flex items-center justify-center">
      <div className="text-center">
        <div className="mx-auto h-16 w-16 bg-gradient-to-r from-blue-500 to-teal-500 rounded-full flex items-center justify-center mb-4 animate-pulse">
          <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Coastal Guard</h2>
        <p className="text-gray-600">Loading application...</p>
        <div className="mt-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    </div>
  );
}
