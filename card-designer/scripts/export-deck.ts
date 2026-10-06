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
 *   --no-compress         Keep the PDF's art as lossless PNG (by default the PDF
 *                         is shrunk with scripts/compress_pdf.py: art re-encoded
 *                         as JPEG at the same pixel size, ~57 MB -> ~6 MB)
 *   --skip-validate       Don't run src/validate_deck.py first
 *   --allow-overflow      Report overflowing text but export anyway
 *
 * Export guard (runs every time, before anything is written):
 *   1. The Python deck validator must report 0 errors (skip with --skip-validate).
 *   2. Layout check on /print/<id>?format=...: every back's text section must fit
 *      (.pp-card .body scrollHeight <= clientHeight + 1px), and every piece of text
 *      must sit inside the format's safe zone (letter: 0.3" margin; 5x7: 0.25"
 *      inside the trim line). Any problem fails the export with card id, side,
 *      format and how many px it is over (export anyway with --allow-overflow).
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
import { spawn, spawnSync, ChildProcess } from 'child_process';
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
  if (compressPdfs) compressPdf(outPath);
}

/**
 * Shrink the PDF with scripts/compress_pdf.py (art re-encoded as JPEG, same
 * pixel size). Best-effort: if python3 or pypdf is missing, warn and keep the
 * uncompressed PDF rather than failing the export.
 */
function compressPdf(pdfPath: string) {
  const repoRoot = path.join(__dirname, '../..');
  console.log('  Compressing PDF images (pass --no-compress to skip)...');
  const result = spawnSync('python3', [path.join(repoRoot, 'scripts', 'compress_pdf.py'), pdfPath], {
    cwd: repoRoot,
    stdio: 'inherit',
  });
  if (result.error || result.status !== 0) {
    const why = result.error ? result.error.message : `exit code ${result.status}`;
    console.warn(`  ⚠ PDF not compressed (${why}). Needs python3 with pypdf + Pillow: pip install pypdf pillow`);
  }
}


// ---------------------------------------------------------------- export guard

/** Find the source deck.json the validator should check (decks/<id> or decks/archive/<id>). */
function sourceDeckPath(deckId: string): string | null {
  const repoRoot = path.join(__dirname, '../..');
  for (const dir of [path.join(repoRoot, 'decks', deckId), path.join(repoRoot, 'decks', 'archive', deckId)]) {
    if (existsSync(path.join(dir, 'deck.json'))) return path.join(dir, 'deck.json');
  }
  return null;
}

/** Run src/validate_deck.py. Returns true when the deck has no errors. */
function runValidator(deckId: string): boolean {
  const repoRoot = path.join(__dirname, '../..');
  const deckPath = sourceDeckPath(deckId) ?? path.join(__dirname, '../content', deckId, 'deck.json');
  console.log(`\nValidating ${path.relative(repoRoot, deckPath)}...`);
  const result = spawnSync('python3', [path.join(repoRoot, 'src', 'validate_deck.py'), deckPath], {
    cwd: repoRoot,
    stdio: 'inherit',
  });
  if (result.error) {
    console.error(`✗ Could not run python3 src/validate_deck.py: ${result.error.message}`);
    return false;
  }
  return result.status === 0;
}

interface LayoutProblem {
  card: string;
  side: string;
  kind: 'overflow' | 'safe-zone';
  px: number;
  text?: string;
}

/** Inches from the sheet edge that text must stay inside. */
function safeInsetIn(format: FormatId): number {
  const f = formats.formats[format] as { margin_in?: number; bleed_in: number; safe_in?: number };
  // letter: the white paper margin. 5x7: the bleed (to the trim line) + the safe zone inside it.
  return f.margin_in ?? f.bleed_in + (f.safe_in ?? 0);
}

/**
 * Render every card side and measure it in the browser:
 *   - overflow: a back's .body section is taller than its box
 *   - safe-zone: some text is closer to the sheet edge than the safe inset
 */
async function checkLayout(browser: Browser, deckId: string, format: FormatId): Promise<LayoutProblem[]> {
  const [pageW] = formats.formats[format].page_in;
  const page = await openPrintView(browser, `${BASE_URL}/print/${deckId}?format=${format}`, pageW, 1);
  const problems = await page.evaluate(
    ({ insetPx }) => {
      const found: LayoutProblem[] = [];
      const sheets = Array.from(document.querySelectorAll<HTMLElement>('.pp-print-page'));
      // Nothing rendered means nothing was measured: treat it as a failure, not a pass
      if (sheets.length === 0) found.push({ card: '(none)', side: '-', kind: 'overflow', px: 0, text: 'no .pp-print-page found' });
      for (const sheet of sheets) {
        const card = sheet.dataset.card ?? '?';
        const side = sheet.dataset.side ?? '?';

        for (const body of Array.from(sheet.querySelectorAll<HTMLElement>('.pp-card .body'))) {
          const over = body.scrollHeight - body.clientHeight;
          if (over > 1) found.push({ card, side, kind: 'overflow', px: over });
        }

        const r = sheet.getBoundingClientRect();
        const safe = { left: r.left + insetPx, right: r.right - insetPx, top: r.top + insetPx, bottom: r.bottom - insetPx };
        let worst = 0;
        let worstText = '';
        const walker = document.createTreeWalker(sheet, NodeFilter.SHOW_TEXT);
        for (let node = walker.nextNode(); node; node = walker.nextNode()) {
          const text = node.textContent?.trim();
          if (!text) continue;
          const range = document.createRange();
          range.selectNodeContents(node);
          for (const box of Array.from(range.getClientRects())) {
            if (box.width === 0 || box.height === 0) continue;
            const out = Math.max(safe.left - box.left, box.right - safe.right, safe.top - box.top, box.bottom - safe.bottom);
            if (out > worst) {
              worst = out;
              worstText = text;
            }
          }
        }
        if (worst > 1) found.push({ card, side, kind: 'safe-zone', px: Math.round(worst), text: worstText.slice(0, 40) });
      }
      return found;
    },
    { insetPx: safeInsetIn(format) * CSS_DPI }
  );
  await page.context().close();
  return problems;
}

function printLayoutProblems(problems: LayoutProblem[], format: FormatId) {
  console.error(`\n✗ Layout check (${format}): ${problems.length} problem(s)`);
  for (const p of problems) {
    const what = p.kind === 'overflow' ? `text overflows its section by ${p.px}px` : `text ${p.px}px outside the safe zone`;
    console.error(`  ${p.card.padEnd(14)} ${p.side.padEnd(6)} ${format.padEnd(7)} ${what}${p.text ? ` ("${p.text}")` : ''}`);
  }
}

// ---------------------------------------------------------------- CLI

const args = process.argv.slice(2);
const deckId = args.find((a, i) => !a.startsWith('--') && args[i - 1] !== '--format');
const formatArg = args.includes('--format') ? args[args.indexOf('--format') + 1] : formats.default;

if (!deckId || !(formatArg in formats.formats)) {
  console.error('Usage: npm run export <deckId> -- [--format letter|5x7] [--backs|--backs-only|--fronts-only] [--pdf] [--no-compress] [--skip-validate] [--allow-overflow]');
  console.error('Example: npm run export bereshit -- --backs --pdf');
  process.exit(1);
}
const format = formatArg as FormatId;
const wantBacks = args.includes('--backs') || args.includes('--backs-only');
const wantFronts = !args.includes('--backs-only');
const wantPdf = args.includes('--pdf');
const compressPdfs = !args.includes('--no-compress');
const skipValidate = args.includes('--skip-validate');
const allowOverflow = args.includes('--allow-overflow');

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

  if (skipValidate) {
    console.log('\n⚠ Skipping the deck validator (--skip-validate)');
  } else if (!runValidator(deckId!)) {
    console.error('\n✗ Export stopped: the deck validator found errors. Fix them, or pass --skip-validate.');
    process.exit(1);
  }

  const server = await startDevServer();
  const browser = await chromium.launch();
  let failed = false;
  try {
    const problems = await checkLayout(browser, deckId!, format);
    if (problems.length === 0) {
      console.log(`\n✓ Layout check (${format}): no overflow, all text inside the safe zone`);
    } else {
      printLayoutProblems(problems, format);
      if (!allowOverflow) {
        console.error('\n✗ Export stopped: shorten the text above, or pass --allow-overflow to export anyway.');
        failed = true;
        return;
      }
      console.error('⚠ Exporting anyway (--allow-overflow)');
    }

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
  if (failed) process.exit(1);
}

main().catch((error) => {
  console.error('Export failed:', error);
  process.exit(1);
});
