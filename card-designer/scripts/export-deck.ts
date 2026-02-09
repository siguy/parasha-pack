/**
 * Export deck cards to PNG using Playwright
 *
 * Usage:
 *   npm run export <deckId>              - Export fronts only
 *   npm run export <deckId> -- --backs   - Export fronts and backs
 *   npm run export <deckId> -- --backs-only  - Export backs only
 *   npm run export <deckId> -- --fronts-only - Export fronts only (default)
 *
 * Examples:
 *   npm run export purim
 *   npm run export purim -- --backs
 *
 * Features:
 * - Auto-starts dev server if not running
 * - Exports card fronts to decks/<deckId>/images/
 * - Exports card backs to decks/<deckId>/backs/
 * - 1500x2100 @ 300 DPI (5x7 print ready)
 *
 * Image Flow:
 *   raw/{id}.png -> Card Designer (React overlay) -> images/{id}.png (fronts)
 *                                                 -> backs/{id}_back.png (backs)
 */

import { chromium, Browser } from 'playwright';
import { spawn, ChildProcess } from 'child_process';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import path from 'path';

const PORT = 3000;
const BASE_URL = `http://localhost:${PORT}`;
const CARD_WIDTH = 1500;
const CARD_HEIGHT = 2100;

interface Card {
  card_id: string;
  card_type: string;
  [key: string]: unknown;
}

interface Deck {
  cards: Card[];
  [key: string]: unknown;
}

async function waitForServer(url: string, maxAttempts = 30): Promise<boolean> {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await fetch(url);
      if (response.ok) return true;
    } catch {
      // Server not ready yet
    }
    await new Promise(r => setTimeout(r, 1000));
    process.stdout.write('.');
  }
  return false;
}

async function isServerRunning(): Promise<boolean> {
  try {
    const response = await fetch(BASE_URL);
    return response.ok;
  } catch {
    return false;
  }
}

async function startDevServer(): Promise<ChildProcess | null> {
  if (await isServerRunning()) {
    console.log('✓ Dev server already running');
    return null;
  }

  console.log('Starting dev server...');
  const serverProcess = spawn('npm', ['run', 'dev'], {
    cwd: path.join(__dirname, '..'),
    stdio: ['ignore', 'pipe', 'pipe'],
    shell: true,
  });

  serverProcess.stdout?.on('data', (data) => {
    const output = data.toString();
    if (output.includes('Ready') || output.includes('started')) {
      // Server is ready
    }
  });

  serverProcess.stderr?.on('data', (data) => {
    const output = data.toString();
    if (!output.includes('ExperimentalWarning')) {
      // Only log non-experimental warnings
      process.stderr.write(data);
    }
  });

  process.stdout.write('Waiting for server');
  const ready = await waitForServer(BASE_URL);
  console.log();

  if (!ready) {
    console.error('✗ Server failed to start');
    serverProcess.kill();
    process.exit(1);
  }

  console.log('✓ Dev server started');
  return serverProcess;
}

async function exportCard(
  browser: Browser,
  deckId: string,
  cardId: string,
  outputPath: string,
  side: 'front' | 'back' = 'front'
): Promise<void> {
  // Use dedicated export page for full-resolution rendering
  // Front: /export/{deckId}/{cardId}
  // Back:  /export/{deckId}/{cardId}/back
  const exportUrl = side === 'back'
    ? `${BASE_URL}/export/${deckId}/${cardId}/back`
    : `${BASE_URL}/export/${deckId}/${cardId}`;

  const context = await browser.newContext({
    viewport: { width: CARD_WIDTH, height: CARD_HEIGHT },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();

  try {
    await page.goto(exportUrl, { waitUntil: 'networkidle' });

    // Wait for card to render
    await page.waitForSelector('[id^="card-"]', { timeout: 10000 });

    // Give fonts and images time to load
    await page.waitForTimeout(500);

    await page.screenshot({
      path: outputPath,
      clip: { x: 0, y: 0, width: CARD_WIDTH, height: CARD_HEIGHT },
    });

    const sideLabel = side === 'back' ? '(back)' : '';
    console.log(`  ✓ ${cardId} ${sideLabel}`);
  } catch (error) {
    console.error(`  ✗ ${cardId} (${side}): ${error instanceof Error ? error.message : 'Unknown error'}`);
  } finally {
    await context.close();
  }
}

interface ExportOptions {
  fronts: boolean;
  backs: boolean;
}

async function exportDeck(deckId: string, options: ExportOptions): Promise<void> {
  // Validate deck exists (content/ is a symlink to decks/)
  const deckPath = path.join(__dirname, '../content', deckId, 'deck.json');
  if (!existsSync(deckPath)) {
    console.error(`✗ Deck not found: ${deckPath}`);
    process.exit(1);
  }

  const deck: Deck = JSON.parse(readFileSync(deckPath, 'utf-8'));
  console.log(`\nExporting deck: ${deckId} (${deck.cards.length} cards)`);
  console.log(`  Fronts: ${options.fronts ? 'Yes' : 'No'}`);
  console.log(`  Backs: ${options.backs ? 'Yes' : 'No'}`);

  // Ensure output directories exist (output to canonical decks/ directory)
  const decksDir = path.join(__dirname, '../..', 'decks', deckId);
  const imagesDir = path.join(decksDir, 'images');
  const backsDir = path.join(decksDir, 'backs');

  if (options.fronts && !existsSync(imagesDir)) {
    mkdirSync(imagesDir, { recursive: true });
  }
  if (options.backs && !existsSync(backsDir)) {
    mkdirSync(backsDir, { recursive: true });
  }

  // Start server if needed
  const serverProcess = await startDevServer();

  // Launch browser
  const browser: Browser = await chromium.launch();

  try {
    // Export fronts
    if (options.fronts) {
      console.log('\nExporting card fronts:');
      for (const card of deck.cards) {
        const outputPath = path.join(imagesDir, `${card.card_id}.png`);
        await exportCard(browser, deckId, card.card_id, outputPath, 'front');
      }
      console.log(`  → Saved to: ${imagesDir}`);
    }

    // Export backs
    if (options.backs) {
      console.log('\nExporting card backs:');
      for (const card of deck.cards) {
        const outputPath = path.join(backsDir, `${card.card_id}_back.png`);
        await exportCard(browser, deckId, card.card_id, outputPath, 'back');
      }
      console.log(`  → Saved to: ${backsDir}`);
    }

    console.log('\n✓ Export complete!');
  } finally {
    await browser.close();

    if (serverProcess) {
      console.log('Stopping dev server...');
      serverProcess.kill();
    }
  }
}

// CLI entry point
const args = process.argv.slice(2);
const deckId = args.find(arg => !arg.startsWith('--'));
const hasBacksFlag = args.includes('--backs');
const hasBacksOnlyFlag = args.includes('--backs-only');
const hasFrontsOnlyFlag = args.includes('--fronts-only');

if (!deckId) {
  console.error('Usage: npm run export <deckId> [options]');
  console.error('');
  console.error('Options:');
  console.error('  --backs        Export both fronts and backs');
  console.error('  --backs-only   Export backs only');
  console.error('  --fronts-only  Export fronts only (default)');
  console.error('');
  console.error('Examples:');
  console.error('  npm run export purim');
  console.error('  npm run export purim -- --backs');
  console.error('  npm run export purim -- --backs-only');
  process.exit(1);
}

// Determine what to export
const options: ExportOptions = {
  fronts: !hasBacksOnlyFlag,
  backs: hasBacksFlag || hasBacksOnlyFlag,
};

// Default: fronts only if no flags
if (!hasBacksFlag && !hasBacksOnlyFlag && !hasFrontsOnlyFlag) {
  options.fronts = true;
  options.backs = false;
}

exportDeck(deckId, options).catch((error) => {
  console.error('Export failed:', error);
  process.exit(1);
});
