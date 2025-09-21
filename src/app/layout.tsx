import { NextIntlClientProvider } from 'next-intl';
import { getMessages, getLocale } from 'next-intl/server';
import TTSProvider from '@/components/Speech/TTSProvider';
import AccessibilityProvider from '@/components/Accessibility/AccessibilityProvider';
import './globals.css';

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = await getLocale();
  const messages = await getMessages();

  // Determine if RTL based on locale
  const isRTL = locale === 'he';

  return (
    <html lang={locale} dir={isRTL ? 'rtl' : 'ltr'} className="h-full">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#3b82f6" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <title>Hebrew AI Tutor - Learn to Code</title>
        <meta
          name="description"
          content="Learn programming through interactive Hebrew lessons with AI guidance"
        />
      </head>
      <body className={`h-full font-hebrew antialiased ${isRTL ? 'layout-rtl' : 'layout-ltr'}`}>
        <NextIntlClientProvider messages={messages}>
          <AccessibilityProvider>
            <TTSProvider defaultConfig={{ enabled: true, language: locale === 'he' ? 'he-IL' : 'en-US' }}>
              <div className="min-h-full bg-gray-50" id="main-content">
                {children}
              </div>
            </TTSProvider>
          </AccessibilityProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}