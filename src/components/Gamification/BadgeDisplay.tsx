'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Award, Lock, Star, Sparkles } from 'lucide-react';

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'concept' | 'achievement' | 'milestone';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  earnedAt?: Date;
  isNew?: boolean;
}

interface BadgeDisplayProps {
  badges: Badge[];
  showNewBadgeAnimation?: boolean;
  newBadge?: Badge;
  compact?: boolean;
}

export default function BadgeDisplay({
  badges,
  showNewBadgeAnimation = false,
  newBadge,
  compact = false,
}: BadgeDisplayProps) {
  const t = useTranslations();
  const [showNewBadgeModal, setShowNewBadgeModal] = useState(false);

  const earnedBadges = badges.filter(badge => badge.earnedAt);
  const lockedBadges = badges.filter(badge => !badge.earnedAt);

  useEffect(() => {
    if (showNewBadgeAnimation && newBadge) {
      setShowNewBadgeModal(true);
      // Auto-close after 3 seconds
      const timer = setTimeout(() => setShowNewBadgeModal(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [showNewBadgeAnimation, newBadge]);

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'border-gray-300 bg-gray-50';
      case 'rare': return 'border-blue-300 bg-blue-50';
      case 'epic': return 'border-purple-300 bg-purple-50';
      case 'legendary': return 'border-yellow-300 bg-yellow-50';
      default: return 'border-gray-300 bg-gray-50';
    }
  };

  const getRarityText = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'רגיל';
      case 'rare': return 'נדיר';
      case 'epic': return 'אפי';
      case 'legendary': return 'אגדי';
      default: return 'רגיל';
    }
  };

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <Award className="w-4 h-4 text-gray-600" />
        <span className="text-sm text-gray-600">
          {earnedBadges.length}/{badges.length} {t('gamification.badges')}
        </span>
        <div className="flex gap-1">
          {earnedBadges.slice(0, 3).map(badge => (
            <div
              key={badge.id}
              className="w-6 h-6 bg-yellow-100 border border-yellow-300 rounded-full flex items-center justify-center text-xs"
              title={badge.name}
            >
              {badge.icon}
            </div>
          ))}
          {earnedBadges.length > 3 && (
            <div className="w-6 h-6 bg-gray-100 border border-gray-300 rounded-full flex items-center justify-center text-xs text-gray-600">
              +{earnedBadges.length - 3}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-display font-semibold text-gray-900">
              {t('gamification.badges')}
            </h3>
          </div>
          <div className="text-sm text-gray-500">
            {earnedBadges.length}/{badges.length}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="progress-container">
            <div
              className="progress-bar"
              style={{ width: `${(earnedBadges.length / badges.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Earned Badges */}
        {earnedBadges.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">תגים שזכיתי בהם</h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {earnedBadges.map(badge => (
                <div
                  key={badge.id}
                  className={`relative p-3 rounded-lg border-2 text-center transition-all hover:scale-105 ${getRarityColor(badge.rarity)}`}
                  title={badge.description}
                >
                  {badge.isNew && (
                    <div className="absolute -top-1 -right-1">
                      <Sparkles className="w-4 h-4 text-yellow-500" />
                    </div>
                  )}

                  <div className="text-2xl mb-2">{badge.icon}</div>
                  <div className="text-xs font-medium text-gray-900 mb-1">
                    {badge.name}
                  </div>
                  <div className="text-xs text-gray-500">
                    {getRarityText(badge.rarity)}
                  </div>

                  {badge.earnedAt && (
                    <div className="text-xs text-gray-400 mt-1">
                      {badge.earnedAt.toLocaleDateString('he-IL')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Locked Badges */}
        {lockedBadges.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">תגים לפתיחה</h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {lockedBadges.slice(0, 8).map(badge => (
                <div
                  key={badge.id}
                  className="relative p-3 rounded-lg border-2 border-gray-200 bg-gray-100 text-center opacity-75"
                  title={badge.description}
                >
                  <div className="absolute top-2 right-2">
                    <Lock className="w-3 h-3 text-gray-400" />
                  </div>

                  <div className="text-2xl mb-2 grayscale">{badge.icon}</div>
                  <div className="text-xs font-medium text-gray-600 mb-1">
                    {badge.name}
                  </div>
                  <div className="text-xs text-gray-400">
                    {getRarityText(badge.rarity)}
                  </div>
                </div>
              ))}

              {lockedBadges.length > 8 && (
                <div className="p-3 rounded-lg border-2 border-gray-200 bg-gray-50 text-center flex items-center justify-center">
                  <div className="text-gray-500">
                    <Star className="w-6 h-6 mx-auto mb-1" />
                    <div className="text-xs">+{lockedBadges.length - 8} נוספים</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Empty State */}
        {badges.length === 0 && (
          <div className="text-center py-8">
            <Award className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-500 mb-2">
              אין תגים עדיין
            </h4>
            <p className="text-sm text-gray-400">
              השלם שיעורים כדי לזכות בתגים ראשונים!
            </p>
          </div>
        )}
      </div>

      {/* New Badge Modal */}
      {showNewBadgeModal && newBadge && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 animate-fade-in">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-4 text-center animate-slide-in-up">
            <div className="w-16 h-16 mx-auto mb-4 bg-yellow-100 rounded-full flex items-center justify-center">
              <div className="text-3xl">{newBadge.icon}</div>
            </div>

            <h3 className="text-xl font-display font-bold text-gray-900 mb-2">
              {t('gamification.newBadge')}
            </h3>

            <h4 className="text-lg font-semibold text-primary-600 mb-2">
              {newBadge.name}
            </h4>

            <p className="text-sm text-gray-600 mb-4 hebrew-text">
              {newBadge.description}
            </p>

            <div className="inline-flex items-center gap-1 bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
              <Star className="w-4 h-4" />
              {getRarityText(newBadge.rarity)}
            </div>

            <button
              onClick={() => setShowNewBadgeModal(false)}
              className="btn-primary mt-4 w-full"
            >
              {t('gamification.congratulations')}
            </button>
          </div>
        </div>
      )}
    </>
  );
}