'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useTranslations } from 'next-intl';

interface TTSConfig {
  enabled: boolean;
  rate: number;
  pitch: number;
  volume: number;
  voice?: SpeechSynthesisVoice;
  language: string;
}

interface TTSContextType {
  config: TTSConfig;
  isSupported: boolean;
  isSpeaking: boolean;
  availableVoices: SpeechSynthesisVoice[];
  hebrewVoices: SpeechSynthesisVoice[];
  speak: (text: string, options?: Partial<TTSConfig>) => Promise<void>;
  stop: () => void;
  pause: () => void;
  resume: () => void;
  updateConfig: (newConfig: Partial<TTSConfig>) => void;
  testVoice: (voice: SpeechSynthesisVoice) => void;
}

const TTSContext = createContext<TTSContextType | null>(null);

export const useTTS = () => {
  const context = useContext(TTSContext);
  if (!context) {
    throw new Error('useTTS must be used within a TTSProvider');
  }
  return context;
};

interface TTSProviderProps {
  children: React.ReactNode;
  defaultConfig?: Partial<TTSConfig>;
}

export default function TTSProvider({ children, defaultConfig = {} }: TTSProviderProps) {
  const t = useTranslations();
  const [isSupported, setIsSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [hebrewVoices, setHebrewVoices] = useState<SpeechSynthesisVoice[]>([]);

  const [config, setConfig] = useState<TTSConfig>({
    enabled: true,
    rate: 0.8,
    pitch: 1.0,
    volume: 0.7,
    language: 'he-IL',
    ...defaultConfig,
  });

  // Check if TTS is supported
  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      setIsSupported(true);

      // Load voices
      const loadVoices = () => {
        const voices = speechSynthesis.getVoices();
        setAvailableVoices(voices);

        // Filter Hebrew voices
        const hebrew = voices.filter(voice =>
          voice.lang.startsWith('he') ||
          voice.lang.includes('hebrew') ||
          voice.name.toLowerCase().includes('hebrew') ||
          voice.name.toLowerCase().includes('iw')
        );
        setHebrewVoices(hebrew);

        // Set default Hebrew voice if none selected
        if (!config.voice && hebrew.length > 0) {
          setConfig(prev => ({ ...prev, voice: hebrew[0] }));
        }
      };

      // Load voices immediately
      loadVoices();

      // Some browsers load voices asynchronously
      speechSynthesis.addEventListener('voiceschanged', loadVoices);

      return () => {
        speechSynthesis.removeEventListener('voiceschanged', loadVoices);
      };
    }
  }, [config.voice]);

  // Monitor speaking state
  useEffect(() => {
    if (!isSupported) return;

    const checkSpeaking = () => {
      setIsSpeaking(speechSynthesis.speaking);
    };

    const interval = setInterval(checkSpeaking, 100);
    return () => clearInterval(interval);
  }, [isSupported]);

  const speak = useCallback(async (text: string, options: Partial<TTSConfig> = {}) => {
    if (!isSupported || !config.enabled) {
      console.warn('TTS not supported or disabled');
      return;
    }

    // Stop any current speech
    speechSynthesis.cancel();

    // Clean and prepare text for Hebrew TTS
    const cleanText = text
      .replace(/[^\u0590-\u05FF\u0020-\u007F]/g, '') // Keep Hebrew and basic Latin chars
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    if (!cleanText) {
      console.warn('No valid text to speak');
      return;
    }

    return new Promise<void>((resolve, reject) => {
      try {
        const utterance = new SpeechSynthesisUtterance(cleanText);

        // Apply configuration
        const finalConfig = { ...config, ...options };
        utterance.rate = finalConfig.rate;
        utterance.pitch = finalConfig.pitch;
        utterance.volume = finalConfig.volume;
        utterance.lang = finalConfig.language;

        // Use selected voice or best Hebrew voice
        if (finalConfig.voice) {
          utterance.voice = finalConfig.voice;
        } else if (hebrewVoices.length > 0) {
          utterance.voice = hebrewVoices[0];
        }

        // Event handlers
        utterance.onstart = () => {
          setIsSpeaking(true);
        };

        utterance.onend = () => {
          setIsSpeaking(false);
          resolve();
        };

        utterance.onerror = (event) => {
          setIsSpeaking(false);
          console.error('TTS Error:', event.error);
          reject(new Error(`TTS Error: ${event.error}`));
        };

        // Start speaking
        speechSynthesis.speak(utterance);

      } catch (error) {
        console.error('TTS Error:', error);
        setIsSpeaking(false);
        reject(error);
      }
    });
  }, [isSupported, config, hebrewVoices]);

  const stop = useCallback(() => {
    if (isSupported) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, [isSupported]);

  const pause = useCallback(() => {
    if (isSupported && speechSynthesis.speaking) {
      speechSynthesis.pause();
    }
  }, [isSupported]);

  const resume = useCallback(() => {
    if (isSupported && speechSynthesis.paused) {
      speechSynthesis.resume();
    }
  }, [isSupported]);

  const updateConfig = useCallback((newConfig: Partial<TTSConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }));
  }, []);

  const testVoice = useCallback((voice: SpeechSynthesisVoice) => {
    const testText = voice.lang.startsWith('he')
      ? 'שלום! זה בדיקת קול בעברית.'
      : 'Hello! This is a voice test.';

    speak(testText, { voice });
  }, [speak]);

  const contextValue: TTSContextType = {
    config,
    isSupported,
    isSpeaking,
    availableVoices,
    hebrewVoices,
    speak,
    stop,
    pause,
    resume,
    updateConfig,
    testVoice,
  };

  return (
    <TTSContext.Provider value={contextValue}>
      {children}
    </TTSContext.Provider>
  );
}