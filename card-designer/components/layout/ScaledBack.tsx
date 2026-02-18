'use client';

import React, { useRef, useState, useEffect } from 'react';

/**
 * Renders card back content at 1500x2100px, then CSS-scales it
 * to fit the parent container width while maintaining 5:7 aspect ratio.
 */
export function ScaledBack({ children }: { children: React.ReactNode }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const observer = new ResizeObserver(([entry]) => {
      setScale(entry.contentRect.width / 1500);
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={containerRef}
      className="w-full overflow-hidden rounded-[24px]"
      style={{ aspectRatio: '5/7' }}
    >
      <div
        className="origin-top-left"
        style={{
          width: '1500px',
          height: '2100px',
          transform: `scale(${scale})`,
          opacity: scale > 0 ? 1 : 0,
        }}
      >
        {children}
      </div>
    </div>
  );
}
