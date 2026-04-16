import { createContext, useContext } from 'react';
import { TRANSLATIONS } from './translations';

export const LanguageContext = createContext('zh');

export const useT = () => {
  const lang = useContext(LanguageContext);
  return TRANSLATIONS[lang] || TRANSLATIONS.zh;
};
