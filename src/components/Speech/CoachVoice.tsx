'use client';

import React, { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useTTS } from './TTSProvider';
import TTSControls from './TTSControls';
import { MessageCircle, Volume2, Lightbulb, Award } from 'lucide-react';

interface CoachMessage {
  id: string;
  type: 'welcome' | 'encouragement' | 'hint' | 'success' | 'error' | 'milestone';
  text: string;
  timestamp: Date;
  autoSpeak?: boolean;
}

interface CoachVoiceProps {
  messages: CoachMessage[];
  onMessageRead?: (messageId: string) => void;
  enabled?: boolean;
  compact?: boolean;
}

export default function CoachVoice({
  messages,
  onMessageRead,
  enabled = true,
  compact = false,
}: CoachVoiceProps) {
  const t = useTranslations();
  const { speak, config, isSpeaking } = useTTS();
  const [lastSpokenMessageId, setLastSpokenMessageId] = useState<string>('');

  // Auto-speak new messages
  useEffect(() => {
    if (!enabled || !config.enabled) return;

    const latestMessage = messages[messages.length - 1];
    if (
      latestMessage &&
      latestMessage.autoSpeak &&
      latestMessage.id !== lastSpokenMessageId &&
      !isSpeaking
    ) {
      speak(latestMessage.text).then(() => {
        setLastSpokenMessageId(latestMessage.id);
        onMessageRead?.(latestMessage.id);
      }).catch(console.error);
    }
  }, [messages, enabled, config.enabled, lastSpokenMessageId, isSpeaking, speak, onMessageRead]);

  const getMessageIcon = (type: CoachMessage['type']) => {
    switch (type) {
      case 'welcome': return <MessageCircle className="w-4 h-4 text-blue-500" />;
      case 'encouragement': return <MessageCircle className="w-4 h-4 text-green-500" />;
      case 'hint': return <Lightbulb className="w-4 h-4 text-yellow-500" />;
      case 'success': return <Award className="w-4 h-4 text-green-500" />;
      case 'error': return <MessageCircle className="w-4 h-4 text-red-500" />;
      case 'milestone': return <Award className="w-4 h-4 text-purple-500" />;
      default: return <MessageCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getMessageBgColor = (type: CoachMessage['type']) => {
    switch (type) {
      case 'welcome': return 'bg-blue-50 border-blue-200';
      case 'encouragement': return 'bg-green-50 border-green-200';
      case 'hint': return 'bg-yellow-50 border-yellow-200';
      case 'success': return 'bg-green-50 border-green-200';
      case 'error': return 'bg-red-50 border-red-200';
      case 'milestone': return 'bg-purple-50 border-purple-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const handleSpeakMessage = (message: CoachMessage) => {
    speak(message.text).then(() => {
      onMessageRead?.(message.id);
    }).catch(console.error);
  };

  if (!enabled) {
    return null;
  }

  if (compact) {
    const latestMessage = messages[messages.length - 1];
    if (!latestMessage) return null;

    return (
      <div className={`flex items-center gap-3 p-3 rounded-lg border ${getMessageBgColor(latestMessage.type)}`}>
        {getMessageIcon(latestMessage.type)}
        <p className="flex-1 text-sm hebrew-text">{latestMessage.text}</p>
        <TTSControls
          text={latestMessage.text}
          showFullControls={false}
          className="flex-shrink-0"
        />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-display font-semibold text-gray-900">
            המדריך שלך
          </h3>
        </div>
        <TTSControls showFullControls={true} />
      </div>

      {/* Messages */}
      <div className="space-y-3 max-h-64 overflow-y-auto scrollbar-rtl">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-sm text-gray-500">המדריך יופיע כאן עם הודעות עזרה</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`p-3 rounded-lg border ${getMessageBgColor(message.type)} transition-all hover:shadow-sm`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getMessageIcon(message.type)}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900 hebrew-text leading-relaxed">
                    {message.text}
                  </p>

                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-gray-500">
                      {message.timestamp.toLocaleTimeString('he-IL', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>

                    <button
                      onClick={() => handleSpeakMessage(message)}
                      className="text-xs text-primary-600 hover:text-primary-700 flex items-center gap-1 transition-colors"
                      title="הקרא הודעה"
                    >
                      <Volume2 className="w-3 h-3" />
                      הקרא
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Quick Actions */}
      {messages.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-100">
          <div className="flex gap-2">
            <button
              onClick={() => {
                const latestMessage = messages[messages.length - 1];
                if (latestMessage) {
                  handleSpeakMessage(latestMessage);
                }
              }}
              disabled={messages.length === 0}
              className="btn-secondary text-xs px-3 py-1.5 flex-1"
            >
              הקרא הודעה אחרונה
            </button>

            <button
              onClick={() => {
                const encouragements = [
                  'אתה עושה עבודה מעולה!',
                  'המשך ככה, אתה לומד מהר!',
                  'אני גאה בך!',
                  'זה נראה נהדר!',
                  'אתה הופך למתכנת אמיתי!'
                ];
                const randomEncouragement = encouragements[Math.floor(Math.random() * encouragements.length)];
                speak(randomEncouragement);
              }}
              className="btn-primary text-xs px-3 py-1.5 flex-1"
            >
              עידוד
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper hook for creating coach messages
export const useCoachMessages = () => {
  const [messages, setMessages] = useState<CoachMessage[]>([]);

  const addMessage = (
    type: CoachMessage['type'],
    text: string,
    autoSpeak: boolean = true
  ) => {
    const message: CoachMessage = {
      id: `${Date.now()}-${Math.random()}`,
      type,
      text,
      timestamp: new Date(),
      autoSpeak,
    };

    setMessages(prev => [...prev, message]);
    return message.id;
  };

  const clearMessages = () => {
    setMessages([]);
  };

  const removeMessage = (messageId: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  };

  return {
    messages,
    addMessage,
    clearMessages,
    removeMessage,
  };
};