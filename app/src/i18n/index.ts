import { getLocales } from "expo-localization";
import { createInstance } from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./en.json";
import es from "./es.json";

export const SUPPORTED_LANGUAGES = ["es", "en"] as const;
export type Language = (typeof SUPPORTED_LANGUAGES)[number];

export function deviceLanguage(): Language {
  const code = getLocales()[0]?.languageCode ?? "es";
  return (SUPPORTED_LANGUAGES as readonly string[]).includes(code) ? (code as Language) : "es";
}

const i18n = createInstance();

void i18n.use(initReactI18next).init({
  resources: { es: { translation: es }, en: { translation: en } },
  lng: deviceLanguage(),
  fallbackLng: "es",
  interpolation: { escapeValue: false },
});

export const t = i18n.t.bind(i18n);
export default i18n;
