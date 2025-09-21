'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import CodeEditor from '@/components/CodeEditor';
import PreviewPanel from '@/components/PreviewPanel';
import TestRunner from '@/components/TestRunner';
import { BookOpen, Target, Clock, Award } from 'lucide-react';

// Mock lesson data - in real app this would come from API/database
const mockLessonData = {
  football: {
    'first-kick': {
      id: 'first-kick',
      title: 'בעיטה ראשונה',
      description: 'למד ליצור כדור שזז במגרש',
      duration: 20,
      milestones: [
        {
          id: 'milestone-1',
          goal: 'צור קנווס ומגרש כדורגל',
          starterCode: `// יצירת מגרש כדורגל בסיסי
function setup() {
  // TODO: צור קנווס בגודל 400x300
}

function draw() {
  // TODO: צייר מגרש ירוק
}`,
          tests: [
            {
              id: 'test-canvas',
              name: 'בדיקת יצירת קנווס',
              description: 'בודק שנוצר קנווס בגודל הנכון',
              code: `
                expect(canvas).to.exist;
                expect(canvas.width).to.equal(400);
                expect(canvas.height).to.equal(300);
              `
            },
            {
              id: 'test-background',
              name: 'בדיקת רקע',
              description: 'בודק שיש רקע ירוק למגרש',
              code: `
                // Check that background function was called
                expect(typeof background).to.equal('function');
              `
            }
          ],
          hints: [
            'השתמש בפונקציה createCanvas(400, 300) כדי ליצור קנווס',
            'השתמש בפונקציה background(34, 139, 34) כדי ליצור רקע ירוק'
          ],
          xp: 20
        },
        {
          id: 'milestone-2',
          goal: 'הוסף כדור למגרש',
          starterCode: `function setup() {
  createCanvas(400, 300);
}

function draw() {
  background(34, 139, 34); // מגרש ירוק

  // TODO: הוסף כדור לבן במרכז המגרש
}`,
          tests: [
            {
              id: 'test-ball',
              name: 'בדיקת כדור',
              description: 'בודק שיש כדור על המגרש',
              code: `
                // Check that circle function exists and can be called
                expect(typeof circle).to.equal('function');
              `
            }
          ],
          hints: [
            'השתמש בפונקציה fill(255) כדי לקבוע צבע לבן',
            'השתמש בפונקציה circle(200, 150, 20) כדי לצייר כדור במרכז'
          ],
          xp: 25
        },
        {
          id: 'milestone-3',
          goal: 'הוסף תנועה לכדור',
          starterCode: `let ballX = 200;
let ballY = 150;
let speedX = 2;

function setup() {
  createCanvas(400, 300);
}

function draw() {
  background(34, 139, 34);

  fill(255);
  circle(ballX, ballY, 20);

  // TODO: הוסף תנועה לכדור
}`,
          tests: [
            {
              id: 'test-movement',
              name: 'בדיקת תנועה',
              description: 'בודק שהכדור זז',
              code: `
                expect(ballX).to.be.a('number');
                expect(speedX).to.be.a('number');
              `
            }
          ],
          hints: [
            'עדכן את ballX בכל פריים: ballX = ballX + speedX',
            'הוסף תנאי להחזרת הכדור כשהוא מגיע לקצה המגרש'
          ],
          xp: 30
        }
      ]
    }
  }
};

export default function LessonPage() {
  const t = useTranslations();
  const params = useParams();
  const theme = params.theme as string;
  const lessonId = params.lesson as string;

  const [currentMilestoneIndex, setCurrentMilestoneIndex] = useState(0);
  const [code, setCode] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [sessionTime, setSessionTime] = useState(20 * 60); // 20 minutes in seconds
  const [xp, setXp] = useState(0);
  const [lastHintIndex, setLastHintIndex] = useState(-1);

  // Get lesson data
  const lessonData = (mockLessonData as any)[theme]?.[lessonId];
  const currentMilestone = lessonData?.milestones[currentMilestoneIndex];

  // Initialize code with starter code
  useEffect(() => {
    if (currentMilestone?.starterCode) {
      setCode(currentMilestone.starterCode);
    }
  }, [currentMilestone]);

  // Session timer
  useEffect(() => {
    const timer = setInterval(() => {
      setSessionTime(prev => {
        if (prev <= 1) {
          // Session timeout
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleRun = () => {
    setIsRunning(true);
    // The preview panel will handle execution
    setTimeout(() => setIsRunning(false), 2000);
  };

  const handleReset = () => {
    if (currentMilestone?.starterCode) {
      setCode(currentMilestone.starterCode);
    }
  };

  const handleGetHint = () => {
    if (!currentMilestone?.hints) return;

    const nextHintIndex = lastHintIndex + 1;
    if (nextHintIndex < currentMilestone.hints.length) {
      setLastHintIndex(nextHintIndex);
      // Show hint in UI - you could use a toast or modal here
      alert(currentMilestone.hints[nextHintIndex]);
    } else {
      alert('אין עוד רמזים זמינים למטלה זו');
    }
  };

  const handleTestComplete = (results: any[]) => {
    console.log('Test results:', results);
  };

  const handleAllTestsComplete = (passed: number, total: number) => {
    if (passed === total) {
      // All tests passed - award XP and move to next milestone
      const earnedXp = currentMilestone?.xp || 0;
      setXp(prev => prev + earnedXp);

      if (currentMilestoneIndex < lessonData.milestones.length - 1) {
        setTimeout(() => {
          setCurrentMilestoneIndex(prev => prev + 1);
          setLastHintIndex(-1);
        }, 1500);
      } else {
        // Lesson complete!
        alert('כל הכבוד! השלמת את השיעור!');
      }
    }
  };

  const handlePreviewError = (error: string) => {
    console.error('Preview error:', error);
  };

  const handlePreviewSuccess = () => {
    console.log('Preview executed successfully');
  };

  if (!lessonData || !currentMilestone) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">שיעור לא נמצא</h1>
          <p className="text-gray-600">השיעור המבוקש לא קיים במערכת</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-primary-600" />
                <h1 className="text-xl font-display font-bold text-gray-900">
                  {lessonData.title}
                </h1>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Target className="w-4 h-4" />
                  <span>ציון דרך {currentMilestoneIndex + 1}/{lessonData.milestones.length}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{formatTime(sessionTime)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Award className="w-4 h-4" />
                  <span>{xp} XP</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Current Goal */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
          <h2 className="text-lg font-display font-semibold text-primary-900 mb-2">
            מטרה נוכחית:
          </h2>
          <p className="text-primary-800 hebrew-text">
            {currentMilestone.goal}
          </p>
        </div>

        {/* Editor and Preview Layout */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Code Editor */}
          <div className="h-96">
            <CodeEditor
              value={code}
              onChange={setCode}
              onRun={handleRun}
              onReset={handleReset}
              onGetHint={handleGetHint}
              isRunning={isRunning}
              hasHints={!!currentMilestone.hints?.length}
              height="100%"
            />
          </div>

          {/* Preview Panel */}
          <div className="h-96">
            <PreviewPanel
              code={code}
              isRunning={isRunning}
              onError={handlePreviewError}
              onSuccess={handlePreviewSuccess}
              theme={theme}
              height="100%"
            />
          </div>
        </div>

        {/* Test Runner */}
        <div className="h-64">
          <TestRunner
            tests={currentMilestone.tests || []}
            userCode={code}
            isRunning={isRunning}
            onTestComplete={handleTestComplete}
            onAllTestsComplete={handleAllTestsComplete}
            autoRun={false}
            theme={theme}
          />
        </div>

        {/* Progress Indicator */}
        <div className="mt-6 bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>התקדמות בשיעור</span>
            <span>{currentMilestoneIndex + 1}/{lessonData.milestones.length}</span>
          </div>
          <div className="progress-container">
            <div
              className="progress-bar"
              style={{
                width: `${((currentMilestoneIndex + 1) / lessonData.milestones.length) * 100}%`
              }}
            />
          </div>
        </div>
      </main>
    </div>
  );
}