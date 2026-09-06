// Core AgriSense UI translations. Keys are dot-namespaced by area
// (nav.*, common.*, dashboard.*, etc). Add a language by adding a new
// top-level key here — useTranslation() falls back to English for any
// key missing in the active language, so partial translations never break.
//
// Coverage note: this first pass covers navigation, page titles/subtitles,
// common buttons/labels, and dashboard card titles/empty-states — the
// highest-traffic chrome a farmer sees on every visit. Deeper page content
// (individual form field labels, longer explanatory text, error message
// bodies) still renders in English in this pass; extend TRANSLATIONS with
// more keys and swap the relevant t('key') calls into those pages the same
// way as the ones already converted.

export const TRANSLATIONS = {
  en: {
    nav: {
      dashboard: 'Dashboard', chat: 'AI Chatbot', weather: 'Weather',
      crop: 'Crop Recommendation', soil: 'Soil Analysis', plantHealth: 'Plant Health',
      irrigation: 'Irrigation Advisor', market: 'Market Info', history: 'History',
      profile: 'Farmer Profile', settings: 'Settings',
    },
    common: {
      loading: 'Loading…', tryAgain: 'Try again', save: 'Save', search: 'Search',
      analyze: 'Analyze', cancel: 'Cancel', language: 'Language', optional: 'optional',
      newChat: 'New chat', send: 'Send', submit: 'Submit',
    },
    dashboard: {
      welcomeBack: 'Welcome back', welcome: 'Welcome to AgriSense',
      subtitle: "Here's what's happening on your farm today.",
      todayWeather: "Today's Weather", currentCrop: 'Current Crop', soilStatus: 'Soil Status',
      irrigation: 'Irrigation', alerts: 'Alerts', noAlerts: 'No alerts right now.',
      incompleteProfile: 'Your farmer profile is incomplete — add your crop and location in Profile for personalized recommendations.',
    },
    weather: { title: 'Weather', subtitle: 'Live data — the chatbot uses this same feed.' },
    crop: { title: 'Crop Recommendation', subtitle: 'Tell us about your farm for suitable crop suggestions.' },
    soil: { title: 'Soil Analysis', subtitle: 'Understand your soil — with or without lab values.' },
    plantHealth: { title: 'Plant Health', subtitle: 'Upload a clear photo of the affected crop for analysis.' },
    irrigationPage: { title: 'Irrigation Advisor', subtitle: 'Combines your location, weather forecast, and crop stage.' },
    market: { title: 'Market Information', subtitle: 'Real mandi prices where available — never estimated numbers.' },
    profile: { title: 'Farmer Profile', subtitle: 'Used to personalize recommendations across the app.' },
    history: { title: 'History', subtitle: 'Your past analyses across AgriSense.' },
    settings: { title: 'Settings', subtitle: 'AgriSense runs locally with a single farm profile — no account needed.' },
    landing: {
      tagline: 'Farming advice that checks the sky before it speaks.',
      cta: 'Open AgriSense',
    },
  },

  hi: {
    nav: {
      dashboard: 'डैशबोर्ड', chat: 'AI सहायक', weather: 'मौसम',
      crop: 'फसल सिफारिश', soil: 'मिट्टी विश्लेषण', plantHealth: 'पौधों का स्वास्थ्य',
      irrigation: 'सिंचाई सलाह', market: 'बाजार भाव', history: 'इतिहास',
      profile: 'किसान प्रोफ़ाइल', settings: 'सेटिंग्स',
    },
    common: {
      loading: 'लोड हो रहा है…', tryAgain: 'पुनः प्रयास करें', save: 'सहेजें', search: 'खोजें',
      analyze: 'विश्लेषण करें', cancel: 'रद्द करें', language: 'भाषा', optional: 'वैकल्पिक',
      newChat: 'नई बातचीत', send: 'भेजें', submit: 'जमा करें',
    },
    dashboard: {
      welcomeBack: 'वापसी पर स्वागत है', welcome: 'AgriSense में आपका स्वागत है',
      subtitle: 'आज आपके खेत में यह हो रहा है।',
      todayWeather: 'आज का मौसम', currentCrop: 'वर्तमान फसल', soilStatus: 'मिट्टी की स्थिति',
      irrigation: 'सिंचाई', alerts: 'चेतावनियाँ', noAlerts: 'अभी कोई चेतावनी नहीं है।',
      incompleteProfile: 'आपकी किसान प्रोफ़ाइल अधूरी है — व्यक्तिगत सिफारिशों के लिए प्रोफ़ाइल में अपनी फसल और स्थान जोड़ें।',
    },
    weather: { title: 'मौसम', subtitle: 'लाइव डेटा — चैटबॉट भी इसी स्रोत का उपयोग करता है।' },
    crop: { title: 'फसल सिफारिश', subtitle: 'उपयुक्त फसल सुझावों के लिए अपने खेत के बारे में बताएं।' },
    soil: { title: 'मिट्टी विश्लेषण', subtitle: 'लैब मूल्यों के साथ या बिना, अपनी मिट्टी को समझें।' },
    plantHealth: { title: 'पौधों का स्वास्थ्य', subtitle: 'विश्लेषण के लिए प्रभावित फसल की स्पष्ट फोटो अपलोड करें।' },
    irrigationPage: { title: 'सिंचाई सलाह', subtitle: 'आपके स्थान, मौसम पूर्वानुमान और फसल की अवस्था को जोड़ती है।' },
    market: { title: 'बाजार भाव', subtitle: 'जहां उपलब्ध हो वहां वास्तविक मंडी भाव — कभी अनुमानित नहीं।' },
    profile: { title: 'किसान प्रोफ़ाइल', subtitle: 'पूरे ऐप में सिफारिशों को व्यक्तिगत बनाने के लिए उपयोग किया जाता है।' },
    history: { title: 'इतिहास', subtitle: 'AgriSense पर आपके पिछले विश्लेषण।' },
    settings: { title: 'सेटिंग्स', subtitle: 'AgriSense एक ही खेत प्रोफ़ाइल के साथ स्थानीय रूप से चलता है — किसी खाते की आवश्यकता नहीं।' },
    landing: {
      tagline: 'ऐसी खेती सलाह जो बोलने से पहले आसमान की जांच करती है।',
      cta: 'AgriSense खोलें — किसी खाते की आवश्यकता नहीं',
    },
  },

  pa: {
    nav: {
      dashboard: 'ਡੈਸ਼ਬੋਰਡ', chat: 'AI ਸਹਾਇਕ', weather: 'ਮੌਸਮ',
      crop: 'ਫਸਲ ਸਿਫਾਰਸ਼', soil: 'ਮਿੱਟੀ ਵਿਸ਼ਲੇਸ਼ਣ', plantHealth: 'ਪੌਦਿਆਂ ਦੀ ਸਿਹਤ',
      irrigation: 'ਸਿੰਚਾਈ ਸਲਾਹ', market: 'ਮੰਡੀ ਭਾਅ', history: 'ਇਤਿਹਾਸ',
      profile: 'ਕਿਸਾਨ ਪ੍ਰੋਫਾਈਲ', settings: 'ਸੈਟਿੰਗਾਂ',
    },
    common: {
      loading: 'ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ…', tryAgain: 'ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ', save: 'ਸੰਭਾਲੋ', search: 'ਖੋਜੋ',
      analyze: 'ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ', cancel: 'ਰੱਦ ਕਰੋ', language: 'ਭਾਸ਼ਾ', optional: 'ਵਿਕਲਪਿਕ',
      newChat: 'ਨਵੀਂ ਗੱਲਬਾਤ', send: 'ਭੇਜੋ', submit: 'ਜਮ੍ਹਾਂ ਕਰੋ',
    },
    dashboard: {
      welcomeBack: 'ਵਾਪਸੀ ਤੇ ਸਵਾਗਤ ਹੈ', welcome: 'AgriSense ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ',
      subtitle: 'ਅੱਜ ਤੁਹਾਡੇ ਖੇਤ ਵਿੱਚ ਇਹ ਹੋ ਰਿਹਾ ਹੈ।',
      todayWeather: 'ਅੱਜ ਦਾ ਮੌਸਮ', currentCrop: 'ਮੌਜੂਦਾ ਫਸਲ', soilStatus: 'ਮਿੱਟੀ ਦੀ ਸਥਿਤੀ',
      irrigation: 'ਸਿੰਚਾਈ', alerts: 'ਚੇਤਾਵਨੀਆਂ', noAlerts: 'ਹੁਣ ਕੋਈ ਚੇਤਾਵਨੀ ਨਹੀਂ ਹੈ।',
      incompleteProfile: 'ਤੁਹਾਡੀ ਕਿਸਾਨ ਪ੍ਰੋਫਾਈਲ ਅਧੂਰੀ ਹੈ — ਨਿੱਜੀ ਸਿਫਾਰਸ਼ਾਂ ਲਈ ਪ੍ਰੋਫਾਈਲ ਵਿੱਚ ਆਪਣੀ ਫਸਲ ਅਤੇ ਸਥਾਨ ਸ਼ਾਮਲ ਕਰੋ।',
    },
    weather: { title: 'ਮੌਸਮ', subtitle: 'ਲਾਈਵ ਡਾਟਾ — ਚੈਟਬੋਟ ਵੀ ਇਸੇ ਸਰੋਤ ਦੀ ਵਰਤੋਂ ਕਰਦਾ ਹੈ।' },
    crop: { title: 'ਫਸਲ ਸਿਫਾਰਸ਼', subtitle: 'ਢੁਕਵੇਂ ਫਸਲ ਸੁਝਾਵਾਂ ਲਈ ਆਪਣੇ ਖੇਤ ਬਾਰੇ ਦੱਸੋ।' },
    soil: { title: 'ਮਿੱਟੀ ਵਿਸ਼ਲੇਸ਼ਣ', subtitle: 'ਲੈਬ ਮੁੱਲਾਂ ਨਾਲ ਜਾਂ ਬਿਨਾਂ, ਆਪਣੀ ਮਿੱਟੀ ਨੂੰ ਸਮਝੋ।' },
    plantHealth: { title: 'ਪੌਦਿਆਂ ਦੀ ਸਿਹਤ', subtitle: 'ਵਿਸ਼ਲੇਸ਼ਣ ਲਈ ਪ੍ਰਭਾਵਿਤ ਫਸਲ ਦੀ ਸਪਸ਼ਟ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ।' },
    irrigationPage: { title: 'ਸਿੰਚਾਈ ਸਲਾਹ', subtitle: 'ਤੁਹਾਡਾ ਸਥਾਨ, ਮੌਸਮ ਪੂਰਵ ਅਨੁਮਾਨ ਅਤੇ ਫਸਲ ਦੀ ਅਵਸਥਾ ਜੋੜਦਾ ਹੈ।' },
    market: { title: 'ਮੰਡੀ ਭਾਅ', subtitle: 'ਜਿੱਥੇ ਉਪਲਬਧ ਹੋਵੇ ਅਸਲ ਮੰਡੀ ਭਾਅ — ਕਦੇ ਅੰਦਾਜ਼ਾ ਨਹੀਂ।' },
    profile: { title: 'ਕਿਸਾਨ ਪ੍ਰੋਫਾਈਲ', subtitle: 'ਪੂਰੀ ਐਪ ਵਿੱਚ ਸਿਫਾਰਸ਼ਾਂ ਨੂੰ ਨਿੱਜੀ ਬਣਾਉਣ ਲਈ ਵਰਤਿਆ ਜਾਂਦਾ ਹੈ।' },
    history: { title: 'ਇਤਿਹਾਸ', subtitle: 'AgriSense ਤੇ ਤੁਹਾਡੇ ਪਿਛਲੇ ਵਿਸ਼ਲੇਸ਼ਣ।' },
    settings: { title: 'ਸੈਟਿੰਗਾਂ', subtitle: 'AgriSense ਇੱਕ ਸਿੰਗਲ ਫਾਰਮ ਪ੍ਰੋਫਾਈਲ ਨਾਲ ਸਥਾਨਕ ਤੌਰ ਤੇ ਚੱਲਦਾ ਹੈ — ਕਿਸੇ ਖਾਤੇ ਦੀ ਲੋੜ ਨਹੀਂ।' },
    landing: {
      tagline: 'ਖੇਤੀ ਸਲਾਹ ਜੋ ਬੋਲਣ ਤੋਂ ਪਹਿਲਾਂ ਅਸਮਾਨ ਦੀ ਜਾਂਚ ਕਰਦੀ ਹੈ।',
      cta: 'AgriSense ਖੋਲ੍ਹੋ — ਕਿਸੇ ਖਾਤੇ ਦੀ ਲੋੜ ਨਹੀਂ',
    },
  },
}

export function translate(lang, key) {
  const path = key.split('.')
  let node = TRANSLATIONS[lang] || TRANSLATIONS.en
  for (const p of path) {
    node = node?.[p]
    if (node === undefined) break
  }
  if (node !== undefined) return node

  // Fall back to English for any key missing in the active language.
  let fallback = TRANSLATIONS.en
  for (const p of path) {
    fallback = fallback?.[p]
    if (fallback === undefined) return key
  }
  return fallback
}
