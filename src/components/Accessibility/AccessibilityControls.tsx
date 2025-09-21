'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useAccessibility } from './AccessibilityProvider';
import {
  Eye,
  MousePointer,
  Volume2,
  Type,
  Contrast,
  Zap,
  Settings,
  RotateCcw,
  ChevronDown,
} from 'lucide-react';

interface AccessibilityControlsProps {
  compact?: boolean;
}

export default function AccessibilityControls({ compact = false }: AccessibilityControlsProps) {
  const t = useTranslations();
  const { settings, updateSetting, resetSettings, announceToScreenReader } = useAccessibility();
  const [isExpanded, setIsExpanded] = useState(false);

  const fontSizeOptions = [
    { value: 'small', label: 'קטן', size: '14px' },
    { value: 'medium', label: 'בינוני', size: '16px' },
    { value: 'large', label: 'גדול', size: '18px' },
    { value: 'xlarge', label: 'ענק', size: '20px' },
  ];

  const handleSettingChange = (setting: string, value: any) => {
    updateSetting(setting as any, value);
    announceToScreenReader(`${setting} השתנה ל${value}`);
  };

  if (compact) {
    return (
      <div className="relative">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="btn-secondary p-2 min-h-touch min-w-touch"
          title={t('accessibility.toggleAccessibility')}
          aria-label="פתח הגדרות נגישות"
          aria-expanded={isExpanded}
        >
          <Eye className="w-4 h-4" />
        </button>

        {isExpanded && (
          <div className="absolute top-full left-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-4 w-80 z-50">
            <h3 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
              <Eye className="w-4 h-4" />
              הגדרות נגישות
            </h3>

            <div className="space-y-4">
              {/* High Contrast */}
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm">
                  <Contrast className="w-4 h-4" />
                  {t('accessibility.highContrast')}
                </label>
                <button
                  onClick={() => handleSettingChange('highContrast', !settings.highContrast)}
                  className={`w-10 h-6 rounded-full transition-colors ${
                    settings.highContrast ? 'bg-primary-600' : 'bg-gray-300'
                  }`}
                  role="switch"
                  aria-checked={settings.highContrast}
                >
                  <div
                    className={`w-4 h-4 bg-white rounded-full transition-transform ${
                      settings.highContrast ? 'translate-x-4' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>

              {/* Reduced Motion */}
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm">
                  <Zap className="w-4 h-4" />
                  {t('accessibility.reduceMotion')}
                </label>
                <button
                  onClick={() => handleSettingChange('reducedMotion', !settings.reducedMotion)}
                  className={`w-10 h-6 rounded-full transition-colors ${
                    settings.reducedMotion ? 'bg-primary-600' : 'bg-gray-300'
                  }`}
                  role="switch"
                  aria-checked={settings.reducedMotion}
                >
                  <div
                    className={`w-4 h-4 bg-white rounded-full transition-transform ${
                      settings.reducedMotion ? 'translate-x-4' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>

              {/* Font Size */}
              <div>
                <label className="flex items-center gap-2 text-sm mb-2">
                  <Type className="w-4 h-4" />
                  {t('settings.fontSize')}
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {fontSizeOptions.map(option => (
                    <button
                      key={option.value}
                      onClick={() => handleSettingChange('fontSize', option.value)}
                      className={`p-2 text-xs rounded border transition-colors ${
                        settings.fontSize === option.value
                          ? 'bg-primary-100 border-primary-300 text-primary-800'
                          : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                      }`}
                      style={{ fontSize: option.size }}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Reset */}
              <button
                onClick={() => {
                  resetSettings();
                  announceToScreenReader('הגדרות נגישות אופסו');
                }}
                className="btn-secondary w-full text-xs"
              >
                <RotateCcw className="w-3 h-3 me-1" />
                איפוס הגדרות
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-xl font-display font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <Eye className="w-5 h-5" />
        הגדרות נגישות
      </h2>

      <div className="space-y-6">
        {/* Visual Settings */}
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center gap-2">
            <Contrast className="w-4 h-4" />
            הגדרות חזותיות
          </h3>

          <div className="space-y-4">
            {/* High Contrast */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">ניגודיות גבוהה</h4>
                <p className="text-sm text-gray-600">
                  מגביר את הניגודיות בין טקסט לרקע לקריאה טובה יותר
                </p>
              </div>
              <button
                onClick={() => handleSettingChange('highContrast', !settings.highContrast)}
                className={`w-12 h-6 rounded-full transition-colors min-h-touch ${
                  settings.highContrast ? 'bg-primary-600' : 'bg-gray-300'
                }`}
                role="switch"
                aria-checked={settings.highContrast}
                aria-label="הפעל ניגודיות גבוהה"
              >
                <div
                  className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    settings.highContrast ? 'translate-x-6' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>

            {/* Font Size */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">גודל גופן</h4>
              <div className="grid grid-cols-2 gap-2">
                {fontSizeOptions.map(option => (
                  <button
                    key={option.value}
                    onClick={() => handleSettingChange('fontSize', option.value)}
                    className={`p-3 rounded border transition-colors min-h-touch ${
                      settings.fontSize === option.value
                        ? 'bg-primary-100 border-primary-300 text-primary-800'
                        : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-100'
                    }`}
                    style={{ fontSize: option.size }}
                  >
                    {option.label} ({option.size})
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Motion Settings */}
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            הגדרות תנועה
          </h3>

          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">הפחתת תנועה</h4>
                <p className="text-sm text-gray-600">
                  מצמצם אנימציות ותנועות עבור חוויה רגועה יותר
                </p>
              </div>
              <button
                onClick={() => handleSettingChange('reducedMotion', !settings.reducedMotion)}
                className={`w-12 h-6 rounded-full transition-colors min-h-touch ${
                  settings.reducedMotion ? 'bg-primary-600' : 'bg-gray-300'
                }`}
                role="switch"
                aria-checked={settings.reducedMotion}
                aria-label="הפעל הפחתת תנועה"
              >
                <div
                  className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    settings.reducedMotion ? 'translate-x-6' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Navigation Settings */}
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center gap-2">
            <MousePointer className="w-4 h-4" />
            הגדרות ניווט
          </h3>

          <div className="space-y-4">
            {/* Enhanced Focus */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">מיקוד משופר</h4>
                <p className="text-sm text-gray-600">
                  מדגיש את האלמנט המוקד בצורה ברורה יותר
                </p>
              </div>
              <button
                onClick={() => handleSettingChange('focusIndicator', !settings.focusIndicator)}
                className={`w-12 h-6 rounded-full transition-colors min-h-touch ${
                  settings.focusIndicator ? 'bg-primary-600' : 'bg-gray-300'
                }`}
                role="switch"
                aria-checked={settings.focusIndicator}
                aria-label="הפעל מיקוד משופר"
              >
                <div
                  className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    settings.focusIndicator ? 'translate-x-6' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>

            {/* Screen Reader Optimization */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">אופטימיזציה לקורא מסך</h4>
                <p className="text-sm text-gray-600">
                  מוסיף תיאורים וסמנטיקה עבור קוראי מסך
                </p>
              </div>
              <button
                onClick={() => handleSettingChange('screenReaderOptimized', !settings.screenReaderOptimized)}
                className={`w-12 h-6 rounded-full transition-colors min-h-touch ${
                  settings.screenReaderOptimized ? 'bg-primary-600' : 'bg-gray-300'
                }`}
                role="switch"
                aria-checked={settings.screenReaderOptimized}
                aria-label="הפעל אופטימיזציה לקורא מסך"
              >
                <div
                  className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    settings.screenReaderOptimized ? 'translate-x-6' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Keyboard Shortcuts */}
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-4">קיצורי מקלדת</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>דלג לתוכן הראשי</span>
                <kbd className="bg-gray-200 px-2 py-1 rounded text-xs">Tab + Enter</kbd>
              </div>
              <div className="flex justify-between">
                <span>פתח/סגור תפריט</span>
                <kbd className="bg-gray-200 px-2 py-1 rounded text-xs">Alt + M</kbd>
              </div>
              <div className="flex justify-between">
                <span>הרץ קוד</span>
                <kbd className="bg-gray-200 px-2 py-1 rounded text-xs">Ctrl + Enter</kbd>
              </div>
              <div className="flex justify-between">
                <span>קבל רמז</span>
                <kbd className="bg-gray-200 px-2 py-1 rounded text-xs">F1</kbd>
              </div>
            </div>
          </div>
        </div>

        {/* Reset Button */}
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={() => {
              resetSettings();
              announceToScreenReader('כל הגדרות הנגישות אופסו לברירת מחדל');
            }}
            className="btn-secondary w-full"
          >
            <RotateCcw className="w-4 h-4 me-2" />
            איפוס לברירת מחדל
          </button>
        </div>
      </div>
    </div>
  );
}