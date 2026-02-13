
import React from 'react';
import { CardData } from '@/types/card';
import { CardFrame } from './CardFrame';
import { cn } from '@/lib/utils';
import { Star, Heart, Zap, Drama } from 'lucide-react';
import { LayoutConfig, DEFAULT_LAYOUT_CONFIG } from '@/types/editor';
import { DraggableElement } from '../editor/DraggableElement';

interface StoryCardProps {
  card: CardData;
  deckId: string;
  config?: LayoutConfig; // Optional override for Editor
  onConfigChange?: (newConfig: LayoutConfig) => void;
}

export function StoryCard({ card, deckId, config, onConfigChange }: StoryCardProps) {
  // Use config or defaults
  const activeConfig = config || DEFAULT_LAYOUT_CONFIG;
  
  // Safe default colors if not provided
  const borderColor = card.border_color || '#FF4136'; // Default red for Story

  // Clean the roleplay prompt to remove "Act it out:" if present
  const cleanRoleplay = card.roleplay_prompt?.replace(/^Act it out:\s*/i, '') || card.roleplay_prompt;

  const handlePositionUpdate = (id: string, x: number, y: number) => {
    if (onConfigChange && config) {
      const newPositions = { ...config.elementPositions, [id]: { x, y } };
      onConfigChange({ ...config, elementPositions: newPositions });
    }
  };

  const LayoutComponents = {
    standard: StandardLayout,
    immersive: ImmersiveLayout,
    'immersive-floating': ImmersiveFloatingLayout,
    'immersive-cinematic': ImmersiveCinematicLayout,
    'immersive-clean': ImmersiveCleanLayout,
    scrapbook: ScrapbookLayout
  };

  const activeTheme = activeConfig.theme || 'standard';
  // activeTheme might be string, need casting or loose check
  const ActiveLayout = (LayoutComponents as any)[activeTheme] || StandardLayout;

  return (
    <div 
      id={`card-${card.card_id}`} 
      className={cn("w-full h-full", activeConfig.fontFamily)}
      style={{ 
        padding: `${activeConfig.containerPadding ?? 4}px`,
        backgroundColor: activeConfig.paddingColor || 'transparent'
      }}
    >
       <ActiveLayout 
         card={card} 
         deckId={deckId} 
         activeConfig={activeConfig} 
         borderColor={borderColor} 
         cleanRoleplay={cleanRoleplay} 
         onPositionUpdate={handlePositionUpdate}
       />
    </div>
  );
}

// ... (omitted code)

// --- SUB-LAYOUTS ---

function StandardLayout({ card, deckId, activeConfig, borderColor, cleanRoleplay, onPositionUpdate }: any) {
  return (
      <CardFrame 
        borderColor={borderColor} 
        className="flex flex-col relative h-full bg-white ring-4 ring-offset-2 ring-white/50 shadow-2xl"
      >
        
            {/* 1. HEADER ZONE - Absolute Top */}
            <div className="absolute top-0 left-0 right-0 z-30 pointer-events-none">
                <DraggableElement id="header-bar" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                    <div 
                        className="w-full shadow-sm px-4 py-3 flex items-center justify-between rounded-t-[18px]"
                        style={{ 
                            backgroundColor: activeConfig.headerBgColor || borderColor 
                        }} 
                    >
                        {/* Icon - White on Color */}
                        <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white shrink-0 shadow-sm border border-white/30">
                            <Zap size={18} fill="currentColor" />
                        </div>

                        {/* Title Group - Single Line */}
                        <div 
                            className="flex flex-row items-baseline gap-2 flex-1 overflow-visible justify-center"
                            style={{ color: activeConfig.titleColor }}
                        >
                            <span 
                                className="font-black font-hebrew leading-normal pt-1 pb-1"
                                style={{ fontSize: `${activeConfig.titleFontSize}px` }}
                            >
                                {card.title_he}
                            </span>
                            <h2 className="text-sm font-bold uppercase tracking-widest font-sans leading-none opacity-90 pt-0.5">
                                {card.title_en}
                            </h2>
                        </div>

                        {/* Badge */}
                        <div 
                            className="w-8 h-8 rounded-full bg-white font-black text-sm flex items-center justify-center shadow-md shrink-0"
                            style={{ color: borderColor }}
                        >
                            {card.sequence_number}
                        </div>
                    </div>
                </DraggableElement>
            </div>

            {/* 2. VISUAL STAGE (Flex-1: Shrinks to fit text) */}
            <div className="flex-1 w-full relative bg-slate-200 min-h-0 rounded-t-[20px] mt-12 overflow-hidden">
                <img 
                    src={`/api/images?deck=${deckId}&path=${card.image_path}`} 
                    alt={card.title_en}
                    className="w-full h-full object-cover"
                />
                <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-white to-transparent" />
            </div>

            {/* 3. NARRATIVE ZONE (Flex-None: Pushes Up) */}
            <div className="flex-none bg-white relative z-10 flex flex-col justify-end w-full pointer-events-none">
                
                {/* Floating Keyword Badge - Dynamic Size */}
                <div className="relative -top-6 flex justify-center z-20 h-0">
                    <DraggableElement id="keyword-badge" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                        <div 
                            className="bg-white shadow-xl rounded-full px-6 py-2 border-[3px] flex items-center gap-3 transform hover:scale-105 transition-transform" 
                            style={{ borderColor: borderColor }}
                        >
                            <span 
                                className="font-black text-slate-800 leading-normal pb-0.5 font-hebrew"
                                style={{ fontSize: `${activeConfig.keywordFontSize}px` }}
                            >
                                {card.hebrew_key_word_nikud || card.hebrew_key_word}
                            </span>
                            <span className="text-sm uppercase font-extrabold tracking-widest text-slate-500 font-sans border-l-2 pl-3 border-slate-200">
                                {card.english_key_word}
                            </span>
                        </div>
                    </DraggableElement>
                </div>

                {/* Description - Full Width */}
                <DraggableElement id="description-section" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                    <div 
                        className="w-full border-y-2 border-red-200 p-3 pt-6 flex items-center justify-center shadow-sm shrink-0 mb-[1px]"
                        style={{ backgroundColor: activeConfig.descriptionBgColor }}
                    >
                        <p 
                            className="text-slate-900 font-semibold leading-relaxed text-center"
                            style={{ fontSize: `${activeConfig.descriptionFontSize}px` }}
                        >
                            {card.english_description}
                        </p>
                    </div>
                </DraggableElement>
                
                {/* Action Footer - Full Width */}
                <DraggableElement id="footer-section" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                    <div 
                        className="w-full border-t border-red-200 p-3 flex items-center gap-4 shrink-0 min-h-[50px] rounded-b-[18px]"
                        style={{ backgroundColor: activeConfig.footerBgColor }}
                    >
                        {/* Drama Icon */}
                        <div className="bg-white p-2 rounded-full shadow-md text-red-500 shrink-0 border border-red-50">
                            <Drama size={20} />
                        </div>
                        
                        <div className="flex-1">
                            <p className="text-base text-red-900 font-bold italic leading-tight">
                                "{cleanRoleplay}"
                            </p>
                        </div>
                    </div>
                </DraggableElement>
            </div>
      </CardFrame>
  );
}

const GlassContainer = ({ children, className }: { children: React.ReactNode, className?: string }) => (
  <div className={cn(
    "bg-black/40 backdrop-blur-md border border-white/10 p-4 rounded-2xl shadow-xl text-white",
    className
  )}>
    {children}
  </div>
);

function ImmersiveLayout({ card, deckId, activeConfig, borderColor, cleanRoleplay, onPositionUpdate }: any) {
    return (
        <div className="relative w-full h-full rounded-[24px] overflow-hidden shadow-2xl bg-black">
            {/* Full Background Image */}
            <div className="absolute inset-0 z-0">
                 <img 
                    src={`/api/images?deck=${deckId}&path=${card.image_path}`} 
                    alt={card.title_en}
                    className="w-full h-full object-cover opacity-90"
                />
                {/* Dark Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/90 pointer-events-none" />
            </div>

            {/* Top Header */}
            <div className="absolute top-6 left-6 right-6 z-10 flex justify-between items-start pointer-events-none">
                 <DraggableElement id="title-group" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                     <div className="flex flex-col text-white drop-shadow-md">
                        <h2 className="text-3xl font-black drop-shadow-lg" style={{ color: activeConfig.titleColor }}>
                             {card.title_en}
                        </h2>
                         <p className="text-lg font-hebrew opacity-90">{card.title_he}</p>
                     </div>
                 </DraggableElement>

                 <DraggableElement id="badge" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                     <div className="bg-white/20 backdrop-blur-md px-3 py-1 rounded-full border border-white/30 font-bold text-sm text-white">
                        #{card.sequence_number}
                     </div>
                 </DraggableElement>
            </div>

            {/* Bottom Elements (Formerly Glass Panel) */}
            <div className="absolute bottom-6 left-6 right-6 z-10 space-y-4 pointer-events-none">
                
                {/* Keyword */}
                <DraggableElement id="keyword-group" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                    <GlassContainer className="inline-block relative">
                        <div className="flex items-center gap-3">
                             <span className="text-3xl font-black font-hebrew text-yellow-400">
                                {card.hebrew_key_word_nikud || card.hebrew_key_word}
                             </span>
                             <span className="text-sm uppercase tracking-widest opacity-70">
                                {card.english_key_word}
                             </span>
                        </div>
                    </GlassContainer>
                </DraggableElement>

                {/* Description */}
                <DraggableElement id="description-group" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                    <GlassContainer>
                        <p className="font-medium text-lg leading-relaxed text-white/90">
                            {card.english_description}
                        </p>
                    </GlassContainer>
                </DraggableElement>

                {/* Footer */}
                <DraggableElement id="footer-group" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                    <GlassContainer className="inline-block">
                        <div className="flex gap-3 text-sm opacity-80 items-center">
                            <Drama size={16} className="text-yellow-400" />
                            <span className="italic">{cleanRoleplay}</span>
                        </div>
                    </GlassContainer>
                </DraggableElement>
            </div>
        </div>
    );
}

function ImmersiveFloatingLayout({ card, deckId, activeConfig, borderColor, cleanRoleplay, onPositionUpdate }: any) {
    return (
        <div className="relative w-full h-full rounded-[24px] overflow-hidden shadow-2xl bg-black">
            {/* Full Background Image */}
            <div className="absolute inset-0 z-0">
                 <img 
                    src={`/api/images?deck=${deckId}&path=${card.image_path}`} 
                    alt={card.title_en}
                    className="w-full h-full object-cover"
                />
            </div>

            {/* Floating Top Header */}
            <div className="absolute top-6 left-6 right-6 z-10 flex justify-between items-start pointer-events-none">
                 <DraggableElement id="title-group" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                     <div className="text-white">
                        <h2 className="text-xl font-black drop-shadow-md" style={{ color: activeConfig.titleColor }}>
                             {card.title_en}
                        </h2>
                     </div>
                 </DraggableElement>

                 <DraggableElement id="badge" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                     <div className="bg-white/20 backdrop-blur-md px-3 py-1 rounded-full border border-white/30 font-bold text-sm text-white">
                        #{card.sequence_number}
                     </div>
                 </DraggableElement>
            </div>

            {/* Floating Bottom Box */}
            <div className="absolute bottom-8 left-8 right-8 z-10 pointer-events-none">
                 <DraggableElement id="content-box" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                     <div className="bg-white/90 backdrop-blur-lg shadow-2xl rounded-2xl p-5 space-y-3 border border-white/50 text-slate-900 w-full">
                        {/* Compact Element Row */}
                        <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                            <div className="flex items-baseline gap-2">
                                 <span className="text-2xl font-black font-hebrew text-slate-800">
                                    {card.hebrew_key_word_nikud || card.hebrew_key_word}
                                 </span>
                                 <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                                    {card.english_key_word}
                                 </span>
                            </div>
                            <Drama size={16} className="text-slate-400" />
                        </div>

                        {/* Description */}
                        <p className="font-semibold text-base leading-snug text-slate-800">
                            {card.english_description}
                        </p>
                     </div>
                 </DraggableElement>
            </div>
        </div>
    );
}

function ImmersiveCinematicLayout({ card, deckId, activeConfig, borderColor, cleanRoleplay, onPositionUpdate }: any) {
    return (
        <CardFrame 
            borderColor={borderColor} 
            className="relative w-full h-full overflow-hidden shadow-2xl"
        >
            {/* Full Background Image */}
            <div className="absolute inset-0 z-0">
                 <img 
                    src={`/api/images?deck=${deckId}&path=${card.image_path}`} 
                    alt={card.title_en}
                    className="w-full h-full object-cover"
                />
                {/* Gradient overlays for text visibility */}
                <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-black/40 to-transparent pointer-events-none" />
                <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-black/50 to-transparent pointer-events-none" />
            </div>

            {/* Top: Title */}
            <div className="absolute top-3 left-0 right-0 z-10 flex justify-center pointer-events-none">
                <DraggableElement id="title-group" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto w-full">
                    <div className="drop-shadow-lg flex flex-col items-center px-6">
                        <span
                            className="font-black font-hebrew text-white text-center"
                            style={{
                                fontSize: '28px',
                                lineHeight: 1.2,
                                textShadow: '2px 2px 0px #000, -1px -1px 0px #000, 1px -1px 0px #000, -1px 1px 0px #000',
                            }}
                        >
                            {card.title_he || ''}
                        </span>
                        <h2 className="text-sm font-bold text-white uppercase tracking-widest mt-1 opacity-90 drop-shadow-md">
                            {card.title_en}
                        </h2>
                    </div>
                </DraggableElement>
            </div>

            {/* Bottom Left: Keyword (no container, red Hebrew + white English) */}
            <div className="absolute bottom-6 left-6 pointer-events-none">
                 <DraggableElement id="keyword-group" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                    <div className="flex flex-col items-start">
                        <span
                            className="font-black text-3xl leading-none font-hebrew drop-shadow-lg"
                            style={{
                                color: borderColor,
                                textShadow: '2px 2px 4px rgba(0,0,0,0.5), -1px -1px 0 rgba(255,255,255,0.3)'
                            }}
                        >
                            {card.hebrew_key_word_nikud || card.hebrew_key_word}
                        </span>
                        <span
                            className="text-sm uppercase font-extrabold tracking-widest mt-1 drop-shadow-md"
                            style={{
                                color: 'white',
                                textShadow: '1px 1px 3px rgba(0,0,0,0.5)'
                            }}
                        >
                            {card.english_key_word}
                        </span>
                    </div>
                </DraggableElement>
            </div>
        </CardFrame>
    );
}

function ImmersiveCleanLayout({ card, deckId, activeConfig, borderColor, cleanRoleplay, onPositionUpdate }: any) {
    return (
        <CardFrame
            borderColor={borderColor}
            className="relative w-full h-full overflow-hidden shadow-2xl"
        >
            {/* Full Background Image */}
            <div className="absolute inset-0 z-0">
                 <img
                    src={`/api/images?deck=${deckId}&path=${card.image_path}`}
                    alt={card.title_en}
                    className="w-full h-full object-cover"
                />
                {/* Gradient overlays for text visibility */}
                <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-black/40 to-transparent pointer-events-none" />
                <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-black/50 to-transparent pointer-events-none" />
            </div>

            {/* Top: Title */}
            <div className="absolute top-3 left-0 right-0 z-10 flex justify-center pointer-events-none">
                <DraggableElement id="title-group" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto w-full">
                    <div className="drop-shadow-lg flex flex-col items-center px-6">
                        <span
                            className="font-black font-hebrew text-white text-center"
                            style={{
                                fontSize: '28px',
                                lineHeight: 1.2,
                                textShadow: '2px 2px 0px #000, -1px -1px 0px #000, 1px -1px 0px #000, -1px 1px 0px #000',
                            }}
                        >
                            {card.title_he || ''}
                        </span>
                        <h2 className="text-sm font-bold text-white uppercase tracking-widest mt-1 opacity-90 drop-shadow-md">
                            {card.title_en}
                        </h2>
                    </div>
                </DraggableElement>
            </div>

            {/* Bottom Left: Keyword (no container, Story-card style) */}
            <div className="absolute bottom-6 left-6 pointer-events-none">
                 <DraggableElement id="keyword-group" config={activeConfig} onUpdate={onPositionUpdate} className="pointer-events-auto">
                    <div className="flex flex-col items-start">
                        <span
                            className="font-black text-3xl leading-none font-hebrew drop-shadow-lg"
                            style={{
                                color: borderColor,
                                textShadow: '2px 2px 4px rgba(0,0,0,0.5), -1px -1px 0 rgba(255,255,255,0.3)'
                            }}
                        >
                            {card.hebrew_key_word_nikud || card.hebrew_key_word}
                        </span>
                        <span
                            className="text-sm uppercase font-extrabold tracking-widest mt-1 drop-shadow-md"
                            style={{
                                color: 'white',
                                textShadow: '1px 1px 3px rgba(0,0,0,0.5)'
                            }}
                        >
                            {card.english_key_word}
                        </span>
                    </div>
                </DraggableElement>
            </div>
        </CardFrame>
    );
}

function ScrapbookLayout({ card, deckId, activeConfig, borderColor, cleanRoleplay, onPositionUpdate }: any) {
    return (
        <div className="relative w-full h-full rounded-[24px] overflow-hidden shadow-2xl bg-[#fffdf5] p-6 flex flex-col gap-4">
            {/* Dotted Border simulated */}
            <div className="absolute inset-4 border-2 border-dashed border-slate-300 rounded-[20px] pointer-events-none opacity-50" />
            
            {/* Header: Sticker Style */}
            <DraggableElement id="sticker-header" config={activeConfig} onUpdate={onPositionUpdate} className="z-10 relative">
                <div className="bg-white border-2 border-slate-900 shadow-[4px_4px_0px_rgba(0,0,0,1)] rounded-xl p-3 flex justify-between items-center transform -rotate-1">
                     <div className="flex flex-col leading-none">
                        <span className="text-xs font-bold uppercase tracking-widest text-slate-500">Parasha Pack</span>
                        <h2 className="text-xl font-black text-slate-900">{card.title_en}</h2>
                     </div>
                     <div className="bg-yellow-400 w-10 h-10 rounded-full flex items-center justify-center font-black border-2 border-slate-900 text-slate-900">
                        {card.sequence_number}
                     </div>
                </div>
            </DraggableElement>

            {/* Image: Polaroid Style */}
            <div className="flex-1 z-10 relative mt-4">
                 <div className="absolute inset-0 bg-white border-4 border-white shadow-lg transform rotate-2 rounded-lg overflow-hidden">
                    <img 
                        src={`/api/images?deck=${deckId}&path=${card.image_path}`} 
                        alt={card.title_en}
                        className="w-full h-full object-cover"
                    />
                 </div>
                  {/* Tape */}
                 <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-24 h-8 bg-yellow-200/80 transform -rotate-2 backdrop-blur-sm" />
            </div>

            {/* Content Card */}
            <DraggableElement id="content-card" config={activeConfig} onUpdate={onPositionUpdate} className="z-10 relative">
                <div className="bg-white border-2 border-slate-200 rounded-xl p-4 shadow-sm mt-4 relative">
                    <div className="absolute -top-5 left-4 bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-bold shadow-md transform -rotate-1">
                        {card.english_key_word} • {card.hebrew_key_word}
                    </div>
                    
                    <p className="mt-2 text-slate-700 font-medium text-lg font-patrick leading-relaxed">
                        {card.english_description}
                    </p>

                     <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2 text-slate-500 text-sm italic">
                        <Drama size={16} />
                        {cleanRoleplay}
                    </div>
                </div>
            </DraggableElement>

        </div>
    );
}
