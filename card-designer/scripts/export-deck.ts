/**
 * Export a deck to PNG (for the web) and PDF (for printing) with Playwright.
 *
 * Usage:
 *   npm run export <deckId> [-- options]
 *
 * Options:
 *   --format letter|5x7   Paper format from print_formats.json (default: letter)
 *   --backs               PNG fronts AND backs
 *   --backs-only          PNG backs only
 *   --fronts-only         PNG fronts only (the default)
 *   --pdf                 Also write decks/<id>/print/<id>-<format>.pdf
 *                         (all cards, pages ordered front1, back1, front2, back2...
 *                         for duplex printing, flip on long edge)
 *
 * Examples:
 *   npm run export bereshit -- --backs --pdf
 *   npm run export bereshit -- --format 5x7 --pdf
 *
 * Output:
 *   letter PNGs: decks/<id>/images/<card>.png and decks/<id>/backs/<card>_back.png
 *   5x7 PNGs:    decks/<id>/images/5x7/...       and decks/<id>/backs/5x7/...
 *   PNGs are the card only (no paper margin, no bleed) at 300 DPI.
 *
 * Everything is rendered from one page, /print/<deckId>, which draws each
 * card side on a sheet of the exact paper size.
 *
 * The dev server runs on port 3000, or CARD_DESIGNER_PORT if set. If a
 * server is already running on that port it is reused, so make sure it is
 * this checkout's server.
 */

import { chromium, Browser, Page } from 'playwright';
import { spawn, ChildProcess } from 'child_process';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import path from 'path';
import formats from '../print_formats.json';

const PORT = Number(process.env.CARD_DESIGNER_PORT || 3000);
const BASE_URL = `http://localhost:${PORT}`;
const CSS_DPI = 96; // browsers lay out 96 CSS pixels per inch
const PRINT_DPI = 300;

type FormatId = keyof typeof formats.formats;

interface Deck {
  version?: string;
  cards: { card_id: string }[];
}

async function isServerRunning(): Promise<boolean> {
  try {
    return (await fetch(BASE_URL)).ok;
  } catch {
    return false;
  }
}

async function startDevServer(): Promise<ChildProcess | null> {
  if (await isServerRunning()) {
    console.log(`✓ Dev server already running on port ${PORT}`);
    return null;
  }

  console.log(`Starting dev server on port ${PORT}...`);
  const server = spawn('npx', ['next', 'dev', '-p', String(PORT)], {
    cwd: path.join(__dirname, '..'),
    stdio: ['ignore', 'ignore', 'pipe'],
    detached: true, // own process group, so we can stop next-server too
  });
  server.stderr?.on('data', (data) => {
    if (!data.toString().includes('ExperimentalWarning')) process.stderr.write(data);
  });

  process.stdout.write('Waiting for server');
  for (let i = 0; i < 60; i++) {
    if (await isServerRunning()) {
      console.log('\n✓ Dev server started');
      return server;
    }
    await new Promise((r) => setTimeout(r, 1000));
    process.stdout.write('.');
  }
  console.error('\n✗ Server failed to start');
  stopServer(server);
  process.exit(1);
}

function stopServer(server: ChildProcess) {
  try {
    process.kill(-server.pid!, 'SIGTERM'); // the whole process group
  } catch {
    server.kill();
  }
}

/** Open the print view and wait until fonts and images are ready. */
async function openPrintView(browser: Browser, url: string, pageWidthIn: number, scale: number): Promise<Page> {
  const context = await browser.newContext({
    viewport: { width: Math.round(pageWidthIn * CSS_DPI), height: 1200 },
    deviceScaleFactor: scale,
  });
  const page = await context.newPage();
  const response = await page.goto(url, { waitUntil: 'networkidle' });
  if (!response?.ok()) throw new Error(`${url} returned ${response?.status()}`);
  await page.evaluate(() => document.fonts.ready);
  return page;
}

async function exportPngs(browser: Browser, deckId: string, deck: Deck, format: FormatId, side: 'front' | 'back') {
  const [pageW] = formats.formats[format].page_in;
  const root = path.join(__dirname, '../..', 'decks', deckId, side === 'front' ? 'images' : 'backs');
  const outDir = format === formats.default ? root : path.join(root, format);
  mkdirSync(outDir, { recursive: true });

  const page = await openPrintView(
    browser,
    `${BASE_URL}/print/${deckId}?format=${format}&side=${side}`,
    pageW,
    PRINT_DPI / CSS_DPI
  );
  console.log(`\nExporting ${side}s (${format}, ${PRINT_DPI} DPI):`);
  for (const card of deck.cards) {
    const fileName = side === 'front' ? `${card.card_id}.png` : `${card.card_id}_back.png`;
    try {
      // The card itself, without the paper margin or bleed around it
      const el = page.locator(`[data-card="${card.card_id}"][data-side="${side}"] .pp-sheet > *`);
      await el.screenshot({ path: path.join(outDir, fileName) });
      console.log(`  ✓ ${fileName}`);
    } catch (error) {
      console.error(`  ✗ ${fileName}: ${error instanceof Error ? error.message : error}`);
    }
  }
  console.log(`  → ${outDir}`);
  await page.context().close();
}

async function exportPdf(browser: Browser, deckId: string, format: FormatId) {
  const [pageW, pageH] = formats.formats[format].page_in;
  const outDir = path.join(__dirname, '../..', 'decks', deckId, 'print');
  mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, `${deckId}-${format}.pdf`);

  const page = await openPrintView(browser, `${BASE_URL}/print/${deckId}?format=${format}`, pageW, 1);
  await page.pdf({
    path: outPath,
    width: `${pageW}in`,
    height: `${pageH}in`,
    margin: { top: '0', right: '0', bottom: '0', left: '0' },
    printBackground: true,
    preferCSSPageSize: true,
  });
  await page.context().close();
  console.log(`\n✓ PDF (${format}, duplex order front/back): ${outPath}`);
}

// ---------------------------------------------------------------- CLI

const args = process.argv.slice(2);
const deckId = args.find((a, i) => !a.startsWith('--') && args[i - 1] !== '--format');
const formatArg = args.includes('--format') ? args[args.indexOf('--format') + 1] : formats.default;

if (!deckId || !(formatArg in formats.formats)) {
  console.error('Usage: npm run export <deckId> -- [--format letter|5x7] [--backs|--backs-only|--fronts-only] [--pdf]');
  console.error('Example: npm run export bereshit -- --backs --pdf');
  process.exit(1);
}
const format = formatArg as FormatId;
const wantBacks = args.includes('--backs') || args.includes('--backs-only');
const wantFronts = !args.includes('--backs-only');
const wantPdf = args.includes('--pdf');

async function main() {
  const deckPath = path.join(__dirname, '../content', deckId!, 'deck.json');
  if (!existsSync(deckPath)) {
    console.error(`✗ Deck not found: ${deckPath} (did you run ./sync-deck.sh ${deckId}?)`);
    process.exit(1);
  }
  const deck: Deck = JSON.parse(readFileSync(deckPath, 'utf-8'));
  if (deck.version !== '3.0') {
    console.error(`✗ ${deckId} is not a v3 deck. Run: python src/migrate_v2_to_v3.py decks/${deckId}/deck.json`);
    process.exit(1);
  }
  console.log(`\nExporting ${deckId}: ${deck.cards.length} cards, format ${format}`);
  console.log(`  PNG fronts: ${wantFronts ? 'yes' : 'no'}  PNG backs: ${wantBacks ? 'yes' : 'no'}  PDF: ${wantPdf ? 'yes' : 'no'}`);

  const server = await startDevServer();
  const browser = await chromium.launch();
  try {
    if (wantFronts) await exportPngs(browser, deckId!, deck, format, 'front');
    if (wantBacks) await exportPngs(browser, deckId!, deck, format, 'back');
    if (wantPdf) await exportPdf(browser, deckId!, format);
    console.log('\n✓ Export complete!');
  } finally {
    await browser.close();
    if (server) {
      console.log('Stopping dev server...');
      stopServer(server);
    }
  }
}

main().catch((error) => {
  console.error('Export failed:', error);
  process.exit(1);
});
