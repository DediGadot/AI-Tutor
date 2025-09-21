'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useTranslations } from 'next-intl';
import { CheckCircle, XCircle, Clock, Play, RotateCcw } from 'lucide-react';

interface TestSpec {
  id: string;
  name: string;
  description: string;
  code: string;
  timeout?: number;
}

interface TestResult {
  id: string;
  name: string;
  status: 'pass' | 'fail' | 'pending' | 'running';
  message?: string;
  duration?: number;
  error?: string;
}

interface TestRunnerProps {
  tests: TestSpec[];
  userCode: string;
  isRunning: boolean;
  onTestComplete: (results: TestResult[]) => void;
  onAllTestsComplete: (passed: number, total: number) => void;
  autoRun?: boolean;
  theme?: string;
}

export default function TestRunner({
  tests,
  userCode,
  isRunning,
  onTestComplete,
  onAllTestsComplete,
  autoRun = false,
  theme = 'football',
}: TestRunnerProps) {
  const t = useTranslations();
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [currentTestIndex, setCurrentTestIndex] = useState(-1);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Initialize test results
  useEffect(() => {
    const initialResults = tests.map(test => ({
      id: test.id,
      name: test.name,
      status: 'pending' as const,
    }));
    setTestResults(initialResults);
  }, [tests]);

  // Create test runner iframe content
  const createTestRunnerContent = (testCode: string, userCodeToTest: string) => {
    return `
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Test Runner</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mocha/10.2.0/mocha.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chai/4.3.10/chai.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/mocha/10.2.0/mocha.min.css">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans Hebrew', Arial, sans-serif;
            direction: rtl;
            font-size: 12px;
        }

        #mocha {
            padding: 10px;
            font-size: 12px;
        }

        .hidden-canvas {
            position: absolute;
            left: -9999px;
            top: -9999px;
        }

        .test-canvas {
            border: 1px solid #ddd;
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div id="mocha"></div>

    <script>
        // Set up Mocha
        mocha.setup({
            ui: 'bdd',
            timeout: 5000,
            reporter: 'json'
        });

        const expect = chai.expect;
        let canvas, width, height;
        let testCanvas;

        // Message passing to parent
        function sendMessage(type, data) {
            window.parent.postMessage({
                type: type,
                data: data,
                timestamp: Date.now()
            }, '*');
        }

        // Mock p5.js functions for testing
        function createTestCanvas(w = 400, h = 300) {
            testCanvas = document.createElement('canvas');
            testCanvas.width = w;
            testCanvas.height = h;
            testCanvas.className = 'hidden-canvas';
            document.body.appendChild(testCanvas);

            // Set global variables that p5.js would set
            canvas = testCanvas;
            width = w;
            height = h;

            return testCanvas;
        }

        function clearTestCanvas() {
            if (testCanvas) {
                testCanvas.parentElement?.removeChild(testCanvas);
                testCanvas = null;
                canvas = null;
            }
        }

        // Override console for test output
        const originalLog = console.log;
        console.log = function(...args) {
            sendMessage('console', { level: 'log', message: args.join(' ') });
            originalLog.apply(console, args);
        };

        // Global error handling
        window.addEventListener('error', function(event) {
            sendMessage('error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error?.stack
            });
        });

        // Execute user code in controlled environment
        function executeUserCode() {
            try {
                // Create a safe execution context
                const userCodeFunction = new Function(\`
                    let setup, draw, mousePressed, keyPressed;
                    let mouseX = 0, mouseY = 0;
                    let key = '', keyCode = 0;

                    // Mock p5.js functions that might be used
                    function createCanvas(w, h) {
                        return createTestCanvas(w, h);
                    }

                    function background(color) {
                        if (testCanvas) {
                            const ctx = testCanvas.getContext('2d');
                            ctx.fillStyle = typeof color === 'number' ? \`rgb(\${color},\${color},\${color})\` : color;
                            ctx.fillRect(0, 0, testCanvas.width, testCanvas.height);
                        }
                    }

                    function circle(x, y, diameter) {
                        if (testCanvas) {
                            const ctx = testCanvas.getContext('2d');
                            ctx.beginPath();
                            ctx.arc(x, y, diameter / 2, 0, Math.PI * 2);
                            ctx.stroke();
                        }
                    }

                    function rect(x, y, w, h) {
                        if (testCanvas) {
                            const ctx = testCanvas.getContext('2d');
                            ctx.strokeRect(x, y, w, h);
                        }
                    }

                    function fill(color) {
                        if (testCanvas) {
                            const ctx = testCanvas.getContext('2d');
                            ctx.fillStyle = typeof color === 'number' ? \`rgb(\${color},\${color},\${color})\` : color;
                        }
                    }

                    function stroke(color) {
                        if (testCanvas) {
                            const ctx = testCanvas.getContext('2d');
                            ctx.strokeStyle = typeof color === 'number' ? \`rgb(\${color},\${color},\${color})\` : color;
                        }
                    }

                    function noFill() {
                        if (testCanvas) {
                            const ctx = testCanvas.getContext('2d');
                            ctx.fillStyle = 'transparent';
                        }
                    }

                    function noStroke() {
                        if (testCanvas) {
                            const ctx = testCanvas.getContext('2d');
                            ctx.strokeStyle = 'transparent';
                        }
                    }

                    // Execute user code
                    \${userCodeToTest}

                    // Return functions for testing
                    return { setup, draw, mousePressed, keyPressed };
                \`);

                return userCodeFunction();
            } catch (error) {
                sendMessage('error', {
                    message: 'שגיאה בביצוע הקוד: ' + error.message,
                    error: error.stack
                });
                return null;
            }
        }

        // Run a single test
        function runSingleTest(testSpec) {
            return new Promise((resolve) => {
                const startTime = Date.now();
                clearTestCanvas();

                try {
                    // Execute user code first
                    const userFunctions = executeUserCode();

                    if (!userFunctions) {
                        resolve({
                            status: 'fail',
                            message: 'שגיאה בביצוע הקוד',
                            duration: Date.now() - startTime
                        });
                        return;
                    }

                    // Make user functions globally available for tests
                    Object.assign(window, userFunctions);

                    // Execute the test
                    const testFunction = new Function('expect', 'canvas', 'width', 'height', testSpec);
                    testFunction(expect, canvas, width, height);

                    resolve({
                        status: 'pass',
                        message: 'הבדיקה עברה בהצלחה',
                        duration: Date.now() - startTime
                    });

                } catch (error) {
                    resolve({
                        status: 'fail',
                        message: error.message || 'הבדיקה נכשלה',
                        error: error.stack,
                        duration: Date.now() - startTime
                    });
                }
            });
        }

        // Test runner function
        async function runTests(testSpecs) {
            const results = [];

            for (let i = 0; i < testSpecs.length; i++) {
                const testSpec = testSpecs[i];
                sendMessage('testStart', { index: i, name: testSpec.name });

                const result = await runSingleTest(testSpec.code);
                results.push({
                    id: testSpec.id,
                    name: testSpec.name,
                    ...result
                });

                sendMessage('testComplete', {
                    index: i,
                    result: {
                        id: testSpec.id,
                        name: testSpec.name,
                        ...result
                    }
                });

                // Small delay between tests
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            sendMessage('allTestsComplete', { results });
            clearTestCanvas();
        }

        // Listen for messages from parent
        window.addEventListener('message', function(event) {
            if (event.data.type === 'runTests') {
                runTests(event.data.tests);
            }
        });

        // Signal that test runner is ready
        sendMessage('ready', {});
    </script>
</body>
</html>`;
  };

  // Handle messages from test runner iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.source !== iframeRef.current?.contentWindow) return;

      const { type, data } = event.data;

      switch (type) {
        case 'ready':
          // Test runner is ready, start tests if auto-run is enabled
          if (autoRun && isRunning) {
            runTests();
          }
          break;

        case 'testStart':
          setCurrentTestIndex(data.index);
          setTestResults(prev => prev.map((result, index) =>
            index === data.index
              ? { ...result, status: 'running' }
              : result
          ));
          break;

        case 'testComplete':
          setTestResults(prev => prev.map((result, index) =>
            index === data.index
              ? { ...result, ...data.result }
              : result
          ));
          break;

        case 'allTestsComplete':
          setCurrentTestIndex(-1);
          const results = data.results;
          setTestResults(results);
          onTestComplete(results);

          const passed = results.filter((r: TestResult) => r.status === 'pass').length;
          onAllTestsComplete(passed, results.length);
          break;

        case 'error':
          console.error('Test runner error:', data);
          break;
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [autoRun, isRunning, onTestComplete, onAllTestsComplete]);

  // Initialize iframe
  useEffect(() => {
    if (iframeRef.current) {
      const iframe = iframeRef.current;
      const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;

      if (iframeDoc) {
        iframeDoc.open();
        iframeDoc.write(createTestRunnerContent('', userCode));
        iframeDoc.close();
      }
    }
  }, [userCode]);

  const runTests = () => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage({
        type: 'runTests',
        tests: tests
      }, '*');
    }
  };

  const resetTests = () => {
    setTestResults(tests.map(test => ({
      id: test.id,
      name: test.name,
      status: 'pending',
    })));
    setCurrentTestIndex(-1);
  };

  const passedCount = testResults.filter(r => r.status === 'pass').length;
  const totalCount = testResults.length;

  return (
    <div className="flex flex-col h-full bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Test Header */}
      <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            {passedCount === totalCount && totalCount > 0 ? (
              <CheckCircle className="w-4 h-4 text-success-600" />
            ) : passedCount > 0 ? (
              <Clock className="w-4 h-4 text-warning-600" />
            ) : (
              <XCircle className="w-4 h-4 text-gray-400" />
            )}
            <h3 className="text-sm font-medium text-gray-700">
              {t('playground.tests')}
            </h3>
          </div>
          <div className="text-xs text-gray-500">
            {passedCount}/{totalCount} {t('playground.testsPassed')}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={resetTests}
            className="btn-secondary text-xs px-3 py-1.5 min-h-touch min-w-touch"
            title="איפוס בדיקות"
            aria-label="איפוס בדיקות"
          >
            <RotateCcw className="w-3 h-3 me-1" />
            איפוס
          </button>

          <button
            onClick={runTests}
            disabled={isRunning}
            className={`btn-primary text-xs px-3 py-1.5 min-h-touch min-w-touch ${
              isRunning ? 'opacity-75 cursor-not-allowed' : ''
            }`}
            title="הרץ בדיקות"
            aria-label="הרץ בדיקות"
          >
            {isRunning ? (
              <div className="spinner me-1" />
            ) : (
              <Play className="w-3 h-3 me-1" />
            )}
            הרץ
          </button>
        </div>
      </div>

      {/* Test Results */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {testResults.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <Clock className="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">{t('playground.noTests')}</p>
          </div>
        ) : (
          testResults.map((result, index) => (
            <div
              key={result.id}
              className={`p-3 rounded-lg border-2 transition-all ${
                result.status === 'pass'
                  ? 'test-pass border-success-200'
                  : result.status === 'fail'
                  ? 'test-fail border-error-200'
                  : result.status === 'running'
                  ? 'test-pending border-warning-200 bg-warning-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {result.status === 'pass' ? (
                    <CheckCircle className="w-4 h-4 text-success-600" />
                  ) : result.status === 'fail' ? (
                    <XCircle className="w-4 h-4 text-error-600" />
                  ) : result.status === 'running' ? (
                    <div className="spinner" />
                  ) : (
                    <Clock className="w-4 h-4 text-gray-400" />
                  )}
                  <span className="font-medium text-sm">{result.name}</span>
                </div>
                {result.duration && (
                  <span className="text-xs text-gray-500">
                    {result.duration}ms
                  </span>
                )}
              </div>

              {result.message && (
                <p className="text-xs text-gray-600 mb-1">{result.message}</p>
              )}

              {result.error && (
                <details className="text-xs text-error-600">
                  <summary className="cursor-pointer">פרטי שגיאה</summary>
                  <pre className="mt-1 p-2 bg-error-50 rounded text-error-800 overflow-x-auto">
                    {result.error}
                  </pre>
                </details>
              )}

              {currentTestIndex === index && (
                <div className="mt-2 h-1 bg-gray-200 rounded overflow-hidden">
                  <div className="h-full bg-primary-500 animate-pulse" />
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Summary */}
      {testResults.length > 0 && (
        <div className="p-3 bg-gray-50 border-t border-gray-200">
          <div className="flex justify-between text-sm">
            <span>
              {passedCount === totalCount && totalCount > 0
                ? t('playground.allTestsPassed')
                : passedCount > 0
                ? t('playground.someTestsFailed')
                : 'טרם הורצו בדיקות'
              }
            </span>
            <span className="text-gray-500">
              {passedCount}/{totalCount}
            </span>
          </div>

          {passedCount < totalCount && totalCount > 0 && (
            <div className="mt-2">
              <div className="progress-container">
                <div
                  className="progress-bar"
                  style={{ width: `${(passedCount / totalCount) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Hidden test runner iframe */}
      <iframe
        ref={iframeRef}
        title="Test Runner"
        className="hidden"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
}