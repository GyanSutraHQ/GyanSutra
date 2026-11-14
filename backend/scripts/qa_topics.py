"""Curated high-frequency scripture and life-guidance Q&A topic definitions (5W1H + Hindi)."""


def _topic(
    slug: str,
    source_id: str,
    title: str,
    keywords: str,
    citation_ids: list[str],
    what: str,
    why: str,
    how: str,
    when: str,
    where: str,
    who: str,
    hi: str,
    extra_questions: list[tuple[str, str]] | None = None,
) -> dict:
    questions = [
        {"q": f"What does Hindu scripture say about {title.lower()}?", "aspect": "what"},
        {"q": f"What is the teaching on {title.lower()}?", "aspect": "what"},
        {"q": f"Why is {title.lower()} important according to the scriptures?", "aspect": "why"},
        {"q": f"Why does {title.lower()} matter in spiritual life?", "aspect": "why"},
        {"q": f"How can I practice {title.lower()} in daily life?", "aspect": "how"},
        {"q": f"How do I overcome or apply {title.lower()}?", "aspect": "how"},
        {"q": f"When is {title.lower()} most needed or emphasized?", "aspect": "when"},
        {
            "q": f"Where is {title.lower()} taught in the Gita, Ramayana, or Vishnu Purana?",
            "aspect": "where",
        },
        {"q": f"Who exemplifies or teaches {title.lower()} in the scriptures?", "aspect": "who"},
        {"q": f"शास्त्रों में {title.lower()} के बारे में क्या शिक्षा दी गई है?", "aspect": "what"},
        {"q": f"{title.lower()} का क्या महत्व है और इसे जीवन में कैसे अपनाएँ?", "aspect": "how"},
    ]
    for q_text, aspect in extra_questions or []:
        questions.append({"q": q_text, "aspect": aspect})
    return {
        "id": f"topic_{slug}",
        "type": "topic",
        "sourceId": source_id,
        "title": title,
        "keywords": keywords,
        "citationIds": citation_ids,
        "questions": questions,
        "answers": {
            "en": {
                "what": what,
                "why": why,
                "how": how,
                "when": when,
                "where": where,
                "who": who,
            },
            "hi": {
                "default": hi,
            },
        },
    }


CURATED_TOPICS = [
    _topic(
        "karma_yoga",
        "bhagavad-gita",
        "Duty Without Attachment (Karma Yoga)",
        "karma yoga duty action fruits nishkama selfless work results effort",
        ["bhagavad-gita_2_47", "bhagavad-gita_3_19"],
        (
            "Karma Yoga teaches that you have authority over your sincere action alone, never over its outcomes [S1]. "
            "Rather than abandoning work or obsessing over reward, you act wholeheartedly out of duty without selfish clinging [S2]. "
            "In daily life, focusing fully on craft and responsibility brings clarity and inner freedom."
        ),
        (
            "Acting only for rewards creates constant anxiety about results beyond your control and keeps the mind bound to fear and greed [S1]. "
            "Performing required duties without attachment purifies the mind and leads to steady spiritual growth and peace [S2]."
        ),
        (
            "Commit your best effort to the task in front of you while consciously releasing anxiety over praise, profit, or failure [S1]. "
            "Treat every responsibility as a dedicated offering rather than a bargain for personal gain, and accept results calmly [S2]."
        ),
        (
            "Krishna delivered this teaching right as Arjuna felt paralyzed by the consequences of action before the Kurukshetra war [S1]. "
            "It applies whenever fear of failure, burnout, or expectation makes you hesitate to do what is right [S2]."
        ),
        (
            "This cornerstone teaching appears in Bhagavad Gita Chapter 2 Verse 47 and is expanded across Chapter 3 on Karma Yoga [S1][S2]."
        ),
        (
            "Sri Krishna teaches Karma Yoga to Arjuna on the battlefield, pointing out that steady, unattached doers attain the highest good [S1][S2]."
        ),
        (
            "गीता के अनुसार आपका अधिकार केवल निष्ठापूर्वक कर्म करने में है, उसके फल पर नहीं [S1]। "
            "फल की आसक्ति छोड़कर किया गया कर्तव्य-कर्म मन को शुद्ध करता है और व्यक्ति को परम शांति की ओर ले जाता है [S2]।"
        ),
        [
            ("What does Krishna say about duty without worrying about results?", "what"),
            ("How should I work without getting attached to outcomes?", "how"),
            ("Why shouldn't fruits of action be my motive?", "why"),
            ("What is Nishkama Karma in the Bhagavad Gita?", "what"),
            ("कर्मयोग क्या है और फल की चिंता किए बिना कर्म कैसे करें?", "how"),
        ],
    ),
    _topic(
        "control_anger",
        "bhagavad-gita",
        "Overcoming Anger and Desire",
        "anger krodha rage desire kama frustration delusion intellect peace",
        ["bhagavad-gita_2_62", "bhagavad-gita_2_63", "bhagavad-gita_16_21"],
        (
            "The Bhagavad Gita traces anger directly back to unfulfilled craving: dwelling on sense objects breeds attachment, which turns into desire and then anger when obstructed [S1]. "
            "Anger clouds judgment into delusion, scatters memory and clarity, and ruins discrimination [S2]."
        ),
        (
            "Together with lust and greed, anger is described as one of the three gates that destroy inner peace and self-mastery [S3]. "
            "Checking anger early protects clear thinking before one impulsive moment undoes years of wisdom [S2]."
        ),
        (
            "Notice attachment and overthinking before a craving hardens into demand [S1]. "
            "Pause when frustrated, recognize the chain reaction from desire to clouded memory, and choose deliberate restraint over impulsive reaction [S2][S3]."
        ),
        (
            "This warning becomes urgent whenever disappointment, criticism, or blocked ambition triggers sudden heat or resentment [S1][S2]."
        ),
        (
            "Krishna outlines the psychological ladder of anger in Bhagavad Gita 2.62-2.63 and names anger among the three destructive gates in 16.21 [S1][S2][S3]."
        ),
        (
            "Sri Krishna warns Arjuna about the chain of desire and anger so seekers can guard their intellect from inner ruin [S2][S3]."
        ),
        (
            "गीता बताती है कि विषयों का लगातार चिंतन आसक्ति और कामना पैदा करता है, और कामना में बाधा आने पर क्रोध जन्म लेता है [S1]। "
            "क्रोध से मोह और बुद्धि का नाश होता है, इसलिए काम, क्रोध और लोभ को त्यागना ही शांति का मार्ग है [S2][S3]।"
        ),
        [
            ("How do I control anger according to the Bhagavad Gita?", "how"),
            ("Why does anger destroy wisdom and memory?", "why"),
            ("Where does anger come from in human mind?", "what"),
            ("What are the three gates to self-destruction in the Gita?", "what"),
            ("क्रोध को कैसे नियंत्रित करें और यह क्यों आता है?", "how"),
        ],
    ),
    _topic(
        "anxiety_fear",
        "bhagavad-gita",
        "Relief from Anxiety, Fear, and Grief",
        "anxiety fear stress worry grief depression calm peace panic mental health",
        ["bhagavad-gita_2_56", "bhagavad-gita_4_10", "bhagavad-gita_18_66"],
        (
            "Scripture connects lasting relief from anxiety and fear with cultivating an unshakeable mind that is neither crushed by sorrow nor carried away by passing pleasure [S1]. "
            "Taking refuge in steady wisdom and divine grace frees a person from attachment, fear, and anger [S2][S3]."
        ),
        (
            "Worry grows when we cling to outcomes we do not control and feel alone under heavy burdens [S1]. "
            "Inner steadiness and trust dissolve paralyzing grief so you can act clearly even under pressure [S2][S3]."
        ),
        (
            "Do your immediate duty sincerely without brooding over every worst-case outcome [S1]. "
            "Practice steady remembrance of the Divine, let go of fear and craving step by step, and lean on trust when overwhelmed [S2][S3]."
        ),
        (
            "These teachings meet us in moments of crisis, bereavement, moral paralysis, or sleepless fear about the future [S1][S3]."
        ),
        (
            "You find this reassurance across Bhagavad Gita 2.56 on steady wisdom, 4.10 on freedom from fear, and 18.66's closing promise [S1][S2][S3]."
        ),
        (
            "Sri Krishna comforts a trembling, grief-stricken Arjuna, showing that steady sages and devoted seekers rise above fear and sorrow [S1][S3]."
        ),
        (
            "दुःख में विचलित न होना और सुख की लालसा न रखना ही स्थिर बुद्धि का लक्षण है [S1]। "
            "आसक्ति, भय और क्रोध से मुक्त होकर ईश्वर की शरण लेने से मन शांत और निर्भय हो जाता है [S2][S3]।"
        ),
        [
            ("How can I overcome anxiety, stress, and fear?", "how"),
            ("What does the Gita say when you feel overwhelmed or depressed?", "what"),
            ("Why does Krishna tell Arjuna not to fear or grieve?", "why"),
            ("Which verse in Gita removes fear and worry?", "where"),
            ("चिंता, तनाव और भय से मुक्ति कैसे पाएं?", "how"),
        ],
    ),
    _topic(
        "mind_control",
        "bhagavad-gita",
        "Mastering a Restless Mind",
        "restless mind focus overthinking concentration discipline abhyasa vairagya",
        ["bhagavad-gita_6_34", "bhagavad-gita_6_35", "bhagavad-gita_6_5"],
        (
            "Even Arjuna admits the mind is turbulent, forceful, and as hard to restrain as the wind [S1]. "
            "Krishna confirms this difficulty but teaches that the restless mind can indeed be mastered through steady practice (abhyasa) and detachment (vairagya) [S2], allowing you to lift yourself up [S3]."
        ),
        (
            "Left undisciplined, the mind acts like an internal enemy, pulling your energy into distraction and self-doubt [S3]. "
            "Trained with patience, that same mind becomes your strongest friend and anchor [S2][S3]."
        ),
        (
            "Gently bring your attention back each time it wanders—that repeated return is abhyasa—while loosening your grip on unproductive cravings (vairagya) [S2]. "
            "Be patient with setbacks and uplift yourself steadily rather than judging yourself harshly [S3]."
        ),
        (
            "Mind mastery applies whenever overthinking, distraction, or lack of focus pulls you away from study, work, or quiet reflection [S1][S2]."
        ),
        (
            "This dialogue sits at the heart of Bhagavad Gita Chapter 6, especially verses 6.5 and 6.34-6.35 [S1][S2][S3]."
        ),
        (
            "Arjuna honestly voices the struggle of every seeker, and Sri Krishna replies with practical encouragement rather than criticism [S1][S2]."
        ),
        (
            "अर्जुन स्वीकार करते हैं कि मन वायु के समान चंचल और कठिन है [S1]। "
            "श्रीकृष्ण उत्तर देते हैं कि निरंतर अभ्यास और वैराग्य के द्वारा इस चंचल मन को निश्चित ही वश में किया जा सकता है [S2][S3]।"
        ),
        [
            ("How do I control a restless and overthinking mind?", "how"),
            ("What is abhyasa and vairagya in Bhagavad Gita?", "what"),
            ("Why is the mind so hard to control?", "why"),
            ("Who helps you conquer your own mind?", "who"),
            ("चंचल मन को शांत और एकाग्र कैसे करें?", "how"),
        ],
    ),
    _topic(
        "meditation",
        "bhagavad-gita",
        "Meditation Practice (Dhyana Yoga)",
        "meditation dhyana yoga posture concentration inner stillness quiet",
        ["bhagavad-gita_6_11", "bhagavad-gita_6_12", "bhagavad-gita_6_19"],
        (
            "Dhyana Yoga describes sitting steadily in a clean, quiet spot, holding body, neck, and head aligned, and drawing wandering attention inward to one point [S1][S2]. "
            "A focused yogi's mind is compared to a lamp flame burning steadily in a windless place [S3]."
        ),
        (
            "Quiet, single-pointed meditation calms scattered thoughts, purifies the heart, and reveals deep inner stillness untouched by external noise [S2][S3]."
        ),
        (
            "Choose a clean, undisturbed seat, sit upright without strain, gaze calmly without looking around, and rest attention steadily on the Self rather than chasing thoughts [S1][S2]. "
            "Combine sitting practice with balanced daily habits [S3]."
        ),
        (
            "Regular daily practice—ideally at quiet hours when distractions are low—builds stillness over time rather than only in moments of crisis [S1][S2]."
        ),
        (
            "Meditation instructions are gathered in Bhagavad Gita Chapter 6 (Atma-Samyama Yoga), especially verses 6.11-6.19 [S1][S2][S3]."
        ),
        (
            "Sri Krishna acts as the teacher of meditation for Arjuna, outlining the discipline practiced by steady yogis [S1][S3]."
        ),
        (
            "ध्यान योग के अनुसार स्वच्छ और शांत स्थान पर सीधा बैठकर मन को एक बिंदु पर स्थिर करना चाहिए [S1][S2]। "
            "संयमित योगी का शांत मन हवा रहित स्थान में जलने वाले दीपक की अचल लौ के समान होता है [S3]।"
        ),
        [
            ("How should I meditate according to the Bhagavad Gita?", "how"),
            ("What is the lamp in a windless place metaphor?", "what"),
            ("Where are meditation techniques described in the Gita?", "where"),
            ("ध्यान या मेडिटेशन करने की सही विधि क्या है?", "how"),
        ],
    ),
    _topic(
        "soul_death",
        "bhagavad-gita",
        "The Eternal Soul (Atman) and Rebirth",
        "soul atman death rebirth reincarnation body clothes eternal immortal",
        ["bhagavad-gita_2_20", "bhagavad-gita_2_22", "bhagavad-gita_2_23"],
        (
            "The Gita teaches that the true Self (Atman) is never born and never dies; when the physical body perishes, the eternal soul is not slain [S1]. "
            "Like a person discarding worn-out clothes to put on new ones, the embodied Self moves on from worn bodies [S2], untouched by weapons, fire, water, or wind [S3]."
        ),
        (
            "Understanding the soul's permanence removes existential terror around aging, loss, and mortality, reminding us not to grieve blindly over the changing body [S1][S2]."
        ),
        (
            "View life and loss with deeper perspective: care responsibly for the body and relationships while recognizing your deeper identity is indestructible and luminous [S1][S3]."
        ),
        (
            "Krishna shares this immediately at the outset of his teaching when Arjuna breaks down over death on the battlefield [S1][S2]."
        ),
        (
            "These core verses on the immortal Self appear in Bhagavad Gita Chapter 2, verses 2.20 through 2.23 [S1][S2][S3]."
        ),
        (
            "Sri Krishna reveals this truth about Atman to Arjuna to lift him out of paralysing sorrow [S1][S2]."
        ),
        (
            "गीता के अनुसार आत्मा अजन्मा, नित्य और अविनाशी है; शरीर के नष्ट होने पर भी आत्मा नष्ट नहीं होती [S1]। "
            "जैसे मनुष्य पुराने वस्त्र त्यागकर नए वस्त्र धारण करता है, वैसे ही आत्मा पुराने शरीर छोड़कर नया शरीर ग्रहण करती है [S2][S3]।"
        ),
        [
            ("What happens to the soul after death according to the Gita?", "what"),
            ("Why is the soul compared to changing worn-out clothes?", "why"),
            ("Can weapons or fire harm the soul?", "what"),
            ("मृत्यु के बाद आत्मा का क्या होता है और क्या आत्मा अमर है?", "what"),
        ],
    ),
    _topic(
        "equanimity",
        "bhagavad-gita",
        "Equanimity in Success and Failure (Samatva)",
        "equanimity balance success failure yoga praise blame samatva steady",
        ["bhagavad-gita_2_38", "bhagavad-gita_2_48", "bhagavad-gita_12_18"],
        (
            "The Gita famously defines Yoga itself as evenness of mind (samatva)—remaining steady and balanced amid both success and failure [S2]. "
            "Seeing pleasure and pain, gain and loss, victory and defeat with equal poise keeps inner peace intact [S1][S3]."
        ),
        (
            "When happiness rises and crashes with every external win or criticism, your peace stays fragile. "
            "Equanimity frees you from ego-driven highs and crushing lows [S1][S2]."
        ),
        (
            "Treat victory and setback as passing weather while staying rooted in your commitment and integrity [S1][S2]. "
            "Meet both praise and blame calmly without letting either inflate pride or spark resentment [S3]."
        ),
        (
            "Equanimity is tested most sharply after major triumphs, sudden disappointments, public praise, or unfair criticism [S2][S3]."
        ),
        (
            "Samatva is taught in Bhagavad Gita 2.38 and 2.48, and praised again among the traits of a true devotee in 12.18 [S1][S2][S3]."
        ),
        (
            "Sri Krishna teaches Arjuna that a balanced yogi remains dear to the Divine precisely through this unshaken steadiness [S2][S3]."
        ),
        (
            "सुख-दुःख, लाभ-हानि और जय-पराजय में समान भाव से रहना ही योग (समत्व) कहलाता है [S1][S2]। "
            "निंदा और स्तुति दोनों में शांत रहने वाला साधक ही सच्चे अर्थों में स्थिर और ईश्वर को प्रिय होता है [S3]।"
        ),
        [
            ("What is Samatva or equanimity in the Bhagavad Gita?", "what"),
            ("How do I stay balanced in success and failure?", "how"),
            ("Why does Krishna say evenness of mind is Yoga?", "why"),
            ("सफलता और असफलता में मन को संतुलित कैसे रखें?", "how"),
        ],
    ),
    _topic(
        "bhakti_devotion",
        "bhagavad-gita",
        "Devotion and Loving Relationship with the Divine (Bhakti Yoga)",
        "bhakti devotion love worship leaf flower water faith prasad prayer",
        ["bhagavad-gita_9_22", "bhagavad-gita_9_26", "bhagavad-gita_12_13"],
        (
            "Bhakti Yoga emphasizes sincere, loving devotion over wealth, status, or elaborate ritual: Krishna joyfully accepts even a leaf, a flower, fruit, or water offered with a pure heart [S2]. "
            "To those who worship with steadfast focus, the Divine sustains what they have and provides what they need [S1]."
        ),
        (
            "Devotion turns everyday living into connection with the sacred and cultivates deep humility, compassion, and freedom from malice toward all beings [S3]."
        ),
        (
            "Offer simple daily acts, gratitude, and prayer with genuine love rather than showiness [S2]. "
            "Pair devotion with goodwill, patience, and non-hatred toward everyone around you [S3]."
        ),
        (
            "Bhakti is accessible at every stage of life, regardless of scholarship or resources, whenever you turn your heart sincerely toward the Divine [S1][S2]."
        ),
        (
            "Devotion shines through Bhagavad Gita Chapter 9 (9.22, 9.26) and throughout Chapter 12 on Bhakti Yoga [S1][S2][S3]."
        ),
        (
            "Sri Krishna personally assures devoted seekers of care and love, describing compassionate, humble devotees as deeply dear to him [S1][S3]."
        ),
        (
            "भक्ति योग में बाहरी आडंबर से अधिक हृदय की शुद्धता का महत्व है—प्रेम से अर्पित एक पत्र, पुष्प, फल या जल भी भगवान स्वीकार करते हैं [S2]। "
            "जो भक्त अनन्य भाव से ध्यान करते हैं, उनका योगक्षेम स्वयं भगवान वहन करते हैं [S1][S3]।"
        ),
        [
            ("What is Bhakti Yoga in the Bhagavad Gita?", "what"),
            ("How can an ordinary person practice true devotion?", "how"),
            ("Why does Krishna say a leaf or flower offered in love is enough?", "why"),
            ("भक्ति योग क्या है और सच्ची भक्ति कैसे करें?", "how"),
        ],
    ),
    _topic(
        "surrender",
        "bhagavad-gita",
        "Surrender and Trust in the Divine (Sharanagati)",
        "surrender sharanagati moksha 18.66 fear refuge trust grace",
        ["bhagavad-gita_18_66", "bhagavad-gita_9_34", "bhagavad-gita_18_62"],
        (
            "In his culminating assurance, Krishna tells Arjuna to lay down rigid clinging to lesser rules and take wholehearted refuge in the Divine alone, promising liberation from fear and past bondage [S1]. "
            "Surrender means aligning mind, heart, and humility with the Supreme rather than stubborn ego [S2][S3]."
        ),
        (
            "Human calculation eventually hits limits under heavy uncertainty; wholehearted surrender replaces exhausting ego-anxiety with deep peace and grace [S1][S3]."
        ),
        (
            "Do your responsible part with integrity, then release stubborn pride—orient your thoughts toward the Divine, stay humble, and trust divine care [S1][S2][S3]."
        ),
        (
            "This teaching crowns the very end of the Gita after exploring action, meditation, knowledge, and devotion, and guides moments when you cannot control everything [S1]."
        ),
        (
            "The supreme verses on surrender appear in Bhagavad Gita 9.34 and 18.62-18.66 [S1][S2][S3]."
        ),
        (
            "Sri Krishna offers this personal pledge directly to Arjuna—telling him, 'Do not grieve'—at the climax of their dialogue [S1]."
        ),
        (
            "गीता के अंतिम उपदेश में श्रीकृष्ण कहते हैं कि सभी अहंकारजनित आश्रयों को छोड़कर अनन्य भाव से मेरी शरण में आओ, मैं तुम्हें समस्त बंधनों से मुक्त कर दूँगा [S1]। "
            "यह शरणागति मनुष्य को भय और शोक से बाहर निकालकर परम शांति प्रदान करती है [S3]।"
        ),
        [
            ("What does complete surrender mean in Gita 18.66?", "what"),
            ("Why did Krishna ask Arjuna to abandon all dharmas and take refuge?", "why"),
            ("How do you practice surrender in real life without becoming lazy?", "how"),
            ("शरणागति का अर्थ क्या है और गीता 18.66 क्या सिखाता है?", "what"),
        ],
    ),
    _topic(
        "dharma_confusion",
        "bhagavad-gita",
        "Clarity During Moral Confusion and Hard Choices",
        "dharma confusion dilemma tough decision right wrong crisis guidance",
        ["bhagavad-gita_2_7", "bhagavad-gita_3_35", "bhagavad-gita_18_47"],
        (
            "When confused about duty, Arjuna admits his mind is bewildered and humbly asks Krishna to teach him what is truly good [S1]. "
            "Krishna guides seekers to act according to their own authentic duty and nature rather than blindly imitating another's path [S2][S3]."
        ),
        (
            "Trying to copy someone else's role out of fear or comparison breeds inner conflict and danger, whereas walking your honest duty builds steady character even if imperfect [S2][S3]."
        ),
        (
            "First pause and seek sincere wisdom rather than reacting defensively [S1]. "
            "Then examine what responsibility truthfully belongs to you in your current role, and carry it out faithfully [S2][S3]."
        ),
        (
            "These teachings speak directly to crossroads in career, family loyalty, ethics, and personal crisis when every choice feels hard [S1][S2]."
        ),
        (
            "Arjuna's honest plea is recorded in Gita 2.7, and Krishna's principle of svadharma is stressed in 3.35 and 18.47 [S1][S2][S3]."
        ),
        (
            "Arjuna models the courage to say 'I am confused, please guide me,' and Sri Krishna responds as teacher and charioteer [S1][S2]."
        ),
        (
            "जब कर्तव्य को लेकर मन भ्रमित हो जाए, तब अर्जुन की तरह विनम्र होकर सत्य और श्रेयस्कर मार्ग पूछना चाहिए [S1]। "
            "गीता सिखाती है कि दूसरे की नकल करने के बजाय अपने स्वभाव और परिस्थिति के अनुसार अपना धर्म (स्वधर्म) निभाना ही श्रेष्ठ है [S2][S3]।"
        ),
        [
            ("What should I do when confused between two duties or hard choices?", "what"),
            ("Why is following your own dharma better than copying someone else?", "why"),
            ("How did Arjuna handle confusion about right and wrong?", "how"),
            ("धर्म संकट या कठिन निर्णय के समय क्या करना चाहिए?", "what"),
        ],
    ),
    _topic(
        "svadharma",
        "bhagavad-gita",
        "Purpose and Your Own Duty (Svadharma)",
        "svadharma purpose calling vocation comparison duty natural path",
        ["bhagavad-gita_3_35", "bhagavad-gita_18_47"],
        (
            "Svadharma is the duty aligned with your own nature, responsibilities, and stage in life; the Gita declares that your own duty performed imperfectly is far better than someone else's duty performed well [S1][S2]."
        ),
        (
            "Borrowing another person's calling or path creates inner alienation and spiritual danger, while embracing your authentic work without arrogance prevents inner conflict [S1][S2]."
        ),
        (
            "Identify the real responsibilities placed in your hands today and honor them sincerely instead of envying more glamorous roles [S1]. "
            "Focus on steady integrity over flashy imitation [S2]."
        ),
        (
            "Remember Svadharma whenever social pressure, envy, or perfectionism tempts you to abandon your authentic work [S1][S2]."
        ),
        (
            "Svadharma is emphasized both near the start of Karma Yoga in Gita 3.35 and in the final chapter at 18.47 [S1][S2]."
        ),
        (
            "Sri Krishna reminds Arjuna of his warrior and protector responsibilities instead of escaping to a forest out of panic [S1][S2]."
        ),
        (
            "स्वधर्म का अर्थ है अपने स्वभाव और उत्तरदायित्व के अनुसार कर्तव्य का पालन करना [S1]। "
            "अच्छी तरह किए गए पराए धर्म की तुलना में गुणहीन प्रतीत होने वाला अपना धर्म भी अधिक कल्याणकारी होता है [S2]।"
        ),
        [
            ("What does Svadharma mean?", "what"),
            ("How do I find my true purpose in life?", "how"),
            ("Why does Gita 3.35 say one's own dharma is better even if flawed?", "why"),
            ("स्वधर्म क्या है और अपने जीवन का उद्देश्य कैसे पहचानें?", "what"),
        ],
    ),
    _topic(
        "action_vs_inaction",
        "bhagavad-gita",
        "Action, Inaction, and Wise Effort (Karma vs Akarma)",
        "action inaction laziness akarma work responsibility effort",
        ["bhagavad-gita_3_4", "bhagavad-gita_3_8", "bhagavad-gita_4_18"],
        (
            "The Gita teaches that simply avoiding action does not produce liberation or peace [S1]; everyone must perform necessary duty, because active engagement is better than idle inaction [S2]. "
            "Wise seers recognize inaction within action (unattached work) and action within inaction [S3]."
        ),
        (
            "Running away from work leaves restlessness untouched inside the mind and fails even to sustain ordinary life [S1][S2]. "
            "True freedom comes from inner non-attachment while acting, not from laziness [S3]."
        ),
        (
            "Show up steadily for your daily responsibilities [S2]. "
            "Act with calm presence and without ego-obsession so even busy effort stays peaceful inside [S3]."
        ),
        (
            "This clarifies things whenever spirituality is mistaken for passivity or when apathy disguises itself as detachment [S1][S2]."
        ),
        ("These ideas appear in Bhagavad Gita 3.4, 3.8, and 4.18 [S1][S2][S3]."),
        (
            "Sri Krishna corrects Arjuna's impulse to drop his bow, distinguishing true renunciation from mere avoidance [S1][S3]."
        ),
        (
            "केवल काम छोड़ देने से मनुष्य निष्कर्मता या सिद्धि प्राप्त नहीं करता [S1]। "
            "अकर्मण्यता से श्रेष्ठ है अपना नियत कर्म करते रहना, और सच्चा ज्ञानी कर्म करते हुए भी आसक्ति से मुक्त रहता है [S2][S3]।"
        ),
        [
            ("Why is action better than inaction in the Bhagavad Gita?", "why"),
            ("What does seeing inaction in action mean in Gita 4.18?", "what"),
            ("Is quitting work considered spiritual in the Gita?", "what"),
            ("कर्म और अकर्म में क्या अंतर है?", "what"),
        ],
    ),
    _topic(
        "detachment",
        "bhagavad-gita",
        "Detachment While Living in the World (Vairagya)",
        "detachment vairagya lotus leaf water worldly life family non-attachment",
        ["bhagavad-gita_5_10", "bhagavad-gita_2_47", "bhagavad-gita_12_17"],
        (
            "True detachment (Vairagya) in the Gita does not mean hating family or fleeing society; it means acting responsibly while offering the work to the Divine—untouched by clinging, just as a lotus leaf remains dry above water [S1][S2]."
        ),
        (
            "Clinging makes every loss unbearable and clouds ethics with fear [S2]. "
            "Healthy non-attachment brings steadiness so you can love and serve freely without inner bondage [S1][S3]."
        ),
        (
            "Engage warmly in your relationships and duties [S2], notice when possessiveness or anxiety over outcomes creeps in, and practice releasing results into higher hands like water sliding off a lotus leaf [S1][S3]."
        ),
        (
            "Vairagya supports you whenever career swings, interpersonal disappointments, or fear of loss threaten your composure [S1][S3]."
        ),
        (
            "The iconic lotus-leaf image stands in Bhagavad Gita 5.10, supported by 2.47 and 12.17 [S1][S2][S3]."
        ),
        (
            "Sri Krishna illustrates how active householders and seekers alike can live calmly in the world without being stained by selfishness [S1][S3]."
        ),
        (
            "सच्चा वैराग्य संसार से भागना नहीं बल्कि कमल के पत्ते की तरह कर्तव्य करते हुए भी आसक्ति से अछूता रहना है [S1]। "
            "निष्काम भाव से कर्म करने वाला व्यक्ति संसार में रहकर भी बंधनों से मुक्त रहता है [S2][S3]।"
        ),
        [
            ("What is true detachment according to the Bhagavad Gita?", "what"),
            ("How can I stay detached while having family and career?", "how"),
            ("Why is a yogi compared to a lotus leaf in water?", "why"),
            ("संसार में रहते हुए वैराग्य या अनासक्ति कैसे अपनाएं?", "how"),
        ],
    ),
    _topic(
        "self_friend",
        "bhagavad-gita",
        "Being Your Own Friend or Enemy (Self-Mastery)",
        "self mastery friend enemy uplift elevate confidence discipline habits",
        ["bhagavad-gita_6_5", "bhagavad-gita_6_6"],
        (
            "The Gita declares that a person must uplift themselves by their own mind and never drag themselves down, because the mind itself acts as your closest friend when disciplined or your worst enemy when uncontrolled [S1][S2]."
        ),
        (
            "Blaming external circumstances forever leaves you powerless. "
            "Recognizing internal agency gives you the power to rebuild habits, self-respect, and calm focus [S1][S2]."
        ),
        (
            "Train daily habits, tame scattered impulses, and refuse self-defeating inner talk [S1]. "
            "Gradual self-conquest turns inner resistance into a steady inner ally [S2]."
        ),
        (
            "This message speaks directly whenever procrastination, self-sabotage, or discouragement weighs you down [S1][S2]."
        ),
        (
            "These two crisp verses open the practical heart of Bhagavad Gita Chapter 6 at 6.5 and 6.6 [S1][S2]."
        ),
        (
            "Sri Krishna teaches Arjuna this principle of self-reliance right before describing the disciplined yogi [S1][S2]."
        ),
        (
            "मनुष्य को चाहिए कि वह अपने द्वारा अपना उद्धार करे और अपने को नीचे न गिरने दे [S1]। "
            "जिसने स्वयं अपने मन को जीत लिया है, उसका मन ही उसका परम मित्र है; और असंयमित मन ही उसका शत्रु बन जाता है [S2]।"
        ),
        [
            ("What does Krishna mean by 'elevate yourself by yourself' in Gita 6.5?", "what"),
            ("When is the mind your friend versus your enemy?", "when"),
            ("How do I build self-discipline and stop self-sabotage?", "how"),
            ("आत्म-उद्धार क्या है और मन हमारा मित्र या शत्रु कैसे बनता है?", "how"),
        ],
    ),
    _topic(
        "three_gunas",
        "bhagavad-gita",
        "The Three Gunas (Sattva, Rajas, Tamas)",
        "gunas sattva rajas tamas clarity passion inertia nature qualities",
        ["bhagavad-gita_14_5", "bhagavad-gita_14_6", "bhagavad-gita_14_17"],
        (
            "The three Gunas are the fundamental qualities of nature that bind and shape our mind and behavior: Sattva (clarity, harmony, wisdom), Rajas (restless drive, craving), and Tamas (dullness, confusion, inertia) [S1][S2][S3]."
        ),
        (
            "Knowing which quality is dominating your thoughts helps you understand sudden moods, restlessness, or sluggishness without confusion [S1][S3]."
        ),
        (
            "Cultivate Sattva through clear thinking, honest habits, clean speech, and quiet reflection [S2][S3], channel Rajas into disciplined duty rather than greed, and push past Tamas with steady routine."
        ),
        (
            "Notice the Gunas whenever you ask why energy swings between clarity, restlessness, and apathy over a week [S1][S3]."
        ),
        (
            "Krishna devotes all of Bhagavad Gita Chapter 14 to the Three Gunas, beginning around 14.5-14.17 [S1][S2][S3]."
        ),
        (
            "Sri Krishna explains the Gunas to Arjuna, showing how wisdom arises from Sattva, greed from Rajas, and negligence from Tamas [S3]."
        ),
        (
            "प्रकृति के तीन गुण—सत्त्व (प्रकाश और ज्ञान), रजस् (चंचलता और तृष्णा), तथा तमस् (अज्ञान और आलस्य)—मन और स्वभाव को बाँधते हैं [S1][S2]। "
            "सत्त्व गुण से ज्ञान उत्पन्न होता है, जबकि रजस् से लोभ और तमस् से मोह बढ़ता है [S3]।"
        ),
        [
            ("What are Sattva, Rajas, and Tamas?", "what"),
            ("How can I increase Sattva in my daily life?", "how"),
            ("Why do the three Gunas bind the soul?", "why"),
            ("त्रिगुण—सत्त्व, रजस् और तमस् क्या हैं?", "what"),
        ],
    ),
    _topic(
        "three_gates_hell",
        "bhagavad-gita",
        "Three Gates to Ruin (Lust, Anger, Greed)",
        "three gates hell kama krodha lobha lust anger greed self destruction",
        ["bhagavad-gita_16_21", "bhagavad-gita_3_37"],
        (
            "The Gita names three destructive impulses—insatiable lust/desire, anger, and greed—as the triple gate that leads to self-destruction and moral ruin [S1]. "
            "Krishna calls intense craving and anger the fierce enemy clouding human wisdom [S2]."
        ),
        (
            "Unchecked, these three drives push people toward dishonesty, harm, and relentless restlessness, destroying inner peace and clarity [S1][S2]."
        ),
        (
            "Recognize craving and greed before they escalate into anger [S2], guard the senses with discipline, and practice contentment and steady restraint [S1]."
        ),
        (
            "Be especially watchful when ambition turns into greed or wounded pride sparks sudden anger [S1][S2]."
        ),
        (
            "Krishna calls lust and anger the great enemy in Gita 3.37 and names the triple gate in 16.21 [S1][S2]."
        ),
        (
            "Arjuna asks what compels a person to do wrong almost against their will, and Sri Krishna identifies desire and anger [S2]."
        ),
        (
            "काम, क्रोध और लोभ—ये तीन आत्म-नाश करने वाले नरक के द्वार कहे गए हैं [S1]। "
            "गीता बताती है कि यही प्रबल कामना और क्रोध मनुष्य के विवेक को ढकने वाले सबसे बड़े शत्रु हैं, जिनका त्याग करना ही श्रेयस्कर है [S2]।"
        ),
        [
            ("What are the three gates to hell mentioned in Bhagavad Gita?", "what"),
            ("Why are desire, anger, and greed considered enemies?", "why"),
            ("How do you guard against greed and uncontrolled desire?", "how"),
            ("काम, क्रोध और लोभ को नरक के तीन द्वार क्यों कहा गया है?", "why"),
        ],
    ),
    _topic(
        "divine_qualities",
        "bhagavad-gita",
        "Noble Virtues and Character (Daivi Sampat)",
        "virtues character daivi sampat fearlessness truthfulness compassion humility",
        ["bhagavad-gita_16_1", "bhagavad-gita_16_2", "bhagavad-gita_16_3"],
        (
            "Daivi Sampat ('divine qualities') lists core ethical and spiritual virtues: fearlessness, purity of heart, generosity, self-restraint, truthfulness, non-violence, absence of anger, gentleness, patience, and freedom from arrogance [S1][S2][S3]."
        ),
        (
            "These qualities liberate the heart from fear and pettiness, fostering trustworthy character and spiritual clarity [S1][S2]."
        ),
        (
            "Build one quiet virtue at a time—speaking truthfully without harshness, restraining anger quickly, practicing honesty in small dealings, and treating others gently [S2][S3]."
        ),
        (
            "Every ordinary conversation, conflict, or leadership moment tests which qualities you choose to strengthen [S1][S3]."
        ),
        (
            "The full list opens Bhagavad Gita Chapter 16 across verses 16.1 through 16.3 [S1][S2][S3]."
        ),
        (
            "Sri Krishna assures Arjuna that these noble qualities belong to seekers inclined toward liberation and inner strength [S1][S2]."
        ),
        (
            "निर्भयता, अंतःकरण की शुद्धि, दान, संयम, सत्य, अहिंसा, अक्रोध, दया, क्षमा और अमानिता—ये दैवी संपदा के प्रमुख सद्गुण हैं [S1][S2][S3]। "
            "इन गुणों का अभ्यास मनुष्य के चरित्र को निखारता है और मोक्ष का मार्ग प्रशस्त करता है।"
        ),
        [
            ("What are the divine qualities (Daivi Sampat) in the Gita?", "what"),
            ("How does the Gita describe good character and virtues?", "how"),
            ("Where in Bhagavad Gita are ethical virtues listed?", "where"),
            ("गीता में बताए गए प्रमुख दैवी गुण या सद्गुण कौन से हैं?", "what"),
        ],
    ),
    _topic(
        "faith_shraddha",
        "bhagavad-gita",
        "Faith, Habits, and Daily Nourishment (Shraddha)",
        "faith shraddha food lifestyle habits belief values character",
        ["bhagavad-gita_17_3", "bhagavad-gita_17_8"],
        (
            "The Gita states that each person's faith aligns with their inner nature: you truly become what your deepest conviction and values are shaped around [S1]. "
            "It even connects lifestyle and pure, nourishing food with strength, vitality, clarity, and cheerfulness [S2]."
        ),
        (
            "What you consistently believe, consume, and practice quietly shapes your resilience, health, and ethics over years [S1][S2]."
        ),
        (
            "Notice what actually commands your loyalty and attention [S1], and nourish both mind and body with fresh, wholesome, non-harming habits [S2]."
        ),
        (
            "Reflection on Shraddha matters whenever setting long-term habits or noticing how lifestyle affects your peace of mind [S1][S2]."
        ),
        (
            "Faith and wholesome nourishment are explored in Bhagavad Gita Chapter 17 (17.3 and 17.8) [S1][S2]."
        ),
        (
            "Arjuna asks about sincere faith without formal scripture mastery, and Sri Krishna explains the threefold nature of faith [S1]."
        ),
        (
            "मनुष्य की श्रद्धा उसके अंतःकरण के अनुरूप होती है—जैसी उसकी श्रद्धा होती है, वैसा ही वह बन जाता है [S1]। "
            "सात्त्विक और शुद्ध आहार तथा स्वस्थ आदतें आयु, बल, आरोग्य, सुख और प्रसन्नता को बढ़ाती हैं [S2]।"
        ),
        [
            ("What does Gita 17.3 say about faith (Shraddha)?", "what"),
            ("What foods promote health and clarity according to the Gita?", "what"),
            ("Why do habits and faith shape who we become?", "why"),
            ("गीता के अनुसार श्रद्धा और सात्त्विक आहार का क्या महत्व है?", "what"),
        ],
    ),
    _topic(
        "knowledge_jnana",
        "bhagavad-gita",
        "True Knowledge, Humility, and Learning",
        "knowledge wisdom jnana humility learning teacher purity truth",
        ["bhagavad-gita_4_34", "bhagavad-gita_4_38", "bhagavad-gita_13_8"],
        (
            "In the Gita, nothing on earth purifies like genuine wisdom (Jnana) [S2], yet true knowledge begins with humility, unpretentiousness, patience, non-violence, and reverence [S3]—approaching wise teachers with sincere inquiry and service [S1]."
        ),
        (
            "Mere intellectual pride cannot transform behavior; real wisdom burns away delusion and brings deep inner peace [S2][S3]."
        ),
        (
            "Cultivate a humble learner's spirit—ask sincere questions without arrogance [S1], verify teachings through lived sincerity, and keep ethical restraint at the center [S3]."
        ),
        (
            "Humility and openness matter most when starting spiritual study or realizing we have outgrown ego-driven opinions [S1][S3]."
        ),
        (
            "Krishna praises wisdom in Gita 4.34 and 4.38 and defines the traits of knowledge in Chapter 13 (13.8 onward) [S1][S2][S3]."
        ),
        (
            "Sri Krishna points Arjuna toward realized seers who know the truth directly, emphasizing humility as the mark of wisdom [S1][S3]."
        ),
        (
            "इस संसार में ज्ञान के समान पवित्र करने वाला कोई दूसरा साधन नहीं है [S2]। "
            "सच्चा ज्ञान विनम्रता, अहिंसा, सरलता और श्रद्धापूर्वक जिज्ञासा से प्राप्त होता है [S1][S3]।"
        ),
        [
            ("What does the Gita say is true knowledge (Jnana)?", "what"),
            ("How should a student seek spiritual wisdom?", "how"),
            ("Why is humility listed first among traits of wisdom?", "why"),
            ("सच्चा ज्ञान क्या है और इसे प्राप्त करने की विधि क्या है?", "how"),
        ],
    ),
    _topic(
        "cosmic_form",
        "bhagavad-gita",
        "Vision of the Cosmic Form (Vishvarupa Darshan)",
        "vishvarupa cosmic form universal form chapter 11 krishna time kala",
        ["bhagavad-gita_11_12", "bhagavad-gita_11_32", "bhagavad-gita_11_54"],
        (
            "In the Vishvarupa Darshan, Arjuna beholds the entire cosmos shining within Krishna's boundless form—more brilliant than a thousand suns rising together [S1]. "
            "Krishna declares Himself as mighty Time (Kala) transforming worlds [S2], yet reminds Arjuna that only undivided devotion truly knows and enters Him [S3]."
        ),
        (
            "The Cosmic Form reveals that human life unfolds inside an immense sacred order, dissolving small-minded arrogance while highlighting devotion as the accessible path to truth [S1][S3]."
        ),
        (
            "Meet awe with humility and devotion rather than fear: remain an upright instrument of dharma while trusting the larger cosmic order [S2][S3]."
        ),
        (
            "This revelation takes place mid-dialogue in Bhagavad Gita Chapter 11 when Arjuna asks to see Krishna's universal reality directly [S1]."
        ),
        (
            "All of Bhagavad Gita Chapter 11 centers on the Vishvarupa Darshan, notably 11.12, 11.32, and 11.54 [S1][S2][S3]."
        ),
        (
            "Sri Krishna grants Arjuna divine sight (divya chakshus) to witness what ordinary eyes cannot bear to look upon [S1][S3]."
        ),
        (
            "अध्याय 11 में अर्जुन श्रीकृष्ण के विश्वरूप के दर्शन करते हैं, जिसका तेज एक साथ उदित हजारों सूर्यों के समान था [S1]। "
            "श्रीकृष्ण स्वयं को महाकाल बताते हैं, पर यह भी स्पष्ट करते हैं कि अनन्य भक्ति से ही उनका वास्तविक स्वरूप जाना जा सकता है [S2][S3]।"
        ),
        [
            ("What happened in the Vishvarupa Darshan in Chapter 11?", "what"),
            ("Why did Krishna say 'I am Time, destroyer of worlds'?", "why"),
            ("How can one know Krishna's cosmic form according to 11.54?", "how"),
            ("विश्वरूप दर्शन में अर्जुन ने क्या देखा और इसका क्या महत्व है?", "what"),
        ],
    ),
    _topic(
        "yada_yada_dharma",
        "bhagavad-gita",
        "Why Avatars Descend (Yada Yada Hi Dharmasya)",
        "yada yada avatar incarnation dharma protection renewal 4.7 4.8",
        ["bhagavad-gita_4_7", "bhagavad-gita_4_8"],
        (
            "In Bhagavad Gita 4.7-4.8, Krishna promises that whenever righteousness (dharma) declines and unrighteousness surges, He manifests Himself age after age to protect the good, curb destructive evil, and re-establish moral order [S1][S2]."
        ),
        (
            "This teaching offers enduring hope: cosmic justice is not absent, and periods of deep moral decay carry the seed of renewal and re-alignment with truth [S1][S2]."
        ),
        (
            "Stay committed to ethical integrity even when surrounding standards slip, aligning your own actions with protecting what is honest and compassionate [S1][S2]."
        ),
        (
            "Divine manifestation is spoken of whenever moral order reaches crisis across ages (yuga yuge) [S1][S2]."
        ),
        ("These famous verses sit at Bhagavad Gita Chapter 4 Verses 4.7 and 4.8 [S1][S2]."),
        (
            "Sri Krishna reveals the mystery of His divine incarnations directly to Arjuna while explaining how eternal Yoga persists through time [S1][S2]."
        ),
        (
            "यदा यदा हि धर्मस्य—जब-जब धर्म की हानि और अधर्म की वृद्धि होती है, तब-तब सज्जनों की रक्षा और धर्म की पुनः स्थापना के लिए ईश्वर युग-युग में अवतरित होते हैं [S1][S2]।"
        ),
        [
            ("What does Yada Yada Hi Dharmasya mean?", "what"),
            ("Why does God take avatar according to Gita 4.7 and 4.8?", "why"),
            ("Where in the Bhagavad Gita are the verses about avatars?", "where"),
            ("यदा यदा हि धर्मस्य श्लोक का अर्थ क्या है और अवतार क्यों होते हैं?", "why"),
        ],
    ),
    _topic(
        "senses_chariot",
        "bhagavad-gita",
        "Guarding the Senses and Awakening Discrimination",
        "senses intellect chariot self mastery hierarchy indriyas buddhi",
        ["bhagavad-gita_2_67", "bhagavad-gita_3_42", "bhagavad-gita_3_43"],
        (
            "Just as a gust of wind sweeps away a helpless boat at sea, letting the mind chase every wandering sense pulls away clear judgment [S1]. "
            "Krishna ranks the inner hierarchy: the mind stands higher than the senses, clear intellect higher than the mind, and the Self highest of all [S2][S3]."
        ),
        (
            "Without guidance from higher reason and Self-awareness, raw sensory impulses steer choices toward regret and inner restlessness [S1][S3]."
        ),
        (
            "Pause before acting on every immediate craving; use higher discernment (buddhi) rooted in the Self to guide the mind rather than letting scattered appetites lead [S2][S3]."
        ),
        (
            "Self-restraint over the senses matters daily whenever digital overload, distraction, or temptation clouds wiser judgment [S1][S3]."
        ),
        (
            "The boat analogy is in Gita 2.67, and the senses-mind-intellect-Self hierarchy closes Chapter 3 at 3.42-3.43 [S1][S2][S3]."
        ),
        (
            "Sri Krishna teaches Arjuna how to conquer desire by awakening strength higher than the restless mind [S2][S3]."
        ),
        (
            "जैसे जल में तेज हवा नाव को बहा ले जाती है, वैसे ही भटकती इंद्रियों के पीछे दौड़ता मन बुद्धि को हर लेता है [S1]। "
            "इंद्रियों से मन, मन से बुद्धि और बुद्धि से श्रेष्ठ आत्मा है—अतः बुद्धि और आत्मबल से इंद्रियों को वश में करना चाहिए [S2][S3]।"
        ),
        [
            ("Why does Gita 2.67 compare senses to wind sweeping a boat?", "why"),
            ("What is higher than the senses and mind in the Gita?", "what"),
            ("How do I discipline wandering senses and impulses?", "how"),
            ("इंद्रियों, मन और बुद्धि का सही नियंत्रण कैसे करें?", "how"),
        ],
    ),
    _topic(
        "steady_wisdom",
        "bhagavad-gita",
        "Person of Steady Wisdom (Sthitaprajna)",
        "sthitaprajna steady wisdom calm sage ocean desires peace",
        ["bhagavad-gita_2_55", "bhagavad-gita_2_56", "bhagavad-gita_2_70"],
        (
            "A person of steady wisdom (Sthitaprajna) lets go of selfish cravings, stays content within the Self, remains unshaken in adversity and ungrasping in comfort, and receives incoming experiences calmly like the ocean receiving rivers without overflowing [S1][S2][S3]."
        ),
        (
            "True maturity is measured not by avoiding challenges but by keeping peace and clear values when storms arrive [S2][S3]."
        ),
        (
            "Notice rising cravings gently without obeying every impulse [S1][S3], avoid feeding fear or anger, and return repeatedly to inner contentment [S2]."
        ),
        (
            "Arjuna specifically asks how a person of steady wisdom speaks, sits, and walks through everyday life—so these signs apply in ordinary routines [S1][S2]."
        ),
        (
            "The Sthitaprajna teaching spans Bhagavad Gita 2.54 through 2.72, highlighted in 2.55, 2.56, and 2.70 [S1][S2][S3]."
        ),
        (
            "Arjuna asks the question and Sri Krishna paints the portrait of inner emotional steadiness as the ideal of Gita wisdom [S1][S3]."
        ),
        (
            "स्थितप्रज्ञ वह व्यक्ति है जो मन की समस्त स्वार्थी कामनाओं को त्यागकर अपने भीतर ही संतुष्ट रहता है [S1]। "
            "वह दुःख में व्याकुल नहीं होता और सुख की ललक नहीं रखता—जिस प्रकार नदियाँ मिलने पर भी समुद्र शांत रहता है, वैसे ही वह स्थिर रहता है [S2][S3]।"
        ),
        [
            ("What are the qualities of a Sthitaprajna (steady wisdom)?", "what"),
            ("How does a wise person behave according to Gita Chapter 2?", "how"),
            ("Why is the steady sage compared to the ocean?", "why"),
            ("स्थितप्रज्ञ व्यक्ति के लक्षण क्या हैं?", "what"),
        ],
    ),
    _topic(
        "food_diet",
        "bhagavad-gita",
        "Yogic Moderation in Lifestyle and Diet",
        "moderation balance sleep food diet health habits lifestyle yoga",
        ["bhagavad-gita_6_17", "bhagavad-gita_17_8", "bhagavad-gita_17_9"],
        (
            "The Gita advocates sensible moderation rather than extremes: yoga removes sorrow for one who is balanced in eating, recreation, daily work, sleep, and wakefulness [S1]. "
            "Pure, fresh, nourishing foods sustain strength and calm joy, while overly harsh, bitter, or excessive foods cause distress [S2][S3]."
        ),
        (
            "Both self-indulgence and reckless deprivation exhaust the body and agitate the mind, making steady focus and serenity hard to sustain [S1][S3]."
        ),
        (
            "Keep regular hours for sleep and work [S1], choose wholesome foods that support vitality and mental clarity [S2], and avoid extremes of overeating or harsh fasting [S3]."
        ),
        (
            "Balance matters every day as the physical foundation for concentration, emotional poise, and spiritual consistency [S1]."
        ),
        (
            "Moderation in routine appears in Gita 6.17 and food qualities are detailed in Chapter 17 (17.8-17.9) [S1][S2][S3]."
        ),
        (
            "Sri Krishna lays down practical health and balance guidelines for practicing seekers and householders alike [S1][S2]."
        ),
        (
            "गीता अति नहीं बल्कि संतुलन सिखाती है—आहार, विहार, कर्म, निद्रा और जागरण में संयम रखने वाले का योग दुःखों को दूर करता है [S1]। "
            "सात्त्विक और ताजा भोजन आरोग्य व शांति बढ़ाता है, जबकि अति तीखा या उत्तेजक भोजन क्लेश पैदा करता है [S2][S3]।"
        ),
        [
            ("What does the Bhagavad Gita say about food, sleep, and moderation?", "what"),
            ("Why is balance better than extreme fasting in Yoga?", "why"),
            ("How should a seeker structure daily eating and rest?", "how"),
            ("गीता में आहार, निद्रा और संतुलित जीवनशैली के बारे में क्या कहा गया है?", "what"),
        ],
    ),
    _topic(
        "renunciation_tyaga",
        "bhagavad-gita",
        "Renunciation vs Giving Up Selfish Fruits (Sannyasa and Tyaga)",
        "renunciation sannyasa tyaga giving up fruits charity sacrifice penance",
        ["bhagavad-gita_18_2", "bhagavad-gita_18_11", "bhagavad-gita_5_2"],
        (
            "Krishna distinguishes Sannyasa (giving up desire-driven works) from Tyaga (giving up attachment to the results of every action) [S1]. "
            "Since embodied beings cannot stop acting altogether, the person who genuinely renounces outcomes is the true renunciate [S2], and Karma Yoga in everyday life stands on par with outward renunciation [S3]."
        ),
        (
            "Dropping responsibilities out of laziness or fear creates guilt and chaos rather than freedom; renouncing selfishness inside action sets the heart free [S2][S3]."
        ),
        (
            "Continue noble acts of generosity, duty, and self-care while deliberately letting go of entitlement and ego credit [S1][S2]."
        ),
        (
            "Understanding Tyaga helps whenever duties feel heavy and you confuse spiritual growth with walking away from commitments [S2][S3]."
        ),
        (
            "The distinction between Sannyasa and Tyaga opens Chapter 18 (18.2, 18.11) and echoes Chapter 5 (5.2) [S1][S2][S3]."
        ),
        (
            "Arjuna opens Chapter 18 by asking for the exact truth behind these two words, and Sri Krishna clarifies them side by side [S1][S2]."
        ),
        (
            "संन्यास काम्य कर्मों के त्याग को और त्याग सभी कर्मों के फल की आसक्ति छोड़ने को कहते हैं [S1]। "
            "शरीरधारी व्यक्ति कर्म पूरी तरह नहीं छोड़ सकता, इसलिए जो कर्मफल की चिंता त्यागता है वही सच्चा त्यागी है [S2][S3]।"
        ),
        [
            ("What is the difference between Sannyasa and Tyaga?", "what"),
            ("Why can nobody completely stop all action according to Gita 18.11?", "why"),
            ("How can a householder practice real renunciation?", "how"),
            ("संन्यास और त्याग में क्या अंतर है?", "what"),
        ],
    ),
    _topic(
        "work_as_worship",
        "bhagavad-gita",
        "Turning Everyday Work into Worship",
        "work worship offering dedication karma devotion excellence service",
        ["bhagavad-gita_9_27", "bhagavad-gita_18_46", "bhagavad-gita_3_30"],
        (
            "The Gita transforms ordinary daily activity into spiritual practice: whatever you do, eat, offer, give, or endure—offer it wholeheartedly to the Divine [S1]. "
            "Worshipping the Creator through your own dedicated work leads toward perfection [S2] when done with serene, focused attention [S3]."
        ),
        (
            "Separating 'spiritual time' from 'ordinary work' leaves most of the day feeling empty; seeing honest work as sacred service infuses every task with meaning and calm [S1][S2]."
        ),
        (
            "Dedicate your tasks at the start of the day, do your craft diligently with honesty, and lay aside fretful selfishness and complaint [S1][S3]."
        ),
        (
            "This teaching applies directly during busy workdays, household chores, studying, or community service when formal temple time is brief [S1][S2]."
        ),
        ("Work as worship stands out clearly in Gita 3.30, 9.27, and 18.46 [S1][S2][S3]."),
        (
            "Sri Krishna teaches Arjuna how ordinary human effort—whether statecraft, teaching, craft, or family care—becomes a path of worship [S1][S2]."
        ),
        (
            "जो कुछ भी तुम करते हो, खाते हो या दान देते हो, उसे ईश्वर को अर्पित कर देने से सामान्य कर्म भी पूजा बन जाता है [S1]। "
            "अपने स्वाभाविक कर्तव्य-कर्म के द्वारा परमेश्वर की आराधना करके मनुष्य सिद्धि प्राप्त करता है [S2][S3]।"
        ),
        [
            ("How can daily work or job become a form of worship?", "how"),
            ("What does Bhagavad Gita 9.27 and 18.46 teach about offering work?", "what"),
            ("Why does Krishna say performing your own duty worships God?", "why"),
            ("दैनिक कर्म को ईश्वर की पूजा कैसे बनाएं?", "how"),
        ],
    ),
    _topic(
        "compassion_love",
        "bhagavad-gita",
        "Compassion, Non-Hatred, and Seeing Oneness in All",
        "compassion empathy love universal oneness kindness brotherhood kindness",
        ["bhagavad-gita_12_13", "bhagavad-gita_12_14", "bhagavad-gita_6_29"],
        (
            "Spiritual realization expresses itself socially as deep goodwill: bearing hatred toward no creature, being friendly and compassionate, free from arrogance and possessiveness, and forgiving [S1][S2]. "
            "A harmonized seer sees the same divine Self dwelling equally in every being [S3]."
        ),
        (
            "Hatred and superiority divide the heart and blind us to shared humanity; seeing the Divine across all beings replaces cruelty with natural respect [S1][S3]."
        ),
        (
            "Practice friendliness and patience even toward difficult people, drop petty grudges quickly, and remember the shared Spirit inside everyone you meet [S1][S2][S3]."
        ),
        (
            "Compassion matters most when disagreements, envy, or prejudice tempt you toward harshness or division [S1][S3]."
        ),
        (
            "Oneness vision appears in Gita 6.29, and the portrait of a compassionate devotee shines in 12.13-12.14 [S1][S2][S3]."
        ),
        (
            "Sri Krishna describes these kind, steady devotees—free from malice and ego—as deeply beloved to Him [S1][S2]."
        ),
        (
            "किसी भी प्राणी से द्वेष न रखना, सबका मित्र और करुणावान होना, क्षमाशील तथा अहंकार से मुक्त रहना सच्चे भक्त के गुण हैं [S1][S2]। "
            "सच्चा योगी समस्त प्राणियों में एक ही परमात्मा का दर्शन करता है [S3]।"
        ),
        [
            ("What does the Bhagavad Gita teach about compassion and kindness?", "what"),
            ("How does spiritual wisdom change the way we treat others?", "how"),
            ("Why does Gita 12.13 begin with 'bearing hatred toward no being'?", "why"),
            ("गीता में करुणा, मैत्री और समदृष्टि के बारे में क्या बताया गया है?", "what"),
        ],
    ),
    _topic(
        "moksha_liberation",
        "bhagavad-gita",
        "Liberation (Moksha) and Ultimate Freedom",
        "moksha liberation freedom nirvana peace final goal salvation",
        ["bhagavad-gita_8_5", "bhagavad-gita_18_65", "bhagavad-gita_18_66"],
        (
            "Moksha in the Gita is complete freedom from ignorance, sorrow, and repeated bondage, reached by remembering the Divine steadily throughout life and at the final moment [S1], loving devotion, humility [S2], and trusting surrender [S3]."
        ),
        (
            "Liberation is the ultimate fruit of wisdom and devotion—ending the restless cycle of fear and rebirth in lasting union with the Supreme [S1][S3]."
        ),
        (
            "Do not wait for a distant hour: cultivate constant remembrance, honest work, loving devotion, and humble surrender right now [S1][S2][S3]."
        ),
        (
            "Remembering the highest truth shapes how you live every day and steadies the heart at life's final transition [S1]."
        ),
        (
            "The path to liberation runs across the Gita, culminating in Chapter 8 (8.5) and Chapter 18 (18.65-18.66) [S1][S2][S3]."
        ),
        (
            "Sri Krishna assures Arjuna unequivocally that steady remembrance and devotion bring the seeker home to Him [S2][S3]."
        ),
        (
            "मोक्ष अज्ञान, दुःख और जन्म-मरण के बंधन से पूर्ण मुक्ति है [S3]। "
            "निरंतर ईश्वर स्मरण, अनन्य भक्ति और पूर्ण शरणागति के द्वारा मनुष्य परम शांति और मुक्ति को प्राप्त होता है [S1][S2][S3]।"
        ),
        [
            ("What is Moksha and how is it attained in the Bhagavad Gita?", "what"),
            ("Why does Gita 8.5 stress thoughts at the time of death?", "why"),
            ("How does Krishna conclude the Gita's path to liberation?", "how"),
            ("मोक्ष क्या है और गीता के अनुसार मुक्ति कैसे मिलती है?", "what"),
        ],
    ),
    _topic(
        "ramayana_overview",
        "valmiki-ramayana",
        "Core Message of the Valmiki Ramayana",
        "valmiki ramayana overview dharma epic valmiki narada ideal story",
        ["valmiki-ramayana_1_1_1", "valmiki-ramayana_1_1_18"],
        (
            "The Valmiki Ramayana opens with Sage Valmiki asking Narada whether any living person embodies courage, righteousness, gratitude, truthfulness, and compassion for all beings—and Narada answers with the life of Sri Rama [S1][S2]."
        ),
        (
            "Through vivid family, friendship, exile, and war narratives, the epic demonstrates how steadfast dharma looks inside real human relationships and difficult dilemmas [S1][S2]."
        ),
        (
            "Read the Ramayana not just as history or adventure, but by watching how Rama, Sita, Lakshmana, Bharata, and Hanuman honor promises, loyalty, and duty under hardship [S1][S2]."
        ),
        (
            "The epic begins at Valmiki's hermitage with Narada's brief retelling before unfolding across all seven Kandas [S1]."
        ),
        (
            "Valmiki's opening inquiry and Narada's answer set the theme right in Bala Kanda, Sarga 1 [S1][S2]."
        ),
        (
            "Sage Valmiki composes the Adi Kavya after hearing the ideal virtues of Rama from the wandering sage Narada [S1][S2]."
        ),
        (
            "वाल्मीकि रामायण का आरंभ महर्षि वाल्मीकि द्वारा नारद मुनि से एक ऐसे आदर्श, सत्यवादी, धैर्यवान और धर्मपरायण व्यक्ति के बारे में पूछने से होता है [S1]। "
            "नारद जी श्रीराम के आदर्श चरित्र और धर्मपालन की कथा सुनाते हैं [S2]।"
        ),
        [
            ("What is the Valmiki Ramayana mainly about?", "what"),
            ("Why did Sage Valmiki ask Narada about an ideal human being?", "why"),
            ("Who inspired Valmiki to compose the Ramayana?", "who"),
            ("वाल्मीकि रामायण की मुख्य कथा और संदेश क्या है?", "what"),
        ],
    ),
    _topic(
        "rama_character",
        "valmiki-ramayana",
        "Ideal Virtues of Lord Rama",
        "lord rama character virtues maryada purushottam qualities leadership dharma",
        ["valmiki-ramayana_1_1_8", "valmiki-ramayana_2_1_10"],
        (
            "Valmiki portrays Sri Rama as courageous yet gentle, truthful in every pledge, deeply learned, respectful toward elders, protective of refugees, and steady in both royal triumph and forest exile [S1][S2]."
        ),
        (
            "Rama's character sets a human standard (Maryada Purushottama): strength without cruelty, power without arrogance, and loyalty that never bends to convenience [S1][S2]."
        ),
        (
            "Follow Rama's example by keeping your word even when costly, listening calmly to differing views, and staying courteous under provocation [S1][S2]."
        ),
        (
            "Rama's virtues shine clearest in Bala Kanda's opening summary and when the citizens of Ayodhya celebrate his suitability as crown prince in Ayodhya Kanda [S1][S2]."
        ),
        (
            "Detailed portraits of Rama's character open Bala Kanda 1.1 and Ayodhya Kanda 2.1 [S1][S2]."
        ),
        (
            "Narada first enumerates Rama's sixteen-plus noble qualities to Valmiki, and citizens across Ayodhya confirm them from lived experience [S1][S2]."
        ),
        (
            "श्रीराम को वाल्मीकि रामायण में सत्यनिष्ठ, धैर्यवान, पराक्रमी, विनम्र, प्रजावत्सल और शरण में आए व्यक्ति की रक्षा करने वाले आदर्श पुरुष के रूप में वर्णित किया गया है [S1][S2]।"
        ),
        [
            ("What were the key qualities of Lord Rama in Valmiki Ramayana?", "what"),
            ("Why is Rama called an ideal leader and son?", "why"),
            ("Where are Rama's sixteen virtues listed in the Ramayana?", "where"),
            ("भगवान राम के प्रमुख गुण और आदर्श चरित्र कैसा था?", "what"),
        ],
    ),
    _topic(
        "rama_exile",
        "valmiki-ramayana",
        "Why Rama Accepted Fourteen Years of Exile",
        "rama exile vanvas dasharatha kaikeyi promise father ayodhya",
        ["valmiki-ramayana_2_18_1", "valmiki-ramayana_2_19_1"],
        (
            "Rama accepted fourteen years of forest exile rather than allowing King Dasharatha's solemn promise to Queen Kaikeyi to become false [S1]. "
            "Without bitterness or delay, Rama prepared cheerfully to uphold his father's honor and family peace [S2]."
        ),
        (
            "In Ayodhya Kanda, truthfulness and honoring a parent's sacred vow outweighed the allure of a royal throne; Rama refused to fight his father's word even though the kingdom stood behind him [S1][S2]."
        ),
        (
            "Observe Rama's poise: respond to sudden injustice or lost plans with dignity, integrity, and concern for others' pain rather than reactive anger [S1][S2]."
        ),
        (
            "This turning point occurs on the very morning scheduled for Rama's royal coronation in Ayodhya Kanda [S1][S2]."
        ),
        (
            "Kaikeyi announces the boons and Rama embraces exile in Ayodhya Kanda, Sargas 18 and 19 [S1][S2]."
        ),
        (
            "Queen Kaikeyi invoked two old boons granted by King Dasharatha to exile Rama and crown Bharata, and Rama calmly honored the pledge [S1][S2]."
        ),
        (
            "राजा दशरथ के कैकेयी को दिए गए वचन की रक्षा और पिता के सत्य की मर्यादा बनाए रखने के लिए श्रीराम ने बिना किसी क्रोध या संकोच के 14 वर्ष का वनवास स्वीकार किया [S1][S2]।"
        ),
        [
            ("Why did Lord Rama go into exile for 14 years?", "why"),
            ("How did Rama react when Kaikeyi asked for his exile?", "how"),
            ("When and where did Rama learn about his exile?", "when"),
            ("श्रीराम ने 14 वर्ष का वनवास क्यों और कैसे स्वीकार किया?", "why"),
        ],
    ),
    _topic(
        "sita_devotion",
        "valmiki-ramayana",
        "Devi Sita's Courage, Steadfastness, and Strength",
        "sita devi ashoka vatika strength courage devotion dharma endurance",
        ["valmiki-ramayana_2_27_1", "valmiki-ramayana_5_24_1"],
        (
            "Devi Sita shines in the Ramayana as a pillar of inner strength and moral clarity: she fearlessly insists on walking into forest exile beside Rama [S1] and refuses every threat and temptation of Ravana during captivity in Lanka [S2]."
        ),
        (
            "Sita demonstrates that quiet loyalty, dignity under captivity, and unbroken self-respect carry greater force than armies or royal threats [S1][S2]."
        ),
        (
            "Learn from Sita how to protect inner dignity and refuse compromise on core values even when isolated or pressured by fear [S1][S2]."
        ),
        (
            "Sita proves her resolve both at the start of the forest exile in Ayodhya and throughout her captivity in Lanka's Ashoka Grove [S1][S2]."
        ),
        (
            "Look to Ayodhya Kanda Sarga 27 for Sita's stand to join Rama, and Sundara Kanda Sargas 15-24 for her steadfastness in Lanka [S1][S2]."
        ),
        (
            "Devi Sita answers Rama's concerns in Ayodhya with reasoned courage and answers Ravana's intimidation in Lanka with unbending truth [S1][S2]."
        ),
        (
            "माता सीता का चरित्र असीम धैर्य, निर्भयता और मर्यादा का प्रतीक है—वनवास में श्रीराम का साथ निभाने से लेकर अशोक वाटिका में रावण के भय और प्रलोभन को ठुकराने तक वे अडिग रहीं [S1][S2]।"
        ),
        [
            ("What does Devi Sita teach about strength and devotion?", "what"),
            ("Why did Sita insist on accompanying Rama to the forest?", "why"),
            ("How did Sita resist Ravana in Ashoka Vatika?", "how"),
            ("माता सीता के चरित्र और धैर्य से हमें क्या सीख मिलती है?", "what"),
        ],
    ),
    _topic(
        "hanuman_courage",
        "valmiki-ramayana",
        "Hanuman's Courage and Wisdom in Sundara Kanda",
        "hanuman sundara kanda lanka leap courage devotion humility service",
        ["valmiki-ramayana_5_1_1", "valmiki-ramayana_5_15_1"],
        (
            "Sundara Kanda showcases Hanuman crossing the vast ocean to Lanka with focused determination [S1], searching diligently through danger until he locates Devi Sita in Ashoka Vatika and restores her hope [S2]."
        ),
        (
            "Hanuman combines mighty strength with sharp presence of mind and utter humility—serving without seeking personal fame [S1][S2]."
        ),
        (
            "Approach intimidating challenges the Hanuman way: bow mentally in humility, stay observant under pressure, adapt wisely, and serve the mission to completion [S1][S2]."
        ),
        (
            "Hanuman undertakes this mission once the southern search party discovers Sita was carried across the sea to Lanka [S1]."
        ),
        (
            "These feats unfold across Sundara Kanda, opening with the ocean leap in Sarga 1 and finding Sita in Sarga 15 [S1][S2]."
        ),
        (
            "Sri Hanuman—son of Vayu and faithful servant of Rama—carries out this single-handed mission to Lanka [S1][S2]."
        ),
        (
            "सुन्दरकाण्ड में हनुमान जी असीम साहस और भक्ति के साथ समुद्र लांघकर लंका पहुँचते हैं और कठिन परिस्थितियों में माता सीता को खोजकर श्रीराम का संदेश देते हैं [S1][S2]। "
            "वे शक्ति और विनम्रता का अद्वितीय संगम हैं।"
        ),
        [
            ("What does Sundara Kanda teach about Hanuman's courage?", "what"),
            ("How did Hanuman find Sita in Lanka?", "how"),
            ("Why is Sundara Kanda considered so auspicious and inspiring?", "why"),
            ("सुन्दरकाण्ड में हनुमान जी के साहस और भक्ति से क्या शिक्षा मिलती है?", "what"),
        ],
    ),
    _topic(
        "hanuman_jambavan",
        "valmiki-ramayana",
        "Overcoming Self-Doubt (Jambavan Reminding Hanuman)",
        "jambavan hanuman self doubt potential confidence forgetting strength leap",
        ["valmiki-ramayana_4_66_1", "valmiki-ramayana_5_1_1"],
        (
            "When the vanara search team reaches the southern seashore and despairs over crossing the ocean, wise elder Jambavan reminds a silent Hanuman of his forgotten divine strength [S1], inspiring Hanuman's victorious leap to Lanka [S2]."
        ),
        (
            "Self-doubt often hides real capability until a wise mentor reminds us who we are and urges us to rise for a higher purpose [S1][S2]."
        ),
        (
            "When feeling inadequate before an overwhelming challenge, seek steady counsel, remember past resilience, and take the first decisive step forward [S1][S2]."
        ),
        (
            "This turning point takes place at the climax of Kishkindha Kanda right before Sundara Kanda begins [S1][S2]."
        ),
        (
            "Jambavan's rousing counsel stands at Kishkindha Kanda Sarga 66, flowing directly into Sundara Kanda Sarga 1 [S1][S2]."
        ),
        (
            "Bear-king Jambavan awakens Hanuman's confidence, transforming despair among the searchers into unstoppable resolve [S1][S2]."
        ),
        (
            "समुद्र तट पर जब सब वानर निराश हो गए, तब बुद्धिमान जाम्बवन्त ने हनुमान जी को उनकी भूली हुई असीम शक्तियों का स्मरण कराया [S1]। "
            "इससे आत्म-संदेह समाप्त हुआ और हनुमान जी ने लंका की ओर छलांग लगाई [S2]।"
        ),
        [
            ("How did Jambavan help Hanuman overcome self-doubt?", "how"),
            ("Why had Hanuman forgotten his own strength?", "why"),
            ("Where does Jambavan encourage Hanuman in the Ramayana?", "where"),
            ("जाम्बवन्त ने हनुमान जी को उनकी शक्ति कैसे याद दिलाई?", "how"),
        ],
    ),
    _topic(
        "bharata_devotion",
        "valmiki-ramayana",
        "Bharata's Brotherly Love and Renunciation (Paduka Rule)",
        "bharata paduka sandals brother love renunciation chitrakuta ayodhya throne",
        ["valmiki-ramayana_2_112_1", "valmiki-ramayana_2_115_1"],
        (
            "Rather than enjoying the throne secured by Kaikeyi, Bharata rejects kingship, journeys into the forest to beg Rama to return, and finally places Rama's wooden sandals (padukas) on the throne [S1], ruling only as a humble caretaker outside Ayodhya at Nandigrama [S2]."
        ),
        (
            "Bharata sets the supreme example of unselfish brotherhood and trusteeship: holding authority in trust rather than grabbing power at a loved one's expense [S1][S2]."
        ),
        (
            "Refuse unfair advantage gained at someone else's hurt, honor legitimate trust with austerity and diligence, and put harmony above ambition [S1][S2]."
        ),
        (
            "This unfolds soon after King Dasharatha's passing when Bharata visits Chitrakuta and returns to Nandigrama for fourteen years [S1][S2]."
        ),
        (
            "Bharata receives the padukas and serves from Nandigrama in Ayodhya Kanda Sargas 112 and 115 [S1][S2]."
        ),
        (
            "Prince Bharata—younger brother of Sri Rama and son of Kaikeyi—turns away a kingdom out of love and integrity [S1][S2]."
        ),
        (
            "भरत ने अन्याय से मिले सिंहासन को अस्वीकार कर दिया और चित्रकूट जाकर श्रीराम की पादुकाएं ले आए [S1]। "
            "चौदह वर्ष तक उन्होंने स्वयं तपस्वी जैसा जीवन जीते हुए नंदिग्राम से राम-पादुका के सेवक बनकर राज्य संभाला [S2]।"
        ),
        [
            ("Why did Bharata place Rama's padukas on the throne?", "why"),
            ("What does Bharata teach about brotherly love and greed?", "what"),
            ("Where did Bharata stay while ruling as caretaker for 14 years?", "where"),
            ("भरत ने श्रीराम की पादुकाएं सिंहासन पर क्यों रखीं?", "why"),
        ],
    ),
    _topic(
        "lakshmana_service",
        "valmiki-ramayana",
        "Lakshmana's Selfless Service and Loyalty",
        "lakshmana service devotion loyalty brother forest exile panchavati protection",
        ["valmiki-ramayana_2_31_1", "valmiki-ramayana_3_15_1"],
        (
            "Lakshmana gives up palace comfort without hesitation to guard and serve Rama and Sita throughout all fourteen years of forest exile [S1], building peaceful dwellings like their hermitage at Panchavati [S2]."
        ),
        (
            "Lakshmana embodies protective love and silent vigilance—putting another's safety and peace ahead of personal rest or recognition [S1][S2]."
        ),
        (
            "Practice steady, unboastful loyalty toward those who depend on you, supporting good causes calmly through quiet everyday care [S1][S2]."
        ),
        (
            "Lakshmana requests to join the exile right as Rama prepares to depart Ayodhya and remains devoted through Aranya Kanda and Yuddha Kanda [S1][S2]."
        ),
        (
            "His vow to serve Rama appears in Ayodhya Kanda Sarga 31 and his quiet care at Panchavati in Aranya Kanda Sarga 15 [S1][S2]."
        ),
        (
            "Prince Lakshmana—twin brother of Shatrughna and devoted younger brother of Sri Rama—stays at Rama's side day and night [S1][S2]."
        ),
        (
            "लक्ष्मण जी ने बिना किसी स्वार्थ के राजसुख त्यागकर चौदह वर्षों तक वन में श्रीराम और माता सीता की सेवा और रक्षा की [S1][S2]। "
            "उनका जीवन निःस्वार्थ सेवा और निष्ठा का आदर्श है।"
        ),
        [
            ("What does Lakshmana teach about loyalty and selfless service?", "what"),
            ("Why did Lakshmana insist on going to the forest with Rama?", "why"),
            ("Where did Lakshmana build Rama and Sita's forest cottage?", "where"),
            ("लक्ष्मण जी की सेवा और निष्ठा से हमें क्या प्रेरणा मिलती है?", "what"),
        ],
    ),
    _topic(
        "vibhishana_sharanagati",
        "valmiki-ramayana",
        "Vibhishana Seeking Refuge (Standing for Truth Against Family Pressure)",
        "vibhishana sharanagati refuge lanka ravana brother truth ethics",
        ["valmiki-ramayana_6_17_1", "valmiki-ramayana_6_18_1"],
        (
            "When Ravana spurned repeated counsel to return Sita, Vibhishana crossed the ocean to seek refuge with Rama [S1]. "
            "Despite mixed advice from his council, Rama famously declared he never turns away anyone who seeks shelter in good faith [S2]."
        ),
        (
            "Vibhishana shows the courage to choose truth over tribal loyalty when kin persist in injustice, while Rama demonstrates boundless grace toward sincere refugees [S1][S2]."
        ),
        (
            "Speak truth respectfully to those close to you first; if harm continues, stand with righteousness cleanly, and meet sincerity in others with welcome [S1][S2]."
        ),
        (
            "This pivotal reception happens on the shoreline before the army marches across the sea to Lanka [S1][S2]."
        ),
        (
            "Vibhishana's arrival and Rama's vow of refuge occupy Yuddha Kanda Sargas 17 and 18 [S1][S2]."
        ),
        (
            "Vibhishana, Ravana's righteous younger brother, asks for shelter and is welcomed warmly by Sri Rama over Sugriva's initial caution [S1][S2]."
        ),
        (
            "असत्य का साथ न देकर विभीषण ने श्रीराम की शरण ली [S1]। "
            "श्रीराम ने अभयदान देते हुए घोषित किया कि सच्चे मन से शरण में आए हर व्यक्ति की रक्षा करना उनका परम धर्म है [S2]।"
        ),
        [
            ("Why did Vibhishana leave Ravana and join Lord Rama?", "why"),
            ("What did Rama promise about anyone seeking refuge (Sharanagati)?", "what"),
            ("Where in Yuddha Kanda does Rama accept Vibhishana?", "where"),
            ("विभीषण ने रावण को छोड़कर श्रीराम की शरण क्यों ली?", "why"),
        ],
    ),
    _topic(
        "jatayu_sacrifice",
        "valmiki-ramayana",
        "Jatayu's Heroic Sacrifice Against Injustice",
        "jatayu sacrifice bird protection courage rescue age old dharma",
        ["valmiki-ramayana_3_50_1", "valmiki-ramayana_3_68_1"],
        (
            "Despite being aged and unarmed against Ravana's celestial chariot, noble vulture-king Jatayu fiercely fought Ravana in midair to save Sita [S1], surviving on sheer willpower just long enough to inform Rama before dying in Rama's arms [S2]."
        ),
        (
            "Jatayu proves that defending the vulnerable does not depend on winning easily or being young and strong—courage lies in refusing to look away from evil [S1][S2]."
        ),
        (
            "Stand up for someone being wronged within the measure of your strength, caring more about honor and compassion than guaranteed victory [S1][S2]."
        ),
        (
            "Jatayu intervenes during Sita's abduction in Dandakaranya and meets Rama shortly afterward [S1][S2]."
        ),
        (
            "Jatayu battles Ravana in Aranya Kanda Sarga 50 and passes away blessed by Rama in Sarga 68 [S1][S2]."
        ),
        (
            "Venerable Jatayu, old friend of King Dasharatha, gives his life defending Devi Sita and receives final rites from Rama himself [S1][S2]."
        ),
        (
            "वृद्ध होने पर भी पक्षीराज जटायु ने माता सीता की रक्षा के लिए रावण से भयंकर युद्ध किया और प्राण न्योछावर कर दिए [S1]। "
            "मृत्यु से पूर्व उन्होंने श्रीराम को दिशा बताई और श्रीराम के हाथों सद्गति पाई [S2]।"
        ),
        [
            ("Who was Jatayu and what did he sacrifice?", "who"),
            ("Why did old Jatayu fight mighty Ravana alone?", "why"),
            ("Where did Rama meet and honor the dying Jatayu?", "where"),
            ("जटायु कौन थे और उनके बलिदान से हमें क्या सीख मिलती है?", "who"),
        ],
    ),
    _topic(
        "shabari_devotion",
        "valmiki-ramayana",
        "Shabari's Pure Devotion",
        "shabari berries bhakti devotion humility forest ascetic pampa",
        ["valmiki-ramayana_3_74_1"],
        (
            "Elderly ascetic Shabari waited faithfully in her forest hermitage by Pampa Lake for Rama's visit, honoring him with simple forest fruits and unwavering love [S1]. "
            "Rama warmly accepted her heartfelt offering, blessing her lifelong devotion [S1]."
        ),
        (
            "Shabari shows that simple sincerity, patience, and pure love matter infinitely more to the Divine than social status, wealth, or grandeur [S1]."
        ),
        (
            "Offer your modest best with sincerity and quiet patience—never let external simplicity make you doubt the worth of your devotion [S1]."
        ),
        (
            "Rama and Lakshmana visit Shabari's peaceful ashram near Lake Pampa shortly before entering Rishyamuka to meet Hanuman and Sugriva [S1]."
        ),
        ("Shabari's meeting with Rama appears in Aranya Kanda Sarga 74 [S1]."),
        (
            "Mata Shabari—disciple of Sage Matanga—welcomes Sri Rama and Lakshmana with humble offerings [S1]."
        ),
        (
            "पंपा सरोवर के पास वृद्धा तपस्विनी शबरी ने वर्षों तक अटूट विश्वास और प्रेम से श्रीराम की प्रतीक्षा की और वन के साधारण फल अर्पित किए [S1]। "
            "श्रीराम ने उनकी शुद्ध भक्ति को बड़े आदर से स्वीकार किया।"
        ),
        [
            ("What does Shabari's story in the Ramayana teach?", "what"),
            ("Why was Rama deeply pleased with Shabari's humble offering?", "why"),
            ("Where in Aranya Kanda is Shabari mentioned?", "where"),
            ("शबरी की भक्ति से हमें क्या शिक्षा मिलती है?", "what"),
        ],
    ),
    _topic(
        "sugriva_friendship",
        "valmiki-ramayana",
        "True Friendship and Mutual Support (Rama and Sugriva)",
        "sugriva friendship alliance help trust loyalty promise rishyamuka",
        ["valmiki-ramayana_4_5_1", "valmiki-ramayana_4_8_1"],
        (
            "Meeting beside the sacred fire on Rishyamuka, Rama and exiled vanara leader Sugriva forge a bond of true friendship—promising to stand together in both sorrow and joy [S1][S2]."
        ),
        (
            "True friendship in the Ramayana means showing up practically during someone's darkest hour and keeping pledges without hesitation [S1][S2]."
        ),
        (
            "Be a friend whose word stays solid under pressure—share burdens practically rather than offering empty sympathy [S1][S2]."
        ),
        (
            "Their alliance begins when both Rama and Sugriva have lost kingdoms and loved ones and unite for justice [S1][S2]."
        ),
        (
            "The friendship pledge between Rama and Sugriva stands in Kishkindha Kanda Sargas 5 and 8 [S1][S2]."
        ),
        (
            "Sri Hanuman introduces Sri Rama and Sugriva, establishing an alliance that leads to finding Sita [S1][S2]."
        ),
        (
            "ऋष्यमूक पर्वत पर अग्नि को साक्षी मानकर श्रीराम और सुग्रीव ने सच्ची मित्रता निभाई—एक-दूसरे के दुःख को अपना मानकर संकट में साथ दिया [S1][S2]।"
        ),
        [
            ("What does the friendship of Rama and Sugriva teach?", "what"),
            ("How did Rama and Sugriva become allies?", "how"),
            ("Where in Kishkindha Kanda do Rama and Sugriva form friendship?", "where"),
            ("श्रीराम और सुग्रीव की मित्रता से क्या सीख मिलती है?", "what"),
        ],
    ),
    _topic(
        "ravana_hubris",
        "valmiki-ramayana",
        "Lessons from Ravana's Pride and Downfall",
        "ravana pride ego hubris downfall counsel arrogance power warning",
        ["valmiki-ramayana_5_21_1", "valmiki-ramayana_6_109_1"],
        (
            "Despite vast learning, strength, and wealth, Ravana brought ruin upon Lanka by letting lust and arrogance silence every wise counselor—including his own wife Mandodari, brother Vibhishana, and captured Sita's warnings [S1][S2]."
        ),
        (
            "Ravana's tragedy warns that great intelligence and power become destructive whenever ego refuses correction and treats others as objects [S1][S2]."
        ),
        (
            "Keep trusted advisors who speak honest truth rather than yes-men, respect boundaries, and conquer arrogance before pride conquers your wisdom [S1][S2]."
        ),
        (
            "Ravana rejects Sita's righteous warning in Ashoka Vatika and continues fighting until his fall in Yuddha Kanda [S1][S2]."
        ),
        (
            "Notice Sita's firm counsel in Sundara Kanda 5.21 and the climax of the battle in Yuddha Kanda 6.109 [S1][S2]."
        ),
        (
            "King Ravana of Lanka—though learned and mighty—falls at Rama's hands through unrepentant ego and injustice [S1][S2]."
        ),
        (
            "प्रकांड विद्वान और शक्तिशाली होने के बावजूद रावण अपने अहंकार, लालसा और शुभचिंतकों की सलाह ठुकराने के कारण नष्ट हुआ [S1][S2]। "
            "यह सिखाता है कि अहंकार बड़ी से बड़ी शक्ति का भी पतन कर देता है।"
        ),
        [
            ("Why did mighty and learned Ravana fall?", "why"),
            ("What does Ravana's story warn us about ego and pride?", "what"),
            ("Where in the Ramayana is Ravana defeated?", "where"),
            ("रावण के पतन से हमें अहंकार के बारे में क्या शिक्षा मिलती है?", "why"),
        ],
    ),
    _topic(
        "sita_swayamvara",
        "valmiki-ramayana",
        "Sita Swayamvara and Breaking Shiva's Bow",
        "sita swayamvara marriage shiva bow janaka mithila bala kanda",
        ["valmiki-ramayana_1_67_1", "valmiki-ramayana_1_73_1"],
        (
            "In King Janaka's Mithila, where great kings failed even to lift Shiva's mighty bow, young Sri Rama effortlessly strung and snapped it, winning Sita's hand [S1] in a sacred marriage uniting Ayodhya and Mithila [S2]."
        ),
        (
            "Calm inner power accomplishes effortlessly what anxious pride fails to move, cementing a bond built on virtue and dharma [S1][S2]."
        ),
        (
            "Approach big tests with calm humility and preparedness rather than boasting—let steady skill speak for itself [S1]."
        ),
        (
            "This celebrated episode takes place during Rama and Lakshmana's journey with Sage Vishwamitra before returning to Ayodhya [S1][S2]."
        ),
        (
            "The bow-breaking and wedding appear near the close of Bala Kanda in Sargas 67 and 73 [S1][S2]."
        ),
        (
            "King Janaka honors Sage Vishwamitra and welcomes Sri Rama, uniting Rama with Sita in sacred matrimony [S1][S2]."
        ),
        (
            "मिथिला में राजा जनक की प्रतिज्ञा के अनुसार श्रीराम ने भगवान शिव का विशाल धनुष सहजता से भंग किया और माता सीता से उनका पाणिग्रहण हुआ [S1][S2]।"
        ),
        [
            ("How did Lord Rama win Sita's hand in Mithila?", "how"),
            ("Where is Sita Swayamvara described in Valmiki Ramayana?", "where"),
            ("Who brought Rama to Mithila for breaking Shiva's bow?", "who"),
            ("सीता स्वयंवर और शिव धनुष भंग की कथा क्या है?", "what"),
        ],
    ),
    _topic(
        "golden_deer_maya",
        "valmiki-ramayana",
        "The Golden Deer and Deceptive Appearances (Maricha Maya)",
        "golden deer maricha illusion maya temptation aranya kanda warning",
        ["valmiki-ramayana_3_43_1", "valmiki-ramayana_3_44_1"],
        (
            "Demon Maricha disguises himself as an enchanting golden deer outside Panchavati, luring Rama into a chase [S1][S2] and mimicking Rama's voice in distress to pull Lakshmana away before Ravana abducts Sita."
        ),
        (
            "The golden deer illustrates how glamorous illusions (maya) can draw careful people away from safety when desire overrides discernment [S1][S2]."
        ),
        (
            "Be skeptical of things that look unnaturally dazzling or urgent; check discernment and keep clear boundaries before abandoning steady ground [S1][S2]."
        ),
        (
            "This trap unfolds in the peaceful forest at Panchavati shortly before Ravana's deception [S1][S2]."
        ),
        (
            "The appearance and pursuit of the golden deer are told in Aranya Kanda Sargas 43 and 44 [S1][S2]."
        ),
        (
            "Maricha plays the illusory deer at Ravana's command, separating Rama and Lakshmana from Sita [S1][S2]."
        ),
        (
            "मायावी मारीच सोने के मृग का रूप धरकर पंचवटी आया और श्रीराम तथा लक्ष्मण को कुटिया से दूर ले गया [S1][S2]। "
            "यह प्रसंग सिखाता है कि चमक-दमक वाले प्रलोभन और माया के प्रति सदैव सावधान रहना चाहिए।"
        ),
        [
            ("What does the golden deer episode teach in Ramayana?", "what"),
            ("Who disguised himself as the golden deer?", "who"),
            ("Why did Maricha take the form of a golden deer?", "why"),
            ("स्वर्ण मृग की घटना रामायण में क्या चेतावनी देती है?", "what"),
        ],
    ),
    _topic(
        "rama_setu",
        "valmiki-ramayana",
        "Building the Bridge Across the Ocean (Nala Setu / Rama Setu)",
        "rama setu bridge ocean lanka nala teamwork collective effort yuddha",
        ["valmiki-ramayana_6_22_1"],
        (
            "When Samudra counsels Rama to bridge the ocean, engineer Nala—son of Vishwakarma—leads the vanara army in building the great stone causeway across the sea to Lanka in just five days [S1]."
        ),
        (
            "Building Rama Setu demonstrates what disciplined teamwork, humble engineering skill, and shared devotion achieve against seemingly impossible natural barriers [S1]."
        ),
        (
            "Respect every person's genuine skill in a team and tackle vast challenges stone by stone rather than giving up at the shoreline [S1]."
        ),
        (
            "This collective construction occurs immediately after Rama calms the ocean at the edge of Lanka's crossing [S1]."
        ),
        ("The construction of the great bridge is described in Yuddha Kanda Sarga 22 [S1]."),
        (
            "Vanara architect Nala guides the army under Sri Rama's supervision while Samudra holds the waves steady [S1]."
        ),
        (
            "नल के नेतृत्व में वानर सेना ने परिश्रम और टीम-भावना से समुद्र पर सेतु निर्माण किया, जिससे सेना लंका पहुँच सकी [S1]। "
            "यह प्रसंग सामूहिक प्रयास और धैर्य की शक्ति दिखाता है।"
        ),
        [
            ("Who built Rama Setu across the ocean in the Ramayana?", "who"),
            ("How did the vanara army cross the sea to Lanka?", "how"),
            ("Where is the building of Rama Setu described?", "where"),
            ("राम सेतु का निर्माण किसने और कैसे किया था?", "how"),
        ],
    ),
    _topic(
        "vishnu_creation",
        "vishnu-purana",
        "Creation of the Cosmos in the Vishnu Purana",
        "vishnu purana creation universe cosmos brahma prakriti purusha time origins",
        ["vishnu-purana_1_2_1", "vishnu-purana_1_4_1"],
        (
            "The Vishnu Purana presents Vishnu as the supreme source, sustainer, and underlying reality behind Prakriti (cosmic matter), Purusha (spirit), and Time (Kala), out of which Brahma unfolds worlds and Vishnu in Varaha form raises the earth from cosmic waters [S1][S2]."
        ),
        (
            "Seeing creation as infused with one sacred presence cultivates reverence for the natural world and perspective on cosmic time cycles [S1][S2]."
        ),
        (
            "Study the opening creation chapters with contemplative wonder—seeing matter, living intelligence, and time working within divine order rather than chaos [S1][S2]."
        ),
        (
            "Parashara narrates cosmic creation at the dawn of each cosmic cycle (Kalpa) in answer to Maitreya's opening questions [S1][S2]."
        ),
        ("Creation cosmology anchors Vishnu Purana Part 1, notably Sections 2 and 4 [S1][S2]."),
        (
            "Sage Parashara teaches his disciple Maitreya how Vishnu guides cosmic manifestation and rescue of the earth [S1][S2]."
        ),
        (
            "विष्णु पुराण के अनुसार भगवान विष्णु ही प्रकृति, पुरुष और काल के मूल आधार हैं जिनसे ब्रह्मांड की सृष्टि और वराह रूप में पृथ्वी का उद्धार होता है [S1][S2]।"
        ),
        [
            ("How does the Vishnu Purana describe creation of the universe?", "how"),
            ("What roles do Vishnu, Brahma, Prakriti, and Time play in creation?", "what"),
            ("Who explains cosmology in Vishnu Purana Part 1?", "who"),
            ("विष्णु पुराण में सृष्टि की उत्पत्ति कैसे बताई गई है?", "how"),
        ],
    ),
    _topic(
        "dhruva_devotion",
        "vishnu-purana",
        "Story and Devotion of Young Dhruva",
        "dhruva pole star penance devotion perseverance child vishnu purana",
        ["vishnu-purana_1_11_1", "vishnu-purana_1_12_1"],
        (
            "Hurt by stepmother Suruchi's cruel dismissal, young Prince Dhruva follows his mother Suniti's gentle advice not to hate anyone, goes to the forest guided by the Seven Sages, and wins Vishnu's direct grace through unwavering meditation—earning the eternal seat of the Pole Star [S1][S2]."
        ),
        (
            "Dhruva proves that age, status, or painful rejection cannot limit a seeker armed with steady resolve, kindness without resentment, and focused faith [S1][S2]."
        ),
        (
            "Turn hurt into constructive discipline rather than bitterness, seek wise teachers cleanly, and stay patient in long-term effort [S1][S2]."
        ),
        (
            "Dhruva performs his focused penance in early childhood after being denied a place on King Uttanapada's lap [S1][S2]."
        ),
        (
            "Dhruva's departure and vision of Vishnu appear in Vishnu Purana Part 1, Sections 11 and 12 [S1][S2]."
        ),
        (
            "Young Dhruva, encouraged by his wise mother Suniti and taught the mantra by the sages, receives Vishnu's blessing [S1][S2]."
        ),
        (
            "सौतेली माता के कटु वचनों से आहत होकर भी बालक ध्रुव ने अपनी माता सुनीति की सलाह मानकर घोर तप किया और श्रीहरि के दर्शन कर अटल ध्रुव तारे का पद प्राप्त किया [S1][S2]।"
        ),
        [
            ("Who was Dhruva in the Vishnu Purana and what does his story teach?", "who"),
            ("Why did young Dhruva go to the forest for penance?", "why"),
            ("Where is Dhruva's story told in the Vishnu Purana?", "where"),
            ("बालक ध्रुव की कथा और उनकी भक्ति से क्या शिक्षा मिलती है?", "what"),
        ],
    ),
    _topic(
        "prahlada_faith",
        "vishnu-purana",
        "Prahlada's Fearless Devotion Amid Persecution",
        "prahlada hiranyakashipu faith devotion courage vishnu narasimha peace",
        ["vishnu-purana_1_17_1", "vishnu-purana_1_20_1"],
        (
            "Even while his father Hiranyakashipu threatens him with serpents, fire, and poison, young Prahlada stays utterly fearless and loving toward all beings because his mind rests continually in Vishnu—praying even for his father's peace [S1][S2]."
        ),
        (
            "Prahlada shows that genuine spirituality thrives inside hostile environments without returning hatred for hatred [S1][S2]."
        ),
        (
            "Keep compassion toward all creatures, stay steadfast in what is true even under pressure from authority, and anchor confidence in the all-pervading Divine [S1][S2]."
        ),
        (
            "Prahlada's trials take place throughout his childhood education under his father's rule [S1][S2]."
        ),
        ("Prahlada's story fills Vishnu Purana Part 1, Sections 17 through 20 [S1][S2]."),
        (
            "Prince Prahlada teaches devotion to his schoolmates and softens even Hiranyakashipu's hostility through fearless grace [S1][S2]."
        ),
        (
            "प्रह्लाद ने अपने पिता हिरण्यकशिपु के भयानक अत्याचारों के बीच भी श्रीविष्णु के प्रति अटूट भक्ति और सब प्राणियों के प्रति करुणा नहीं छोड़ी [S1][S2]।"
        ),
        [
            ("What does Prahlada's story in Vishnu Purana teach?", "what"),
            ("How did Prahlada stay fearless against Hiranyakashipu?", "how"),
            ("Where are Prahlada's teachings found in Vishnu Purana?", "where"),
            ("भक्त प्रह्लाद के जीवन और भक्ति से क्या सीख मिलती है?", "what"),
        ],
    ),
    _topic(
        "samudra_manthan",
        "vishnu-purana",
        "Churning of the Ocean of Milk (Samudra Manthan)",
        "samudra manthan churning ocean milk lakshmi nectar amrita kurma vishnu",
        ["vishnu-purana_1_9_1", "vishnu-purana_1_9_2"],
        (
            "Following Sage Durvasa's curse that drained cosmic prosperity, Devas and Asuras cooperate to churn the Ocean of Milk using Mount Mandara and Vasuki, yielding sacred treasures—most memorably Goddess Lakshmi, who shines eternally with Lord Vishnu [S1][S2]."
        ),
        (
            "Samudra Manthan reveals that lost prosperity is recovered only through sustained cooperative effort, patience through toxic setbacks, and reverence for grace [S1][S2]."
        ),
        (
            "Keep churning steadily through hard seasons without quitting halfway; treat wisdom and inner purity as deeper wealth than fleeting prizes [S1][S2]."
        ),
        (
            "This cosmic event follows Indra's loss of fortune after disrespecting a garland given by Durvasa [S1][S2]."
        ),
        (
            "The Samudra Manthan and emergence of Lakshmi are recounted in Vishnu Purana Part 1, Section 9 [S1][S2]."
        ),
        (
            "Vishnu guides the Devas, sustains Mount Mandara, and welcomes Sri Lakshmi from the ocean [S1][S2]."
        ),
        (
            "दुर्वासा ऋषि के शाप के बाद श्रीविष्णु के मार्गदर्शन में देवों और असुरों ने क्षीरसागर का मंथन किया, जिससे दिव्य रत्न और माता लक्ष्मी प्रकट हुईं [S1][S2]।"
        ),
        [
            ("What happened during the Churning of the Ocean (Samudra Manthan)?", "what"),
            ("Why did Devas and Asuras churn the Ocean of Milk?", "why"),
            ("Where is Samudra Manthan described in Vishnu Purana?", "where"),
            ("समुद्र मंथन क्यों हुआ और इससे क्या प्राप्त हुआ?", "why"),
        ],
    ),
    _topic(
        "four_yugas",
        "vishnu-purana",
        "The Four Ages (Yugas) and Kali Yuga",
        "four yugas kali satya treta dvapara cycles dharma age future",
        ["vishnu-purana_6_1_1", "vishnu-purana_6_2_1"],
        (
            "The Vishnu Purana describes time moving across four Yugas—Krita (Satya), Treta, Dvapara, and Kali—noting how outer social ethics gradually decline into Kali Yuga [S1], yet praising Kali Yuga because great spiritual merit can then be gained swiftly through simple remembrance of the Divine [S2]."
        ),
        (
            "Rather than inspiring despair over modern decline, Kali Yuga teaches that sincere inner remembrance and charity carry extraordinary transformative value right now [S1][S2]."
        ),
        (
            "Stay truthful in your personal habits, simplify devotion into heartfelt remembrance of Krishna/Hari, and act generously regardless of surrounding trends [S2]."
        ),
        (
            "Sage Parashara explains the Yugas near the close of the Vishnu Purana, addressing how seekers live in the present Kali age [S1][S2]."
        ),
        (
            "The four ages and Kali Yuga's unique grace appear in Vishnu Purana Part 6, Sections 1 and 2 [S1][S2]."
        ),
        (
            "Sage Parashara reveals to Maitreya and the sages why even Kali Yuga holds tremendous spiritual blessing [S1][S2]."
        ),
        (
            "विष्णु पुराण के छठे अंश में चारों युगों का वर्णन है—कलियुग में अधर्म बढ़ने पर भी केवल सच्चे मन से भगवान के नाम-स्मरण और भक्ति से महान पुण्य प्राप्त हो जाता है [S1][S2]।"
        ),
        [
            ("What are the four Yugas in the Vishnu Purana?", "what"),
            ("Why did Vyasa praise Kali Yuga despite its faults?", "why"),
            ("How should a seeker live spiritually in Kali Yuga?", "how"),
            ("चार युग और कलियुग के बारे में विष्णु पुराण क्या कहता है?", "what"),
        ],
    ),
    _topic(
        "krishna_lila",
        "vishnu-purana",
        "Life of Sri Krishna in Vishnu Purana Part 5",
        "krishna childhood vrindavan kaliya govardhana life vishnu purana avatar",
        ["vishnu-purana_5_7_1", "vishnu-purana_5_11_1"],
        (
            "Vishnu Purana Part 5 narrates the complete earthly life of Sri Krishna—from birth in Mathura and childhood in Vrindavan, taming serpent Kaliya to protect cows and friends [S1], to lifting Mount Govardhana against Indra's storm to shield the villagers [S2]."
        ),
        (
            "Krishna's Vrindavan episodes highlight fearless protection of nature and community, humility before arrogance, and joyful devotion uniting ordinary folk [S1][S2]."
        ),
        (
            "Honor everyday work, community, and nature over showy pride, trusting that sincere love calls forth divine protection [S1][S2]."
        ),
        (
            "Part 5 spans Krishna's birth, Vrindavan youth, defeat of Kamsa, Dwaraka rule, and final departure [S1][S2]."
        ),
        (
            "Krishna's exploits fill all of Vishnu Purana Part 5, including Kaliya (Section 7) and Govardhana (Section 11) [S1][S2]."
        ),
        (
            "Lord Krishna nurtures the cowherd families of Vraja, teaching humility to both Kaliya and Indra [S1][S2]."
        ),
        (
            "विष्णु पुराण के पांचवें अंश में श्रीकृष्ण के जन्म से लेकर कालिया दमन [S1] और गोवर्धन पर्वत धारण [S2] जैसी लीलाओं का वर्णन है, जो प्रकृति, समुदाय और विनम्र भक्ति का संदेश देती हैं।"
        ),
        [
            ("What stories of Krishna are told in Vishnu Purana Part 5?", "what"),
            ("Why did Krishna subdue Kaliya and lift Mount Govardhana?", "why"),
            ("Where in Vishnu Purana is Sri Krishna's life recounted?", "where"),
            ("विष्णु पुराण में श्रीकृष्ण की प्रमुख लीलाएं कौन सी हैं?", "what"),
        ],
    ),
    _topic(
        "bharat_jadabharata",
        "vishnu-purana",
        "Wisdom and Detachment of Jadabharata",
        "jadabharata king bharata detachment equality wisdom sauvira vishnu purana",
        ["vishnu-purana_2_13_1", "vishnu-purana_2_15_1"],
        (
            "Former righteous king Bharata grew overly attached to a rescued fawn and was reborn as serene sage Jadabharata, who lived completely free of pride before teaching King Sauvira that ultimate truth transcends outward status, body, and ego [S1][S2]."
        ),
        (
            "Jadabharata's story cautions against subtle attachment—even to good intentions—while celebrating inward freedom beyond social applause [S1][S2]."
        ),
        (
            "Care compassionately without blind clinging [S1], look past outer labels or titles, and recognize one luminous consciousness across all lives [S2]."
        ),
        (
            "After teaching King Sauvira while carrying his palanquin, Jadabharata reveals deep Advaitic wisdom about the Self [S2]."
        ),
        (
            "King Bharata and Jadabharata appear in Vishnu Purana Part 2, Sections 13 through 16 [S1][S2]."
        ),
        (
            "Sage Jadabharata humbly instructs King Sauvira (Rahuugana) about the true nature of the Self [S1][S2]."
        ),
        (
            "जड़भरत और राजा भरत की कथा बताती है कि अत्यधिक मोह बंधन का कारण बनता है, जबकि समदृष्टि और आत्मज्ञान से सच्ची स्वतंत्रता मिलती है [S1][S2]।"
        ),
        [
            ("Who was Jadabharata in the Vishnu Purana?", "who"),
            ("What lesson did King Bharata learn from attachment to a deer?", "what"),
            ("Where does Jadabharata teach King Sauvira?", "where"),
            ("जड़भरत कौन थे और उनकी कथा क्या सिखाती है?", "who"),
        ],
    ),
    _topic(
        "varnashrama_duties",
        "vishnu-purana",
        "Ethical Household and Social Duties",
        "householder duties ethics charity family guests hospitality vishnu purana",
        ["vishnu-purana_3_8_1", "vishnu-purana_3_11_1"],
        (
            "Vishnu Purana Part 3 explains that true worship of Vishnu lies in living honestly in one's station—practicing truthfulness, harmlessness, clean livelihood, kindness to dependents, and open-hearted hospitality to guests [S1][S2]."
        ),
        (
            "Spiritual life does not begin after ignoring family and community ethics; daily kindness, honesty, and generosity are how Vishnu is honored in society [S1][S2]."
        ),
        (
            "Earn cleanly, speak without deceit, honor elders and guests warmly, and share what you have with those in need [S1][S2]."
        ),
        (
            "These practical duties apply across all stages of life—student, householder, elder, and seeker [S1][S2]."
        ),
        (
            "Social and householder duties are laid out in Vishnu Purana Part 3, Sections 8 through 12 [S1][S2]."
        ),
        (
            "Sage Aurva and Sage Parashara describe how ordinary householders please Vishnu simply by walking ethically [S1][S2]."
        ),
        (
            "विष्णु पुराण सिखाता है कि अपने कर्तव्यों का ईमानदारी से पालन, सत्य, अहिंसा, अतिथि-सत्कार और परिवार व समाज के प्रति दया रखना ही भगवान विष्णु की सच्ची आराधना है [S1][S2]।"
        ),
        [
            ("How does Vishnu Purana describe ethical daily duties for householders?", "how"),
            ("What virtues are required in social and family life?", "what"),
            ("Where in Vishnu Purana are daily householder ethics explained?", "where"),
            ("विष्णु पुराण के अनुसार गृहस्थ जीवन के मुख्य कर्तव्य क्या हैं?", "what"),
        ],
    ),
    # ── Additional Bhagavad Gita Deep Topics ─────────────────────────────
    _topic(
        "svadharma_paradharma",
        "bhagavad-gita",
        "Following One's Own Path (Svadharma vs Paradharma)",
        "svadharma paradharma own duty path calling comparison authentic life",
        ["bhagavad-gita_3_35", "bhagavad-gita_18_47"],
        (
            "Svadharma is the duty aligned with your own nature, capacities, and responsibilities; Paradharma is imitating someone else's path [S1]. Krishna states clearly that fulfilling your own duty imperfectly brings greater peace and growth than imitating another's path brilliantly [S1][S2]."
        ),
        (
            "Copying another person's calling or lifestyle out of envy or glamour creates inner conflict and anxiety, whereas owning your authentic responsibility builds steadiness and zero guilt [S1][S2]."
        ),
        (
            "Identify your true strengths, family commitments, and ethical duties right now; invest wholeheartedly in doing your own role well instead of constantly measuring yourself against others [S1][S2]."
        ),
        (
            "Remember Svadharma whenever social comparison, career uncertainty, or peer pressure tempts you to abandon honest responsibility [S1][S2]."
        ),
        (
            "Krishna teaches this principle in Bhagavad Gita 3.35 and reinforces it near the conclusion in 18.47 [S1][S2]."
        ),
        (
            "Sri Krishna teaches Arjuna this principle when Arjuna briefly considers dropping his warrior duty to live like a forest mendicant [S1][S2]."
        ),
        (
            "अपना स्वाभाविक धर्म (स्वधर्म) चाहे गुणों में कम प्रतीत हो, फिर भी दूसरों के धर्म (परधर्म) की नकल करने से श्रेष्ठ है—अपने स्वभावानुसार कर्म करने से व्यक्ति को दोष नहीं लगता [S1][S2]।"
        ),
        [
            ("What is the difference between Svadharma and Paradharma?", "what"),
            ("Why is one's own imperfect duty better than another's duty?", "why"),
            ("Svadharma aur Paradharma mein kya antar hai?", "what"),
        ],
    ),
    _topic(
        "yajna_sacrifice",
        "bhagavad-gita",
        "Living in the Spirit of Yajna (Selfless Offering)",
        "yajna sacrifice gratitude cosmos ecology giving back cooperation",
        ["bhagavad-gita_3_9", "bhagavad-gita_4_24"],
        (
            "In the Gita, Yajna expands beyond ritual fire into every selfless act done in harmony and service [S1]. Work performed without yajna binds the ego, whereas seeing the tool, offering, performer, and goal as sacred transforms daily life into liberation [S1][S2]."
        ),
        (
            "Human beings receive air, knowledge, food, and community support continuously; living as a taker breeds emptiness, whereas mutual offering sustains harmony and freedom [S1][S2]."
        ),
        (
            "Begin tasks by asking how your effort serves family, community, and truth rather than hoarding only for yourself [S1][S2]."
        ),
        (
            "The spirit of Yajna turns daily meals, work, learning, and charity into continual spiritual practice [S1][S2]."
        ),
        (
            "Yajna as selfless action appears in Gita 3.9 and its meditative vision is expressed in 4.24 [S1][S2]."
        ),
        (
            "Sri Krishna redefines ancient Vedic Yajna for Arjuna as an inner attitude of grateful, dedicated service [S1][S2]."
        ),
        (
            "गीता में यज्ञ का अर्थ केवल कर्मकांड नहीं बल्कि ईश्वर को समर्पित निस्वार्थ सेवा है—यज्ञ भाव से किए गए कर्म बंधन से मुक्त कर देते हैं [S1][S2]।"
        ),
        [
            ("What does Yajna mean in the Bhagavad Gita?", "what"),
            ("Why does Gita 3.9 say work outside Yajna creates bondage?", "why"),
        ],
    ),
    _topic(
        "kshetra_kshetrajna",
        "bhagavad-gita",
        "Body as the Field and Consciousness as the Knower (Kshetra and Kshetrajna)",
        "kshetra kshetrajna body mind field knower witness awareness consciousness",
        ["bhagavad-gita_13_1", "bhagavad-gita_13_2"],
        (
            "Krishna describes the body, senses, thoughts, and changing emotions as the 'Field' (Kshetra), and the silent witnessing awareness observing them as the 'Knower of the Field' (Kshetrajna) [S1]. Knowing both the field and the Divine Knower within all beings constitutes true wisdom [S2]."
        ),
        (
            "Confusing yourself entirely with an aging body or passing moods creates needless suffering; discovering the calm observer inside brings lasting freedom [S1][S2]."
        ),
        (
            "During strong stress or praise, silently step back and notice: thoughts and bodily sensations are moving in the 'field', while calm awareness simply witnesses them [S1][S2]."
        ),
        (
            "This teaching is especially freeing when illness, aging, mood swings, or external criticism shake confidence [S1][S2]."
        ),
        (
            "The distinction between Kshetra and Kshetrajna opens Bhagavad Gita Chapter 13 (13.1-13.2) [S1][S2]."
        ),
        (
            "Sri Krishna teaches Arjuna that the Lord Himself is the universal Kshetrajna dwelling quietly in every field (body) [S2]."
        ),
        (
            "गीता अध्याय 13 में शरीर को 'क्षेत्र' और उसे जानने वाली साक्षी चेतना को 'क्षेत्रज्ञ' कहा गया है—इन दोनों के भेद को जानना ही वास्तविक ज्ञान है [S1][S2]।"
        ),
        [
            ("What is Kshetra and Kshetrajna in Bhagavad Gita Chapter 13?", "what"),
            ("Who is the Knower of the Field in all bodies?", "who"),
        ],
    ),
    _topic(
        "akshara_purushottama",
        "bhagavad-gita",
        "The Cosmic Tree and Purushottama (Mutable, Immutable, and Supreme)",
        "ashvattha tree kshara akshara purushottama chapter 15 supreme spirit",
        ["bhagavad-gita_15_16", "bhagavad-gita_15_18"],
        (
            "Chapter 15 distinguishes two aspects across existence: the perishable changeable realm of bodies (Kshara) and the unchanging witness Spirit (Akshara) [S1]. Beyond both stands the Supreme Person (Purushottama), who permeates, upholds, and transcends all three worlds [S2]."
        ),
        (
            "Seeing only changeable matter causes insecurity; knowing both the changeless Self and the all-loving Supreme Reality integrates wisdom with heartfelt devotion [S1][S2]."
        ),
        (
            "Look past surface appearances in changing circumstances to trust the enduring Spirit present behind both nature and consciousness [S1][S2]."
        ),
        (
            "Chapter 15 provides a concise synthesis of Vedantic metaphysics just before the Gita turns toward ethics in Chapters 16-18 [S1][S2]."
        ),
        ("These core definitions sit at Bhagavad Gita Chapter 15 Verses 16 and 18 [S1][S2]."),
        (
            "Sri Krishna reveals Himself as Purushottama—revered across Vedas and lived wisdom alike [S2]."
        ),
        (
            "गीता अध्याय 15 में क्षर (नाशवान जगत), अक्षर (अविनाशी जीवात्मा) और इन दोनों से परे परम ब्रह्म पुरुषोत्तम का वर्णन किया गया है [S1][S2]।"
        ),
        [
            ("What are Kshara, Akshara, and Purushottama in Gita Chapter 15?", "what"),
            ("Why is Krishna called Purushottama?", "why"),
        ],
    ),
    _topic(
        "vibhuti_divine_manifestation",
        "bhagavad-gita",
        "Seeing Divine Glories Throughout the World (Vibhuti Yoga)",
        "vibhuti yoga wonder nature greatness chapter 10 creation spark",
        ["bhagavad-gita_10_20", "bhagavad-gita_10_41"],
        (
            "Krishna reveals that He is the Self seated within every heart—the beginning, middle, and end of all beings [S1]. Whatever displays beauty, strength, courage, clarity, or brilliance in nature and humanity shines from a tiny spark of His splendor [S2]."
        ),
        (
            "Instead of feeling jealous of others' gifts or starved of wonder, Vibhuti Yoga trains your eyes to see every excellence in nature, art, and people as a reminder of the Divine [S1][S2]."
        ),
        (
            "Whenever you admire a mountain, wise teacher, sunrise, music, or kind act, bow mentally to the infinite Source shining through it [S2]."
        ),
        (
            "Practice Vibhuti vision daily while walking outdoors, studying great work, or appreciating virtues in people around you [S1][S2]."
        ),
        (
            "Divine splendors are celebrated across Gita Chapter 10, framed clearly by 10.20 and 10.41 [S1][S2]."
        ),
        (
            "Arjuna asks how to recognize and contemplate the Divine everywhere, and Sri Krishna answers with poetic Vibhutis [S1][S2]."
        ),
        (
            "विभूति योग (अध्याय 10) सिखाता है कि विश्व में जहाँ कहीं भी सौंदर्य, बल, ज्ञान और तेज दिखाई देता है, वह सब परमात्मा के ही एक अंश से प्रकट हुआ है [S1][S2]।"
        ),
        [
            ("What is Vibhuti Yoga in Bhagavad Gita Chapter 10?", "what"),
            ("How can I see the Divine in nature and everyday excellence?", "how"),
        ],
    ),
    _topic(
        "threefold_charity_dana",
        "bhagavad-gita",
        "Right Way to Give Charity (Sattvic, Rajasic, and Tamasic Dana)",
        "charity dana generosity giving selfless help humility",
        ["bhagavad-gita_17_20", "bhagavad-gita_17_21"],
        (
            "Pure (Sattvic) charity is given simply as a duty to someone worthy, at the right place and time, without expecting any favor or praise in return [S1]. Charity given reluctantly or to boast and seek payback falls under Rajas [S2]."
        ),
        (
            "Generosity loses spiritual depth when done for social applause or manipulation; quiet, respectful giving purifies both giver and society [S1][S2]."
        ),
        (
            "Give discreetly to genuine need, preserve the recipient's dignity, and drop any mental ledger keeping score [S1]."
        ),
        (
            "Apply this discernment whenever donating time, money, knowledge, or encouragement [S1][S2]."
        ),
        (
            "The three kinds of charity are taught in Bhagavad Gita Chapter 17 Verses 17.20-17.22 [S1][S2]."
        ),
        (
            "Sri Krishna explains to Arjuna why intention and attitude matter more than the size of a donation [S1][S2]."
        ),
        (
            "गीता अध्याय 17 के अनुसार बिना किसी बदले की आशा के, उचित पात्र, समय और स्थान देखकर कर्तव्य-भाव से दिया गया दान सात्त्विक दान है [S1][S2]।"
        ),
        [
            ("What makes charity Sattvic according to the Bhagavad Gita?", "what"),
            ("How should we practice generosity without ego?", "how"),
        ],
    ),
    _topic(
        "threefold_austerity_tapas",
        "bhagavad-gita",
        "Threefold Self-Discipline of Body, Speech, and Mind (Tapas)",
        "tapas austerity discipline speech truthfulness gentleness purity mind",
        ["bhagavad-gita_17_14", "bhagavad-gita_17_17"],
        (
            "Krishna classifies daily self-discipline (Tapas) into three domains: bodily discipline (cleanliness, non-violence, respect), disciplined speech (words that are true, pleasant, helpful, and non-hurting), and mental discipline (serenity, friendliness, silence, self-control, and pure intent) [S1]. Practiced without selfish pride, this becomes Sattvic discipline [S2]."
        ),
        (
            "True spiritual discipline is not dramatic self-torture; it shines through respectful conduct, kind truthful speech, and a calm, uncluttered mind [S1][S2]."
        ),
        (
            "Before speaking or posting online, test your words against Gita standards: is it true, helpful, and gentle? Daily cultivate calm thoughts and honest habits [S1][S2]."
        ),
        (
            "Bodily, verbal, and mental discipline build character continuously in family conversations, work, and solitude [S1]."
        ),
        ("The three austerities are taught in Bhagavad Gita 17.14-17.17 [S1][S2]."),
        (
            "Sri Krishna outlines balanced discipline of body, speech, and thought for Arjuna [S1][S2]."
        ),
        (
            "गीता अध्याय 17 में शरीर (अहिंसा, पवित्रता), वाणी (सत्य, प्रिय और हितकारी वचन) तथा मन (प्रसन्नता, सौम्यता, संयम) के तीन प्रकार के तप बताए गए हैं [S1][S2]।"
        ),
        [
            ("What are the three kinds of Tapas (austerity) in Gita Chapter 17?", "what"),
            ("What does the Bhagavad Gita say about disciplined speech?", "what"),
        ],
    ),
    _topic(
        "threefold_happiness",
        "bhagavad-gita",
        "Three Kinds of Happiness (Short Pleasure vs Lasting Joy)",
        "happiness joy sukha pleasure contentment satisfaction nectar poison",
        ["bhagavad-gita_18_36", "bhagavad-gita_18_37"],
        (
            "The Gita notes three forms of happiness [S1]: pure (Sattvic) joy often tastes bitter at first—like patience, study, or steady discipline—yet ripens into nectar-like peace rooted in clarity [S2]. By contrast, impulsive sensual pleasure (Rajasic) thrills briefly at first yet leaves exhaustion and regret afterward."
        ),
        (
            "Understanding why meaningful growth feels demanding initially keeps you from quitting early for cheap distractions [S1][S2]."
        ),
        (
            "Look past immediate comfort: choose habits—honest learning, calm dialogue, daily meditation—that bring lasting clarity even if they take patient effort first [S2]."
        ),
        (
            "Reflect on Gita 18.37 whenever instant gratification competes with long-term wellbeing [S2]."
        ),
        ("Threefold happiness appears in Bhagavad Gita Chapter 18 Verses 18.36-18.39 [S1][S2]."),
        (
            "Sri Krishna explains the psychology of real lasting joy versus fleeting excitement to Arjuna [S1][S2]."
        ),
        (
            "गीता 18.37 के अनुसार सात्त्विक सुख आरंभ में अभ्यास और संयम के कारण विष जैसा कठिन लग सकता है, किंतु परिणाम में अमृत के समान स्थायी शांति देता है [S1][S2]।"
        ),
        [
            ("What does the Bhagavad Gita teach about lasting happiness (Sukha)?", "what"),
            ("Why does Sattvic happiness feel like poison at first and nectar later?", "why"),
            ("Gita ke anusar asli khushi aur sukh kya hai?", "what"),
        ],
    ),
    _topic(
        "four_types_seekers",
        "bhagavad-gita",
        "Four Types of People Who Turn to God",
        "four seekers distressed wealth curious wise jnani devotion chapter 7",
        ["bhagavad-gita_7_16", "bhagavad-gita_7_17"],
        (
            "Krishna welcomes four kinds of sincere seekers who turn toward the Divine: the distressed looking for relief, seekers of worldly support, curious truth-inquirers, and the wise person rooted in loving understanding (Jnani) [S1]. All four are noble, and the steadfast wise devotee is extraordinarily dear [S2]."
        ),
        (
            "Spiritual life has no shame in beginning out of pain or hardship; every sincere step toward God refines the heart toward unselfish wisdom [S1][S2]."
        ),
        (
            "Begin wherever you honestly stand—whether praying during trouble or asking deep philosophical questions—and gradually let curiosity mature into steadfast love [S1][S2]."
        ),
        (
            "Revisit these verses whenever someone feels unworthy because they started praying only in crisis [S1]."
        ),
        (
            "The four seekers are described in Bhagavad Gita Chapter 7 Verses 7.16 and 7.17 [S1][S2]."
        ),
        (
            "Sri Krishna assures Arjuna that all four types of devotees are large-hearted and precious [S1][S2]."
        ),
        (
            "गीता 7.16 के अनुसार आर्त (दुःखी), जिज्ञासु (ज्ञान के इच्छुक), अर्थार्थी और ज्ञानी—ये चार प्रकार के श्रेष्ठ मनुष्य भगवान का भजन करते हैं [S1][S2]।"
        ),
        [
            ("Who are the four types of devotees in Bhagavad Gita Chapter 7?", "who"),
            ("Why does Krishna value even distressed prayers?", "why"),
        ],
    ),
    _topic(
        "remembrance_at_death",
        "bhagavad-gita",
        "Thought at Death and Habitual Remembrance",
        "death end of life remembrance mind thought chapter 8 transition rebirth",
        ["bhagavad-gita_8_5", "bhagavad-gita_8_6"],
        (
            "Krishna teaches a deep psychological law: whatever dominant state of mind a person dwells on and remembers at the moment of leaving the body shapes where consciousness goes next [S1][S2]. Therefore, steady daily remembrance ensures peace now and clarity at life's close [S1]."
        ),
        (
            "Final thoughts rarely appear by accident—they reflect what our mind practiced loving and dwelling on throughout decades of ordinary life [S1][S2]."
        ),
        (
            "Saturate daily routines with noble values, compassion, and quiet remembrance of the Divine now, rather than postponing inner cultivation [S1][S2]."
        ),
        (
            "Practice steady remembrance consistently day by day—both while active in work and at quiet evening reflection [S1]."
        ),
        ("This teaching sits in Bhagavad Gita Chapter 8 Verses 8.5 through 8.7 [S1][S2]."),
        (
            "Sri Krishna answers Arjuna's opening questions in Chapter 8 regarding Brahman, action, and the hour of departure [S1][S2]."
        ),
        (
            "गीता 8.5-8.6 के अनुसार अंत समय में मनुष्य जिस भाव का स्मरण करते हुए शरीर त्यागता है, उसी को प्राप्त होता है—इसलिए प्रतिदिन निरंतर अभ्यास से भगवान का स्मरण करना चाहिए [S1][S2]।"
        ),
        [
            ("What does the Bhagavad Gita say about thoughts at the time of death?", "what"),
            ("Why does Gita 8.6 say final thoughts reflect our life habits?", "why"),
        ],
    ),
    _topic(
        "samadarshana_equality",
        "bhagavad-gita",
        "True Equality: Seeing the Same Divine Presence in All (Samadarshana)",
        "equality respect caste humility animals wisdom same vision samadarshana",
        ["bhagavad-gita_5_18", "bhagavad-gita_6_29"],
        (
            "True sages look with equal respect upon a learned, humble scholar, a cow, an elephant, a dog, and an outcaste—because one immutable Spirit illuminates all [S1]. Realizing the Self in every being dissolves arrogance and prejudice [S2]."
        ),
        (
            "Equal vision does not ignore different roles in practical society, yet it eradicates contempt, cruelty, and superiority by honoring sacred consciousness everywhere [S1][S2]."
        ),
        (
            "Treat elders, helpers, strangers, and animals with quiet dignity; catch yourself whenever pride ranks human worth by status [S1][S2]."
        ),
        (
            "Samadarshana is essential whenever social bias, status pride, or bitterness tries to harden your heart [S1][S2]."
        ),
        ("This teaching shines in Bhagavad Gita 5.18 and Chapter 6 Verse 6.29 [S1][S2]."),
        (
            "Sri Krishna defines genuine spiritual enlightenment through humble, impartial respect toward every creature [S1][S2]."
        ),
        (
            "गीता 5.18 और 6.29 सिखाते हैं कि सच्चा ज्ञानी विद्या-विनययुक्त विद्वान, गाय, हाथी, श्वान और चांडाल सभी में एक ही परमात्मा को समभाव से देखता है [S1][S2]।"
        ),
        [
            (
                "What does the Bhagavad Gita teach about equality and respect for all beings?",
                "what",
            ),
            ("Why does Gita 5.18 list a scholar, cow, dog, and outcaste together?", "why"),
        ],
    ),
    _topic(
        "laziness_procrastination",
        "bhagavad-gita",
        "Overcoming Laziness, Heedlessness, and Procrastination (Tamas)",
        "laziness procrastination sleep apathy tamas motivation discipline inertia",
        ["bhagavad-gita_14_8", "bhagavad-gita_18_28"],
        (
            "The Gita traces chronic inertia, heedlessness, oversleeping, and endless procrastination to Tamas—confusion that clouds alertness and delays rightful duty [S1][S2]. Growth moves from sluggish Tamas into purposeful effort (Rajas) and onward to joyful clarity (Sattva) [S1]."
        ),
        (
            "Chronic postponement steals energy and confidence; awakening wholesome energy and clear priorities restores momentum without burnout [S1][S2]."
        ),
        (
            "Break large tasks into one concrete immediate step [S1], guard sleep moderation, avoid negative delay loops, and build steady small routines daily [S2]."
        ),
        (
            "Recognize Tamas whenever sluggishness, doomscrolling, or self-pity stalls necessary work [S1][S2]."
        ),
        (
            "Tamasic inertia is analyzed in Gita 14.8 and Tamasic action/procrastination in Chapter 18 (18.28, 18.39) [S1][S2]."
        ),
        (
            "Sri Krishna maps the three gunas so Arjuna—and modern readers—can spot sluggishness and rise cleanly into clarity [S1][S2]."
        ),
        (
            "गीता में आलस्य, प्रमाद और कार्य को टालने की प्रवृत्ति को तमोगुण का प्रभाव बताया गया है—सत्त्वगुण और नियमित कर्तव्य-अभ्यास से आलस्य पर विजय मिलती है [S1][S2]।"
        ),
        [
            ("What does the Bhagavad Gita say about laziness and procrastination?", "what"),
            ("How can I overcome laziness and lack of motivation using the Gita?", "how"),
            ("Aalas aur procrastination kaise khatam karein Gita ke anusar?", "how"),
        ],
    ),
    _topic(
        "loneliness_self_support",
        "bhagavad-gita",
        "Handling Loneliness and Finding Inner Support",
        "loneliness alone support friend within refuge divine presence isolation",
        ["bhagavad-gita_6_5", "bhagavad-gita_9_29"],
        (
            "Krishna reminds seekers that your deepest companion lives within: lift yourself by becoming your own steady friend [S1], and know that the Supreme Lord dwells impartially in every heart—whoever turns to Him in love abides in Him, and He abides in them [S2]."
        ),
        (
            "Loneliness sharpens when we feel unvalued or abandoned; discovering self-respect and an abiding inward relationship with the Divine restores warmth and steadiness [S1][S2]."
        ),
        (
            "Speak kindly to yourself rather than fueling self-criticism [S1], stay open to serving others, and cultivate quiet inner remembrance in prayer or reflection [S2]."
        ),
        (
            "Return to these verses during seasons of solitude, relocation, or feeling misunderstood [S1][S2]."
        ),
        (
            "Inner self-friendship is taught in Gita 6.5 and universal divine closeness in 9.29 [S1][S2]."
        ),
        (
            "Sri Krishna assures Arjuna that nobody devoted with sincere heart is ever truly alone [S2]."
        ),
        (
            "गीता 6.5 और 9.29 सिखाते हैं कि मनुष्य को स्वयं अपना मित्र बनना चाहिए और ईश्वर समभाव से प्रत्येक हृदय में स्थित होकर अपने भक्त के सदा साथ रहते हैं [S1][S2]।"
        ),
        [
            ("What does the Bhagavad Gita teach about loneliness?", "what"),
            ("How can scripture comfort someone feeling alone or unsupported?", "how"),
            ("Akelapan aur loneliness mein Gita kya sahara deti hai?", "what"),
        ],
    ),
    _topic(
        "jealousy_envy",
        "bhagavad-gita",
        "Dealing with Jealousy, Envy, and Comparison",
        "jealousy envy comparison resentment goodwill contentment peace",
        ["bhagavad-gita_12_13", "bhagavad-gita_3_30"],
        (
            "Envy flourishes when we tie self-worth to beating others; Krishna marks freedom from envy and malice as a core trait of a dear devotee [S1], while advising us to offer all work cleanly without selfish fever or possessiveness [S2]."
        ),
        (
            "Jealousy poisons your own peace long before affecting anyone else, distracting energy away from your true calling [S1][S2]."
        ),
        (
            "Practice wishing others well silently, pivot attention back to your own Svadharma and daily craft, and express gratitude for your unique growth [S1][S2]."
        ),
        (
            "Apply Gita 12.13 whenever others' recognition, wealth, or success triggers bitterness [S1]."
        ),
        ("Non-envy and contentment stand out in Gita 3.30, 12.13, and 4.22 [S1][S2]."),
        ("Sri Krishna praises hearts free from envy and possessive comparison [S1]."),
        (
            "ईर्ष्या और द्वेष से मुक्त रहकर सबका मित्र बनना, संतुष्ट रहना और अपने कर्तव्य को निष्काम भाव से निभाना सच्चे आत्मिक विकास का मार्ग है [S1][S2]।"
        ),
        [
            ("How can I overcome jealousy and envy according to the Gita?", "how"),
            ("Why is comparison harmful to peace of mind?", "why"),
            ("Jalan aur jealousy ko kaise kam karein?", "how"),
        ],
    ),
    _topic(
        "wealth_prosperity",
        "bhagavad-gita",
        "Ethical Wealth, Ambition, and Simplicity",
        "wealth money greed ambition simplicity honest earning prosperity",
        ["bhagavad-gita_10_38", "bhagavad-gita_16_13"],
        (
            "The Gita never opposes honest prosperity, skill, or victory rooted in righteousness—Krishna honors wise governance and righteous statesmanship as divine manifestations [S1]. Yet Chapter 16 warns sharply against insatiable greed that measures life only by hoarding and pride ('Today I gained this, tomorrow I will hoard more') [S2]."
        ),
        (
            "Money serves life well as an instrument for care, charity, and dignified work, but turns destructive when greed becomes an endless master [S1][S2]."
        ),
        (
            "Pursue work cleanly with skill and honesty [S1], reject deceit or ruthless greed [S2], and share prosperity generously while keeping inner peace untied to net worth."
        ),
        (
            "Reflect on ethical wealth whenever career ambition, business deals, or financial worries arise [S1][S2]."
        ),
        (
            "Righteous leadership appears in Gita 10.38 and the portrait of toxic greed in 16.13-16.16 [S1][S2]."
        ),
        ("Sri Krishna contrasts righteous strength with unchecked egoistic accumulation [S1][S2]."),
        (
            "गीता ईमानदारी से समृद्धि और कर्तव्य-सफलता के विरुद्ध नहीं है, परंतु अंधे लोभ और अहंकारपूर्ण धन-संग्रह की निंदा करती है [S1][S2]।"
        ),
        [
            ("What does the Bhagavad Gita say about money, wealth, and greed?", "what"),
            ("Why does Gita Chapter 16 warn against unchecked ambition?", "why"),
            ("Paisa aur safalta ke baare mein Gita kya kehti hai?", "what"),
        ],
    ),
    _topic(
        "forgiveness_kshama",
        "bhagavad-gita",
        "Strength of Forgiveness (Kshama) and Freedom from Grudges",
        "forgiveness kshama grudge resentment letting go mercy patience",
        ["bhagavad-gita_16_1", "bhagavad-gita_16_3"],
        (
            "In Gita Chapter 16, Krishna places forgiveness (Kshama), patience, non-anger, and absence of malice among the highest divine virtues [S1][S2]. Holding bitterness locks your mind into past injury; forgiveness frees your heart to act cleanly in the present [S2]."
        ),
        (
            "Forgiveness is a sign of inner power rather than weakness—it refuses to let someone else's mistake turn you into a bitter person [S1][S2]."
        ),
        (
            "Set healthy ethical boundaries where necessary, while consciously dropping ongoing hatred, vengeful fantasies, and constant replay of wrongs [S2]."
        ),
        (
            "Practice Kshama whenever old family hurts, workplace conflicts, or unthinking remarks weigh on your heart [S1][S2]."
        ),
        ("Forgiveness appears prominently in Bhagavad Gita 16.1-16.3 and 12.13-12.14 [S1][S2]."),
        (
            "Sri Krishna counts Kshama among the noble qualities that lead toward inner liberation [S1][S2]."
        ),
        (
            "गीता अध्याय 16 में क्षमा (माफ करना), क्रोध न करना, धैर्य और द्वेष-रहित भाव को दैवी संपत्ति के मुख्य गुणों में गिना गया है [S1][S2]।"
        ),
        [
            ("What does the Bhagavad Gita teach about forgiveness?", "what"),
            ("Why is forgiveness called a divine strength in Gita Chapter 16?", "why"),
            ("Kisi ko maaf (forgive) kaise karein Gita ke anusar?", "how"),
        ],
    ),
    _topic(
        "how_to_read_gita",
        "bhagavad-gita",
        "How to Start Reading and Studying the Bhagavad Gita",
        "start reading guide beginner order chapters study bhagavad gita",
        ["bhagavad-gita_2_7", "bhagavad-gita_2_47"],
        (
            "Begin the Bhagavad Gita with curiosity and sincerity—much like Arjuna asking Krishna cleanly for guidance [S1]. Many readers start with Chapter 2 for the core overview of immortal Self and Karma Yoga [S2], Chapter 12 for gentle Bhakti, and Chapter 6 for meditation before reading straight through 1 to 18."
        ),
        (
            "Approaching the Gita as practical dialogue rather than a rushed exam lets each verse answer real questions about work, grief, mind, and purpose [S1][S2]."
        ),
        (
            "Read 3 to 5 verses daily with plain English or Hindi translation, reflect on one verse you can practice that day, and ask Sarathi whenever a Sanskrit term feels unclear [S1][S2]."
        ),
        (
            "Any quiet ten-minute window—morning before work or evening before rest—works smoothly to begin reading [S2]."
        ),
        (
            "Gyan Sutra organizes all 18 chapters and 701 verses with Sanskrit, transliteration, translations, and audio [S1][S2]."
        ),
        (
            "Just as Arjuna asks humbly in 2.7, any sincere reader can enter Krishna and Arjuna's dialogue today [S1]."
        ),
        (
            "भगवद्गीता पढ़ना शुरू करने के लिए प्रतिदिन 3-5 श्लोक शांत मन से पढ़ें—विशेषकर अध्याय 2 (मूल सार) और अध्याय 12 (भक्ति) से आरंभ करना सरल होता है [S1][S2]।"
        ),
        [
            ("How should a beginner start reading the Bhagavad Gita?", "how"),
            ("Which Bhagavad Gita chapter should I read first?", "what"),
            ("Bhagavad Gita padhna kaise shuru karein?", "how"),
        ],
    ),
    # ── Additional Valmiki Ramayana Stories & Themes ────────────────────
    _topic(
        "krauncha_valmiki_origin",
        "valmiki-ramayana",
        "Why Valmiki Composed the Ramayana (The Krauncha Bird Episode)",
        "krauncha bird shoka shloka valmiki adi kavya poetry origin tamasa",
        ["valmiki-ramayana_1_1_1", "valmiki-ramayana_1_2_15"],
        (
            "Moved by deep compassion after seeing a hunter shoot one of two devoted Krauncha birds beside River Tamasa [S2], Sage Valmiki's sorrow (Shoka) overflowed spontaneously as the first metered verse (Shloka)—leading Brahma to bless him to compose Rama's story in that meter [S1][S2]."
        ),
        (
            "The episode reveals that eternal poetry and sacred storytelling are born from empathy with another creature's pain, not cold intellect [S2]."
        ),
        (
            "Let deep empathy motivate creative expression, justice, and speech that protects life rather than causing needless harm [S2]."
        ),
        (
            "This famous origin event occurs right before the main narrative begins in Bala Kanda, Sarga 2 [S2]."
        ),
        ("On the banks of the Tamasa River near Valmiki's ashram in Bala Kanda, Sarga 2 [S2]."),
        (
            "Sage Valmiki witnesses the hunter and grieving female Krauncha bird after earlier conversing with Narada in Sarga 1 [S1][S2]."
        ),
        (
            "तमसा नदी के तट पर व्याध द्वारा क्रौंच पक्षी के वध से उपजे करुणा-शोक से ही महर्षि वाल्मीकि के मुख से प्रथम श्लोक प्रस्फुटित हुआ और रामायण की रचना आरंभ हुई [S1][S2]।"
        ),
        [
            ("How was the first Sanskrit verse (shloka) of the Ramayana born?", "how"),
            ("Why did Sage Valmiki curse the hunter in Bala Kanda?", "why"),
        ],
    ),
    _topic(
        "vishwamitra_yajna_training",
        "valmiki-ramayana",
        "Sage Vishwamitra's Yajna and Young Rama's Training",
        "vishwamitra bala atibala tataka yajna training youth mentorship rama lakshmana",
        ["valmiki-ramayana_1_19_1", "valmiki-ramayana_1_22_1"],
        (
            "Sage Vishwamitra asks King Dasharatha to send young Rama to defend a sacred forest sacrifice threatened by fierce Maricha and Subahu [S1]. Though reluctant at first, Dasharatha lets Rama and Lakshmana go—and Vishwamitra imparts empowering Bala and Atibala mantras [S2]."
        ),
        (
            "Leaving royal comfort under a strict mentor transforms sheltered courage into disciplined mastery ready to serve society [S1][S2]."
        ),
        (
            "Welcome demanding mentors, step beyond protective comfort zones early in life, and use strength to safeguard peaceful communities [S1][S2]."
        ),
        (
            "Occurs during Rama's adolescence in Bala Kanda prior to his journey toward Mithila [S1][S2]."
        ),
        (
            "Begins in Ayodhya palace (Sarga 19) and unfolds along the Sarayu bank to Siddhashrama [S1][S2]."
        ),
        (
            "Sage Vishwamitra guides princes Rama and Lakshmana after persuading King Dasharatha [S1][S2]."
        ),
        (
            "बालकाण्ड में महर्षि विश्वामित्र धर्म-यज्ञ की रक्षा हेतु युवा श्रीराम और लक्ष्मण को वन ले जाते हैं और उन्हें 'बला' व 'अतिबला' विद्या प्रदान करते हैं [S1][S2]।"
        ),
        [
            ("Why did Vishwamitra take Rama and Lakshmana to the forest?", "why"),
            ("What did Sage Vishwamitra teach Rama in Bala Kanda?", "what"),
        ],
    ),
    _topic(
        "ahalya_redemption",
        "valmiki-ramayana",
        "Redemption of Ahalya by Lord Rama",
        "ahalya gautama grace forgiveness redemption purification mithila",
        ["valmiki-ramayana_1_48_1", "valmiki-ramayana_1_49_1"],
        (
            "Along the road to Mithila, Sage Vishwamitra shares the story of Ahalya undergoing long austere penance under Sage Gautama's curse [S1]. When Rama enters the lonely hermitage respectfully, Ahalya is purified, honored, and joyfully reunited with Gautama [S2]."
        ),
        (
            "Ahalya's release reveals divine grace that values sincere remorse and restores excluded souls without harsh judgment [S1][S2]."
        ),
        (
            "Offer compassion and a clean second chance to anyone genuinely striving to rise past past errors [S2]."
        ),
        (
            "Happens en route to King Janaka's kingdom in Mithila near the end of Bala Kanda's journey [S1][S2]."
        ),
        (
            "At Sage Gautama's secluded hermitage outside Mithila in Bala Kanda, Sargas 48-49 [S1][S2]."
        ),
        ("Lord Rama honors Ahalya in the presence of Lakshmana and Sage Vishwamitra [S2]."),
        (
            "मिथिला जाते समय गौतम ऋषि के आश्रम में श्रीराम के चरण-स्पर्श व करुणा से तपस्विनी अहल्या का उद्धार होता है और वे पुनः आदरपूर्वक अपने परिवार से मिलती हैं [S1][S2]।"
        ),
        [
            ("Who was Ahalya and how did Lord Rama free her?", "who"),
            ("What is the story of Ahalya in Bala Kanda?", "what"),
        ],
    ),
    _topic(
        "kaikeyi_boons_dasharatha",
        "valmiki-ramayana",
        "Kaikeyi's Two Boons and King Dasharatha's Grief",
        "kaikeyi manthara dasharatha two boons bharata throne ayodhya sorrow",
        ["valmiki-ramayana_2_11_1", "valmiki-ramayana_2_12_1"],
        (
            "Swayed by Manthara's fear-driven whispers, Queen Kaikeyi invokes two past boons granted by King Dasharatha: crowning Bharata and exiling Rama for fourteen years [S1]. Heartbroken, Dasharatha pleads for mercy yet refuses to break his royal word [S2]."
        ),
        (
            "The episode warns how jealousy and malicious counsel can shatter a loving family, and shows the tragic cost of honoring truth [S1][S2]."
        ),
        (
            "Guard close relationships against insecurity and manipulative whispers; think carefully before making open-ended promises under emotion [S1][S2]."
        ),
        (
            "Unfolds through the fateful night before Rama's planned coronation in Ayodhya Kanda [S1][S2]."
        ),
        ("Inside Kaikeyi's chamber in Ayodhya (Ayodhya Kanda, Sargas 10-14) [S1][S2]."),
        ("Queen Kaikeyi demands the boons from agonized King Dasharatha [S1][S2]."),
        (
            "मंथरा के बहकावे में आकर कैकेयी ने राजा दशरथ से भरत के राज्याभिषेक और श्रीराम के लिए 14 वर्ष के वनवास के दो वर मांग लिए, जिससे दशरथ अत्यंत व्यथित हो गए [S1][S2]।"
        ),
        [
            ("What were the two boons Queen Kaikeyi asked from Dasharatha?", "what"),
            ("Why could King Dasharatha not refuse Kaikeyi's demand?", "why"),
        ],
    ),
    _topic(
        "guha_friendship_ganga",
        "valmiki-ramayana",
        "Guha's Devotion and Crossing the Ganga",
        "guha nishada boatman ganga equality hospitality devotion ayodhya",
        ["valmiki-ramayana_2_50_1", "valmiki-ramayana_2_52_1"],
        (
            "Upon reaching the banks of the Ganga at Shringiberapura, exiled Rama warmly embraces Guha, chief of the Nishada forest-dwellers [S1]. Declining luxurious royal hospitality out of vow discipline, Rama accepts Guha's loving brotherhood and crosses the Ganga in Guha's boat toward forest exile [S2]."
        ),
        (
            "Rama's embrace of Guha demonstrates that sincere love and friendship transcend wealth, social birth, and external status [S1][S2]."
        ),
        (
            "Honor sincere friendship warmly across every social background while staying steadfast to personal commitments [S1][S2]."
        ),
        (
            "Takes place shortly after Rama, Sita, and Lakshmana leave Ayodhya for the forest [S1][S2]."
        ),
        ("At Shringiberapura on the banks of River Ganga in Ayodhya Kanda, Sargas 50-52 [S1][S2]."),
        (
            "Lord Rama honors Chief Guha, who stays awake guarding the sleeping exiles and ferries them across the Ganga [S1][S2]."
        ),
        (
            "शृंगवेरपुर में निषादराज गुह ने वनवासी श्रीराम का प्रेमपूर्वक स्वागत किया और उन्हें गंगा पार कराया—यह प्रसंग सच्ची मित्रता व सामाजिक समरसता का उदाहरण है [S1][S2]।"
        ),
        [
            ("Who was Guha and how did he help Rama cross the Ganga?", "who"),
            ("What does Rama and Guha's friendship teach?", "what"),
        ],
    ),
    _topic(
        "jabali_argument_truth",
        "valmiki-ramayana",
        "Jabali's Pragmatic Materialism vs Rama's Defense of Truth",
        "jabali truth philosophy honesty materialism ethics promise chitrakuta",
        ["valmiki-ramayana_2_108_1", "valmiki-ramayana_2_109_1"],
        (
            "At Chitrakuta, royal minister Jabali urges Rama to drop his late father's pledge using skeptical, materialistic arguments—claiming human ties end at death [S1]. Rama firmly rejects expediency over truth, declaring that truth sustains the cosmos and righteousness is the highest pillar of life [S2]."
        ),
        (
            "This dialogue proves that Rama's exile isn't blind submission—it is a reasoned, conscious stand that society collapses without trustworthy truth [S1][S2]."
        ),
        (
            "Refuse convenient excuses when your word or ethical principle is tested; let truthfulness anchor leadership and trust [S2]."
        ),
        (
            "Occurs during Bharata's emotional council trying to persuade Rama to return from Chitrakuta [S1][S2]."
        ),
        ("At Chitrakuta hermitage in Ayodhya Kanda, Sargas 108-109 [S1][S2]."),
        (
            "Sage-counselor Jabali tests Rama with skeptical reasoning, and Lord Rama refutes it calmly [S1][S2]."
        ),
        (
            "चित्रकूट में मंत्री जाबालि ने व्यावहारिक तर्क देकर श्रीराम को अयोध्या लौटने के लिए कहा, तब श्रीराम ने सत्य और वचन-पालन को सृष्टि का आधार बताकर धर्म की रक्षा की [S1][S2]।"
        ),
        [
            ("What did Jabali argue to Rama at Chitrakuta and how did Rama reply?", "what"),
            ("Why did Rama reject Jabali's advice to break the exile vow?", "why"),
        ],
    ),
    _topic(
        "agastya_dandaka_forest",
        "valmiki-ramayana",
        "Sage Agastya's Blessing and Entering Panchavati",
        "agastya sage divine bow weapons panchavati aranya kanda forest",
        ["valmiki-ramayana_3_11_1", "valmiki-ramayana_3_12_1"],
        (
            "After visiting virtuous sages in Dandakaranya [S1], Rama, Sita, and Lakshmana reach Sage Agastya's ashram, where Agastya honors Rama and entrusts him with celestial bow and unfailing weapons before directing them to settle beside the Godavari at peaceful Panchavati [S2]."
        ),
        (
            "Wisdom and preparedness walk together: saints recognize the moral need to empower righteous protectors against oppression [S1][S2]."
        ),
        ("Seek blessing and guidance from wise elders when taking up major responsibilities [S2]."),
        (
            "After ten years of peaceful forest wanderings, leading into the Panchavati years in Aranya Kanda [S1][S2]."
        ),
        ("At Sage Agastya's hermitage in Dandaka forest (Aranya Kanda, Sargas 11-13) [S1][S2]."),
        (
            "Sage Agastya welcomes Rama, Sita, and Lakshmana and equips Rama to protect the forest sages [S2]."
        ),
        (
            "अरण्यकाण्ड में महर्षि अगस्त्य श्रीराम को दिव्य धनुष-बाण सौंपते हैं और उन्हें गोदावरी तट पर पंचवटी में निवास करने का मार्गदर्शन देते हैं [S1][S2]।"
        ),
        [
            ("Why did Sage Agastya give divine weapons to Lord Rama?", "why"),
            ("What happened when Rama met Sage Agastya in Aranya Kanda?", "what"),
        ],
    ),
    _topic(
        "vali_sugriva_ethics",
        "valmiki-ramayana",
        "Why Rama Slew Vali and the Debate on Justice",
        "vali sugriva kishkindha debate justice hidden arrow kingship dharma",
        ["valmiki-ramayana_4_17_1", "valmiki-ramayana_4_18_1"],
        (
            "Wounded by Rama's arrow from concealment during his duel with Sugriva, mighty King Vali charges Rama with deceit and unkingly conduct [S1]. Rama explains soberly that as sovereign deputy upholding moral law across the realm, he executed just punishment for Vali's grave abuse of his brother's wife and exile of Sugriva [S2]."
        ),
        (
            "Valmiki includes Vali's raw critique alongside Rama's legal defense—inviting readers to wrestle honestly with justice, accountability, and power [S1][S2]."
        ),
        (
            "Do not use physical strength or high position to oppress family or vulnerable dependents; recognize accountability under universal dharma [S2]."
        ),
        (
            "Happens right after Rama and Sugriva forge their friendship alliance in Kishkindha Kanda [S1][S2]."
        ),
        ("At the gates of Kishkindha in Kishkindha Kanda, Sargas 17 and 18 [S1][S2]."),
        (
            "Dying King Vali questions Lord Rama candidly, and Rama states his moral justification cleanly before blessing Vali's son Angada [S1][S2]."
        ),
        (
            "किष्किन्धाकाण्ड में बालि ने छिपकर बाण चलाने पर श्रीराम से प्रश्न किया, तब श्रीराम ने राजधर्म और नैतिक मर्यादा के उल्लंघन का दंड बताते हुए न्याय का कारण स्पष्ट किया [S1][S2]।"
        ),
        [
            ("Why did Lord Rama kill Vali from behind a tree?", "why"),
            ("How did Rama answer Vali's accusations in Kishkindha Kanda?", "how"),
        ],
    ),
    _topic(
        "tara_wisdom_counsel",
        "valmiki-ramayana",
        "Queen Tara's Foresight, Dignity, and Peacemaking",
        "tara queen vali sugriva lakshmana wisdom diplomacy peace",
        ["valmiki-ramayana_4_15_1", "valmiki-ramayana_4_33_1"],
        (
            "Queen Tara demonstrates exceptional foresight and diplomatic grace twice in Kishkindha Kanda: first wisely warning Vali against fighting Sugriva once backed by Rama [S1], and later stepping calmly forward to pacify furious Lakshmana when Sugriva's delay nearly sparks war [S2]."
        ),
        (
            "Tara proves how calm reason, emotional intelligence, and timely humility can prevent fatal arrogance or needless conflict [S1][S2]."
        ),
        (
            "Listen carefully when perceptive allies warn of danger [S1], and step into tense disputes with respectful tact rather than escalating anger [S2]."
        ),
        (
            "Before Vali's fatal duel and later when the rainy season ends and Lakshmana arrives angrily in Kishkindha [S1][S2]."
        ),
        ("In Kishkindha palace (Kishkindha Kanda, Sargas 15 and 33-35) [S1][S2]."),
        (
            "Queen Tara counsels Vali honestly and mediates peaceably with Lakshmana on Sugriva's behalf [S1][S2]."
        ),
        (
            "रानी तारा की दूरदर्शिता किष्किन्धाकाण्ड में दो बार दिखती है—पहले वे बालि को समझदारी से सचेत करती हैं और बाद में क्रोधित लक्ष्मण को विनम्रता से शांत करती हैं [S1][S2]।"
        ),
        [
            ("Who was Tara in the Ramayana and how did she guide Kishkindha?", "who"),
            ("How did Queen Tara pacify Lakshmana's anger?", "how"),
        ],
    ),
    _topic(
        "sampati_guidance",
        "valmiki-ramayana",
        "Sampati Helping the Search Party Find Sita",
        "sampati jatayu vulture wings ocean search direction lanka confidence",
        ["valmiki-ramayana_4_56_1", "valmiki-ramayana_4_58_1"],
        (
            "Despairing beside the southern sea after failing to find Sita, Angada and Hanuman meet aged wingless vulture Sampati—elder brother of Jatayu [S1]. Hearing of Jatayu's heroic sacrifice, grieving Sampati uses his extraordinary far-seeing vision to confirm Sita is held in Ravana's Lanka across the ocean [S2]."
        ),
        (
            "Even broken, aged beings unable to fly themselves can pass on vital truth and encouragement that unlocks someone else's great leap [S1][S2]."
        ),
        (
            "Never discount how your lived knowledge or truthful clue can renew courage for those continuing the journey [S1][S2]."
        ),
        (
            "At the climactic turning point near the end of Kishkindha Kanda just before Hanuman's leap [S1][S2]."
        ),
        (
            "On the southern ocean cliffs at Mount Mahendra in Kishkindha Kanda, Sargas 56-59 [S1][S2]."
        ),
        (
            "Sampati informs Angada, Jambavan, Hanuman, and the Vanaras of Sita's exact whereabouts in Lanka [S1][S2]."
        ),
        (
            "समुद्र तट पर निराश वानरों को जटायु के बड़े भाई संपाती ने अपनी दूरदृष्टि से यह सूचना दी कि सीता लंका में अशोक वाटिका में हैं, जिससे खोज को नई दिशा मिली [S1][S2]।"
        ),
        [
            ("Who was Sampati and how did he help find Sita?", "who"),
            ("What happened when the Vanaras met Sampati?", "what"),
        ],
    ),
    _topic(
        "hanuman_obstacles_lanka",
        "valmiki-ramayana",
        "How Hanuman Faced Obstacles During His Ocean Leap (Mainaka, Surasa, Simhika)",
        "mainaka surasa simhika hanuman ocean leap obstacles humility wit courage",
        ["valmiki-ramayana_5_1_1", "valmiki-ramayana_5_2_1"],
        (
            "Leaping across the ocean from Mount Mahendra toward Lanka, Hanuman meets three symbolic tests [S1]: hospitable comfort (Mount Mainaka offering rest, politely declined until mission's end), wit and humility (Surasa expanding, whom Hanuman outsmarts by shrinking tiny and slipping out), and hidden malice (Simhika, defeated swiftly) before scouting Lanka calmly [S2]."
        ),
        (
            "Every noble mission meets premature comfort, ego traps, and hidden hostility—Hanuman models focus, adaptability, humility, and decisive courage [S1][S2]."
        ),
        (
            "Politely postpone unnecessary comfort before finishing core duty, adapt cleverly instead of fighting foolishly, and crush malicious interference boldly [S1][S2]."
        ),
        (
            "Occurs across Sundara Kanda's opening sea crossing and arrival at Lanka's gates [S1][S2]."
        ),
        ("Over the ocean between Mount Mahendra and Lanka in Sundara Kanda, Sargas 1-2 [S1][S2]."),
        (
            "Hanuman navigates Mainaka, Surasa, and Simhika seamlessly before entering Lanka [S1][S2]."
        ),
        (
            "सुन्दरकाण्ड में समुद्र पार करते समय हनुमान ने मैनाक का सत्कार विनम्रता से टाला, सुरसा को बुद्धि व लघुता से संतुष्ट किया और सिंहिका का वध कर लंका में प्रवेश किया [S1][S2]।"
        ),
        [
            ("How did Hanuman overcome Mainaka, Surasa, and Simhika?", "how"),
            ("What do Hanuman's tests while crossing the ocean symbolize?", "what"),
        ],
    ),
    _topic(
        "burning_of_lanka",
        "valmiki-ramayana",
        "Lanka Dahan: Hanuman's Fearless Warning to Ravana",
        "lanka dahan fire tail ashoka garden warning ravana power fearlessness",
        ["valmiki-ramayana_5_53_1", "valmiki-ramayana_5_54_1"],
        (
            "Captured intentionally after advising Ravana cleanly to return Sita, Ravana orders demons to wrap Hanuman's tail in oil-soaked cloth and set it aflame [S1]. Unharmed by fire, Hanuman leaps free across Lanka's palaces, burning Ravana's fortress as an unmistakable warning while keeping Sita safe [S2]."
        ),
        (
            "Evil intoxicated with power refuses polite counsel; Lanka's blaze demonstrates that unrighteous strength is brittle against disciplined fearlessness [S1][S2]."
        ),
        (
            "Speak truth cleanly first; if injustice still tries to humiliate you, turn adversity into fearless strength without losing care for the innocent [S1][S2]."
        ),
        (
            "Happens late in Sundara Kanda right before Hanuman bids Sita farewell and returns to Rama [S1][S2]."
        ),
        ("Inside Ravana's court and across golden Lanka in Sundara Kanda, Sargas 53-54 [S1][S2]."),
        (
            "Ravana orders Hanuman's humiliation, and Hanuman turns the burning tail against Lanka [S1][S2]."
        ),
        (
            "लंका दहन प्रसंग में रावण के आदेश से पूँछ में आग लगने पर भी हनुमान ने निडरता से लंका के महलों को जलाकर रावण के अहंकार को कड़ी चेतावनी दी [S1][S2]।"
        ),
        [
            ("Why and how did Hanuman set Lanka on fire?", "how"),
            ("What happened when Ravana ordered Hanuman's tail burned?", "what"),
        ],
    ),
    _topic(
        "kumbhakarna_counsel",
        "valmiki-ramayana",
        "Kumbhakarna's Honest Counsel and Tragic Loyalty",
        "kumbhakarna ravana counsel ethics loyalty brother yuddha kanda sleep",
        ["valmiki-ramayana_6_63_1", "valmiki-ramayana_6_67_1"],
        (
            "Awakened during the desperate war in Lanka, giant Kumbhakarna tells Ravana bluntly in assembly that abducting Sita and ignoring wise ministers was utterly wrong [S1]. Yet out of fierce fraternal loyalty, he marches into battle and falls gloriously in combat against Rama [S2]."
        ),
        (
            "Kumbhakarna models honest truth-speaking to loved ones in error, while showing the tragedy of loyalty separated from higher righteousness (contrast Vibhishana) [S1][S2]."
        ),
        (
            "Speak truth honestly to family and leaders before disaster strikes—never silence conscience just to flatter [S1]."
        ),
        ("Midway through Yuddha Kanda's Lanka war after major demon commanders fall [S1][S2]."),
        ("Ravana's war council and the Lanka battlefield in Yuddha Kanda, Sargas 63-67 [S1][S2]."),
        ("Kumbhakarna admonishes Ravana candidly before confronting Rama on the field [S1][S2]."),
        (
            "युद्धकाण्ड में कुंभकर्ण ने रावण के समक्ष स्पष्ट कहा कि सीता का हरण अधर्म है, यद्यपि भ्रातृ-निष्ठा के कारण उसने युद्ध में जाकर श्रीराम के हाथों वीरगति पाई [S1][S2]।"
        ),
        [
            ("What advice did Kumbhakarna give Ravana before fighting?", "what"),
            ("Why did Kumbhakarna fight despite knowing Ravana was wrong?", "why"),
        ],
    ),
    _topic(
        "sanjeevani_hanuman_lakshmana",
        "valmiki-ramayana",
        "Hanuman Bringing the Herb Mountain (Sanjeevani) to Save Lakshmana",
        "sanjeevani herb mountain dhanvantari sushena lakshmana devotion rescue himalayas",
        ["valmiki-ramayana_6_74_1", "valmiki-ramayana_6_101_1"],
        (
            "When Lakshmana lies gravely wounded on the battlefield by a deadly spear [S2], physician Sushena names rare healing herbs atop the distant Himalayas; unable to single out one herb quickly enough in darkness, Hanuman uproots the entire luminous mountain peak and rushes back in time to save Lakshmana [S1][S2]."
        ),
        (
            "Selfless service never wastes time over pride or hesitation: when a loved one's life hangs by a thread, Hanuman gives maximum effort unconditionally [S1][S2]."
        ),
        (
            "Act swiftly and decisively when someone needs urgent help—bring your whole strength rather than offering half-measures [S1]."
        ),
        ("During critical night battles and Indrajit/Ravana encounters in Yuddha Kanda [S1][S2]."),
        ("Between the Lanka battlefield and Himalayas (Yuddha Kanda, Sargas 74 and 101) [S1][S2]."),
        (
            "Directed by Jambavan and physician Sushena, Hanuman rescues Lakshmana and thousands of fallen Vanaras [S1][S2]."
        ),
        (
            "युद्धकाण्ड में लक्ष्मण के मूर्छित होने पर समय न गंवाते हुए हनुमान हिमालय से पूरा संजीवनी औषधि-पर्वत उठा लाए और उनके प्राण बचाए [S1][S2]।"
        ),
        [
            ("Why did Hanuman lift the entire mountain instead of picking one herb?", "why"),
            ("How was Lakshmana saved when wounded in the Lanka war?", "how"),
        ],
    ),
    _topic(
        "aditya_hridayam",
        "valmiki-ramayana",
        "Aditya Hridayam: Sage Agastya's Hymn of Courage Before Battle",
        "aditya hridayam surya sun agastya courage fatigue victory yuddha",
        ["valmiki-ramayana_6_107_1"],
        (
            "Seeing Rama fatigued during the grueling duel with Ravana, Sage Agastya arrives on the battlefield and imparts the sacred Aditya Hridayam hymn celebrating the radiant Sun (Surya) as inner light and energy—instantly renewing Rama's strength and clarity to defeat Ravana [S1]."
        ),
        (
            "Even the strongest heroes experience exhaustion; turning quietly toward divine light restores inner vigor and overcomes despair before final effort [S1]."
        ),
        (
            "When overwhelmed or fatigued before an important challenge, pause briefly, breathe calmly, and reconnect with radiant inner courage and purpose [S1]."
        ),
        ("Taught immediately prior to the final decisive battle between Rama and Ravana [S1]."),
        ("Delivered on the Lanka battlefield in Yuddha Kanda, Sarga 107 [S1]."),
        ("Sage Agastya instructs fatigued Sri Rama in the sacred Aditya Hridayam hymn [S1]."),
        (
            "रावण से कठिन युद्ध के बीच थकान दूर करने और विजय प्राप्त करने के लिए महर्षि अगस्त्य ने श्रीराम को सूर्य देव की स्तुति 'आदित्य हृदय स्तोत्र' का उपदेश दिया [S1]।"
        ),
        [
            ("Who taught Aditya Hridayam to Lord Rama and why?", "who"),
            ("What is the significance of Aditya Hridayam in the Ramayana?", "why"),
        ],
    ),
    _topic(
        "sita_agni_pariksha",
        "valmiki-ramayana",
        "Sita's Agni Pariksha and Testimony of Truth",
        "sita agni pariksha fire trial purity lanka truth vindication",
        ["valmiki-ramayana_6_119_1", "valmiki-ramayana_6_121_1"],
        (
            "After Ravana's defeat, wounded by Rama's harsh public words questioning honor amid gossip, Devi Sita responds with fearless dignity and enters blazing fire to prove her unbroken purity [S1]. Agni, the Fire God, emerges holding her unharmed before gods and armies, affirming her absolute innocence as Rama joyfully embraces her [S2]."
        ),
        (
            "Valmiki gives voice to Sita's righteous protest alongside divine vindication—leaving an enduring moment of reflection on honor, public slander, and integrity [S1][S2]."
        ),
        (
            "Stand firmly in truth and self-respect without caving to false rumors, while guarding against harsh suspicion toward those who stood loyal [S1][S2]."
        ),
        (
            "Immediately following Ravana's fall in Lanka before the triumphant return to Ayodhya [S1][S2]."
        ),
        ("Outside Lanka's assembly of gods and warriors in Yuddha Kanda, Sargas 118-121 [S1][S2]."),
        (
            "Devi Sita defends her spotless character fiercely and Agni testifies to her innocence before Lord Rama and Brahma [S1][S2]."
        ),
        (
            "रावण वध के बाद माता सीता ने आत्मसम्मान व सत्य की प्रमाणिकता हेतु अग्नि परीक्षा दी, जिसमें अग्निदेव ने स्वयं प्रकट होकर उनकी परम पवित्रता की साक्षी दी [S1][S2]।"
        ),
        [
            ("Why did Sita enter fire (Agni Pariksha) after Ravana was defeated?", "why"),
            ("How did the Fire God testify for Sita in Yuddha Kanda?", "how"),
        ],
    ),
    _topic(
        "rama_rajya_ideal",
        "valmiki-ramayana",
        "Rama Rajya: Ideal Governance, Peace, and Prosperity",
        "rama rajya coronation ayodhya ideal governance justice welfare peace",
        ["valmiki-ramayana_6_131_1"],
        (
            "After returning to Ayodhya and celebrating Rama's grand coronation with Bharata, Hanuman, Vibhishana, and Sugriva, Valmiki describes Rama Rajya: a peaceful, fear-free reign where rains arrive on time, people speak truthfully, none envy or harm one another, citizens enjoy health and justice, and rulers serve like caring guardians [S1]."
        ),
        (
            "Rama Rajya embodies good governance grounded in ethical leadership, accountability, social harmony, and care for every citizen regardless of wealth [S1]."
        ),
        (
            "Practice small daily acts of Rama Rajya: keep honest promises, speak without malice, fulfill civic duties cleanly, and protect vulnerable neighbors [S1]."
        ),
        (
            "Crowning conclusion of the main epic at the close of Yuddha Kanda, continuing throughout Rama's reign [S1]."
        ),
        ("Described joyfully in Yuddha Kanda, Sarga 131 upon Rama's coronation in Ayodhya [S1]."),
        (
            "King Sri Rama governs justly alongside Queen Sita and his devoted brothers, ministers, and allies [S1]."
        ),
        (
            "युद्धकाण्ड के समापन पर अयोध्या में श्रीराम के राज्याभिषेक के साथ 'रामराज्य' की स्थापना हुई, जहाँ न्याय, सत्य, समृद्धि, निडरता और परस्पर सद्भाव व्याप्त था [S1]।"
        ),
        [
            ("What was Rama Rajya like in the Valmiki Ramayana?", "what"),
            ("Where is Rama's coronation and ideal rule described?", "where"),
        ],
    ),
    _topic(
        "lava_kusha_uttara",
        "valmiki-ramayana",
        "Birth of Lava and Kusha and the Closing Teachings of Uttara Kanda",
        "lava kusha sita ashram valmiki uttara kanda singing twins truth",
        ["valmiki-ramayana_7_66_1", "valmiki-ramayana_7_98_1"],
        (
            "In Uttara Kanda, Devi Sita gives birth to twin sons Lava and Kusha at Sage Valmiki's peaceful hermitage [S1], where the boys memorize and sing the entire Ramayana across Ayodhya. In the poignant closing climax, Sita affirms her lifelong devotion to truth and returns gracefully into Mother Earth [S2]."
        ),
        (
            "Uttara Kanda deepens the epic beyond triumph—exploring royal burden, painful sacrifice, artistic transmission of dharma through music, and Sita's sovereign integrity [S1][S2]."
        ),
        (
            "Pass sacred stories and values lovingly to children [S1], while remembering that inward truth outlives royal power or public misunderstanding [S2]."
        ),
        ("Unfolds in the years following Rama's coronation across Uttara Kanda [S1][S2]."),
        (
            "At Sage Valmiki's forest ashram and Naimisha assembly in Uttara Kanda (Sargas 66-98) [S1][S2]."
        ),
        (
            "Twins Lava and Kusha sing Valmiki's Ramayana before Rama, while Sita stands radiant in truth [S1][S2]."
        ),
        (
            "उत्तरकाण्ड में महर्षि वाल्मीकि के आश्रम में लव-कुश का जन्म व रामायण गान तथा अंत में माता सीता द्वारा सत्य की साक्षी देकर धरती माता की गोद में समा जाने का मार्मिक वर्णन है [S1][S2]।"
        ),
        [
            ("Who raised Lava and Kusha and what happens at the end of Uttara Kanda?", "who"),
            ("What is told in the Uttara Kanda of Valmiki Ramayana?", "what"),
        ],
    ),
    # ── Additional Vishnu Purana Stories & Teachings ────────────────────
    _topic(
        "parashara_maitreya_dialogue",
        "vishnu-purana",
        "How the Vishnu Purana Begins (Maitreya and Sage Parashara)",
        "parashara maitreya invocation opening lineage origins vishnu purana",
        ["vishnu-purana_1_1_1", "vishnu-purana_1_2_1"],
        (
            "The Vishnu Purana opens with respectful salutations as disciple Maitreya approaches wise Sage Parashara to ask how the universe was created, sustained, dissolved, and what its true substance is [S1]. Parashara recalls receiving the Purana through Brahma, Pulastya, and Vasishtha—pointing straight to Lord Vishnu (Vasudeva) as the eternal ground of all [S2]."
        ),
        (
            "Every Purana begins with respectful questions from a prepared seeker—modeling humility, intellectual curiosity, and unbroken guru-disciple transmission [S1][S2]."
        ),
        (
            "Approach big cosmic and spiritual questions with both reverence and clear inquiry [S1][S2]."
        ),
        (
            "Forms the opening two sections of Vishnu Purana Part 1 before cosmological narration begins [S1][S2]."
        ),
        ("Vishnu Purana Part 1, Sections 1 and 2 [S1][S2]."),
        (
            "Sage Parashara teaches devoted pupil Maitreya throughout all six books of the Vishnu Purana [S1][S2]."
        ),
        (
            "विष्णु पुराण का आरंभ शिष्य मैत्रेय के विनम्र प्रश्नों और महर्षि पराशर द्वारा भगवान विष्णु (वासुदेव) की वंदना व सृष्टि के मूल रहस्य के वर्णन से होता है [S1][S2]।"
        ),
        [
            ("Who narrates the Vishnu Purana and to whom?", "who"),
            ("How does the Vishnu Purana open in Part 1 Section 1?", "how"),
        ],
    ),
    _topic(
        "varaha_avatar_earth",
        "vishnu-purana",
        "Varaha Avatar: Lord Vishnu Rescuing the Earth",
        "varaha boar avatar earth prithivi creation kalpa cosmic rescue",
        ["vishnu-purana_1_4_1"],
        (
            "At the dawn of the cosmic day (Kalpa), finding the Earth submerged deep beneath primordial waters, Narayana assumes the mighty sacred form of Varaha (the cosmic Boar), dives to lift Earth up effortlessly on His tusks, and restores stability while Earth sings hymns praising His protective grace [S1]."
        ),
        (
            "Varaha symbolizes divine care that rescues the world whenever stability sinks, uplifting both nature and cosmic order [S1]."
        ),
        (
            "Honor and protect the Earth's ecological balance while trusting that cosmic order has deep restorative power [S1]."
        ),
        ("Takes place at the beginning of the present cosmic Kalpa following dissolution [S1]."),
        ("Narrated vividly in Vishnu Purana Part 1, Section 4 [S1]."),
        ("Lord Narayana manifests as Varaha and Earth (Prithivi) offers heartfelt praise [S1]."),
        (
            "विष्णु पुराण प्रथम अंश अध्याय 4 में कल्प के आरंभ में भगवान नारायण वराह अवतार धारण कर जल में डूबी पृथ्वी को अपनी दाढ़ों पर ऊपर उठाकर स्थापित करते हैं [S1]।"
        ),
        [
            ("What does the Varaha Avatar story in Vishnu Purana 1.4 teach?", "what"),
            ("Where in the Vishnu Purana does Vishnu rescue the Earth as Varaha?", "where"),
        ],
    ),
    _topic(
        "bharata_varsha_geography",
        "vishnu-purana",
        "Sacred Geography and Why Birth in Bharata-Varsha Is Praised",
        "jambudwipa bharata varsha geography nine divisions karma bhumi purana",
        ["vishnu-purana_2_1_1", "vishnu-purana_2_3_1"],
        (
            "Vishnu Purana Part 2 describes the continents and oceans surrounding Jambudwipa [S1] and celebrates Bharata-Varsha (the land stretching north from the ocean to the Himalayas) as the blessed 'land of action' (Karma-bhumi)—where beings can cultivate virtues, wisdom, and devotion leading straight to liberation [S2]."
        ),
        (
            "Rather than merely admiring heaven's effortless pleasures, the Purana elevates earthly life because conscious moral choice and selfless love grow right here [S2]."
        ),
        (
            "Treat your present human life and duties as a rare opportunity for spiritual growth and service instead of squandering them [S2]."
        ),
        ("Studied within the cosmic cosmology and earth-geography chapters of Part 2 [S1][S2]."),
        (
            "Vishnu Purana Part 2, Sections 1 through 4 (notably Section 3 on Bharata-Varsha) [S1][S2]."
        ),
        (
            "Sage Parashara teaches Maitreya about King Priyavrata's lineage and sacred earth geography [S1][S2]."
        ),
        (
            "विष्णु पुराण के दूसरे अंश में जम्बूद्वीप और भारतवर्ष का वर्णन है—इसे कर्मभूमि कहकर सराहा गया है क्योंकि यहीं सद्कर्म व भक्ति से मोक्ष प्राप्त किया जा सकता है [S1][S2]।"
        ),
        [
            ("How does Vishnu Purana describe Bharata-Varsha and Jambudwipa?", "what"),
            ("Why is Bharata-Varsha praised by even the celestials?", "why"),
        ],
    ),
    _topic(
        "ribhu_nidagha_nonduality",
        "vishnu-purana",
        "Ribhu and Nidagha: Seeing Non-Duality Beyond Distinctions",
        "ribhu nidagha advaita non duality one self illusion royal procession equality",
        ["vishnu-purana_2_15_1", "vishnu-purana_2_16_1"],
        (
            "To illustrate real Advaita wisdom, Sage Parashara recounts how sage Ribhu taught his learned student Nidagha to drop intellectual pride and 'I vs other' separation [S1]. Using the humorous example of watching a king ride an elephant—'Which is above and which is below?'—Ribhu awakens Nidagha to see one seamless divine reality everywhere [S2]."
        ),
        (
            "Bookish scholarship that only divides life into hierarchies misses truth; real non-dual insight makes the heart humble and deeply equal toward all [S1][S2]."
        ),
        (
            "Check whether your spiritual knowledge softens ego and hostility—if not, pause and practice seeing one shared consciousness behind surface roles [S2]."
        ),
        ("Told by Jadabharata to King Sauvira near the end of Vishnu Purana Part 2 [S1][S2]."),
        ("Vishnu Purana Part 2, Sections 15 and 16 [S1][S2]."),
        (
            "Sage Ribhu gently awakens disciple Nidagha to non-dual wisdom, recounted through Jadabharata [S1][S2]."
        ),
        (
            "ऋभु और निदाघ के प्रसिद्ध संवाद (द्वितीय अंश 15-16) में दिखाया गया है कि बाहरी भेदभाव से ऊपर उठकर सर्वत्र एक ही परमात्मा का दर्शन करना सच्चा ज्ञान है [S1][S2]।"
        ),
        [
            ("What does the dialogue of Ribhu and Nidagha in Vishnu Purana teach?", "what"),
            ("How did Ribhu awaken Nidagha to non-duality?", "how"),
        ],
    ),
    _topic(
        "vyasa_vedas_division",
        "vishnu-purana",
        "Why and How Veda Vyasa Divided the Vedas into Four",
        "veda vyasa four vedas rig yajur sama atharva krishna dwaipayana compilation",
        ["vishnu-purana_3_3_1", "vishnu-purana_3_4_1"],
        (
            "Vishnu Purana Part 3 explains that originally one vast Vedic wisdom existed; seeing human lifespan and memory grow shorter across Kali-approaching ages, Krishna Dwaipayana Veda Vyasa divided the Veda into four manageable streams—Rig, Yajur, Sama, and Atharva—and entrusted them to devoted disciples Paila, Vaishampayana, Jaimini, and Sumantu [S1][S2]."
        ),
        (
            "The arrangement shows deep pedagogical compassion: organizing boundless wisdom into clear study branches so ordinary generations would not lose sacred knowledge [S1][S2]."
        ),
        (
            "Honor the preserved fourfold Vedic heritage and approach spiritual study patiently, step by step [S1][S2]."
        ),
        (
            "Occurs near the end of every Dwapara age, especially before the present Kali age [S1][S2]."
        ),
        ("Vishnu Purana Part 3, Sections 3 and 4 [S1][S2]."),
        (
            "Krishna Dwaipayana (Veda Vyasa) transmits the four Vedas through his principal disciples [S2]."
        ),
        (
            "विष्णु पुराण के तीसरे अंश (अध्याय 3-4) में वर्णन है कि द्वापर के अंत में महर्षि वेदव्यास ने मानव क्षमता देखकर एक वेद को ऋग्, यजुः, साम और अथर्व चार भागों में विभक्त किया [S1][S2]।"
        ),
        [
            ("Why did Veda Vyasa divide the Veda into four parts?", "why"),
            ("Which disciples received the four Vedas from Vyasa?", "who"),
        ],
    ),
    _topic(
        "yama_overcome_devotion",
        "vishnu-purana",
        "Who Stands Beyond Fear of Yama (Lord of Death)",
        "yama death fear devotion compassion honesty kindness vishnu purana 3.7",
        ["vishnu-purana_3_7_1"],
        (
            "Asked how mortals transcend fear of Yama, Parashara narrates Bhishma's dialogue telling how Yama instructs his own messengers to spare true devotees of Vishnu: not merely ritualists, but people who speak truth calmly, avoid harming creatures, harbor no greed for others' possessions, stay compassionate, and remember Vishnu sincerely [S1]."
        ),
        (
            "This passage demolishes shallow ritualism: true devotion proves itself by ethical kindness, truthfulness, and pure heart, freeing a person from existential dread [S1]."
        ),
        (
            "Cultivate harmlessness, clean honesty, freedom from jealousy, and steady remembrance of the Divine—the marks Yama himself honors [S1]."
        ),
        ("Applies lifelong in daily conduct and removes fear when facing mortality [S1]."),
        ("Vishnu Purana Part 3, Section 7 [S1]."),
        (
            "Yama instructs his servants, recounted by Bhishma to Nakula and shared by Sage Parashara [S1]."
        ),
        (
            "विष्णु पुराण (अंश 3, अध्याय 7) में यमराज अपने दूतों को बताते हैं कि जो सत्य, अहिंसा, परोपकार और निष्कपट भाव से विष्णु भक्ति करते हैं, उन पर यम-पाश का भय नहीं रहता [S1]।"
        ),
        [
            ("According to Vishnu Purana 3.7, whom does Yama's noose never touch?", "who"),
            ("How can one conquer the fear of death according to Vishnu Purana?", "how"),
        ],
    ),
    _topic(
        "yayati_desire_never_quenched",
        "vishnu-purana",
        "King Yayati's Discovery: Why Craving Never Ends Through Indulgence",
        "yayati desire craving addiction fire ghee pleasure contentment lesson",
        ["vishnu-purana_4_10_1"],
        (
            "King Yayati exchanges his premature old age for his youngest son Puru's youth to enjoy worldly pleasures for ages, only to discover a timeless truth [S1]: 'Desires are never satisfied by indulging them; like fire fed with clarified butter (ghee), craving only blazes higher.' Returning Puru's youth, Yayati turns toward inner contentment [S1]."
        ),
        (
            "Yayati's story exposes the modern illusion that 'one more acquisition' will bring peace—real satisfaction comes from conscious contentment, not endless consumption [S1]."
        ),
        (
            "Stop feeding restless cravings hoping they will tire out; cultivate deliberate moderation and joyful gratitude for enough [S1]."
        ),
        (
            "Vital whenever chasing pleasure, shopping, status, or endless sensory novelty fails to bring lasting peace [S1]."
        ),
        ("Vishnu Purana Part 4, Section 10 [S1]."),
        ("King Yayati learns directly from experience alongside his devoted son Puru [S1]."),
        (
            "राजा ययाति की कथा (चतुर्थ अंश, अध्याय 10) यह अमर सत्य सिखाती है कि कामनाएँ भोगने से कभी शांत नहीं होतीं, बल्कि घी डालने पर अग्नि की तरह और बढ़ती हैं—संतोष ही शांति देता है [S1]।"
        ),
        [
            ("What did King Yayati realize about human desires?", "what"),
            ("Why does Yayati compare indulgence to pouring ghee on fire?", "why"),
        ],
    ),
    _topic(
        "ganga_bhagiratha_sagara",
        "vishnu-purana",
        "Sagara's Sons, Kapila, and the Sacred Descent of Ganga",
        "ganga sagar bhagiratha kapila penance persistence ancestors water",
        ["vishnu-purana_4_4_1"],
        (
            "Tracing the Solar Dynasty, Vishnu Purana Part 4 tells how King Sagara's proud sons offended Sage Kapila and perished, and how generations of relentless penance by their descendants—culminating in King Bhagiratha—brought the celestial River Ganga gently down to Earth to purify their ancestors and bless all humanity [S1]."
        ),
        (
            "The epic account contrasts arrogant aggression (which brings ruin) with patient, multi-generational perseverance in service of others ('Bhagiratha effort') [S1]."
        ),
        (
            "Keep working patiently toward a worthy goal for family and society even when previous setbacks look insurmountable [S1]."
        ),
        ("Appears inside the Solar Dynasty chronicles in Vishnu Purana Part 4 [S1]."),
        ("Vishnu Purana Part 4, Section 4 [S1]."),
        (
            "Kings Sagara, Amshumat, Dilipa, and steadfast King Bhagiratha with Sage Kapila and Shiva [S1]."
        ),
        (
            "विष्णु पुराण (अंश 4, अध्याय 4) में सगर पुत्रों के उद्धार और भागीरथ की अटूट तपस्या से पवित्र गंगा के पृथ्वी पर अवतरण की प्रेरणादायक कथा वर्णित है [S1]।"
        ),
        [
            ("What is the story of Sagara's sons and Bhagiratha bringing the Ganga?", "what"),
            ("Why is King Bhagiratha remembered as a symbol of perseverance?", "why"),
        ],
    ),
    _topic(
        "krishna_birth_mathura",
        "vishnu-purana",
        "Birth of Lord Krishna in Mathura and Crossing the Yamuna",
        "krishna birth mathura devaki vasudeva yamuna gokula yasoda kamsa",
        ["vishnu-purana_5_3_1"],
        (
            "To liberate Earth from cruel oppression under Kamsa, Lord Vishnu enters the womb of Devaki; at auspicious midnight in Mathura prison, baby Krishna appears luminously before Vasudeva and Devaki [S1]. Prison guards sleep, chains fall open, and Vasudeva carries the infant across the swollen Yamuna safely to Gokula into Yashoda and Nanda's loving home [S1]."
        ),
        (
            "Krishna's birth amid locked iron bars shows that no tyrant's walls can stop divine grace from arriving quietly where hearts are faithful [S1]."
        ),
        (
            "Hold steady hope even when circumstances feel confining—quiet devotion opens paths through seemingly locked doors [S1]."
        ),
        ("Opens Krishna's earthly life story early in Vishnu Purana Part 5 [S1]."),
        (
            "Between Kamsa's prison in Mathura and Nandagokula in Vishnu Purana Part 5, Section 3 [S1]."
        ),
        (
            "Vasudeva and Devaki welcome newborn Sri Krishna, exchanged safely with Yashoda's daughter [S1]."
        ),
        (
            "विष्णु पुराण (अंश 5, अध्याय 3) में मथुरा के कारागार में देवकी-वसुदेव के यहाँ भगवान श्रीकृष्ण के दिव्य जन्म और यमुना पार गोकुल पहुँचने की कथा है [S1]।"
        ),
        [
            ("How was Lord Krishna born and taken safely to Gokula in Vishnu Purana?", "how"),
            ("Where is Sri Krishna's birth narrated in the Vishnu Purana?", "where"),
        ],
    ),
    _topic(
        "govardhana_humility",
        "vishnu-purana",
        "Lifting Mount Govardhana: Caring for Nature and Humbling Pride",
        "govardhana indra mountain rain pride humility cowherds krishna nature ecology",
        ["vishnu-purana_5_11_1"],
        (
            "When proud Indra unleashes torrential storms over Vraja because Krishna taught villagers to honor the nourishing cows and Govardhana hill rather than ego-driven ritual pride, young Krishna effortlessly lifts Mount Govardhana on His finger for seven days like a vast umbrella—sheltering every villager and animal until Indra humbles himself [S1]."
        ),
        (
            "Govardhana celebrates stewardship of real local life—forests, hills, cattle, and community—above pompous pride, showing even mighty powers must bow to humble service [S1]."
        ),
        (
            "Value real livelihood and ecological care around you, and meet sudden crises calmly while protecting vulnerable people beside you [S1]."
        ),
        ("Narrated during Krishna's Vrindavan youth in Vishnu Purana Part 5 [S1]."),
        ("At Mount Govardhana in Vraja (Vishnu Purana Part 5, Section 11) [S1]."),
        (
            "Child Krishna shields the cowherd community while Indra realizes his arrogant mistake [S1]."
        ),
        (
            "विष्णु पुराण (अंश 5, अध्याय 11) में इंद्र का अहंकार तोड़ने और ब्रजवासियों व गोधन की रक्षा करने के लिए बालकृष्ण सात दिनों तक गोवर्धन पर्वत धारण करते हैं [S1]।"
        ),
        [
            ("Why did Lord Krishna lift Mount Govardhana in the Vishnu Purana?", "why"),
            ("What does the Govardhana episode teach about pride and ecology?", "what"),
        ],
    ),
    _topic(
        "kamsa_end_mathura",
        "vishnu-purana",
        "Krishna Overthrowing Tyranny and Defeating Kamsa in Mathura",
        "kamsa mathura akrura tyranny liberation dhanushya wrestling krishna",
        ["vishnu-purana_5_20_1"],
        (
            "Arriving in Mathura with Balarama, Krishna blesses humble Kubja straightens her bent frame, breaks the great ceremonial bow, overcomes ferocious traps and wrestlers, and leaps swiftly onto Kamsa's high platform to end the tyrant's terror—freeing aged Devaki, Vasudeva, and King Ugrasena while refusing royal pomp for Himself [S1]."
        ),
        (
            "Strength in Vishnu's hands protects ordinary humble people like Kubja, overthrows cruel tyranny, and restores justice to others rather than seizing power [S1]."
        ),
        (
            "Stand up against injustice cleanly without growing intoxicated by power after victory [S1]."
        ),
        (
            "Climaxes Krishna's youth journey from Vrindavan to Mathura in Vishnu Purana Part 5 [S1]."
        ),
        ("In Mathura city and Kamsa's arena (Vishnu Purana Part 5, Section 20) [S1]."),
        ("Lord Krishna and Balarama defeat Kamsa and liberate their parents and citizens [S1]."),
        (
            "मथुरा में भगवान श्रीकृष्ण और बलराम ने कुब्जा का उद्धार कर क्रूर कंस का वध किया तथा अपने माता-पिता और प्रजा को अत्याचार से मुक्त कराया [S1]।"
        ),
        [
            ("How did Krishna defeat Kamsa in Mathura?", "how"),
            (
                "What happened when Krishna and Balarama met Kubja and entered Kamsa's court?",
                "what",
            ),
        ],
    ),
    _topic(
        "dissolution_pralaya",
        "vishnu-purana",
        "Cosmic Cycles of Creation and Dissolution (Pralaya)",
        "pralaya dissolution time kalpa cycles cosmos rebirth impermanence part 6",
        ["vishnu-purana_6_3_1", "vishnu-purana_6_4_1"],
        (
            "Vishnu Purana Part 6 outlines cosmic time and dissolution (Pralaya): periodic rest at the end of Brahma's day (Naimittika), deep elemental merger into subtle Prakriti (Prakritika) [S1][S2], and ultimate individual spiritual dissolution (Atyantika) through liberation beyond rebirth."
        ),
        (
            "Contemplating vast cosmic cycles cures shortsighted panic over temporary ups and downs, reminding us to anchor hope in what does not dissolve [S1][S2]."
        ),
        (
            "Step back from passing worldly setbacks with cosmic perspective while focusing seriously on inner realization and compassion [S1][S2]."
        ),
        ("Concludes cosmic philosophy near the end of Vishnu Purana Part 6 [S1][S2]."),
        ("Vishnu Purana Part 6, Sections 3 and 4 [S1][S2]."),
        (
            "Sage Parashara instructs Maitreya on vast timescales, Kalpas, and ultimate liberation [S1][S2]."
        ),
        (
            "विष्णु पुराण के छठे अंश (अध्याय 3-4) में नैमित्तिक, प्राकृतिक और आत्यंतिक प्रलय तथा ब्रह्मांड के सृष्टि-संहार चक्र का वर्णन है [S1][S2]।"
        ),
        [
            ("What are the kinds of cosmic dissolution (Pralaya) in Vishnu Purana?", "what"),
            ("Where does Vishnu Purana explain cosmic cycles and Pralaya?", "where"),
        ],
    ),
    _topic(
        "keshidhwaja_khandikya_yoga",
        "vishnu-purana",
        "Keshidhwaja and Khandikya: Overcoming Ignorance Through Contemplative Yoga",
        "keshidhwaja khandikya yoga meditation overcoming ignorance brahman liberation part 6",
        ["vishnu-purana_6_6_1", "vishnu-purana_6_7_1"],
        (
            "At the grand climax of the Vishnu Purana, rival royal cousins Keshidhwaja and Khandikya lay aside hostility to help one another—exchanging ritual guidance for supreme contemplative Yoga [S1]. Keshidhwaja explains how ignorance confuses the eternal Self with the transient body, and how disciplined breath, ethical restraint, focus, and meditation on Vasudeva dissolve ignorance into liberation [S2]."
        ),
        (
            "True spiritual mastery transforms even old enemies into mutual teachers—showing how Yoga unites serene intellect, ethical conduct, and devotion at the Purana's finale [S1][S2]."
        ),
        (
            "Begin meditation by purifying conduct, settling the mind gently onto one pure form or truth, and gradually resting in quiet unity without ego [S2]."
        ),
        (
            "Serves as the philosophical and practical crown closing the entire Vishnu Purana in Part 6 [S1][S2]."
        ),
        ("Vishnu Purana Part 6, Sections 6 and 7 [S1][S2]."),
        (
            "Wise king Keshidhwaja instructs former rival Khandikya in contemplative Yoga, concluding Parashara's teaching to Maitreya [S1][S2]."
        ),
        (
            "विष्णु पुराण के समापन (अंश 6, अध्याय 6-7) में राजा केशिध्वज और खांडिक्य के संवाद द्वारा अज्ञान के नाश व ध्यान-योग से मोक्ष प्राप्त करने का मार्ग बताया गया है [S1][S2]।"
        ),
        [
            ("What did Keshidhwaja teach Khandikya about Yoga and ignorance?", "what"),
            ("How does Vishnu Purana end its teachings on liberation and meditation?", "how"),
        ],
    ),
    # ── Cross-Scripture Comparisons & Synthesis ─────────────────────────
    _topic(
        "three_scriptures_unity",
        "all",
        "How the Bhagavad Gita, Ramayana, and Vishnu Purana Connect",
        "compare gita ramayana vishnu purana difference connection how texts relate",
        ["bhagavad-gita_4_7", "valmiki-ramayana_1_1_1", "vishnu-purana_1_1_1"],
        (
            "Together, these three classics present dharma from complementary angles: the Bhagavad Gita distills crisp philosophy and Yoga directly at a moment of crisis [S1]; the Valmiki Ramayana shows lived dharma unfolding across family, exile, friendship, and leadership [S2]; and the Vishnu Purana maps cosmic origins, devotion, stories of avatars, and liberating meditation across ages [S3]."
        ),
        (
            "Studying philosophy (Gita), human character (Ramayana), and cosmic vision (Vishnu Purana) side by side prevents narrow readings and deepens balanced wisdom [S1][S2][S3]."
        ),
        (
            "Turn to the Gita when seeking sharp daily clarity [S1], the Ramayana for role-model choices in relationships [S2], and the Vishnu Purana for sweeping cosmic devotion [S3]."
        ),
        (
            "Anytime you explore Gyan Sutra's library and wonder which text suits your current question [S1][S2][S3]."
        ),
        (
            "All three texts are complete in Gyan Sutra: Gita 4.7 [S1], Ramayana 1.1 [S2], and Vishnu Purana 1.1 [S3]."
        ),
        (
            "Krishna teaches Arjuna in the Gita, Valmiki narrates Rama from Narada's account, and Parashara instructs Maitreya in the Vishnu Purana [S1][S2][S3]."
        ),
        (
            "भगवद्गीता जीवन के कठिन मोड़ों पर स्पष्ट कर्म-ज्ञान-भक्ति दर्शन देती है [S1], वाल्मीकि रामायण श्रीराम के आदर्श चरित्र से मानवीय संबंधों में धर्म सिखाती है [S2], और विष्णु पुराण सृष्टि, भक्ति व ब्रह्मांडीय दृष्टि प्रदान करता है [S3]।"
        ),
        [
            ("How do the Bhagavad Gita, Ramayana, and Vishnu Purana differ and connect?", "what"),
            ("Which scripture should I read for philosophy vs stories vs devotion?", "what"),
            ("Gita, Ramayana aur Vishnu Purana mein kya sambandh aur antar hai?", "what"),
        ],
    ),
    _topic(
        "rama_embodies_gita",
        "all",
        "How Lord Rama Embodies Equanimity and Karma Yoga",
        "compare rama krishna sthitaprajna equanimity duty exile connection gita ramayana",
        ["bhagavad-gita_2_56", "valmiki-ramayana_2_19_1"],
        (
            "In Gita 2.56, Krishna defines a person of steady wisdom (Sthitaprajna) as unshaken by sorrow and free from craving pleasure, anger, or fear [S1]. When sudden forest exile strips away Rama's royal coronation in Ayodhya Kanda, Rama accepts the hardship serenely without bitterness or rage—living out that exact inner equipoise in action [S2]."
        ),
        (
            "Seeing Gita principles mirrored in Rama's conduct transforms abstract philosophy into an unmistakable human example [S1][S2]."
        ),
        (
            "Keep calm integrity during sudden loss or praise—acting diligently on right responsibility just as Krishna teaches and Rama demonstrates [S1][S2]."
        ),
        ("Reflect on both passages whenever sudden reversals test emotional balance [S1][S2]."),
        (
            "Compare Gita Chapter 2 Verse 2.56 [S1] directly with Ayodhya Kanda Sarga 19 Verse 1 [S2]."
        ),
        (
            "Sri Krishna defines steady wisdom in philosophy while Sri Rama models it effortlessly in lived conduct [S1][S2]."
        ),
        (
            "भगवद्गीता 2.56 में श्रीकृष्ण जिस 'स्थितप्रज्ञ' समत्व की परिभाषा देते हैं [S1], श्रीराम राज्याभिषेक से अचानक 14 वर्ष का वनवास मिलने पर भी शांत रहकर उसी आदर्श को जीवन में जी कर दिखाते हैं [S2]।"
        ),
        [
            ("How does Lord Rama demonstrate the Bhagavad Gita's teaching on equanimity?", "how"),
            ("What connects Gita 2.56 and Rama accepting exile?", "what"),
        ],
    ),
    _topic(
        "vishvarupa_cosmic_vision",
        "bhagavad-gita",
        "Cosmic Form of Krishna (Vishvarupa Darshan)",
        "vishvarupa cosmic form universal form chapter 11 arjuna time awe",
        ["bhagavad-gita_11_32", "bhagavad-gita_11_55"],
        (
            "In Gita Chapter 11, Krishna grants Arjuna divine sight to witness the Vishvarupa—cosmic time, creation, galaxies, and dissolution unfolding within one limitless Reality [S1]. Yet Krishna closes the chapter gently by stating that pure, malice-free loving devotion attains Him most intimately [S2]."
        ),
        (
            "Cosmic awe cures human arrogance: remembering the vastness of time humbles personal fear while devotion anchors that cosmic majesty directly in love [S1][S2]."
        ),
        (
            "Work diligently as an instrument of justice without ego [S1], holding both deep wonder toward creation and tender goodwill toward all beings [S2]."
        ),
        (
            "Revealed mid-dialogue at Arjuna's heartfelt request right at the heart of the Bhagavad Gita [S1][S2]."
        ),
        (
            "Bhagavad Gita Chapter 11 (highlighting 11.32 and the concluding essence 11.55) [S1][S2]."
        ),
        (
            "Arjuna beholds the universal cosmic form and bows to Sri Krishna with humbled devotion [S1][S2]."
        ),
        (
            "भगवद्गीता अध्याय 11 में श्रीकृष्ण अर्जुन को अपना विराट विश्वरूप दिखाते हैं और अंत में समझाते हैं कि द्वेष-रहित अनन्य भक्ति से ही परमात्मा की प्राप्ति होती है [S1][S2]।"
        ),
        [
            ("What is Vishvarupa in Bhagavad Gita Chapter 11?", "what"),
            ("How is the Cosmic Form attained according to Gita 11.55?", "how"),
        ],
    ),
    _topic(
        "lakshmana_anklets_respect",
        "valmiki-ramayana",
        "Lakshmana Recognizing Only Sita's Anklets (Nupura Episode)",
        "lakshmana sita anklets jewels respect dignity kishkindha devotion",
        ["valmiki-ramayana_4_6_1"],
        (
            "When Sugriva shows the bundle of jewels Sita dropped from Ravana's aerial chariot, tearful Rama asks Lakshmana to identify them [S1]. Lakshmana gently replies that out of lifelong reverence he never raised his gaze to Devi Sita's face or necklaces—he recognizes only her anklets because he bowed daily at her feet [S1]."
        ),
        (
            "This tender Kishkindha Kanda episode sets an enduring model of respectful family boundaries, chastity of gaze, and quiet honor [S1]."
        ),
        (
            "Cultivate respectful eyes and dignified humility in family and community life without loud boastfulness [S1]."
        ),
        (
            "Takes place shortly after Rama meets Sugriva at Rishyamuka mountain during the search for Sita [S1]."
        ),
        ("In Kishkindha Kanda, Sarga 6 upon examining Sita's fallen ornaments [S1]."),
        ("Lakshmana speaks respectfully to grieving Sri Rama in Sugriva's presence [S1]."),
        (
            "किष्किन्धाकाण्ड में सीता जी के आभूषण देखकर लक्ष्मण कहते हैं कि वे न तो कंगन और न ही कुंडल पहचानते हैं—वे केवल प्रतिदिन चरण-वंदना करने के कारण केवल नूपुर (पायल) ही पहचानते हैं [S1]।"
        ),
        [
            ("Why could Lakshmana recognize only Sita's anklets?", "why"),
            ("Where does Sugriva show Sita's ornaments to Rama and Lakshmana?", "where"),
        ],
    ),
    _topic(
        "trijata_hope_ashoka_vatika",
        "valmiki-ramayana",
        "Trijata's Compassion and Hopeful Dream for Sita in Lanka",
        "trijata dream hope compassion ashoka vatika rakshasi sita endurance",
        ["valmiki-ramayana_5_27_1"],
        (
            "Among fierce captors threatening Sita in Ashoka Vatika, elderly sage-like Trijata treats Sita tenderly like a daughter and shares a vivid prophetic dream foreseeing Rama's victory, Ravana's downfall, and Sita's reunion with her beloved—giving Sita vital strength to hold on [S1]."
        ),
        (
            "Trijata shows that individual conscience and kindness can shine anywhere—even inside hostile surroundings—and bring hope to those in despair [S1]."
        ),
        (
            "Refuse to join cruelty just because everyone around you does; speak gentle truth and stand kindly with vulnerable people [S1]."
        ),
        ("Unfolds on the night before Hanuman meets Sita directly in Ashoka Vatika [S1]."),
        ("Ashoka Vatika in Sundara Kanda, Sarga 27 [S1]."),
        ("Compassionate Trijata comforts Devi Sita while rebuking cruel guards [S1]."),
        (
            "सुन्दरकाण्ड (सर्ग 27) में त्रिजटा अपने शुभ स्वप्न का वर्णन कर अशोक वाटिका में माता सीता को ढांढस बंधाती हैं और श्रीराम की विजय का विश्वास दिलाती हैं [S1]।"
        ),
        [
            ("Who was Trijata and how did she comfort Sita in Sundara Kanda?", "who"),
            ("What did Trijata see in her dream in Sundara Kanda Sarga 27?", "what"),
        ],
    ),
    _topic(
        "prithu_earth_stewardship",
        "vishnu-purana",
        "King Vena, Ideal King Prithu, and Care for the Earth",
        "prithu vena king earth ecology stewardship prosperity vishnu purana 1.13",
        ["vishnu-purana_1_13_1"],
        (
            "Vishnu Purana Part 1 Section 13 contrasts arrogant tyrant King Vena (whose selfishness caused famine and disorder) with virtuous King Prithu, who honored sages, cared for citizens' nourishment, and leveled Earth gently with Mother Earth's consent so crops, law, and prosperity flourished—earning the Earth her name 'Prithvi' [S1]."
        ),
        (
            "Prithu and Vena contrast extractive tyranny against nurturing stewardship—teaching that true kingship thrives only when nature and citizens flourish together [S1]."
        ),
        (
            "Lead family, work, or civic life with stewardship: nurture resources sustainably and reject arrogant entitlement [S1]."
        ),
        (
            "Told within the early royal lineage narratives following Dhruva in Vishnu Purana Part 1 [S1]."
        ),
        ("Vishnu Purana Part 1, Section 13 [S1]."),
        ("Wise King Prithu succeeds tyrannical Vena and establishes harmonious prosperity [S1]."),
        (
            "विष्णु पुराण (अंश 1, अध्याय 13) में अधर्मी राजा वेन के विपरीत आदर्श राजा पृथु की कथा है, जिन्होंने पृथ्वी का पोषण और प्रजा की रक्षा कर धरती को 'पृथ्वी' नाम दिया [S1]।"
        ),
        [
            ("Why is the Earth named Prithvi after King Prithu in the Vishnu Purana?", "why"),
            ("What does the contrast between Vena and Prithu teach?", "what"),
        ],
    ),
    _topic(
        "rasa_lila_gopis_vrindavan",
        "vishnu-purana",
        "Autumn Moon in Vrindavan: Krishna and the Gopis' Pure Love",
        "gopis vrindavan rasa lila autumn flute love bhakti krishna vishnu purana 5.13",
        ["vishnu-purana_5_13_1"],
        (
            "On radiant autumn nights in Vrindavan, hearing Krishna's enchanting flute calls, the cowherd women (Gopis) set aside pride and household distraction to celebrate joyful sacred dance around Krishna [S1]. When Krishna briefly vanishes to test egotistic clinging and the Gopis feel His presence everywhere inside themselves, He returns to bless each soul equally [S1]."
        ),
        (
            "In the Vishnu Purana, Rasa expresses the longing of the individual heart (Atman) for unbroken union with the Divine—showing love blooms brightest when pride fades [S1]."
        ),
        (
            "Keep devotion joyful, humble, and free from possessive vanity—feeling the Divine close even in seasons of longing [S1]."
        ),
        (
            "During autumn nights in Vrindavan, midway through Krishna's youth in Vishnu Purana Part 5 [S1]."
        ),
        ("Vishnu Purana Part 5, Section 13 [S1]."),
        ("Sri Krishna and the devoted Gopis along the Yamuna woods in Vrindavan [S1]."),
        (
            "विष्णु पुराण (अंश 5, अध्याय 13) में शरद् पूर्णिमा की रात्रि में श्रीकृष्ण और गोपियों की रासलीला तथा अहंकार-रहित विशुद्ध प्रेम-भक्ति का सुंदर वर्णन है [S1]।"
        ),
        [
            (
                "What is the deeper meaning of Krishna and the Gopis' Rasa in Vishnu Purana 5.13?",
                "what",
            ),
            ("Where in the Vishnu Purana is the autumn dance with the Gopis told?", "where"),
        ],
    ),
]
