// Exact text matching prevents an outdated meaning or different verse playing.
export const recordingKey = ({ locale, kind, text }) => JSON.stringify([locale, kind, text]);

export function getPreparedRecording(segment, inventory) {
  const item = inventory[recordingKey(segment)];
  if (!item || !/^\/narration\/[a-f0-9]{64}\.wav$/.test(item.url)) return null;
  return item;
}
