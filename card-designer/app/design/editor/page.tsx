'use client';
import React, { useState } from 'react';
import { StoryCard } from '@/components/cards/StoryCard';
import { EditorSidebar } from '@/components/editor/EditorSidebar';
import { DEFAULT_LAYOUT_CONFIG, LayoutConfig } from '@/types/editor';

// Hardcoded Story 1 Card Data
const DEMO_CARD: any = {
    card_id: "story-editor-demo",
    title_en: "A Special Request",
    title_he: "בַּקָּשָׁה מְיֻחֶדֶת", 
    english_description: "God asks Moses for help. \"Tell the people to bring gifts from their hearts. We are going to build something special!\"",
    roleplay_prompt: "Act it out: Put your hand on your heart - that's where giving comes from!",
    hebrew_key_word: "לֵב",
    english_key_word: "HEART",
    sequence_number: 1,
    border_color: "#ef4444",
    image_path: "images/story_1.png" // Mock path, will use api
};

export default function EditorPage() {
  const [config, setConfig] = useState<LayoutConfig>(DEFAULT_LAYOUT_CONFIG);

  React.useEffect(() => {
    fetch('/api/config')
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(err => console.error("Failed to load config", err));
  }, []);

  const handleSave = async () => {
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      if (res.ok) {
        alert("Configuration Saved to Disk!");
      } else {
        alert("Failed to save configuration.");
      }
    } catch (e) {
      console.error(e);
      alert("Error saving configuration.");
    }
  };

  return (
    <div className="flex h-screen bg-neutral-900 overflow-hidden">
        {/* Main Canvas Area */}
        <div className="flex-1 flex flex-col items-center justify-center p-12 bg-[url('/bg-grid.png')] bg-repeat relative"> 
            
            {/* The Canvas */}
            <div className="transform scale-100 transition-all duration-200">
                 {/* 
                     Using fixed dimensions for the physical card size (5x7 approx scaled)
                     Usually 500x700px for comfortable editing 
                 */}
                 <div className="w-[500px] h-[700px] bg-white rounded-[24px] shadow-2xl relative">
                    <StoryCard 
                        card={DEMO_CARD} 
                        deckId="terumah" 
                        config={config} 
                    />
                 </div>
            </div>

            <div className="absolute bottom-8 text-neutral-500 text-sm">
                Real-time Preview • Drag sliders to update
            </div>
        </div>

        {/* Sidebar Controls */}
        <EditorSidebar 
            config={config} 
            onChange={setConfig} 
            onSave={handleSave}
        />
    </div>
  );
}
