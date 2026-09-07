// Import completed local generations into the web / Capacitor static bundle.
import { readFile, writeFile, mkdir, copyFile, rename } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { recordingKey } from '../../frontend/src/utils/recitations.js';

const source = process.argv[2];
if (!source) throw new Error('Usage: node import-audio.mjs /path/to/generated-folder');
const root = fileURLToPath(new URL('../../frontend/', import.meta.url));
const destination = path.join(root, 'public/narration');
const inventoryPath = path.join(root, 'src/data/narrationInventory.json');
const manifest = JSON.parse(await readFile(path.join(source, 'manifest.json'), 'utf8'));
const inventory = JSON.parse(await readFile(inventoryPath, 'utf8'));
await mkdir(destination, { recursive: true });
let imported = 0;
for (const [key, item] of Object.entries(manifest)) {
  if (item.demoOnly) continue;
  if (!['public-domain', 'project-original', 'permission-granted'].includes(item.rights) || !item.rightsNote) {
    throw new Error(`Missing commercial text rights: ${item.label}`);
  }
  if (key !== recordingKey(item) || !/^[a-f0-9]{64}\.wav$/.test(item.file)) throw new Error('Invalid manifest entry');
  const bytes = await readFile(path.join(source, item.file));
  if (bytes.length > 4 * 1024 * 1024 || bytes.subarray(0, 4).toString() !== 'RIFF'
    || bytes.subarray(8, 12).toString() !== 'WAVE'
    || createHash('sha256').update(bytes).digest('hex') !== item.audioSHA256) throw new Error('Audio integrity check failed');
  await copyFile(path.join(source, item.file), path.join(destination, item.file));
  inventory[key] = { url: `/narration/${item.file}`, voice: item.voice, model: item.model,
    revision: item.revision, rights: item.rights, rightsNote: item.rightsNote,
    listeningReviewed: item.listeningReviewed, seconds: item.seconds };
  imported++;
}
await writeFile(`${inventoryPath}.tmp`, JSON.stringify(inventory, null, 2) + '\n');
await rename(`${inventoryPath}.tmp`, inventoryPath);
console.log(`Imported ${imported} clips. ${Object.keys(inventory).length} exact spoken segments now have saved audio.`);
