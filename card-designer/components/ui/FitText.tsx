'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';

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
 * Uses Canvas API for measurement — works correctly for RTL Hebrew text
 * without DOM layout dependencies.
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
  const [fontSize, setFontSize] = useState(minSize);

  const measure = useCallback(() => {
    const container = containerRef.current;
    const text = textRef.current;
    if (!container || !text || !children) return;

    const availableWidth = container.clientWidth - padding * 2;
    if (availableWidth <= 0) return;

    // Get computed font properties from the rendered element
    const computed = window.getComputedStyle(text);
    const fontFamily = computed.fontFamily;
    const fontWeight = computed.fontWeight;

    // Use Canvas API to measure text width at maxSize.
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.font = `${fontWeight} ${maxSize}px ${fontFamily}`;

    // Account for CSS letter-spacing (Canvas ignores it by default)
    let letterSpacingPx = 0;
    const ls = style?.letterSpacing;
    if (ls) {
      if (typeof ls === 'string' && ls.endsWith('em')) {
        letterSpacingPx = parseFloat(ls) * maxSize;
      } else if (typeof ls === 'string' && ls.endsWith('px')) {
        letterSpacingPx = parseFloat(ls);
      }
    }

    const baseWidth = ctx.measureText(children).width;
    const naturalWidth = baseWidth + letterSpacingPx * children.length;

    if (naturalWidth <= 0) return;

    if (naturalWidth <= availableWidth) {
      setFontSize(maxSize);
    } else {
      const scale = availableWidth / naturalWidth;
      // Let text shrink as far as needed — never overflow.
      // minSize is a soft preference, absolute floor is 12px.
      const scaled = Math.floor(maxSize * scale);
      setFontSize(Math.max(12, scaled));
    }
  }, [children, maxSize, minSize, padding, style]);

  useEffect(() => {
    const run = () => {
      requestAnimationFrame(() => {
        measure();
      });
    };

    // Wait for fonts to load — critical for Hebrew fonts
    if (document.fonts?.ready) {
      document.fonts.ready.then(run);
    } else {
      run();
    }

    // Re-measure when container resizes
    const observer = new ResizeObserver(() => {
      measure();
    });
    if (containerRef.current) {
      observer.observe(containerRef.current);
    }
    return () => observer.disconnect();
  }, [children, measure]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: '100%', overflow: 'visible', ...style }}
    >
      <span
        ref={textRef}
        style={{
          fontSize: `${fontSize}px`,
          whiteSpace: 'nowrap',
          display: 'block',
          lineHeight: 1.3,
          textAlign: 'center',
          padding: `0 ${padding}px`,
        }}
      >
        {children}
      </span>
    </div>
  );
}
