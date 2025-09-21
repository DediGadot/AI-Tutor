'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Star, TrendingUp, Zap } from 'lucide-react';

interface XPDisplayProps {
  currentXP: number;
  level: number;
  xpForNextLevel: number;
  totalXPForNextLevel: number;
  showAnimation?: boolean;
  earnedXP?: number;
}

export default function XPDisplay({
  currentXP,
  level,
  xpForNextLevel,
  totalXPForNextLevel,
  showAnimation = false,
  earnedXP = 0,
}: XPDisplayProps) {
  const t = useTranslations();
  const [animateEarnedXP, setAnimateEarnedXP] = useState(false);
  const [animateLevelUp, setAnimateLevelUp] = useState(false);

  const progressPercentage = ((totalXPForNextLevel - xpForNextLevel) / totalXPForNextLevel) * 100;

  useEffect(() => {
    if (showAnimation && earnedXP > 0) {
      setAnimateEarnedXP(true);
      const timer = setTimeout(() => setAnimateEarnedXP(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [showAnimation, earnedXP]);

  useEffect(() => {
    if (xpForNextLevel === 0) {
      setAnimateLevelUp(true);
      const timer = setTimeout(() => setAnimateLevelUp(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [xpForNextLevel]);

  return (
    <div className="relative bg-white rounded-lg border border-gray-200 p-4">
      {/* Level Badge */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`flex items-center justify-center w-10 h-10 rounded-full bg-primary-100 text-primary-800 font-bold ${
            animateLevelUp ? 'animate-bounce' : ''
          }`}>
            {level}
          </div>
          <div>
            <div className="text-sm font-medium text-gray-900">
              {t('gamification.level')} {level}
            </div>
            <div className="text-xs text-gray-500">
              {currentXP.toLocaleString('he-IL')} {t('gamification.xp')}
            </div>
          </div>
        </div>

        {/* XP Animation */}
        {animateEarnedXP && earnedXP > 0 && (
          <div className="absolute top-2 left-1/2 transform -translate-x-1/2 pointer-events-none">
            <div className="xp-animation bg-success-500 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg">
              +{earnedXP} XP
            </div>
          </div>
        )}

        {/* Level Up Animation */}
        {animateLevelUp && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="badge-animation bg-warning-500 text-white px-4 py-2 rounded-lg text-lg font-bold shadow-lg">
              {t('gamification.levelUp')}
            </div>
          </div>
        )}

        <div className="flex items-center gap-1 text-warning-500">
          <Star className="w-4 h-4" />
          <span className="text-sm font-medium">{level}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-gray-500">
          <span>הרמה הנוכחית</span>
          <span>הרמה הבאה</span>
        </div>

        <div className="progress-container relative">
          <div
            className="progress-bar transition-all duration-1000 ease-out"
            style={{ width: `${progressPercentage}%` }}
          />

          {/* XP needed indicator */}
          <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-700">
            {xpForNextLevel > 0 ? (
              <span>{xpForNextLevel} XP נותרו</span>
            ) : (
              <span className="text-success-700">רמה הושלמה!</span>
            )}
          </div>
        </div>

        <div className="flex justify-between text-xs text-gray-400">
          <span>0</span>
          <span>{totalXPForNextLevel.toLocaleString('he-IL')}</span>
        </div>
      </div>

      {/* Stats */}
      <div className="mt-4 grid grid-cols-2 gap-4 pt-3 border-t border-gray-100">
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-primary-600 mb-1">
            <TrendingUp className="w-4 h-4" />
          </div>
          <div className="text-xs text-gray-500">נקודות כולל</div>
          <div className="text-sm font-semibold text-gray-900">
            {currentXP.toLocaleString('he-IL')}
          </div>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-warning-600 mb-1">
            <Zap className="w-4 h-4" />
          </div>
          <div className="text-xs text-gray-500">רמה נוכחית</div>
          <div className="text-sm font-semibold text-gray-900">
            {level}
          </div>
        </div>
      </div>
    </div>
  );
}