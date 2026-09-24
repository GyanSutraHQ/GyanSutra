'use strict';

const { normalizeQuestion } = require('./ragUtils');

// This is deliberately a high-precision, deterministic filter. It is not a
// topic classifier: broad filtering would incorrectly reject valid questions
// such as "What is dharma?" before the scripture corpus can answer them.
const GREETING = /^(?:hi|hello|hey|namaste|namaskar|good (?:morning|afternoon|evening))(?:\s+(?:sarathi|saarthi))?[!?.]*$/i;
const IDENTITY = /^(?:who|what) (?:are|is) (?:you|sarathi|saarthi)(?:\?)*$/i;
const WELLBEING = /^(?:how are you|how(?:'s| is) it going|are you (?:okay|well))(?:\?)*$/i;
const THANKS = /^(?:thanks|thank you|thankyou|dhanyavad|shukriya)(?:\s+(?:sarathi|saarthi))?[!?.]*$/i;

const GENERAL_UTILITY = [
  /\b(?:what|which) (?:day|date) (?:is it|is today|is today\'?s)\b/i,
  /\b(?:what(?:'s| is) )?(?:today\'?s|current) (?:day|date|time)\b/i,
  /\b(?:weather|temperature|forecast)\b/i,
  /\b(?:what is|define|tell me about) python\b/i,
  /\b(?:what is|define|tell me about) (?:javascript|java|programming|coding|an algorithm)\b/i,
  /\b(?:write|debug|fix) (?:a |the )?(?:python|javascript|java|code|program)\b/i,
];

const COPY = {
  en: {
    greeting: 'Namaste — I’m Sarathi, Gyan Sutra’s guide to the Bhagavad Gita, Valmiki Ramayana, and Vishnu Purana. Ask me about a teaching, character, theme, or verse.',
    identity: 'I’m Sarathi, Gyan Sutra’s scripture guide. I can help you explore the Bhagavad Gita, Valmiki Ramayana, and Vishnu Purana with source-backed answers.',
    wellbeing: 'Namaste! I’m here and ready to help you explore the Bhagavad Gita, Valmiki Ramayana, or Vishnu Purana.',
    thanks: 'You’re welcome. Ask whenever you would like to explore a teaching, character, theme, or verse.',
    outOfScope: 'I’m focused on the Bhagavad Gita, Valmiki Ramayana, and Vishnu Purana, so I won’t guess at general current-information or programming questions. Ask me about a teaching, character, theme, or verse instead.',
  },
  hi: {
    greeting: 'नमस्ते — मैं सारथि हूँ। मैं भगवद्गीता, वाल्मीकि रामायण और विष्णु पुराण के विषयों में स्रोत-आधारित सहायता कर सकता हूँ।',
    identity: 'मैं ज्ञान सूत्र का सारथि हूँ। मैं भगवद्गीता, वाल्मीकि रामायण और विष्णु पुराण को स्रोतों के आधार पर समझने में सहायता करता हूँ।',
    wellbeing: 'नमस्ते! मैं भगवद्गीता, वाल्मीकि रामायण या विष्णु पुराण के विषयों में आपकी सहायता के लिए तैयार हूँ।',
    thanks: 'आपका स्वागत है। आप किसी शिक्षा, पात्र, विषय या श्लोक के बारे में पूछ सकते हैं।',
    outOfScope: 'मैं भगवद्गीता, वाल्मीकि रामायण और विष्णु पुराण पर केंद्रित हूँ, इसलिए सामान्य वर्तमान जानकारी या प्रोग्रामिंग के प्रश्नों का अनुमान से उत्तर नहीं दूँगा।',
  },
};

function copyFor(language) {
  return COPY[language] || COPY.en;
}

function classifySarathiGuardrail(question, language = 'en') {
  const normalized = normalizeQuestion(question);
  if (!normalized) return null;

  const copy = copyFor(language);
  if (GREETING.test(normalized)) return { type: 'conversational', answer: copy.greeting };
  if (IDENTITY.test(normalized)) return { type: 'conversational', answer: copy.identity };
  if (WELLBEING.test(normalized)) return { type: 'conversational', answer: copy.wellbeing };
  if (THANKS.test(normalized)) return { type: 'conversational', answer: copy.thanks };
  if (GENERAL_UTILITY.some((pattern) => pattern.test(normalized))) {
    return { type: 'out_of_scope', answer: copy.outOfScope };
  }
  return null;
}

module.exports = { classifySarathiGuardrail };
