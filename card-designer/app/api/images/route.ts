/**
 * Image serving API route
 *
 * By default serves from raw/ (scene-only AI images without text).
 * Use source=images to serve from images/ (final composited images after export).
 *
 * Usage:
 *   /api/images?deck=purim&path=raw/story_1.png       -> serves raw AI image
 *   /api/images?deck=purim&path=images/story_1.png   -> serves final export
 *   /api/images?deck=purim&cardId=story_1            -> auto-serves raw/{cardId}.png
 */
import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const deckStart = searchParams.get('deck');
  let imagePath = searchParams.get('path');
  const cardId = searchParams.get('cardId');
  const source = searchParams.get('source') || 'raw'; // 'raw' or 'images'

  // Support cardId shortcut: /api/images?deck=purim&cardId=story_1
  if (!imagePath && cardId) {
    const safeCardId = cardId.replace(/[^a-zA-Z0-9_-]/g, '');
    imagePath = `${source}/${safeCardId}.png`;
  }

  if (!deckStart || !imagePath) {
    return new NextResponse('Missing parameters', { status: 400 });
  }

  // Security: Prevent directory traversal
  const safeDeck = deckStart.replace(/[^a-zA-Z0-9_-]/g, '');
  const safePath = imagePath.replace(/\.\./g, '');

  const fullPath = path.join(process.cwd(), 'content', safeDeck, safePath);

  try {
    const file = await fs.readFile(fullPath);
    // Determine mime type (simple)
    const ext = path.extname(fullPath).toLowerCase();
    let contentType = 'application/octet-stream';
    if (ext === '.png') contentType = 'image/png';
    if (ext === '.jpg' || ext === '.jpeg') contentType = 'image/jpeg';

    return new NextResponse(file, {
      headers: { 'Content-Type': contentType }
    });
  } catch (error) {
    console.error('Error serving image:', error);
    return new NextResponse('Image not found', { status: 404 });
  }
}
