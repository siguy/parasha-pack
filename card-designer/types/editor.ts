export interface LayoutConfig {
  fontFamily: 'font-fredoka' | 'font-mali' | 'font-patrick';
  imageHeightPercent: number; // e.g. 72
  descriptionFontSize: number; // e.g. 18
  titleFontSize: number; // e.g. 20
  
  // Colors
  headerBgColor?: string; // If undefined, use borderColor
  titleColor: string; // e.g. #ffffff
  descriptionBgColor: string; // e.g. #f8fafc
  footerBgColor: string; // e.g. #fef2f2
  
  // Padding
  containerPadding: number; // e.g. 0 (full width) or 4 (padded)
  paddingColor?: string; // e.g. #000000 or transparent
  
  // Elements
  keywordFontSize: number; // e.g. 24
  
  // Theme
  theme: 'standard' | 'immersive' | 'scrapbook' | 'immersive-floating' | 'immersive-cinematic' | 'immersive-clean';

  // Freeform Positions
  elementPositions?: Record<string, { x: number; y: number }>;
}

export const DEFAULT_LAYOUT_CONFIG: LayoutConfig = {
    fontFamily: 'font-fredoka',
    imageHeightPercent: 72,
    descriptionFontSize: 18,
    titleFontSize: 20,
    headerBgColor: undefined, 
    titleColor: '#ffffff',
    descriptionBgColor: '#f8fafc',
    footerBgColor: '#fee2e2',
    containerPadding: 0,
    keywordFontSize: 24,
    theme: 'standard'
};
