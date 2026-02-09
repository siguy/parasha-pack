import React from 'react';
import { LayoutConfig, DEFAULT_LAYOUT_CONFIG } from '@/types/editor';
import { RefreshCw, Save } from 'lucide-react';

interface EditorSidebarProps {
  config: LayoutConfig;
  onChange: (config: LayoutConfig) => void;
  onSave: () => void;
}

export function EditorSidebar({ config, onChange, onSave }: EditorSidebarProps) {
  
  const update = (key: keyof LayoutConfig, value: any) => {
    onChange({ ...config, [key]: value });
  };

  return (
    <div className="w-80 bg-slate-900/40 backdrop-blur-xl border-l border-white/10 p-6 flex flex-col gap-6 overflow-y-auto h-full shrink-0 shadow-2xl relative">
      {/* Background Gradient Mesh for Vibe */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-transparent pointer-events-none" />
      
      <div className="flex items-center justify-between relative z-10">
        <h2 className="text-white font-bold text-lg tracking-tight drop-shadow-md">Card Designer</h2>
        <button 
          onClick={onSave}
          className="flex items-center gap-2 bg-blue-600/90 hover:bg-blue-500 text-white text-xs px-3 py-1.5 rounded-lg font-bold transition-all shadow-lg hover:shadow-blue-500/25 border border-white/10"
        >
          <Save size={14} />
          Save
        </button>
      </div>

      {/* Theme Selection */}
      <div className="space-y-2 pb-6 border-b border-white/10 relative z-10">
        <h3 className="text-[10px] font-extrabold uppercase text-slate-400 tracking-widest pl-1">Theme</h3>
        <select 
            className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none shadow-inner"
            value={config.theme || 'standard'}
            onChange={(e) => update('theme', e.target.value)}
        >
            <option value="standard">Standard (Golden Master)</option>
            <option value="immersive">Immersive (Glass Panel)</option>
            <option value="immersive-floating">Immersive (Floating Box)</option>
            <option value="immersive-cinematic">Immersive (Cinematic)</option>
            <option value="immersive-clean">Immersive (Clean Strip)</option>
            <option value="scrapbook">Scrapbook (Playful)</option>
        </select>
      </div>

      {/* Layout Controls */}
      <div className="space-y-5 relative z-10">
        <h3 className="text-[10px] font-extrabold uppercase text-slate-400 tracking-widest pl-1">Layout</h3>

        <div>
             <label className="text-xs font-bold text-slate-300 flex justify-between mb-2">
                Image Height <span>{config.imageHeightPercent}%</span>
            </label>
            <input 
                type="range" min="30" max="100" step="1"
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-500 hover:accent-purple-400 transition-colors"
                value={config.imageHeightPercent}
                onChange={(e) => update('imageHeightPercent', parseInt(e.target.value))}
            />
        </div>



        <div>
             <label className="text-xs font-bold text-slate-300 flex justify-between mb-2">
                Container Padding <span>{config.containerPadding}px</span>
            </label>
            <input 
                type="range" min="0" max="40" step="4"
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-pink-500 hover:accent-pink-400 transition-colors"
                value={config.containerPadding}
                onChange={(e) => update('containerPadding', parseInt(e.target.value))}
            />
        </div>

        <div>
             <label className="text-xs font-bold text-slate-300 flex justify-between mb-2">
                Frame Color
            </label>
            <div className="flex gap-2">
                <input 
                    type="color"
                    className="w-8 h-8 rounded cursor-pointer bg-transparent border-0 p-0"
                    value={config.paddingColor || '#000000'}
                    onChange={(e) => update('paddingColor', e.target.value)}
                />
                <button 
                    onClick={() => update('paddingColor', 'transparent')}
                    className="text-[10px] bg-slate-800 text-slate-400 px-2 rounded border border-slate-700 hover:bg-slate-700 transition-colors"
                >
                    Clear
                </button>
            </div>
        </div>

        <div>
            <button 
                onClick={() => update('elementPositions', {})}
                className="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-2 rounded-lg font-bold border border-slate-700 transition-colors"
            >
                Reset Dragged Positions
            </button>
        </div>
      </div>

      {/* Typography Section */}
      <div className="space-y-5 pt-6 border-t border-white/10 relative z-10">
        <h3 className="text-[10px] font-extrabold uppercase text-slate-400 tracking-widest pl-1">Typography</h3>
        
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-300 mb-1 block">Font Family</label>
          <select 
            className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none"
            value={config.fontFamily}
            onChange={(e) => update('fontFamily', e.target.value)}
          >
            <option value="font-fredoka">Option A: Fredoka (Soft)</option>
            <option value="font-mali">Option B: Mali (Handwritten)</option>
            <option value="font-patrick">Option C: Patrick Hand (Marker)</option>
          </select>
        </div>

        <div>
            <label className="text-xs font-bold text-slate-300 flex justify-between mb-2">
                Title Size <span>{config.titleFontSize}px</span>
            </label>
            <input 
                type="range" min="16" max="64" step="1"
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500 hover:accent-blue-400"
                value={config.titleFontSize}
                onChange={(e) => update('titleFontSize', parseInt(e.target.value))}
            />
        </div>

        <div>
            <label className="text-xs font-bold text-slate-300 flex justify-between mb-2">
                Keyword Size <span>{config.keywordFontSize || 24}px</span>
            </label>
            <input 
                type="range" min="18" max="96" step="1"
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500 hover:accent-cyan-400"
                value={config.keywordFontSize || 24}
                onChange={(e) => update('keywordFontSize', parseInt(e.target.value))}
            />
        </div>

        <div>
            <label className="text-xs font-bold text-slate-300 flex justify-between mb-2">
                Description Size <span>{config.descriptionFontSize}px</span>
            </label>
            <input 
                type="range" min="12" max="32" step="1"
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500 hover:accent-emerald-400"
                value={config.descriptionFontSize}
                onChange={(e) => update('descriptionFontSize', parseInt(e.target.value))}
            />
        </div>
      </div>

      {/* Colors Section */}
      <div className="space-y-4 pt-6 border-t border-white/10 relative z-10">
        <h3 className="text-[10px] font-extrabold uppercase text-slate-400 tracking-widest pl-1">Colors</h3>

        <div className="grid grid-cols-2 gap-4">
             <div className="space-y-1">
                 <label className="text-[10px] text-slate-400 font-bold uppercase">Title</label>
                 <div className="flex items-center gap-2 bg-black/20 p-1.5 rounded-lg border border-white/5">
                     <input 
                         type="color" 
                         className="w-6 h-6 rounded cursor-pointer border-0 bg-transparent p-0"
                         value={config.titleColor || '#ffffff'}
                         onChange={(e) => update('titleColor', e.target.value)}
                     />
                     <span className="text-[10px] font-mono text-slate-400">{config.titleColor}</span>
                 </div>
             </div>
             
             <div className="space-y-1">
                 <label className="text-[10px] text-slate-400 font-bold uppercase">Header Bg</label>
                 <div className="flex items-center gap-2 bg-black/20 p-1.5 rounded-lg border border-white/5">
                     <input 
                         type="color" 
                         className="w-6 h-6 rounded cursor-pointer border-0 bg-transparent p-0"
                         value={config.headerBgColor || '#ef4444'}
                         onChange={(e) => update('headerBgColor', e.target.value)}
                     />
                     <span className="text-[10px] font-mono text-slate-400">Auto</span>
                 </div>
             </div>

             <div className="space-y-1">
                 <label className="text-[10px] text-slate-400 font-bold uppercase">Desc Bg</label>
                 <div className="flex items-center gap-2 bg-black/20 p-1.5 rounded-lg border border-white/5">
                     <input 
                         type="color" 
                         className="w-6 h-6 rounded cursor-pointer border-0 bg-transparent p-0"
                         value={config.descriptionBgColor}
                         onChange={(e) => update('descriptionBgColor', e.target.value)}
                     />
                 </div>
             </div>

             <div className="space-y-1">
                 <label className="text-[10px] text-slate-400 font-bold uppercase">Footer Bg</label>
                 <div className="flex items-center gap-2 bg-black/20 p-1.5 rounded-lg border border-white/5">
                     <input 
                         type="color" 
                         className="w-6 h-6 rounded cursor-pointer border-0 bg-transparent p-0"
                         value={config.footerBgColor}
                         onChange={(e) => update('footerBgColor', e.target.value)}
                     />
                 </div>
             </div>
        </div>
      </div>

    </div>
  );
}
