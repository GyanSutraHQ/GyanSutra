// Import completed local generations into the web / Capacitor static bundle.
import { readFile, writeFile, mkdir, copyFile, rename, readdir, unlink } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { recordingKey } from '../../frontend/src/utils/recitations.js';

const source = process.argv[2];
const encodeAAC = process.argv.includes('--aac');
const prune = process.argv.includes('--prune');
if (!source) throw new Error('Usage: node import-audio.mjs /path/to/generated-folder [--aac] [--prune]');
const run = promisify(execFile);
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
  const sourceFile = path.join(source, item.file);
  const bytes = await readFile(sourceFile);
  if (bytes.length > 4 * 1024 * 1024 || bytes.subarray(0, 4).toString() !== 'RIFF'
    || bytes.subarray(8, 12).toString() !== 'WAVE'
    || createHash('sha256').update(bytes).digest('hex') !== item.audioSHA256) throw new Error('Audio integrity check failed');
  const outputFile = encodeAAC ? item.file.replace(/\.wav$/, '.m4a') : item.file;
  const destinationFile = path.join(destination, outputFile);
  if (encodeAAC) {
    let encoded;
    try {
      encoded = await readFile(destinationFile);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
    if (!encoded || encoded.length < 12 || encoded.subarray(4, 8).toString() !== 'ftyp') {
      const temporary = `${destinationFile}.tmp.m4a`;
      await run('ffmpeg', ['-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-i', sourceFile,
        '-map_metadata', '-1', '-vn', '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', temporary]);
      encoded = await readFile(temporary);
      if (encoded.length < 12 || encoded.subarray(4, 8).toString() !== 'ftyp') throw new Error('AAC integrity check failed');
      await rename(temporary, destinationFile);
    }
  } else {
    await copyFile(sourceFile, destinationFile);
  }
  inventory[key] = { url: `/narration/${outputFile}`, voice: item.voice, model: item.model,
    revision: item.revision, generationSeed: item.generationSeed,
    rights: item.rights, rightsNote: item.rightsNote,
    listeningReviewed: item.listeningReviewed, seconds: item.seconds };
  imported++;
  if (imported % 100 === 0) console.log(`Imported ${imported} clips...`);
}
await writeFile(`${inventoryPath}.tmp`, JSON.stringify(inventory, null, 2) + '\n');
await rename(`${inventoryPath}.tmp`, inventoryPath);
if (prune) {
  const referenced = new Set(Object.values(inventory).map((entry) => path.basename(entry.url)));
  for (const file of await readdir(destination)) {
    if (/^[a-f0-9]{64}\.(?:wav|m4a)$/.test(file) && !referenced.has(file)) await unlink(path.join(destination, file));
  }
}
console.log(`Imported ${imported} clips. ${Object.keys(inventory).length} exact spoken segments now have saved audio.`);
