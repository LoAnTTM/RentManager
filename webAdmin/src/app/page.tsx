'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to login or dashboard
    const token = localStorage.getItem('token');
    if (token) {
      router.replace('/dashboard');
    } else {
      router.replace('/login');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-warm-50">
      <div className="text-center">
        <div className="text-6xl mb-4">🏠</div>
        <h1 className="text-3xl font-bold text-primary-600">Minh Rental</h1>
        <p className="text-gray-500 mt-2">Đang tải...</p>
      </div>
    </div>
  );
}

