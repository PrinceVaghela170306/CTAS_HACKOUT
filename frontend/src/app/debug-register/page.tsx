'use client';

import { useState } from 'react';
import { signUp } from '../../../lib/supabase';

export default function DebugRegisterPage() {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testRegistration = async () => {
    setLoading(true);
    setResult('');
    
    try {
      console.log('Testing Supabase registration...');
      const testEmail = `test${Date.now()}@gmail.com`;
      const testPassword = 'TestPassword123!';
      
      console.log('Attempting to register:', testEmail);
      const { data, error } = await signUp(testEmail, testPassword);
      
      if (error) {
        console.error('Supabase error:', error);
        setResult(`Supabase Error: ${error.message}`);
      } else {
        console.log('Registration successful:', data);
        setResult(`Registration successful: ${JSON.stringify(data, null, 2)}`);
      }
    } catch (err: any) {
      console.error('Network error:', err);
      setResult(`Network Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-4">Debug Registration</h1>
        
        <button
          onClick={testRegistration}
          disabled={loading}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:opacity-50 mb-4"
        >
          {loading ? 'Testing...' : 'Test Registration'}
        </button>
        
        {result && (
          <div className="mt-4 p-4 bg-gray-50 rounded border">
            <h3 className="font-semibold mb-2">Result:</h3>
            <pre className="text-sm whitespace-pre-wrap">{result}</pre>
          </div>
        )}
        
        <div className="mt-4 text-sm text-gray-600">
          <p><strong>Supabase URL:</strong> {process.env.NEXT_PUBLIC_SUPABASE_URL}</p>
          <p><strong>Has Anon Key:</strong> {process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? 'Yes' : 'No'}</p>
        </div>
      </div>
    </div>
  );
}