'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useTTS } from './TTSProvider';
import { Volume2, VolumeX, Play, Pause, Square, Settings, TestTube } from 'lucide-react';

interface TTSControlsProps {
  text?: string;
  showFullControls?: boolean;
  className?: string;
}

export default function TTSControls({
  text,
  showFullControls = false,
  className = '',
}: TTSControlsProps) {
  const t = useTranslations();
  const {
    config,
    isSupported,
    isSpeaking,
    hebrewVoices,
    speak,
    stop,
    pause,
    resume,
    updateConfig,
    testVoice,
  } = useTTS();

  const [showSettings, setShowSettings] = useState(false);

  if (!isSupported) {
    return (
      <div className={`text-sm text-gray-500 ${className}`}>
        הדפדפן לא תומך בהקראת טקסט
      </div>
    );
  }

  const handleSpeak = () => {
    if (text) {
      speak(text);
    }
  };

  const handleTogglePlaying = () => {
    if (isSpeaking) {
      stop();
    } else {
      handleSpeak();
    }
  };

  const handleVolumeToggle = () => {
    updateConfig({ enabled: !config.enabled });
  };

  const handleRateChange = (rate: number) => {
    updateConfig({ rate });
  };

  const handlePitchChange = (pitch: number) => {
    updateConfig({ pitch });
  };

  const handleVolumeChange = (volume: number) => {
    updateConfig({ volume });
  };

  const handleVoiceChange = (voiceIndex: number) => {
    const voice = hebrewVoices[voiceIndex];
    if (voice) {
      updateConfig({ voice });
    }
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Main Toggle */}
      <button
        onClick={handleVolumeToggle}
        className={`btn-secondary p-2 min-h-touch min-w-touch ${
          config.enabled ? 'text-primary-600' : 'text-gray-400'
        }`}
        title={config.enabled ? t('settings.voiceEnabled') : t('settings.voiceDisabled')}
        aria-label={config.enabled ? t('settings.voiceEnabled') : t('settings.voiceDisabled')}
      >
        {config.enabled ? (
          <Volume2 className="w-4 h-4" />
        ) : (
          <VolumeX className="w-4 h-4" />
        )}
      </button>

      {/* Play/Pause Controls */}
      {config.enabled && text && (
        <>
          <button
            onClick={handleTogglePlaying}
            disabled={!text}
            className="btn-primary p-2 min-h-touch min-w-touch"
            title={isSpeaking ? 'עצור הקראה' : 'התחל הקראה'}
            aria-label={isSpeaking ? 'עצור הקראה' : 'התחל הקראה'}
          >
            {isSpeaking ? (
              <Square className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </button>
        </>
      )}

      {/* Settings */}
      {showFullControls && config.enabled && (
        <div className="relative">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="btn-secondary p-2 min-h-touch min-w-touch"
            title="הגדרות קול"
            aria-label="הגדרות קול"
          >
            <Settings className="w-4 h-4" />
          </button>

          {showSettings && (
            <div className="absolute top-full left-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-4 w-72 z-50">
              <h4 className="font-medium text-gray-900 mb-3">הגדרות קול</h4>

              {/* Voice Selection */}
              {hebrewVoices.length > 0 && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    קול
                  </label>
                  <select
                    value={config.voice ? hebrewVoices.indexOf(config.voice) : 0}
                    onChange={(e) => handleVoiceChange(parseInt(e.target.value))}
                    className="w-full p-2 border border-gray-300 rounded text-sm"
                  >
                    {hebrewVoices.map((voice, index) => (
                      <option key={voice.name} value={index}>
                        {voice.name} ({voice.lang})
                      </option>
                    ))}
                  </select>
                  {config.voice && (
                    <button
                      onClick={() => testVoice(config.voice!)}
                      className="mt-2 btn-secondary text-xs px-3 py-1"
                    >
                      <TestTube className="w-3 h-3 me-1" />
                      בדוק קול
                    </button>
                  )}
                </div>
              )}

              {/* Rate Control */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  מהירות: {config.rate.toFixed(1)}x
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  value={config.rate}
                  onChange={(e) => handleRateChange(parseFloat(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>איטי</span>
                  <span>מהיר</span>
                </div>
              </div>

              {/* Pitch Control */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  גובה צליל: {config.pitch.toFixed(1)}
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  value={config.pitch}
                  onChange={(e) => handlePitchChange(parseFloat(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>נמוך</span>
                  <span>גבוה</span>
                </div>
              </div>

              {/* Volume Control */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  עוצמת קול: {Math.round(config.volume * 100)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={config.volume}
                  onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>שקט</span>
                  <span>חזק</span>
                </div>
              </div>

              {/* Reset Button */}
              <button
                onClick={() => {
                  updateConfig({
                    rate: 0.8,
                    pitch: 1.0,
                    volume: 0.7,
                  });
                }}
                className="btn-secondary w-full text-sm"
              >
                איפוס להגדרות ברירת מחדל
              </button>
            </div>
          )}
        </div>
      )}

      {/* Speaking Indicator */}
      {isSpeaking && (
        <div className="flex items-center gap-1 text-xs text-primary-600">
          <div className="flex gap-1">
            <div className="w-1 h-3 bg-primary-600 rounded animate-pulse" />
            <div className="w-1 h-3 bg-primary-600 rounded animate-pulse" style={{ animationDelay: '0.2s' }} />
            <div className="w-1 h-3 bg-primary-600 rounded animate-pulse" style={{ animationDelay: '0.4s' }} />
          </div>
          <span>מקריא...</span>
        </div>
      )}
    </div>
  );
}