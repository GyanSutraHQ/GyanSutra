import './ReadingAssistant.css';

const COPY = {
  en: {
    title: 'Reading Assistant',
    description: 'Choose how this passage is shaped for the screen. The words and their order stay unchanged.',
    label: 'Reading layout',
    comfortable: 'Comfortable reading',
    short: 'Two-line paragraphs',
    points: 'Key points',
    note: 'AI-assisted layout · source text preserved',
  },
  hi: {
    title: 'रीडिंग असिस्टेंट',
    description: 'स्क्रीन पर यह पाठ कैसे दिखे, चुनें। शब्द और उनका क्रम नहीं बदलता।',
    label: 'पढ़ने का रूप',
    comfortable: 'सहज पाठ',
    short: 'दो-पंक्ति अनुच्छेद',
    points: 'मुख्य बिंदु',
    note: 'AI-सहायित रूप · मूल पाठ सुरक्षित',
  },
  bn: { title: 'রিডিং অ্যাসিস্ট্যান্ট', description: 'স্ক্রিনে পাঠটি কীভাবে সাজানো হবে বেছে নিন। শব্দ ও ক্রম অপরিবর্তিত থাকে।', label: 'পাঠের বিন্যাস', comfortable: 'স্বচ্ছন্দ পাঠ', short: 'দুই-লাইনের অনুচ্ছেদ', points: 'মূল বিষয়', note: 'AI-সহায়িত বিন্যাস · মূল পাঠ অক্ষুণ্ণ' },
  mr: { title: 'रीडिंग असिस्टंट', description: 'हा मजकूर स्क्रीनवर कसा मांडायचा ते निवडा. शब्द आणि त्यांचा क्रम बदलत नाही.', label: 'वाचन मांडणी', comfortable: 'सहज वाचन', short: 'दोन-ओळींचे परिच्छेद', points: 'मुख्य मुद्दे', note: 'AI-सहाय्यित मांडणी · मूळ मजकूर सुरक्षित' },
  te: { title: 'రీడింగ్ అసిస్టెంట్', description: 'ఈ పాఠం తెరపై ఎలా కనిపించాలో ఎంచుకోండి. పదాలు, వాటి క్రమం మారవు.', label: 'పఠన అమరిక', comfortable: 'సౌకర్యవంతమైన పఠనం', short: 'రెండు-లైన్ల పేరాలు', points: 'ముఖ్యాంశాలు', note: 'AI సహాయక అమరిక · మూల పాఠం భద్రం' },
  ta: { title: 'ரீடிங் அசிஸ்டெண்ட்', description: 'திரையில் இந்த உரை எவ்வாறு அமைக்கப்பட வேண்டும் என்பதைத் தேர்ந்தெடுக்கவும். சொற்களும் வரிசையும் மாறாது.', label: 'வாசிப்பு அமைப்பு', comfortable: 'எளிய வாசிப்பு', short: 'இரண்டு-வரி பத்திகள்', points: 'முக்கிய குறிப்புகள்', note: 'AI உதவி அமைப்பு · மூல உரை பாதுகாக்கப்பட்டது' },
};

export const READING_LAYOUTS = new Set(['comfortable', 'short', 'points']);

export default function ReadingAssistant({ language = 'en', layout, onLayoutChange }) {
  const labels = COPY[language] || COPY.en;

  return (
    <section className="reading-assistant" aria-labelledby="reading-assistant-title">
      <div className="reading-assistant__mark" aria-hidden="true">✦</div>
      <div className="reading-assistant__body">
        <div className="reading-assistant__intro">
          <div>
            <h2 id="reading-assistant-title">{labels.title}</h2>
            <p>{labels.description}</p>
          </div>
          <span className="reading-assistant__note">{labels.note}</span>
        </div>
        <label className="reading-assistant__field">
          <span>{labels.label}</span>
          <select value={layout} onChange={(event) => onLayoutChange(event.target.value)}>
            <option value="comfortable">{labels.comfortable}</option>
            <option value="short">{labels.short}</option>
            <option value="points">{labels.points}</option>
          </select>
        </label>
      </div>
    </section>
  );
}
