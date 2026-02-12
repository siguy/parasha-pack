'use client';

import React, { useRef, useEffect, useState } from 'react';

interface FitTextProps {
  children: string;
  /** Maximum font size in pixels */
  maxSize?: number;
  /** Minimum font size in pixels */
  minSize?: number;
  /** Horizontal padding on each side in pixels */
  padding?: number;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Dynamically scales text to fill its container width.
 * Starts at maxSize, measures natural width, scales down until text fits in one line.
 * Works with Hebrew (RTL) and English text.
 */
export function FitText({
  children,
  maxSize = 120,
  minSize = 36,
  padding = 40,
  className = '',
  style = {},
}: FitTextProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLSpanElement>(null);
  const [fontSize, setFontSize] = useState(maxSize);

  useEffect(() => {
    const container = containerRef.current;
    const text = textRef.current;
    if (!container || !text) return;

    const availableWidth = container.offsetWidth - padding * 2;
    if (availableWidth <= 0) return;

    // Measure at max size to get natural width
    text.style.fontSize = `${maxSize}px`;
    const naturalWidth = text.scrollWidth;

    if (naturalWidth <= availableWidth) {
      setFontSize(maxSize);
    } else {
      const scale = availableWidth / naturalWidth;
      const scaled = Math.floor(maxSize * scale);
      setFontSize(Math.max(minSize, scaled));
    }
  }, [children, maxSize, minSize, padding]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: '100%', overflow: 'hidden', ...style }}
    >
      <span
        ref={textRef}
        style={{
          fontSize: `${fontSize}px`,
          whiteSpace: 'nowrap',
          display: 'block',
          lineHeight: 1.1,
          textAlign: 'center',
          padding: `0 ${padding}px`,
        }}
      >
        {children}
      </span>
    </div>
  );
}
