'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Palette, Lock, Star, Eye, ShoppingBag } from 'lucide-react';

export interface CosmeticItem {
  id: string;
  name: string;
  description: string;
  category: 'ball_trails' | 'robot_skins' | 'space_effects' | 'backgrounds';
  theme: 'football' | 'space' | 'robots' | 'all';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  unlockRequirement: {
    type: 'xp' | 'badge' | 'streak' | 'level';
    value: number | string;
  };
  isUnlocked: boolean;
  isEquipped: boolean;
  previewUrl?: string;
}

interface CosmeticsDisplayProps {
  cosmetics: CosmeticItem[];
  onEquip: (itemId: string) => void;
  onPreview: (itemId: string) => void;
  selectedTheme?: string;
}

export default function CosmeticsDisplay({
  cosmetics,
  onEquip,
  onPreview,
  selectedTheme = 'all',
}: CosmeticsDisplayProps) {
  const t = useTranslations();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [previewItem, setPreviewItem] = useState<CosmeticItem | null>(null);

  const categories = [
    { id: 'all', name: 'הכל', icon: ShoppingBag },
    { id: 'ball_trails', name: 'עקבות כדור', icon: '⚽' },
    { id: 'robot_skins', name: 'רובוט סקינס', icon: '🤖' },
    { id: 'space_effects', name: 'אפקטי חלל', icon: '🚀' },
    { id: 'backgrounds', name: 'רקעים', icon: '🎨' },
  ];

  const filteredCosmetics = cosmetics.filter(item => {
    const categoryMatch = selectedCategory === 'all' || item.category === selectedCategory;
    const themeMatch = selectedTheme === 'all' || item.theme === selectedTheme || item.theme === 'all';
    return categoryMatch && themeMatch;
  });

  const unlockedItems = filteredCosmetics.filter(item => item.isUnlocked);
  const lockedItems = filteredCosmetics.filter(item => !item.isUnlocked);

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'border-gray-300 bg-gray-50';
      case 'rare': return 'border-blue-300 bg-blue-50';
      case 'epic': return 'border-purple-300 bg-purple-50';
      case 'legendary': return 'border-yellow-300 bg-yellow-50 shadow-lg';
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

  const getCategoryName = (category: string) => {
    switch (category) {
      case 'ball_trails': return 'עקבות כדור';
      case 'robot_skins': return 'רובוט סקינס';
      case 'space_effects': return 'אפקטי חלל';
      case 'backgrounds': return 'רקעים';
      default: return category;
    }
  };

  const getUnlockText = (requirement: CosmeticItem['unlockRequirement']) => {
    switch (requirement.type) {
      case 'xp': return `${requirement.value} XP`;
      case 'level': return `רמה ${requirement.value}`;
      case 'streak': return `רצף ${requirement.value} ימים`;
      case 'badge': return `תג: ${requirement.value}`;
      default: return 'לא ידוע';
    }
  };

  const handlePreview = (item: CosmeticItem) => {
    setPreviewItem(item);
    onPreview(item.id);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Palette className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-display font-semibold text-gray-900">
            {t('gamification.cosmetics')}
          </h3>
        </div>
        <div className="text-sm text-gray-500">
          {unlockedItems.length}/{filteredCosmetics.length} פתוח
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              selectedCategory === category.id
                ? 'bg-primary-100 text-primary-800 border-2 border-primary-200'
                : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'
            }`}
          >
            {typeof category.icon === 'string' ? (
              <span className="text-base">{category.icon}</span>
            ) : (
              <category.icon className="w-4 h-4" />
            )}
            {category.name}
          </button>
        ))}
      </div>

      {/* Unlocked Items */}
      {unlockedItems.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
            <Star className="w-4 h-4 text-yellow-500" />
            פריטים פתוחים
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {unlockedItems.map(item => (
              <div
                key={item.id}
                className={`relative p-3 rounded-lg border-2 transition-all hover:scale-105 ${getRarityColor(item.rarity)} ${
                  item.isEquipped ? 'ring-2 ring-primary-500' : ''
                }`}
              >
                {item.isEquipped && (
                  <div className="absolute -top-1 -right-1 bg-primary-500 text-white rounded-full p-1">
                    <Star className="w-3 h-3" />
                  </div>
                )}

                {/* Preview */}
                <div className="w-full h-16 bg-gray-100 rounded mb-2 flex items-center justify-center text-2xl">
                  {item.previewUrl ? (
                    <img src={item.previewUrl} alt={item.name} className="max-w-full max-h-full" />
                  ) : (
                    '🎨'
                  )}
                </div>

                <div className="text-xs font-medium text-gray-900 mb-1">
                  {item.name}
                </div>
                <div className="text-xs text-gray-500 mb-2">
                  {getRarityText(item.rarity)}
                </div>

                {/* Actions */}
                <div className="flex gap-1">
                  <button
                    onClick={() => handlePreview(item)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-2 py-1 rounded text-xs transition-colors"
                    title="תצוגה מקדימה"
                  >
                    <Eye className="w-3 h-3 mx-auto" />
                  </button>

                  {!item.isEquipped && (
                    <button
                      onClick={() => onEquip(item.id)}
                      className="flex-1 bg-primary-500 hover:bg-primary-600 text-white px-2 py-1 rounded text-xs transition-colors"
                      title="הצטייד"
                    >
                      הצטייד
                    </button>
                  )}

                  {item.isEquipped && (
                    <div className="flex-1 bg-success-100 text-success-700 px-2 py-1 rounded text-xs text-center">
                      מצויד
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Locked Items */}
      {lockedItems.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
            <Lock className="w-4 h-4 text-gray-400" />
            פריטים נעולים
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {lockedItems.map(item => (
              <div
                key={item.id}
                className="relative p-3 rounded-lg border-2 border-gray-200 bg-gray-100 opacity-75"
              >
                <div className="absolute top-2 right-2">
                  <Lock className="w-3 h-3 text-gray-400" />
                </div>

                {/* Preview */}
                <div className="w-full h-16 bg-gray-200 rounded mb-2 flex items-center justify-center text-2xl grayscale">
                  {item.previewUrl ? (
                    <img src={item.previewUrl} alt={item.name} className="max-w-full max-h-full" />
                  ) : (
                    '🎨'
                  )}
                </div>

                <div className="text-xs font-medium text-gray-600 mb-1">
                  {item.name}
                </div>
                <div className="text-xs text-gray-400 mb-2">
                  {getRarityText(item.rarity)}
                </div>

                {/* Unlock requirement */}
                <div className="bg-gray-200 text-gray-600 px-2 py-1 rounded text-xs text-center">
                  דרוש: {getUnlockText(item.unlockRequirement)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredCosmetics.length === 0 && (
        <div className="text-center py-8">
          <Palette className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-gray-500 mb-2">
            אין פריטים בקטגוריה זו
          </h4>
          <p className="text-sm text-gray-400">
            נסה לבחור קטגוריה אחרת או נושא אחר
          </p>
        </div>
      )}

      {/* Preview Modal */}
      {previewItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 animate-fade-in">
          <div className="bg-white rounded-lg p-6 max-w-md mx-4 text-center animate-slide-in-up">
            <h3 className="text-xl font-display font-bold text-gray-900 mb-4">
              תצוגה מקדימה
            </h3>

            <div className="w-32 h-32 bg-gray-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
              {previewItem.previewUrl ? (
                <img
                  src={previewItem.previewUrl}
                  alt={previewItem.name}
                  className="max-w-full max-h-full rounded"
                />
              ) : (
                <div className="text-4xl">🎨</div>
              )}
            </div>

            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              {previewItem.name}
            </h4>

            <p className="text-sm text-gray-600 mb-4 hebrew-text">
              {previewItem.description}
            </p>

            <div className="flex gap-2">
              <button
                onClick={() => setPreviewItem(null)}
                className="btn-secondary flex-1"
              >
                {t('common.close')}
              </button>

              {previewItem.isUnlocked && !previewItem.isEquipped && (
                <button
                  onClick={() => {
                    onEquip(previewItem.id);
                    setPreviewItem(null);
                  }}
                  className="btn-primary flex-1"
                >
                  הצטייד
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}