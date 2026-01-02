'use client';

import React from 'react';

interface LoadingProps {
  text?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function Loading({ text = 'Đang tải...', size = 'md' }: LoadingProps) {
  const sizeClasses = {
    sm: 'w-6 h-6 border-2',
    md: 'w-10 h-10 border-3',
    lg: 'w-16 h-16 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <div
        className={`
          ${sizeClasses[size]}
          border-primary-200 border-t-primary-500
          rounded-full animate-spin
        `}
      />
      {text && <p className="text-gray-500 text-lg">{text}</p>}
    </div>
  );
}

export function PageLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-warm-50">
      <Loading size="lg" text="Đang tải..." />
    </div>
  );
}

