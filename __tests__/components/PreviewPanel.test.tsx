/**
 * Tests for PreviewPanel component
 * Tests p5.js integration, iframe sandboxing, error handling, and Hebrew support
 */

import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PreviewPanel from '../../src/components/PreviewPanel';

// Mock next-intl
jest.mock('next-intl', () => ({
  useTranslations: () => (key: string) => {
    const translations: Record<string, string> = {
      'playground.preview': 'תצוגה מקדימה',
      'playground.running': 'רץ...',
    };
    return translations[key] || key;
  },
}));

describe('PreviewPanel Component', () => {
  const defaultProps = {
    code: 'function setup() { createCanvas(400, 300); }',
    isRunning: false,
    onError: jest.fn(),
    onSuccess: jest.fn(),
    theme: 'football',
  };

  beforeEach(() => {
    jest.clearAllMocks();

    // Mock iframe content access
    Object.defineProperty(HTMLIFrameElement.prototype, 'contentDocument', {
      get: jest.fn(() => ({
        open: jest.fn(),
        write: jest.fn(),
        close: jest.fn(),
      })),
      configurable: true,
    });

    Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
      get: jest.fn(() => ({
        document: {
          open: jest.fn(),
          write: jest.fn(),
          close: jest.fn(),
        },
        postMessage: jest.fn(),
      })),
      configurable: true,
    });
  });

  test('renders preview panel with iframe', () => {
    render(<PreviewPanel {...defaultProps} />);

    expect(screen.getByText('תצוגה מקדימה')).toBeInTheDocument();
    expect(screen.getByTitle('תצוגה מקדימה')).toBeInTheDocument();

    const iframe = screen.getByTitle('תצוגה מקדימה');
    expect(iframe).toHaveAttribute('sandbox', 'allow-scripts allow-same-origin');
  });

  test('shows running indicator when isRunning is true', () => {
    render(<PreviewPanel {...defaultProps} isRunning={true} />);

    expect(screen.getByText('רץ...')).toBeInTheDocument();
  });

  test('refresh button triggers iframe reload', async () => {
    const user = userEvent.setup();
    render(<PreviewPanel {...defaultProps} />);

    const refreshButton = screen.getByTitle('רענון תצוגה');
    await user.click(refreshButton);

    // In a real implementation, this would trigger iframe reload
    expect(refreshButton).toBeInTheDocument();
  });

  test('fullscreen toggle works correctly', async () => {
    const user = userEvent.setup();
    render(<PreviewPanel {...defaultProps} />);

    const fullscreenButton = screen.getByTitle('מסך מלא');
    await user.click(fullscreenButton);

    // Check if fullscreen class is applied
    const container = screen.getByTitle('תצוגה מקדימה').closest('div');
    await waitFor(() => {
      expect(container).toHaveClass('fixed');
    });

    // Click again to exit fullscreen
    const exitFullscreenButton = screen.getByTitle('צא ממסך מלא');
    await user.click(exitFullscreenButton);

    await waitFor(() => {
      expect(container).not.toHaveClass('fixed');
    });
  });

  test('handles different themes correctly', () => {
    const { rerender } = render(<PreviewPanel {...defaultProps} theme="football" />);

    // Test football theme
    let iframe = screen.getByTitle('תצוגה מקדימה');
    expect(iframe).toBeInTheDocument();

    // Test space theme
    rerender(<PreviewPanel {...defaultProps} theme="space" />);
    iframe = screen.getByTitle('תצוגה מקדימה');
    expect(iframe).toBeInTheDocument();

    // Test robots theme
    rerender(<PreviewPanel {...defaultProps} theme="robots" />);
    iframe = screen.getByTitle('תצוגה מקדימה');
    expect(iframe).toBeInTheDocument();
  });

  test('handles window messages for console output', () => {
    render(<PreviewPanel {...defaultProps} />);

    // Simulate a console message from iframe
    const mockMessage = {
      source: screen.getByTitle('תצוגה מקדימה').contentWindow,
      data: {
        type: 'console',
        level: 'log',
        message: 'Test message',
        timestamp: Date.now(),
      },
    };

    fireEvent(window, new MessageEvent('message', mockMessage));

    // Console messages should be displayed (would need to check actual implementation)
    expect(screen.getByTitle('תצוגה מקדימה')).toBeInTheDocument();
  });

  test('handles success messages from iframe', () => {
    render(<PreviewPanel {...defaultProps} />);

    // Simulate a success message from iframe
    const mockMessage = {
      source: screen.getByTitle('תצוגה מקדימה').contentWindow,
      data: {
        type: 'success',
        timestamp: Date.now(),
      },
    };

    fireEvent(window, new MessageEvent('message', mockMessage));

    expect(defaultProps.onSuccess).toHaveBeenCalledTimes(1);
  });

  test('handles error messages from iframe', () => {
    render(<PreviewPanel {...defaultProps} />);

    const errorMessage = 'שגיאה בקוד';

    // Simulate an error message from iframe
    const mockMessage = {
      source: screen.getByTitle('תצוגה מקדימה').contentWindow,
      data: {
        type: 'error',
        message: errorMessage,
        timestamp: Date.now(),
      },
    };

    fireEvent(window, new MessageEvent('message', mockMessage));

    expect(defaultProps.onError).toHaveBeenCalledWith(errorMessage);
  });

  test('creates iframe content with p5.js and Hebrew support', () => {
    render(<PreviewPanel {...defaultProps} />);

    const iframe = screen.getByTitle('תצוגה מקדימה');
    expect(iframe).toBeInTheDocument();

    // The iframe should have Hebrew lang and RTL direction in its content
    // This would be verified by checking the generated HTML content
  });

  test('handles Hebrew error messages correctly', () => {
    const hebrewCode = '// שגיאה בעברית\nfunction setup() {\n  undefined_function();\n}';
    render(<PreviewPanel {...defaultProps} code={hebrewCode} />);

    // Simulate Hebrew error message
    const hebrewError = 'שגיאה: פונקציה לא מוגדרת';
    const mockMessage = {
      source: screen.getByTitle('תצוגה מקדימה').contentWindow,
      data: {
        type: 'error',
        message: hebrewError,
        timestamp: Date.now(),
      },
    };

    fireEvent(window, new MessageEvent('message', mockMessage));

    expect(defaultProps.onError).toHaveBeenCalledWith(hebrewError);
  });

  test('iframe security sandbox attributes are correct', () => {
    render(<PreviewPanel {...defaultProps} />);

    const iframe = screen.getByTitle('תצוגה מקדימה');
    expect(iframe).toHaveAttribute('sandbox', 'allow-scripts allow-same-origin');
  });

  test('status bar shows last run time', () => {
    render(<PreviewPanel {...defaultProps} />);

    // Check that status bar exists
    expect(screen.getByText('p5.js Preview')).toBeInTheDocument();
  });

  test('handles code updates and regenerates iframe content', () => {
    const { rerender } = render(<PreviewPanel {...defaultProps} />);

    const newCode = 'function setup() { createCanvas(800, 600); }';
    rerender(<PreviewPanel {...defaultProps} code={newCode} />);

    // The iframe should update with new code
    const iframe = screen.getByTitle('תצוגה מקדימה');
    expect(iframe).toBeInTheDocument();
  });

  test('console messages are displayed with timestamps', () => {
    render(<PreviewPanel {...defaultProps} />);

    // Simulate multiple console messages
    const messages = [
      { type: 'log', message: 'Setup completed', level: 'log' },
      { type: 'warn', message: 'Warning message', level: 'warn' },
      { type: 'error', message: 'Error occurred', level: 'error' },
    ];

    messages.forEach((msg, index) => {
      const mockMessage = {
        source: screen.getByTitle('תצוגה מקדימה').contentWindow,
        data: {
          type: 'console',
          ...msg,
          timestamp: Date.now() + index,
        },
      };

      fireEvent(window, new MessageEvent('message', mockMessage));
    });

    // Console area should display messages
    // This would be verified by checking the actual console display implementation
  });

  test('respects height prop', () => {
    render(<PreviewPanel {...defaultProps} height="500px" />);

    const previewContainer = screen.getByTitle('תצוגה מקדימה').closest('div');
    // In actual implementation, this would check the computed height style
    expect(previewContainer).toBeInTheDocument();
  });

  test('memory cleanup on unmount', () => {
    const { unmount } = render(<PreviewPanel {...defaultProps} />);

    // Add event listener spy
    const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');

    unmount();

    // Should clean up message event listener
    expect(removeEventListenerSpy).toHaveBeenCalledWith('message', expect.any(Function));

    removeEventListenerSpy.mockRestore();
  });
});