import { useEffect, useState } from 'react';

declare global {
  interface Window {
    Telegram?: {
      WebApp: any;
    };
  }
}

export function useTelegram() {
  const [webApp, setWebApp] = useState<any>(null);
  const [user, setUser] = useState<any>(null);
  const [initDataRaw, setInitDataRaw] = useState<string>('');

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
      setWebApp(tg);
      setUser(tg.initDataUnsafe?.user);
      setInitDataRaw(tg.initData || '');

      // هماهنگ‌سازی رنگ تم مینی‌اپ با تلگرام کلاینت
      document.documentElement.style.setProperty('--tg-theme-bg-color', tg.backgroundColor || '#ffffff');
      document.documentElement.style.setProperty('--tg-theme-text-color', tg.textColor || '#000000');
      document.documentElement.style.setProperty('--tg-theme-button-color', tg.buttonColor || '#2481cc');
    }
  }, []);

  const showScanQrPopup = (callback: (text: string) => boolean | void) => {
    if (webApp?.showScanQrPopup) {
      webApp.showScanQrPopup({ text: "دوربین را مقابل بارکد کالا بگیرید" }, (scannedData: string) => {
        const shouldClose = callback(scannedData);
        if (shouldClose !== false) {
          webApp.closeScanQrPopup();
        }
      });
    }
  };

  const sendHapticFeedback = (type: 'impact' | 'notification' | 'selection' = 'impact') => {
    webApp?.HapticFeedback?.impactOccurred('medium');
  };

  return {
    webApp,
    user,
    initDataRaw,
    isInsideTelegram: Boolean(webApp && initDataRaw),
    showScanQrPopup,
    sendHapticFeedback
  };
}