'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { Flame, Calendar, Zap, Shield } from 'lucide-react';

interface StreakDisplayProps {
  currentStreak: number;
  longestStreak: number;
  streakSavers: number;
  lastActiveDate?: Date;
  compact?: boolean;
}

export default function StreakDisplay({
  currentStreak,
  longestStreak,
  streakSavers,
  lastActiveDate,
  compact = false,
}: StreakDisplayProps) {
  const t = useTranslations();

  const isActiveToday = lastActiveDate &&
    new Date().toDateString() === lastActiveDate.toDateString();

  const getStreakColor = (streak: number) => {
    if (streak >= 30) return 'text-purple-600';
    if (streak >= 14) return 'text-orange-600';
    if (streak >= 7) return 'text-yellow-600';
    if (streak >= 3) return 'text-blue-600';
    return 'text-gray-600';
  };

  const getStreakBgColor = (streak: number) => {
    if (streak >= 30) return 'bg-purple-100 border-purple-200';
    if (streak >= 14) return 'bg-orange-100 border-orange-200';
    if (streak >= 7) return 'bg-yellow-100 border-yellow-200';
    if (streak >= 3) return 'bg-blue-100 border-blue-200';
    return 'bg-gray-100 border-gray-200';
  };

  const getStreakMessage = (streak: number) => {
    if (streak >= 30) return 'אלוף הרצף! 🏆';
    if (streak >= 14) return 'רצף מדהים! 🔥';
    if (streak >= 7) return 'רצף שבועי! ⭐';
    if (streak >= 3) return 'רצף יפה! 👍';
    if (streak >= 1) return 'התחלה טובה! 🎯';
    return 'התחל רצף חדש! 🚀';
  };

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <Flame className={`w-4 h-4 ${getStreakColor(currentStreak)}`} />
        <span className="text-sm font-medium">
          {currentStreak} {t('gamification.streak')}
        </span>
        {streakSavers > 0 && (
          <div className="flex items-center gap-1">
            <Shield className="w-3 h-3 text-blue-500" />
            <span className="text-xs text-blue-600">{streakSavers}</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Flame className={`w-5 h-5 ${getStreakColor(currentStreak)}`} />
          <h3 className="text-lg font-display font-semibold text-gray-900">
            {t('gamification.streak')}
          </h3>
        </div>

        {isActiveToday && (
          <div className="flex items-center gap-1 bg-success-100 text-success-800 px-2 py-1 rounded-full text-xs">
            <Zap className="w-3 h-3" />
            פעיל היום
          </div>
        )}
      </div>

      {/* Current Streak Display */}
      <div className={`text-center p-6 rounded-lg border-2 mb-4 ${getStreakBgColor(currentStreak)}`}>
        <div className={`text-4xl font-bold mb-2 ${getStreakColor(currentStreak)}`}>
          {currentStreak}
        </div>
        <div className="text-sm font-medium text-gray-700 mb-1">
          ימים ברצף
        </div>
        <div className="text-xs text-gray-500">
          {getStreakMessage(currentStreak)}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-center gap-1 text-orange-600 mb-1">
            <Flame className="w-4 h-4" />
          </div>
          <div className="text-xs text-gray-500 mb-1">רצף הכי ארוך</div>
          <div className="text-lg font-semibold text-gray-900">
            {longestStreak}
          </div>
        </div>

        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-center gap-1 text-blue-600 mb-1">
            <Shield className="w-4 h-4" />
          </div>
          <div className="text-xs text-gray-500 mb-1">מגיני רצף</div>
          <div className="text-lg font-semibold text-gray-900">
            {streakSavers}
          </div>
        </div>
      </div>

      {/* Last Activity */}
      {lastActiveDate && (
        <div className="flex items-center gap-2 text-sm text-gray-500 p-3 bg-gray-50 rounded-lg">
          <Calendar className="w-4 h-4" />
          <span>
            פעילות אחרונה: {lastActiveDate.toLocaleDateString('he-IL', {
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })}
          </span>
        </div>
      )}

      {/* Streak Tips */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-sm font-medium text-blue-900 mb-2">
          💡 טיפים לשמירה על רצף
        </h4>
        <ul className="text-xs text-blue-800 space-y-1">
          <li>• השלם לפחות שיעור אחד בכל יום</li>
          <li>• השתמש במגני רצף במקרה חירום</li>
          <li>• קבע זמן קבוע ללמידה</li>
          {currentStreak >= 7 && <li>• כל הכבוד על הרצף המדהים! 🔥</li>}
        </ul>
      </div>

      {/* Streak Savers Info */}
      {streakSavers > 0 && (
        <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-4 h-4 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-900">
              מגיני רצף זמינים: {streakSavers}
            </span>
          </div>
          <p className="text-xs text-yellow-800">
            מגיני רצף מאפשרים לך לפספס יום אחד מבלי לאבד את הרצף.
            משתמש באופן אוטומטי אם לא למדת במשך 24 שעות.
          </p>
        </div>
      )}

      {/* Call to Action */}
      {currentStreak === 0 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600 mb-3">
            התחל רצף חדש היום! 🚀
          </p>
          <button className="btn-primary text-sm px-4 py-2">
            התחל שיעור
          </button>
        </div>
      )}
    </div>
  );
}