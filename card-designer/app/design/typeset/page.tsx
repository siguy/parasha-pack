import React from 'react';
import { CardFrame } from '@/components/cards/CardFrame';
import { cn } from '@/lib/utils';
import { Zap, Heart, Drama } from 'lucide-react';

export default function TypesettingWorkbench() {
  const card = {
    title_en: "A Special Request",
    title_he: "בַּקָּשָׁה מְיֻחֶדֶת", 
    description: "God asks Moses for help. \"Tell the people to bring gifts from their hearts. We are going to build something special!\"",
    roleplay: "Put your hand on your heart - that's where giving comes from!",
    keyword_he: "לֵב",
    keyword_en: "HEART",
    sequence: 1,
    borderColor: "#ef4444" 
  };

  const variants = [
      { name: "Option A: Fredoka", font: "font-fredoka", label: "Modern & Soft" },
      { name: "Option B: Mali", font: "font-mali", label: "Childlike & Warm" },
      { name: "Option C: Patrick Hand", font: "font-patrick", label: "Marker Style" },
  ];

  return (
    <div className="min-h-screen bg-neutral-900 p-8 overflow-x-auto">
       <div className="flex gap-8 min-w-max mx-auto justify-center">
       {variants.map((v, idx) => (
           <div key={idx} className="flex flex-col items-center gap-4">
             <div className="text-white text-center">
                 <h2 className="text-xl font-bold text-red-400">{v.name}</h2>
                 <p className="text-sm text-neutral-400">{v.label}</p>
             </div>

             <div className="w-[420px] h-[600px] bg-white rounded-[24px]"> 
                <CardFrame 
                    borderColor={card.borderColor} 
                    className="flex flex-col relative h-full bg-white ring-4 ring-offset-2 ring-white/50 shadow-2xl"
                >
                    {/* 1. HEADER - Font Applied to English Title */}
                    <div className="absolute top-0 left-0 right-0 z-30">
                       <div 
                         className="w-full shadow-sm px-4 py-3 flex items-center justify-between rounded-t-[18px]"
                         style={{ backgroundColor: card.borderColor }}
                       >
                          <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white shrink-0 shadow-sm border border-white/30">
                            <Zap size={18} fill="currentColor" />
                          </div>
                          <div className="flex flex-row items-baseline gap-2 flex-1 overflow-hidden justify-center text-white">
                            <span className="text-xl font-black font-hebrew leading-none">
                                {card.title_he}
                            </span>
                            <h2 className={cn("text-sm font-bold uppercase tracking-widest leading-none opacity-90 pt-0.5", v.font)}>
                                {card.title_en}
                            </h2>
                          </div>
                          <div className="w-8 h-8 rounded-full bg-white text-red-500 font-black text-sm flex items-center justify-center shadow-md shrink-0">
                            {card.sequence}
                          </div>
                       </div>
                    </div>

                    {/* 2. VISUAL STAGE */}
                    <div className="h-[72%] w-full relative bg-slate-200 shrink-0 overflow-hidden z-0 rounded-t-[20px] mt-12">
                      <img 
                        src={`/api/images?deck=terumah&path=images/story_1.png`} 
                        alt="Story 1 Art"
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-white to-transparent" />
                    </div>

                    {/* 3. NARRATIVE ZONE */}
                    <div className="flex-1 bg-white relative z-10 flex flex-col justify-end">
                        <div className="relative -top-6 flex justify-center z-20 h-0">
                            <div 
                                className="bg-white shadow-xl rounded-full px-6 py-1.5 border-[3px] flex items-center gap-3 transform hover:scale-105 transition-transform" 
                                style={{ borderColor: card.borderColor }}
                            >
                                <span className="text-2xl font-black text-slate-800 leading-none pb-1 font-hebrew">
                                    {card.keyword_he}
                                </span>
                                <span className={cn("text-sm uppercase font-extrabold tracking-widest text-slate-500 border-l-2 pl-3 border-slate-200", v.font)}>
                                    {card.keyword_en}
                                </span>
                            </div>
                        </div>

                        <div className="w-full bg-slate-50 border-y-2 border-red-200 p-3 flex items-center justify-center shadow-sm shrink-0 mb-[1px]">
                          <p className={cn("text-slate-900 font-semibold text-lg leading-snug text-center", v.font)}>
                            {card.description}
                          </p>
                        </div>
                        
                        <div className="w-full bg-red-100 border-t border-red-200 p-3 flex items-center gap-4 shrink-0 min-h-[50px] rounded-b-[18px]">
                           {/* DRAMA ICON */}
                           <div className="bg-white p-2 rounded-full shadow-md text-red-500 shrink-0 border border-red-50">
                             <Drama size={20} />
                           </div>
                           
                           <div className="flex-1">
                             <p className={cn("text-base text-red-900 font-bold italic leading-tight", v.font)}>
                               "{card.roleplay}"
                             </p>
                           </div>
                        </div>
                    </div>
                </CardFrame>
             </div>
           </div>
       ))}
       </div>
    </div>
  );
}
