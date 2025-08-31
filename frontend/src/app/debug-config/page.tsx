'use client';

import { supabase } from '../../../lib/supabase';

export default function DebugConfigPage() {
  const checkConfig = () => {
    console.log('🔥 CHECK CONFIG BUTTON CLICKED!');
    alert('Check Config clicked! See console for details.');
    console.log('=== SUPABASE CONFIGURATION DEBUG ===');
    console.log('NEXT_PUBLIC_SUPABASE_URL:', process.env.NEXT_PUBLIC_SUPABASE_URL);
    console.log('NEXT_PUBLIC_SUPABASE_ANON_KEY exists:', !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);
    console.log('NEXT_PUBLIC_SUPABASE_ANON_KEY length:', process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.length);
    console.log('Supabase client:', supabase);
    console.log('Supabase auth:', supabase.auth);
    console.log('=== END DEBUG ===');
  };

  const testConnection = async () => {
    console.log('🚀 TEST CONNECTION BUTTON CLICKED!');
    alert('Test Connection clicked! See console for details.');
    try {
      console.log('Testing Supabase connection...');
      const { data, error } = await supabase.auth.getSession();
      console.log('Session test result:', { data, error });
    } catch (err) {
      console.error('Connection test failed:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-4">Debug Configuration</h1>
        
        <div className="space-y-4">
          <button
            onClick={checkConfig}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 cursor-pointer transition-colors duration-200 active:bg-blue-700"
          >
            Check Config (Console)
          </button>
          
          <button
            onClick={testConnection}
            className="w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 cursor-pointer transition-colors duration-200 active:bg-green-700"
          >
            Test Connection (Console)
          </button>
        </div>
        
        <div className="mt-6 text-sm text-gray-600 space-y-2">
          <p><strong>URL:</strong> {process.env.NEXT_PUBLIC_SUPABASE_URL || 'Not set'}</p>
          <p><strong>Anon Key:</strong> {process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? 'Set' : 'Not set'}</p>
          <p><strong>Key Length:</strong> {process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.length || 0}</p>
        </div>
      </div>
    </div>
  );
}