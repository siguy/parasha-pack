import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { DEFAULT_LAYOUT_CONFIG, LayoutConfig } from '@/types/editor';

const CONFIG_PATH = path.join(process.cwd(), 'layout_settings.json');

export async function GET() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const data = fs.readFileSync(CONFIG_PATH, 'utf-8');
      return NextResponse.json(JSON.parse(data));
    }
    return NextResponse.json(DEFAULT_LAYOUT_CONFIG);
  } catch (error) {
    return NextResponse.json(DEFAULT_LAYOUT_CONFIG, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const config = await req.json();
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to save config' }, { status: 500 });
  }
}
