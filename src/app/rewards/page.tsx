'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { ArrowLeft, Trophy, Star, Flame, Palette } from 'lucide-react';
import XPDisplay from '@/components/Gamification/XPDisplay';
import BadgeDisplay, { Badge } from '@/components/Gamification/BadgeDisplay';
import StreakDisplay from '@/components/Gamification/StreakDisplay';
import CosmeticsDisplay, { CosmeticItem } from '@/components/Gamification/CosmeticsDisplay';

// Mock data - in real app would come from user profile/database
const mockUserData = {
  xp: 350,
  level: 4,
  currentStreak: 5,
  longestStreak: 12,
  streakSavers: 2,
  lastActiveDate: new Date(),
};

const mockBadges: Badge[] = [
  {
    id: 'first-goal',
    name: 'שער ראשון',
    description: 'יצרת את השער הראשון שלך במשחק כדורגל',
    icon: '⚽',
    category: 'achievement',
    rarity: 'common',
    earnedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days ago
  },
  {
    id: 'variable-master',
    name: 'מאסטר משתנים',
    description: 'למדת להשתמש במשתנים בצורה מושלמת',
    icon: '📊',
    category: 'concept',
    rarity: 'rare',
    earnedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
    isNew: true,
  },
  {
    id: 'speed-coder',
    name: 'מתכנת מהיר',
    description: 'השלמת שיעור בפחות מ-10 דקות',
    icon: '⚡',
    category: 'achievement',
    rarity: 'epic',
  },
  {
    id: 'robot-builder',
    name: 'בונה רובוטים',
    description: 'יצרת את הרובוט הראשון שלך',
    icon: '🤖',
    category: 'milestone',
    rarity: 'rare',
  },
  {
    id: 'space-explorer',
    name: 'חוקר חלל',
    description: 'השגת החללית הראשונה שלך',
    icon: '🚀',
    category: 'milestone',
    rarity: 'legendary',
  },
];

const mockCosmetics: CosmeticItem[] = [
  {
    id: 'basic-trail',
    name: 'עקבות בסיסיים',
    description: 'עקבות פשוטים לכדור',
    category: 'ball_trails',
    theme: 'football',
    rarity: 'common',
    unlockRequirement: { type: 'xp', value: 0 },
    isUnlocked: true,
    isEquipped: true,
  },
  {
    id: 'sparkle-trail',
    name: 'עקבות נוצצים',
    description: 'עקבות מנצנצים וססימים',
    category: 'ball_trails',
    theme: 'football',
    rarity: 'rare',
    unlockRequirement: { type: 'xp', value: 100 },
    isUnlocked: true,
    isEquipped: false,
  },
  {
    id: 'rainbow-trail',
    name: 'עקבות קשת',
    description: 'עקבות בצבעי קשת בענן',
    category: 'ball_trails',
    theme: 'football',
    rarity: 'epic',
    unlockRequirement: { type: 'level', value: 5 },
    isUnlocked: false,
    isEquipped: false,
  },
  {
    id: 'classic-robot',
    name: 'רובוט קלאסי',
    description: 'עיצוב רובוט כחול וכסוף',
    category: 'robot_skins',
    theme: 'robots',
    rarity: 'common',
    unlockRequirement: { type: 'badge', value: 'robot-builder' },
    isUnlocked: false,
    isEquipped: false,
  },
  {
    id: 'neon-robot',
    name: 'רובוט ניאון',
    description: 'רובוט עם אורות ניאון זוהרים',
    category: 'robot_skins',
    theme: 'robots',
    rarity: 'epic',
    unlockRequirement: { type: 'level', value: 10 },
    isUnlocked: false,
    isEquipped: false,
  },
  {
    id: 'starfield',
    name: 'שדה כוכבים',
    description: 'רקע עם כוכבים נוצצים',
    category: 'space_effects',
    theme: 'space',
    rarity: 'rare',
    unlockRequirement: { type: 'badge', value: 'space-explorer' },
    isUnlocked: false,
    isEquipped: false,
  },
];

// Calculate XP for next level
const calculateXPForNextLevel = (level: number) => {
  const baseXP = 100;
  const multiplier = 1.2;
  return Math.floor(baseXP * Math.pow(multiplier, level - 1));
};

export default function RewardsPage() {
  const t = useTranslations();
  const [activeTab, setActiveTab] = useState<'overview' | 'badges' | 'cosmetics'>('overview');
  const [showNewBadgeAnimation, setShowNewBadgeAnimation] = useState(false);

  const totalXPForNextLevel = calculateXPForNextLevel(mockUserData.level);
  const xpForNextLevel = Math.max(0, totalXPForNextLevel - (mockUserData.xp % totalXPForNextLevel));

  // Simulate new badge earned animation
  useEffect(() => {
    const newBadge = mockBadges.find(badge => badge.isNew);
    if (newBadge) {
      setShowNewBadgeAnimation(true);
      setTimeout(() => setShowNewBadgeAnimation(false), 4000);
    }
  }, []);

  const handleEquipCosmetic = (itemId: string) => {
    // In real app, would update user's equipped cosmetics
    console.log('Equipping cosmetic:', itemId);
  };

  const handlePreviewCosmetic = (itemId: string) => {
    // In real app, would show preview of cosmetic
    console.log('Previewing cosmetic:', itemId);
  };

  const tabs = [
    { id: 'overview', name: 'סקירה', icon: Trophy },
    { id: 'badges', name: 'תגים', icon: Star },
    { id: 'cosmetics', name: 'קוסמטיקה', icon: Palette },
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
            <h1 className="text-xl font-display font-bold text-gray-900">
              {t('navigation.rewards')}
            </h1>
            <div className="w-20" /> {/* Spacer for centering */}
          </div>
        </div>
      </nav>

      {/* Tab Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-8">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-4 px-2 border-b-2 text-sm font-medium transition-colors ${
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
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Hero Stats */}
            <div className="grid md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <XPDisplay
                  currentXP={mockUserData.xp}
                  level={mockUserData.level}
                  xpForNextLevel={xpForNextLevel}
                  totalXPForNextLevel={totalXPForNextLevel}
                  showAnimation={false}
                />
              </div>
              <div>
                <StreakDisplay
                  currentStreak={mockUserData.currentStreak}
                  longestStreak={mockUserData.longestStreak}
                  streakSavers={mockUserData.streakSavers}
                  lastActiveDate={mockUserData.lastActiveDate}
                />
              </div>
            </div>

            {/* Recent Achievements */}
            <div className="grid md:grid-cols-2 gap-6">
              <BadgeDisplay
                badges={mockBadges.slice(0, 4)}
                showNewBadgeAnimation={showNewBadgeAnimation}
                newBadge={mockBadges.find(badge => badge.isNew)}
                compact={false}
              />

              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-lg font-display font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Flame className="w-5 h-5 text-orange-500" />
                  סטטיסטיקות
                </h3>

                <div className="space-y-4">
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">שיעורים הושלמו</span>
                    <span className="text-sm font-semibold text-gray-900">12</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">זמן למידה כולל</span>
                    <span className="text-sm font-semibold text-gray-900">4.2 שעות</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">מושגים נלמדו</span>
                    <span className="text-sm font-semibold text-gray-900">8</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">משחקים נוצרו</span>
                    <span className="text-sm font-semibold text-gray-900">5</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-sm text-gray-600">דירוג דיוק</span>
                    <span className="text-sm font-semibold text-success-600">87%</span>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-gray-100">
                  <Link href="/learn" className="btn-primary w-full">
                    המשך ללמוד
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'badges' && (
          <BadgeDisplay
            badges={mockBadges}
            showNewBadgeAnimation={false}
            compact={false}
          />
        )}

        {activeTab === 'cosmetics' && (
          <CosmeticsDisplay
            cosmetics={mockCosmetics}
            onEquip={handleEquipCosmetic}
            onPreview={handlePreviewCosmetic}
            selectedTheme="all"
          />
        )}
      </main>
    </div>
  );
}