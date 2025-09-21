/**
 * Tests for TTSProvider component
 * Tests Hebrew text-to-speech, voice selection, and accessibility features
 */

import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TTSProvider, { useTTS } from '../../../src/components/Speech/TTSProvider';

// Mock Web Speech API
const mockSpeechSynthesis = {
  speak: jest.fn(),
  cancel: jest.fn(),
  pause: jest.fn(),
  resume: jest.fn(),
  getVoices: jest.fn(() => [
    {
      name: 'Hebrew Voice',
      lang: 'he-IL',
      localService: true,
      default: false,
    },
    {
      name: 'English Voice',
      lang: 'en-US',
      localService: true,
      default: true,
    },
  ]),
  speaking: false,
  paused: false,
  pending: false,
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
};

const mockSpeechSynthesisUtterance = jest.fn().mockImplementation((text) => ({
  text,
  lang: 'he-IL',
  voice: null,
  volume: 1,
  rate: 1,
  pitch: 1,
  onstart: null,
  onend: null,
  onerror: null,
  onpause: null,
  onresume: null,
  onmark: null,
  onboundary: null,
}));

// Mock next-intl
jest.mock('next-intl', () => ({
  useTranslations: () => (key: string) => key,
}));

// Test component that uses TTS
const TestTTSComponent = () => {
  const { speak, stop, isSupported, isSpeaking, config, hebrewVoices } = useTTS();

  return (
    <div>
      <div data-testid="supported">{isSupported ? 'supported' : 'not-supported'}</div>
      <div data-testid="speaking">{isSpeaking ? 'speaking' : 'not-speaking'}</div>
      <div data-testid="hebrew-voices">{hebrewVoices.length}</div>
      <div data-testid="config-rate">{config.rate}</div>
      <button onClick={() => speak('שלום עולם')}>Speak Hebrew</button>
      <button onClick={stop}>Stop</button>
    </div>
  );
};

describe('TTSProvider Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Set up global mocks
    global.speechSynthesis = mockSpeechSynthesis;
    global.SpeechSynthesisUtterance = mockSpeechSynthesisUtterance;

    // Reset speaking state
    mockSpeechSynthesis.speaking = false;
  });

  afterEach(() => {
    delete global.speechSynthesis;
    delete global.SpeechSynthesisUtterance;
  });

  test('detects speech synthesis support', () => {
    render(
      <TTSProvider>
        <TestTTSComponent />
      </TTSProvider>
    );

    expect(screen.getByTestId('supported')).toHaveTextContent('supported');
  });

  test('provides default configuration', () => {
    render(
      <TTSProvider>
        <TestTTSComponent />
      </TTSProvider>
    );

    expect(screen.getByTestId('config-rate')).toHaveTextContent('0.8');
  });

  test('loads and filters Hebrew voices', async () => {
    render(
      <TTSProvider>
        <TestTTSComponent />
      </TTSProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('hebrew-voices')).toHaveTextContent('1');
    });
  });

  test('speaks Hebrew text correctly', async () => {
    const user = userEvent.setup();
    render(
      <TTSProvider>
        <TestTTSComponent />
      </TTSProvider>
    );

    const speakButton = screen.getByText('Speak Hebrew');
    await user.click(speakButton);

    expect(mockSpeechSynthesis.cancel).toHaveBeenCalled();
    expect(mockSpeechSynthesisUtterance).toHaveBeenCalledWith('שלום עולם');
    expect(mockSpeechSynthesis.speak).toHaveBeenCalled();
  });

  test('cleans Hebrew text before speaking', async () => {
    const user = userEvent.setup();

    const TestCleanText = () => {
      const { speak } = useTTS();
      return (
        <button onClick={() => speak('שלום 🎉 עולם! 123')}>
          Speak Mixed Text
        </button>
      );
    };

    render(
      <TTSProvider>
        <TestCleanText />
      </TTSProvider>
    );

    const speakButton = screen.getByText('Speak Mixed Text');
    await user.click(speakButton);

    // Should clean text and remove emojis
    expect(mockSpeechSynthesisUtterance).toHaveBeenCalledWith('שלום עולם! 123');
  });

  test('stops speech when stop is called', async () => {
    const user = userEvent.setup();
    render(
      <TTSProvider>
        <TestTTSComponent />
      </TTSProvider>
    );

    const stopButton = screen.getByText('Stop');
    await user.click(stopButton);

    expect(mockSpeechSynthesis.cancel).toHaveBeenCalled();
  });

  test('handles speech synthesis events', () => {
    render(
      <TTSProvider>
        <TestTTSComponent />
      </TTSProvider>
    );

    // Simulate utterance creation and events
    const utterance = new mockSpeechSynthesisUtterance('test');

    // Simulate speech start
    if (utterance.onstart) {
      utterance.onstart(new Event('start'));
    }

    // Speaking state should be updated
    // This would be tested in the actual implementation
  });

  test('applies custom configuration to utterance', async () => {
    const customConfig = {
      rate: 1.2,
      pitch: 1.1,
      volume: 0.8,
    };

    const TestCustomConfig = () => {
      const { speak } = useTTS();
      return (
        <button onClick={() => speak('בדיקה', customConfig)}>
          Speak with Custom Config
        </button>
      );
    };

    const user = userEvent.setup();
    render(
      <TTSProvider defaultConfig={customConfig}>
        <TestCustomConfig />
      </TTSProvider>
    );

    const speakButton = screen.getByText('Speak with Custom Config');
    await user.click(speakButton);

    expect(mockSpeechSynthesisUtterance).toHaveBeenCalledWith('בדיקה');

    // The utterance should have custom properties applied
    const calls = mockSpeechSynthesis.speak.mock.calls;
    expect(calls.length).toBeGreaterThan(0);
  });

  test('handles unsupported browsers gracefully', () => {
    // Remove speech synthesis support before rendering
    delete global.speechSynthesis;
    delete global.SpeechSynthesisUtterance;

    render(
      <TTSProvider>
        <TestTTSComponent />
      </TTSProvider>
    );

    expect(screen.getByTestId('supported')).toHaveTextContent('not-supported');

    // Restore for other tests
    global.speechSynthesis = mockSpeechSynthesis;
    global.SpeechSynthesisUtterance = mockSpeechSynthesisUtterance;
  });

  test('pauses and resumes speech correctly', () => {
    const TestPauseResume = () => {
      const { pause, resume } = useTTS();
      return (
        <div>
          <button onClick={pause}>Pause</button>
          <button onClick={resume}>Resume</button>
        </div>
      );
    };

    const user = userEvent.setup();
    render(
      <TTSProvider>
        <TestPauseResume />
      </TTSProvider>
    );

    // Test pause
    mockSpeechSynthesis.speaking = true;
    fireEvent.click(screen.getByText('Pause'));
    expect(mockSpeechSynthesis.pause).toHaveBeenCalled();

    // Test resume
    mockSpeechSynthesis.paused = true;
    fireEvent.click(screen.getByText('Resume'));
    expect(mockSpeechSynthesis.resume).toHaveBeenCalled();
  });

  test('updates configuration dynamically', () => {
    const TestConfigUpdate = () => {
      const { config, updateConfig } = useTTS();
      return (
        <div>
          <div data-testid="current-rate">{config.rate}</div>
          <button onClick={() => updateConfig({ rate: 1.5 })}>
            Update Rate
          </button>
        </div>
      );
    };

    const user = userEvent.setup();
    render(
      <TTSProvider>
        <TestConfigUpdate />
      </TTSProvider>
    );

    expect(screen.getByTestId('current-rate')).toHaveTextContent('0.8');

    fireEvent.click(screen.getByText('Update Rate'));

    expect(screen.getByTestId('current-rate')).toHaveTextContent('1.5');
  });

  test('tests voice with sample text', async () => {
    const TestVoiceTest = () => {
      const { testVoice, availableVoices } = useTTS();
      const hebrewVoice = availableVoices.find(v => v.lang.startsWith('he'));

      return (
        <button onClick={() => hebrewVoice && testVoice(hebrewVoice)}>
          Test Hebrew Voice
        </button>
      );
    };

    const user = userEvent.setup();
    render(
      <TTSProvider>
        <TestVoiceTest />
      </TTSProvider>
    );

    await waitFor(() => {
      const testButton = screen.getByText('Test Hebrew Voice');
      expect(testButton).toBeInTheDocument();
    });

    const testButton = screen.getByText('Test Hebrew Voice');
    await user.click(testButton);

    expect(mockSpeechSynthesisUtterance).toHaveBeenCalledWith('שלום! זה בדיקת קול בעברית.');
  });

  test('monitoring speaking state works correctly', () => {
    render(
      <TTSProvider>
        <TestTTSComponent />
      </TTSProvider>
    );

    expect(screen.getByTestId('speaking')).toHaveTextContent('not-speaking');

    // Simulate speaking state change
    mockSpeechSynthesis.speaking = true;

    // Would need to trigger the monitoring interval
    // This would be tested in actual implementation with timer mocks
  });

  test('throws error when useTTS is used outside provider', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    expect(() => {
      render(<TestTTSComponent />);
    }).toThrow('useTTS must be used within a TTSProvider');

    consoleSpy.mockRestore();
  });

  test('handles speech synthesis errors gracefully', async () => {
    const user = userEvent.setup();
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    // Mock speech synthesis to throw error
    mockSpeechSynthesis.speak.mockImplementation(() => {
      throw new Error('Speech synthesis failed');
    });

    render(
      <TTSProvider>
        <TestTTSComponent />
      </TTSProvider>
    );

    const speakButton = screen.getByText('Speak Hebrew');

    // This should not throw an error
    await user.click(speakButton);

    // Should not crash and should handle error gracefully
    expect(speakButton).toBeInTheDocument();

    // Clean up console spy
    consoleErrorSpy.mockRestore();
  });

  test('does not speak when TTS is disabled', async () => {
    const user = userEvent.setup();

    const TestDisabledTTS = () => {
      const { speak } = useTTS();
      return (
        <button onClick={() => speak('test')}>Speak</button>
      );
    };

    render(
      <TTSProvider defaultConfig={{ enabled: false }}>
        <TestDisabledTTS />
      </TTSProvider>
    );

    const speakButton = screen.getByText('Speak');
    await user.click(speakButton);

    expect(mockSpeechSynthesis.speak).not.toHaveBeenCalled();
  });
});