'use client';

import React, { useRef, useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { Monitor, AlertCircle, RefreshCw, Maximize2, Minimize2 } from 'lucide-react';

interface PreviewPanelProps {
  code: string;
  isRunning: boolean;
  onError: (error: string) => void;
  onSuccess: () => void;
  theme?: string;
  height?: string;
}

interface ConsoleMessage {
  type: 'log' | 'error' | 'warn' | 'info';
  message: string;
  timestamp: number;
}

export default function PreviewPanel({
  code,
  isRunning,
  onError,
  onSuccess,
  theme = 'football',
  height = '400px',
}: PreviewPanelProps) {
  const t = useTranslations();
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [consoleMessages, setConsoleMessages] = useState<ConsoleMessage[]>([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [lastRunTime, setLastRunTime] = useState<number>(0);

  // Create the sandboxed iframe content
  const createIframeContent = (userCode: string) => {
    return `
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 10px;
            background: #f8f9fa;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: calc(100vh - 20px);
            font-family: 'Noto Sans Hebrew', Arial, sans-serif;
            overflow: hidden;
        }

        main {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            max-width: 600px;
        }

        .canvas-container {
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .error-message {
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 6px;
            padding: 12px;
            margin-top: 10px;
            color: #dc2626;
            font-size: 14px;
            max-width: 500px;
            direction: rtl;
        }

        .success-message {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 6px;
            padding: 8px 12px;
            margin-top: 10px;
            color: #16a34a;
            font-size: 14px;
            direction: rtl;
        }

        .theme-football {
            --primary-color: #22c55e;
            --secondary-color: #ffffff;
            --accent-color: #000000;
        }

        .theme-space {
            --primary-color: #3b82f6;
            --secondary-color: #1e1b4b;
            --accent-color: #fbbf24;
        }

        .theme-robots {
            --primary-color: #6366f1;
            --secondary-color: #374151;
            --accent-color: #f59e0b;
        }
    </style>
</head>
<body class="theme-${theme}">
    <main>
        <div id="canvas-container" class="canvas-container"></div>
        <div id="messages"></div>
    </main>

    <script>
        // Override console methods to capture messages
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;

        function sendMessage(type, message) {
            window.parent.postMessage({
                type: 'console',
                level: type,
                message: String(message),
                timestamp: Date.now()
            }, '*');
        }

        console.log = function(...args) {
            sendMessage('log', args.join(' '));
            originalLog.apply(console, args);
        };

        console.error = function(...args) {
            sendMessage('error', args.join(' '));
            originalError.apply(console, args);
        };

        console.warn = function(...args) {
            sendMessage('warn', args.join(' '));
            originalWarn.apply(console, args);
        };

        // Error handling
        window.addEventListener('error', function(event) {
            const errorMsg = \`שגיאה בשורה \${event.lineno}: \${event.message}\`;
            sendMessage('error', errorMsg);

            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = \`
                <div class="error-message">
                    <strong>שגיאה:</strong> \${errorMsg}
                </div>
            \`;
        });

        window.addEventListener('unhandledrejection', function(event) {
            const errorMsg = \`שגיאה אסינכרונית: \${event.reason}\`;
            sendMessage('error', errorMsg);
        });

        // Override p5.js to use our container
        window.addEventListener('load', function() {
            // Set up p5.js to use our container
            const originalCreateCanvas = window.createCanvas;
            window.createCanvas = function(w, h, renderer) {
                const canvas = originalCreateCanvas.call(this, w || 400, h || 300, renderer);

                // Move canvas to our container
                const container = document.getElementById('canvas-container');
                if (container && canvas) {
                    // Remove from body and add to container
                    if (canvas.parentElement === document.body) {
                        container.appendChild(canvas);
                    }
                }

                return canvas;
            };

            try {
                // Execute user code
                ${userCode}

                // Send success message
                sendMessage('info', 'הקוד רץ בהצלחה!');
                window.parent.postMessage({
                    type: 'success',
                    timestamp: Date.now()
                }, '*');

            } catch (error) {
                const errorMsg = \`שגיאה בקוד: \${error.message}\`;
                sendMessage('error', errorMsg);

                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML = \`
                    <div class="error-message">
                        <strong>שגיאה:</strong> \${errorMsg}
                    </div>
                \`;

                window.parent.postMessage({
                    type: 'error',
                    message: errorMsg,
                    timestamp: Date.now()
                }, '*');
            }
        });

        // Memory and performance monitoring
        let executionTimeout;
        function startExecutionTimer() {
            executionTimeout = setTimeout(() => {
                sendMessage('error', 'הקוד לוקח יותר מדי זמן לרוץ - ייתכן שיש לולאה אינסופית');
            }, 10000); // 10 second timeout
        }

        function clearExecutionTimer() {
            if (executionTimeout) {
                clearTimeout(executionTimeout);
            }
        }

        startExecutionTimer();
    </script>
</body>
</html>`;
  };

  // Handle messages from iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.source !== iframeRef.current?.contentWindow) return;

      const { type, level, message, timestamp } = event.data;

      switch (type) {
        case 'console':
          setConsoleMessages(prev => [
            ...prev.slice(-9), // Keep only last 10 messages
            { type: level, message, timestamp }
          ]);
          break;

        case 'success':
          onSuccess();
          break;

        case 'error':
          onError(message);
          break;
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [onError, onSuccess]);

  // Run code when it changes
  useEffect(() => {
    if (!code.trim() || !iframeRef.current) return;

    setLastRunTime(Date.now());
    setConsoleMessages([]);

    const iframe = iframeRef.current;
    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;

    if (iframeDoc) {
      iframeDoc.open();
      iframeDoc.write(createIframeContent(code));
      iframeDoc.close();
    }
  }, [code, theme]);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const refreshPreview = () => {
    if (iframeRef.current) {
      const iframe = iframeRef.current;
      const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;

      if (iframeDoc) {
        iframeDoc.open();
        iframeDoc.write(createIframeContent(code));
        iframeDoc.close();
      }
    }
  };

  return (
    <div className={`flex flex-col h-full bg-white border border-gray-200 rounded-lg overflow-hidden ${
      isFullscreen ? 'fixed inset-4 z-50' : ''
    }`}>
      {/* Preview Header */}
      <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Monitor className="w-4 h-4 text-gray-600" />
          <h3 className="text-sm font-medium text-gray-700">
            {t('playground.preview')}
          </h3>
          {isRunning && (
            <div className="flex items-center gap-1 text-xs text-blue-600">
              <div className="spinner" />
              <span>{t('playground.running')}</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Refresh Button */}
          <button
            onClick={refreshPreview}
            className="btn-secondary text-xs px-3 py-1.5 min-h-touch min-w-touch"
            title="רענון תצוגה"
            aria-label="רענון תצוגה"
          >
            <RefreshCw className="w-3 h-3" />
          </button>

          {/* Fullscreen Toggle */}
          <button
            onClick={toggleFullscreen}
            className="btn-secondary text-xs px-3 py-1.5 min-h-touch min-w-touch"
            title={isFullscreen ? 'צא ממסך מלא' : 'מסך מלא'}
            aria-label={isFullscreen ? 'צא ממסך מלא' : 'מסך מלא'}
          >
            {isFullscreen ? (
              <Minimize2 className="w-3 h-3" />
            ) : (
              <Maximize2 className="w-3 h-3" />
            )}
          </button>
        </div>
      </div>

      {/* Preview Content */}
      <div className="flex-1 relative" style={{ height: isFullscreen ? 'calc(100vh - 200px)' : height }}>
        <iframe
          ref={iframeRef}
          title={t('playground.preview')}
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin"
          style={{ background: '#f8f9fa' }}
        />

        {/* Loading overlay */}
        {isRunning && (
          <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <div className="spinner w-8 h-8" />
              <span className="text-sm text-gray-600">{t('playground.running')}</span>
            </div>
          </div>
        )}
      </div>

      {/* Console Messages */}
      {consoleMessages.length > 0 && (
        <div className="border-t border-gray-200 bg-gray-900 text-white max-h-32 overflow-y-auto">
          <div className="p-2">
            <div className="text-xs font-medium mb-1 text-gray-300">Console:</div>
            {consoleMessages.map((msg, index) => (
              <div
                key={`${msg.timestamp}-${index}`}
                className={`text-xs mb-1 ${
                  msg.type === 'error' ? 'text-red-400' :
                  msg.type === 'warn' ? 'text-yellow-400' :
                  msg.type === 'info' ? 'text-blue-400' :
                  'text-gray-300'
                }`}
              >
                <span className="text-gray-500">
                  {new Date(msg.timestamp).toLocaleTimeString('he-IL')}
                </span>
                {' '}
                {msg.message}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Status bar */}
      <div className="px-3 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
        <div className="flex justify-between items-center">
          <span>p5.js Preview</span>
          <span>
            {lastRunTime > 0 && (
              <>רץ לאחרונה: {new Date(lastRunTime).toLocaleTimeString('he-IL')}</>
            )}
          </span>
        </div>
      </div>
    </div>
  );
}