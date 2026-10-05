// Frozen reference for migration tests only; not a backend runtime dependency.
// Retains the original Hugging Face adapter's preprocessing and pooling.
import fs from 'node:fs';
import { pipeline, env } from '@huggingface/transformers';

const root = process.env.LEGACY_REFERENCE_ROOT;
if (!root) throw new Error('Set LEGACY_REFERENCE_ROOT to the backend directory');
env.allowRemoteModels = false;
env.localModelPath = root + '/models/';
const model = await pipeline('feature-extraction', 'Xenova/gte-small', { dtype: 'q8' });
const cases = JSON.parse(fs.readFileSync(root + '/tests/fixtures/legacy_embeddings.json'));
const outputs = [];
for (const item of cases) {
  const input = item.text.replace(/\s+/g, ' ').trim();
  const tensor = await model(input, { pooling: 'mean', normalize: true });
  outputs.push({ ...item, vector: Array.from(tensor.data) });
}
fs.writeFileSync(process.argv[2], JSON.stringify(outputs));
