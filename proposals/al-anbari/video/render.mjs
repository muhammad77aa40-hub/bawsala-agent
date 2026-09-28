// Renders scene.html frame-by-frame with Playwright and encodes an MP4 with ffmpeg.
// node render.mjs                 -> ../output/Al-Anbari-System-Video.mp4
// node render.mjs --stills 2,8,17 -> ../output/video-stills/t-XX.png (preview frames)
import { createRequire } from 'module';
import { spawn, execSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
const npmRoot = execSync('npm root -g').toString().trim();
const { chromium } = require(path.join(npmRoot, 'playwright'));

const here = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(here, '..', 'output');
const FPS = 30;
const FFMPEG = process.env.FFMPEG || 'ffmpeg';

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto('file://' + path.join(here, 'scene.html'));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);

const stillsArg = process.argv.indexOf('--stills');
if (stillsArg > -1) {
  const dir = path.join(out, 'video-stills');
  fs.mkdirSync(dir, { recursive: true });
  for (const t of process.argv[stillsArg + 1].split(',').map(Number)) {
    await page.evaluate((t) => window.render(t), t);
    await page.screenshot({ path: path.join(dir, `t-${String(t).padStart(5, '0')}.png`) });
  }
  await browser.close();
  process.exit(0);
}

const duration = await page.evaluate(() => window.DURATION);
const total = Math.round(duration * FPS);
const file = path.join(out, 'Al-Anbari-System-Video.mp4');
const ff = spawn(FFMPEG, ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', file],
  { stdio: ['pipe', 'inherit', 'inherit'] });

for (let i = 0; i < total; i++) {
  await page.evaluate((t) => window.render(t), i / FPS);
  const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  if (i % 150 === 0) console.log(`frame ${i}/${total}`);
}
ff.stdin.end();
await new Promise((r) => ff.on('close', r));
await browser.close();
console.log('video:', file);
