'use client';

export default function TestJSPage() {
  const testAlert = () => {
    alert('JavaScript is working!');
    console.log('🚀 TEST ALERT CLICKED - JavaScript is working!');
  };

  const testConsole = () => {
    console.log('🔥 CONSOLE TEST - This should appear in browser console');
    console.log('Environment check:');
    console.log('- SUPABASE_URL:', process.env.NEXT_PUBLIC_SUPABASE_URL);
    console.log('- SUPABASE_KEY exists:', !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-4">JavaScript Test</h1>
        
        <div className="space-y-4">
          <button
            onClick={testAlert}
            className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 cursor-pointer"
          >
            Test Alert (Should show popup)
          </button>
          
          <button
            onClick={testConsole}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 cursor-pointer"
          >
            Test Console (Check browser console)
          </button>
        </div>
        
        <div className="mt-6 text-sm text-gray-600">
          <p>Click the buttons above to test JavaScript functionality.</p>
          <p>Open browser console (F12) to see console logs.</p>
        </div>
      </div>
    </div>
  );
}