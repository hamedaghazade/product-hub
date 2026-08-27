import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
}

interface TelegramContextType {
  tg: any | null;
  user: TelegramUser | null;
  initData: string;
  isReady: boolean;
  hapticNotification: (type: 'error' | 'success' | 'warning') => void;
  hapticImpact: (style: 'light' | 'medium' | 'heavy') => void;
  closeApp: () => void;
}

const TelegramContext = createContext<TelegramContextType>({
  tg: null,
  user: null,
  initData: '',
  isReady: false,
  hapticNotification: () => {},
  hapticImpact: () => {},
  closeApp: () => {},
});

export const TelegramProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [tg, setTg] = useState<any>(null);
  const [isReady, setIsReady] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      const webapp = window.Telegram.WebApp;
      webapp.ready();
      webapp.expand();
      
      // تنظیم رنگ هدر با پالت تلگرام
      if (webapp.setHeaderColor) {
        webapp.setHeaderColor('secondary_bg_color');
      }
      
      setTg(webapp);
      setIsReady(true);
    } else {
      setIsReady(true); // اجرای مستقل در مرورگر وب
    }
  }, []);

  const user = useMemo<TelegramUser | null>(() => {
    return tg?.initDataUnsafe?.user || null;
  }, [tg]);

  const initData = useMemo<string>(() => {
    return tg?.initData || '';
  }, [tg]);

  const hapticNotification = (type: 'error' | 'success' | 'warning') => {
    tg?.HapticFeedback?.notificationOccurred(type);
  };

  const hapticImpact = (style: 'light' | 'medium' | 'heavy') => {
    tg?.HapticFeedback?.impactOccurred(style);
  };

  const closeApp = () => {
    tg?.close();
  };

  return (
    <TelegramContext.Provider
      value={{
        tg,
        user,
        initData,
        isReady,
        hapticNotification,
        hapticImpact,
        closeApp,
      }}
    >
      {children}
    </TelegramContext.Provider>
  );
};

export const useTelegramContext = () => useContext(TelegramContext);