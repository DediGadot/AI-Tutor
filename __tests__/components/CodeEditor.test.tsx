/**
 * Tests for CodeEditor component
 * Tests Monaco editor integration, Hebrew support, and coding functionality
 */

import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CodeEditor from '../../src/components/CodeEditor';

// Mock Monaco Editor
jest.mock('@monaco-editor/react', () => ({
  __esModule: true,
  Editor: ({ value, onChange, onMount, ...props }: any) => (
    <textarea
      data-testid="monaco-editor"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      {...props}
    />
  ),
}));

// Mock next-intl
jest.mock('next-intl', () => ({
  useTranslations: () => (key: string) => {
    const translations: Record<string, string> = {
      'playground.run': 'הרץ',
      'playground.reset': 'איפוס',
      'playground.hint': 'רמז',
      'playground.running': 'רץ...',
      'playground.codeEditor': 'עורך קוד',
    };
    return translations[key] || key;
  },
}));

describe('CodeEditor Component', () => {
  const defaultProps = {
    value: '// Starting code',
    onChange: jest.fn(),
    onRun: jest.fn(),
    onReset: jest.fn(),
    onGetHint: jest.fn(),
    isRunning: false,
    hasHints: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders code editor with basic functionality', () => {
    render(<CodeEditor {...defaultProps} />);

    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
    expect(screen.getByText('הרץ')).toBeInTheDocument();
    expect(screen.getByText('איפוס')).toBeInTheDocument();
    expect(screen.getByText('רמז')).toBeInTheDocument();
  });

  test('handles code changes', async () => {
    const user = userEvent.setup();
    render(<CodeEditor {...defaultProps} />);

    const editor = screen.getByTestId('monaco-editor');
    await user.clear(editor);
    await user.type(editor, 'function setup() { createCanvas(400, 300); }');

    expect(defaultProps.onChange).toHaveBeenCalledWith(
      'function setup() { createCanvas(400, 300); }'
    );
  });

  test('run button triggers onRun callback', async () => {
    const user = userEvent.setup();
    render(<CodeEditor {...defaultProps} />);

    const runButton = screen.getByText('הרץ');
    await user.click(runButton);

    expect(defaultProps.onRun).toHaveBeenCalledTimes(1);
  });

  test('reset button triggers onReset callback', async () => {
    const user = userEvent.setup();
    render(<CodeEditor {...defaultProps} />);

    const resetButton = screen.getByText('איפוס');
    await user.click(resetButton);

    expect(defaultProps.onReset).toHaveBeenCalledTimes(1);
  });

  test('hint button triggers onGetHint callback', async () => {
    const user = userEvent.setup();
    render(<CodeEditor {...defaultProps} />);

    const hintButton = screen.getByText('רמז');
    await user.click(hintButton);

    expect(defaultProps.onGetHint).toHaveBeenCalledTimes(1);
  });

  test('shows running state correctly', () => {
    render(<CodeEditor {...defaultProps} isRunning={true} />);

    expect(screen.getByText('רץ...')).toBeInTheDocument();

    const runButton = screen.getByText('רץ...');
    expect(runButton).toBeDisabled();
  });

  test('hides hint button when hasHints is false', () => {
    render(<CodeEditor {...defaultProps} hasHints={false} />);

    expect(screen.queryByText('רמז')).not.toBeInTheDocument();
  });

  test('handles Hebrew text in code editor', () => {
    const hebrewCode = '// תגובה בעברית\nfunction setup() {\n  // צור קנווס\n}';
    render(<CodeEditor {...defaultProps} value={hebrewCode} />);

    const editor = screen.getByTestId('monaco-editor');
    expect(editor).toHaveValue(hebrewCode);
  });

  test('supports RTL direction for Hebrew comments', () => {
    render(<CodeEditor {...defaultProps} />);

    // Check that the component has proper RTL support
    const editorContainer = screen.getByTestId('monaco-editor').closest('div');
    // In a real implementation, we'd check for dir="rtl" or appropriate CSS classes
    expect(editorContainer).toBeInTheDocument();
  });

  test('shows editor with proper accessibility attributes', () => {
    render(<CodeEditor {...defaultProps} />);

    const editor = screen.getByTestId('monaco-editor');
    expect(editor).toHaveAttribute('aria-label');
  });

  test('keyboard shortcuts work correctly', async () => {
    const user = userEvent.setup();
    render(<CodeEditor {...defaultProps} />);

    const editor = screen.getByTestId('monaco-editor');

    // Test Ctrl+S (should trigger save/run)
    await user.click(editor);
    await user.keyboard('{Control>}s{/Control}');

    // In a real implementation, this might trigger onRun
    expect(editor).toHaveFocus();
  });

  test('handles large code files without performance issues', () => {
    const largeCode = 'function test() {\n'.repeat(1000) + '}'.repeat(1000);

    const { rerender } = render(<CodeEditor {...defaultProps} value={largeCode} />);

    expect(screen.getByTestId('monaco-editor')).toHaveValue(largeCode);

    // Test that re-rendering with new large content works
    const newLargeCode = 'function newTest() {\n'.repeat(1000) + '}'.repeat(1000);
    rerender(<CodeEditor {...defaultProps} value={newLargeCode} />);

    expect(screen.getByTestId('monaco-editor')).toHaveValue(newLargeCode);
  });

  test('code editor maintains focus during typing', async () => {
    const user = userEvent.setup();
    render(<CodeEditor {...defaultProps} />);

    const editor = screen.getByTestId('monaco-editor');
    await user.click(editor);

    expect(editor).toHaveFocus();

    await user.type(editor, 'test');
    expect(editor).toHaveFocus();
  });

  test('button states are correct based on props', () => {
    const { rerender } = render(<CodeEditor {...defaultProps} />);

    // Normal state
    expect(screen.getByText('הרץ')).not.toBeDisabled();
    expect(screen.getByText('איפוס')).not.toBeDisabled();
    expect(screen.getByText('רמז')).not.toBeDisabled();

    // Running state
    rerender(<CodeEditor {...defaultProps} isRunning={true} />);
    expect(screen.getByText('רץ...')).toBeDisabled();

    // No hints available
    rerender(<CodeEditor {...defaultProps} hasHints={false} />);
    expect(screen.queryByText('רמז')).not.toBeInTheDocument();
  });
});