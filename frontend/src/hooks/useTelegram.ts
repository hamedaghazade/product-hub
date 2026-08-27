import { useEffect, useState } from 'react';

declare global {
  interface Window {
    Telegram?: {
      WebApp: any;
    };
  }
}

export function useTelegram() {
  const [tg, setTg] = useState<any>(null);
  const [user, setUser] = useState<any>(null);
  const [initData, setInitData] = useState<string>('');

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      const webapp = window.Telegram.WebApp;
      webapp.ready();
      webapp.expand();
      setTg(webapp);
      setInitData(webapp.initData || '');
      setUser(webapp.initDataUnsafe?.user || null);
    }
  }, []);

  const closeApp = () => tg?.close();
  const sendData = (data: object) => tg?.sendData(JSON.stringify(data));

  return {
    tg,
    user,
    initData,
    closeApp,
    sendData,
    isTelegram: !!window.Telegram?.WebApp?.initData
  };
}