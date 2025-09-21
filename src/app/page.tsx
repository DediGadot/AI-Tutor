import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { Play, Award, Settings, User } from 'lucide-react';

export default function HomePage() {
  const t = useTranslations();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-display font-bold text-gray-900">
                {t('navigation.home')} - Hebrew AI Tutor
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/settings"
                className="btn-secondary text-sm"
                aria-label={t('navigation.settings')}
              >
                <Settings className="w-4 h-4 me-2" />
                {t('navigation.settings')}
              </Link>
              <Link
                href="/parent"
                className="btn-secondary text-sm"
                aria-label={t('navigation.parent')}
              >
                <User className="w-4 h-4 me-2" />
                {t('navigation.parent')}
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-display font-bold text-gray-900 mb-6">
            ברוכים הבאים למדריך הקוד!
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 hebrew-text">
            למד לתכנת דרך משחקים אינטראקטיביים בעברית עם הדרכה של בינה מלאכותית.
            צור משחקי כדורגל, חלל ורובוטים בצורה מהנה ובטוחה!
          </p>
        </div>

        {/* Theme Selection Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="card-hover text-center group">
            <div className="text-6xl mb-4">⚽</div>
            <h3 className="text-xl font-display font-semibold mb-2">
              {t('themes.football')}
            </h3>
            <p className="text-gray-600 mb-4 hebrew-text">
              צור משחקי כדורגל עם פיזיקה אמיתית, בעיטות ושערים!
            </p>
            <Link
              href="/play/football"
              className="btn-primary w-full group-hover:scale-105 transition-transform"
            >
              <Play className="w-4 h-4 me-2" />
              {t('common.start')}
            </Link>
          </div>

          <div className="card-hover text-center group">
            <div className="text-6xl mb-4">🚀</div>
            <h3 className="text-xl font-display font-semibold mb-2">
              {t('themes.space')}
            </h3>
            <p className="text-gray-600 mb-4 hebrew-text">
              חקור את החלל עם חלליות, כוכבי לכת וכבידה!
            </p>
            <Link
              href="/play/space"
              className="btn-primary w-full group-hover:scale-105 transition-transform"
            >
              <Play className="w-4 h-4 me-2" />
              {t('common.start')}
            </Link>
          </div>

          <div className="card-hover text-center group">
            <div className="text-6xl mb-4">🤖</div>
            <h3 className="text-xl font-display font-semibold mb-2">
              {t('themes.robots')}
            </h3>
            <p className="text-gray-600 mb-4 hebrew-text">
              בנה וחקר רובוטים עם תנועה, חיישנים ובינה מלאכותית!
            </p>
            <Link
              href="/play/robots"
              className="btn-primary w-full group-hover:scale-105 transition-transform"
            >
              <Play className="w-4 h-4 me-2" />
              {t('common.start')}
            </Link>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex justify-center gap-6">
          <Link
            href="/rewards"
            className="btn-secondary text-lg px-8 py-4"
            aria-label={t('navigation.rewards')}
          >
            <Award className="w-5 h-5 me-2" />
            {t('navigation.rewards')}
          </Link>
          <Link
            href="/learn"
            className="btn-primary text-lg px-8 py-4"
            aria-label={t('navigation.learn')}
          >
            {t('navigation.learn')}
          </Link>
        </div>

        {/* Features */}
        <div className="mt-16 grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl mb-2">🎯</div>
            <h3 className="font-semibold mb-1">שיעורים קצרים</h3>
            <p className="text-sm text-gray-600">עד 20 דקות</p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-2">🎮</div>
            <h3 className="font-semibold mb-1">משחקים אינטראקטיביים</h3>
            <p className="text-sm text-gray-600">למידה דרך יצירה</p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-2">🏆</div>
            <h3 className="font-semibold mb-1">מערכת הישגים</h3>
            <p className="text-sm text-gray-600">תגים ונקודות</p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-2">🔒</div>
            <h3 className="font-semibold mb-1">בטוח לחלוטין</h3>
            <p className="text-sm text-gray-600">ללא איסוף מידע אישי</p>
          </div>
        </div>
      </main>

      {/* Skip links for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 bg-primary-600 text-white p-2 rounded"
      >
        {t('accessibility.skipToContent')}
      </a>
    </div>
  );
}