'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { ArrowLeft, Settings, Volume2, Eye, Globe, Palette } from 'lucide-react';
import AccessibilityControls from '@/components/Accessibility/AccessibilityControls';
import TTSControls from '@/components/Speech/TTSControls';

export default function SettingsPage() {
  const t = useTranslations();
  const [activeTab, setActiveTab] = useState<'general' | 'accessibility' | 'voice' | 'appearance'>('general');

  const tabs = [
    { id: 'general', name: 'כללי', icon: Settings },
    { id: 'accessibility', name: 'נגישות', icon: Eye },
    { id: 'voice', name: 'קול', icon: Volume2 },
    { id: 'appearance', name: 'מראה', icon: Palette },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-4 h-4" />
              חזור לדף הבית
            </Link>
            <h1 className="text-xl font-display font-bold text-gray-900 flex items-center gap-2">
              <Settings className="w-5 h-5" />
              {t('navigation.settings')}
            </h1>
            <div className="w-20" /> {/* Spacer for centering */}
          </div>
        </div>
      </nav>

      {/* Tab Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-8 overflow-x-auto">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-4 px-2 border-b-2 text-sm font-medium transition-colors whitespace-nowrap min-h-touch ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'general' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-display font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <Globe className="w-5 h-5" />
                הגדרות כלליות
              </h2>

              <div className="space-y-6">
                {/* Language */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('settings.language')}
                  </label>
                  <select className="w-full max-w-xs p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                    <option value="he">עברית</option>
                    <option value="en">English</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    בחר את השפה המועדפת עליך לממשק המשתמש
                  </p>
                </div>

                {/* Theme */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    נושא מועדף
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {['football', 'space', 'robots'].map(theme => (
                      <button
                        key={theme}
                        className="p-4 border-2 border-gray-200 rounded-lg text-center hover:border-primary-300 transition-colors focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                      >
                        <div className="text-2xl mb-2">
                          {theme === 'football' ? '⚽' : theme === 'space' ? '🚀' : '🤖'}
                        </div>
                        <div className="text-sm font-medium">
                          {t(`themes.${theme}`)}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Session Length */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('settings.sessionLength')}
                  </label>
                  <select className="w-full max-w-xs p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                    <option value="15">15 דקות</option>
                    <option value="20">20 דקות</option>
                    <option value="25">25 דקות</option>
                    <option value="30">30 דקות</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    כמה זמן תרצה להקדיש לכל שיעור
                  </p>
                </div>

                {/* Difficulty */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('settings.difficulty')}
                  </label>
                  <div className="flex gap-4">
                    {[
                      { value: 'beginner', label: 'מתחיל', color: 'bg-green-100 text-green-800' },
                      { value: 'intermediate', label: 'בינוני', color: 'bg-yellow-100 text-yellow-800' },
                      { value: 'advanced', label: 'מתקדם', color: 'bg-red-100 text-red-800' },
                    ].map(level => (
                      <button
                        key={level.value}
                        className={`px-4 py-2 rounded-lg text-sm font-medium border-2 border-transparent hover:border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 ${level.color}`}
                      >
                        {level.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Privacy Settings */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-display font-semibold text-gray-900 mb-4">
                פרטיות ונתונים
              </h3>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">שמירת התקדמות מקומית</h4>
                    <p className="text-sm text-gray-600">
                      שמור את ההתקדמות שלך במחשב זה בלבד
                    </p>
                  </div>
                  <div className="w-12 h-6 bg-primary-600 rounded-full p-1">
                    <div className="w-4 h-4 bg-white rounded-full translate-x-6" />
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">🛡️ הגנת פרטיות</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• לא נאספים נתונים אישיים</li>
                    <li>• כל הקוד רץ במחשב שלך</li>
                    <li>• אין העלאות לשרת</li>
                    <li>• ניתן למחוק את כל הנתונים בכל עת</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'accessibility' && (
          <AccessibilityControls />
        )}

        {activeTab === 'voice' && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-display font-semibold text-gray-900 mb-6 flex items-center gap-2">
              <Volume2 className="w-5 h-5" />
              הגדרות קול
            </h2>

            <div className="space-y-6">
              <TTSControls
                text="זהו טקסט לדוגמה בעברית לבדיקת הגדרות הקול"
                showFullControls={true}
              />

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">💡 טיפים לשימוש בקול</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• הקול עוזר לזכור מידע טוב יותר</li>
                  <li>• ניתן להקשיב למדריך תוך כדי כתיבת קוד</li>
                  <li>• מהירות איטית יותר מקלה על הבנה</li>
                  <li>• ניתן לכבות את הקול בכל עת</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'appearance' && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-display font-semibold text-gray-900 mb-6 flex items-center gap-2">
              <Palette className="w-5 h-5" />
              מראה וצבעים
            </h2>

            <div className="space-y-6">
              {/* Color Theme */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  ערכת צבעים
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {[
                    { name: 'ברירת מחדל', colors: ['bg-blue-500', 'bg-green-500', 'bg-purple-500'] },
                    { name: 'חם', colors: ['bg-red-500', 'bg-orange-500', 'bg-yellow-500'] },
                    { name: 'קר', colors: ['bg-blue-500', 'bg-cyan-500', 'bg-teal-500'] },
                  ].map(theme => (
                    <button
                      key={theme.name}
                      className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-300 transition-colors focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                    >
                      <div className="flex justify-center gap-2 mb-2">
                        {theme.colors.map((color, index) => (
                          <div key={index} className={`w-6 h-6 rounded-full ${color}`} />
                        ))}
                      </div>
                      <div className="text-sm font-medium">{theme.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Dark Mode */}
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">מצב לילה</h4>
                  <p className="text-sm text-gray-600">
                    צבעים כהים לשימוש נוח בערב
                  </p>
                </div>
                <button
                  className="w-12 h-6 bg-gray-300 rounded-full p-1 transition-colors hover:bg-gray-400"
                  role="switch"
                  aria-checked={false}
                >
                  <div className="w-4 h-4 bg-white rounded-full transition-transform" />
                </button>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 className="font-medium text-yellow-900 mb-2">🎨 בקרוב</h4>
                <p className="text-sm text-yellow-800">
                  מצב לילה ועוד ערכות צבעים יתווספו בגרסאות עתידיות
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}