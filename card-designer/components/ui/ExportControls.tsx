
'use client';

import React, { useState } from 'react';
import * as htmlToImage from 'html-to-image';
import { saveAs } from 'file-saver';
import { Download, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ExportControlsProps {
  cardId: string;
  className?: string;
}

export function ExportControls({ cardId, className }: ExportControlsProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    const element = document.getElementById(`card-${cardId}`);
    
    if (!element) {
      console.error('Card element not found');
      setIsExporting(false);
      return;
    }

    try {
      // 1500px width / 500px rendered width = scale 3 (approx)
      // We force specific dimensions to ensure 1500x2100
      const dataUrl = await htmlToImage.toPng(element, {
        pixelRatio: 3, 
        width: 500, // Rendered width in preview
        height: 700, // Rendered height in preview
        cacheBust: true,
      });
      
      saveAs(dataUrl, `parasha-card-${cardId}.png`);
    } catch (error) {
      console.error('Failed to export card:', error);
      alert('Failed to export card image. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className={cn("flex gap-2", className)}>
      <button
        onClick={handleExport}
        disabled={isExporting}
        className="flex items-center gap-2 px-4 py-2 bg-slate-800 text-white rounded-full font-bold shadow-lg hover:bg-slate-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isExporting ? <Loader2 className="animate-spin" size={16} /> : <Download size={16} />}
        {isExporting ? 'Exporting...' : 'Print to PNG'}
      </button>
    </div>
  );
}
