'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Editor } from '@monaco-editor/react';
import { useTranslations } from 'next-intl';
import { Play, RotateCcw, Lightbulb, Code } from 'lucide-react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  onRun: () => void;
  onReset: () => void;
  onGetHint: () => void;
  language?: string;
  theme?: 'light' | 'dark';
  readOnly?: boolean;
  height?: string;
  isRunning?: boolean;
  hasHints?: boolean;
}

export default function CodeEditor({
  value,
  onChange,
  onRun,
  onReset,
  onGetHint,
  language = 'javascript',
  theme = 'light',
  readOnly = false,
  height = '400px',
  isRunning = false,
  hasHints = true,
}: CodeEditorProps) {
  const t = useTranslations();
  const editorRef = useRef<any>(null);
  const [isEditorReady, setIsEditorReady] = useState(false);

  // Monaco editor configuration for Hebrew RTL support
  const editorOptions = {
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: readOnly,
    cursorStyle: 'line' as const,
    automaticLayout: true,
    scrollBeyondLastLine: false,
    wordWrap: 'on' as const,
    minimap: { enabled: false },
    fontSize: 14,
    lineHeight: 20,
    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
    tabSize: 2,
    insertSpaces: true,
    detectIndentation: false,
    // RTL support
    renderControlCharacters: false,
    renderWhitespace: 'none' as const,
    // Accessibility
    ariaLabel: t('playground.editor'),
    accessibilitySupport: 'on' as const,
    // Hebrew comment support
    bracketPairColorization: { enabled: true },
    guides: {
      bracketPairs: true,
      indentation: true,
    },
  };

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    setIsEditorReady(true);

    // Configure Hebrew language support for comments
    monaco.languages.setLanguageConfiguration('javascript', {
      comments: {
        lineComment: '//',
        blockComment: ['/*', '*/']
      },
      brackets: [
        ['{', '}'],
        ['[', ']'],
        ['(', ')']
      ],
      autoClosingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"' },
        { open: "'", close: "'" }
      ],
      surroundingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"' },
        { open: "'", close: "'" }
      ]
    });

    // Add Hebrew snippets
    monaco.languages.registerCompletionItemProvider('javascript', {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions = [
          {
            label: 'setup',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'function setup() {\n  createCanvas(400, 300);\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'יוצר פונקציית setup בסיסית עם קנווס'
          },
          {
            label: 'draw',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'function draw() {\n  background(220);\n  // הוסף כאן את הקוד שלך\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'יוצר פונקציית draw בסיסית'
          },
          {
            label: 'createCanvas',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'createCanvas(${1:400}, ${2:300});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'יוצר קנווס עם רוחב וגובה'
          },
          {
            label: 'background',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'background(${1:220});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'קובע צבע רקע'
          },
          {
            label: 'circle',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'circle(${1:x}, ${2:y}, ${3:diameter});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'משרטט עיגול'
          },
          {
            label: 'rect',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'rect(${1:x}, ${2:y}, ${3:width}, ${4:height});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'משרטט מלבן'
          }
        ];
        return { suggestions };
      }
    });

    // Focus the editor for immediate use
    editor.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl/Cmd + Enter to run code
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (!isRunning) {
        onRun();
      }
    }
    // F1 for hint
    if (e.key === 'F1') {
      e.preventDefault();
      if (hasHints) {
        onGetHint();
      }
    }
  };

  return (
    <div className="flex flex-col h-full bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Editor Header */}
      <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Code className="w-4 h-4 text-gray-600" />
          <h3 className="text-sm font-medium text-gray-700">
            {t('playground.editor')}
          </h3>
        </div>

        <div className="flex items-center gap-2">
          {/* Hint Button */}
          {hasHints && (
            <button
              onClick={onGetHint}
              className="btn-secondary text-xs px-3 py-1.5 min-h-touch min-w-touch"
              title={t('playground.getHint')}
              aria-label={t('playground.getHint')}
            >
              <Lightbulb className="w-3 h-3 me-1" />
              {t('playground.hint')}
            </button>
          )}

          {/* Reset Button */}
          <button
            onClick={onReset}
            className="btn-secondary text-xs px-3 py-1.5 min-h-touch min-w-touch"
            title="איפוס קוד"
            aria-label="איפוס קוד"
          >
            <RotateCcw className="w-3 h-3 me-1" />
            איפוס
          </button>

          {/* Run Button */}
          <button
            onClick={onRun}
            disabled={isRunning}
            className={`btn-primary text-xs px-4 py-1.5 min-h-touch min-w-touch ${
              isRunning ? 'opacity-75 cursor-not-allowed' : ''
            }`}
            title={t('playground.runAndCheck')}
            aria-label={t('playground.runAndCheck')}
          >
            {isRunning ? (
              <div className="spinner me-1" />
            ) : (
              <Play className="w-3 h-3 me-1" />
            )}
            {isRunning ? t('playground.running') : t('playground.runAndCheck')}
          </button>
        </div>
      </div>

      {/* Editor */}
      <div
        className="flex-1 relative"
        onKeyDown={handleKeyDown}
        style={{ height }}
      >
        <Editor
          height="100%"
          language={language}
          theme={theme === 'dark' ? 'vs-dark' : 'vs'}
          value={value}
          onChange={(newValue) => onChange(newValue || '')}
          onMount={handleEditorDidMount}
          options={editorOptions}
          loading={
            <div className="flex items-center justify-center h-full">
              <div className="flex items-center gap-2 text-gray-500">
                <div className="spinner" />
                <span>{t('common.loading')}</span>
              </div>
            </div>
          }
        />

        {/* Keyboard shortcuts overlay */}
        <div className="absolute bottom-2 left-2 text-xs text-gray-400 bg-white bg-opacity-90 px-2 py-1 rounded">
          <div>Ctrl/Cmd + Enter: {t('playground.runAndCheck')}</div>
          <div>F1: {t('playground.getHint')}</div>
        </div>
      </div>

      {/* Status bar */}
      <div className="px-3 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
        <div className="flex justify-between items-center">
          <span>JavaScript (p5.js)</span>
          <span>
            {isEditorReady ? 'מוכן' : t('common.loading')}
          </span>
        </div>
      </div>
    </div>
  );
}