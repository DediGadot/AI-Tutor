'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Play, Lock, CheckCircle, Clock, Star } from 'lucide-react';

// Mock lessons data
const mockLessons = {
  football: [
    {
      id: 'first-kick',
      title: 'בעיטה ראשונה',
      description: 'למד ליצור כדור שזז במגרש',
      difficulty: 1,
      duration: 20,
      xp: 75,
      status: 'available',
      milestones: 3,
      concepts: ['variables', 'functions', 'canvas']
    },
    {
      id: 'goal-keeper',
      title: 'שוער חכם',
      description: 'צור שוער שתופס כדורים',
      difficulty: 2,
      duration: 20,
      xp: 100,
      status: 'locked',
      milestones: 4,
      concepts: ['collision', 'conditions', 'movement']
    },
    {
      id: 'penalty-shootout',
      title: 'קרב פנדלים',
      description: 'בנה משחק פנדלים מלא',
      difficulty: 3,
      duration: 20,
      xp: 150,
      status: 'locked',
      milestones: 5,
      concepts: ['physics', 'arrays', 'score']
    }
  ],
  space: [
    {
      id: 'rocket-launch',
      title: 'שיגור חללית',
      description: 'שגר חללית לחלל',
      difficulty: 1,
      duration: 20,
      xp: 75,
      status: 'locked',
      milestones: 3,
      concepts: ['variables', 'movement', 'gravity']
    }
  ],
  robots: [
    {
      id: 'first-robot',
      title: 'הרובוט הראשון',
      description: 'בנה רובוט פשוט',
      difficulty: 1,
      duration: 20,
      xp: 75,
      status: 'locked',
      milestones: 3,
      concepts: ['objects', 'sensors', 'movement']
    }
  ]
};

const themeConfig = {
  football: {
    name: 'כדורגל',
    emoji: '⚽',
    color: 'success',
    bgGradient: 'from-green-500 to-emerald-600'
  },
  space: {
    name: 'חלל',
    emoji: '🚀',
    color: 'primary',
    bgGradient: 'from-blue-500 to-indigo-600'
  },
  robots: {
    name: 'רובוטים',
    emoji: '🤖',
    color: 'warning',
    bgGradient: 'from-purple-500 to-indigo-600'
  }
};

export default function ThemePage() {
  const t = useTranslations();
  const params = useParams();
  const theme = params.theme as string;

  const themeData = (themeConfig as any)[theme];
  const lessons = (mockLessons as any)[theme] || [];

  if (!themeData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">נושא לא נמצא</h1>
          <p className="text-gray-600">הנושא המבוקש לא קיים במערכת</p>
          <Link href="/" className="btn-primary mt-4">
            חזור לדף הבית
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className={`bg-gradient-to-r ${themeData.bgGradient} text-white`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="text-8xl mb-4">{themeData.emoji}</div>
            <h1 className="text-4xl md:text-5xl font-display font-bold mb-4">
              {themeData.name}
            </h1>
            <p className="text-xl opacity-90 max-w-2xl mx-auto hebrew-text">
              למד תכנות דרך יצירת משחקים מהנים ואינטראקטיביים בנושא {themeData.name}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
              ← חזור לדף הבית
            </Link>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">נושא:</span>
              <span className="text-sm font-medium text-gray-900">{themeData.name}</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Lessons Grid */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-display font-bold text-gray-900 mb-4">
            שיעורים זמינים
          </h2>
          <p className="text-gray-600 hebrew-text">
            בחר שיעור להתחיל ללמוד. כל שיעור אורך כ-20 דקות ומכיל מספר ציוני דרך.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {lessons.map((lesson: any, index: number) => (
            <div
              key={lesson.id}
              className={`card-hover relative ${
                lesson.status === 'locked' ? 'opacity-75' : ''
              }`}
            >
              {/* Status Badge */}
              <div className="absolute top-4 left-4">
                {lesson.status === 'completed' ? (
                  <div className="flex items-center gap-1 bg-success-100 text-success-800 px-2 py-1 rounded-full text-xs">
                    <CheckCircle className="w-3 h-3" />
                    הושלם
                  </div>
                ) : lesson.status === 'locked' ? (
                  <div className="flex items-center gap-1 bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                    <Lock className="w-3 h-3" />
                    נעול
                  </div>
                ) : (
                  <div className="flex items-center gap-1 bg-primary-100 text-primary-800 px-2 py-1 rounded-full text-xs">
                    <Star className="w-3 h-3" />
                    זמין
                  </div>
                )}
              </div>

              {/* Difficulty */}
              <div className="absolute top-4 right-4">
                <div className="flex gap-1">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-2 h-2 rounded-full ${
                        i < lesson.difficulty ? 'bg-warning-400' : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
              </div>

              {/* Content */}
              <div className="pt-12 pb-6">
                <h3 className="text-xl font-display font-semibold text-gray-900 mb-2">
                  {lesson.title}
                </h3>
                <p className="text-gray-600 text-sm mb-4 hebrew-text">
                  {lesson.description}
                </p>

                {/* Lesson Stats */}
                <div className="grid grid-cols-3 gap-4 text-center py-4 border-t border-gray-100">
                  <div>
                    <div className="text-lg font-semibold text-gray-900">{lesson.milestones}</div>
                    <div className="text-xs text-gray-500">ציוני דרך</div>
                  </div>
                  <div>
                    <div className="text-lg font-semibold text-gray-900">{lesson.duration}m</div>
                    <div className="text-xs text-gray-500">זמן</div>
                  </div>
                  <div>
                    <div className="text-lg font-semibold text-gray-900">{lesson.xp}</div>
                    <div className="text-xs text-gray-500">XP</div>
                  </div>
                </div>

                {/* Concepts */}
                <div className="mb-4">
                  <div className="text-xs text-gray-500 mb-2">מושגים:</div>
                  <div className="flex flex-wrap gap-1">
                    {lesson.concepts.map((concept: string) => (
                      <span
                        key={concept}
                        className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs"
                      >
                        {t(`concepts.${concept}`)}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action Button */}
                {lesson.status === 'available' ? (
                  <Link
                    href={`/learn/${theme}/${lesson.id}`}
                    className="btn-primary w-full"
                  >
                    <Play className="w-4 h-4 me-2" />
                    {t('common.start')}
                  </Link>
                ) : lesson.status === 'completed' ? (
                  <Link
                    href={`/learn/${theme}/${lesson.id}`}
                    className="btn-secondary w-full"
                  >
                    <CheckCircle className="w-4 h-4 me-2" />
                    שחק שוב
                  </Link>
                ) : (
                  <button
                    disabled
                    className="btn-secondary w-full opacity-50 cursor-not-allowed"
                  >
                    <Lock className="w-4 h-4 me-2" />
                    נעול
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Coming Soon */}
        {lessons.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🚧</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              שיעורים בפיתוח
            </h3>
            <p className="text-gray-600">
              השיעורים בנושא {themeData.name} עדיין בפיתוח. חזור בקרוב!
            </p>
            <Link href="/" className="btn-primary mt-4">
              חזור לדף הבית
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}