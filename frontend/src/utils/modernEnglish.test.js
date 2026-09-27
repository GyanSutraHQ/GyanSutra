import test from 'node:test';
import assert from 'node:assert/strict';
import { modernizeEnglish } from './modernEnglish.js';

test('modernizes common archaic English forms for readers', () => {
  assert.equal(
    modernizeEnglish('If Thou thinkest that knowledge is superior to action, why dost Thou ask me to fight?'),
    'If You think that knowledge is superior to action, why do you ask me to fight?',
  );
});
