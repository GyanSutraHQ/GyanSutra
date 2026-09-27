const { modernizeEnglish } = require('../services/modernEnglish');

describe('modernizeEnglish', () => {
  test('replaces archaic pronouns and verb forms while keeping the meaning', () => {
    expect(modernizeEnglish('If Thou thinkest that knowledge is superior to action, why dost Thou ask me to fight?'))
      .toBe('If You think that knowledge is superior to action, why do you ask me to fight?');
  });

  test('handles common source-language constructions', () => {
    expect(modernizeEnglish('Thy duty is to act; thou shalt not grieve, for he hath spoken unto thee.'))
      .toBe('Your duty is to act; you shall not grieve, for he has spoken to you.');
  });
});
