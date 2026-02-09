'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { LayoutConfig } from '@/types/editor';

interface DraggableElementProps {
  id: string;
  config: LayoutConfig;
  onUpdate: (id: string, x: number, y: number) => void;
  children: React.ReactNode;
  className?: string;
}

export function DraggableElement({ id, config, onUpdate, children, className }: DraggableElementProps) {
  // Get saved position or default to 0,0
  const position = config.elementPositions?.[id] || { x: 0, y: 0 };

  return (
    <motion.div
      drag
      dragMomentum={false}
      initial={{ x: position.x, y: position.y }}
      animate={{ x: position.x, y: position.y }}
      onDragEnd={(_, info) => {
        onUpdate(id, position.x + info.offset.x, position.y + info.offset.y);
      }}
      className={className}
      // Add a visual cue when hovering to show it's draggable
      whileHover={{ cursor: 'grab', scale: 1.01 }}
      whileTap={{ cursor: 'grabbing', scale: 1.02 }}
    >
      {children}
    </motion.div>
  );
}
