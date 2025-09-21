'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';

interface AccessibilitySettings {
  highContrast: boolean;
  reducedMotion: boolean;
  fontSize: 'small' | 'medium' | 'large' | 'xlarge';
  focusIndicator: boolean;
  screenReaderOptimized: boolean;
}

interface AccessibilityContextType {
  settings: AccessibilitySettings;
  updateSetting: <K extends keyof AccessibilitySettings>(
    key: K,
    value: AccessibilitySettings[K]
  ) => void;
  resetSettings: () => void;
  announceToScreenReader: (message: string) => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | null>(null);

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within AccessibilityProvider');
  }
  return context;
};

interface AccessibilityProviderProps {
  children: React.ReactNode;
}

const defaultSettings: AccessibilitySettings = {
  highContrast: false,
  reducedMotion: false,
  fontSize: 'medium',
  focusIndicator: true,
  screenReaderOptimized: false,
};

export default function AccessibilityProvider({ children }: AccessibilityProviderProps) {
  const [settings, setSettings] = useState<AccessibilitySettings>(defaultSettings);
  const [announcements, setAnnouncements] = useState<string[]>([]);

  // Load settings from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('accessibility-settings');
      if (saved) {
        try {
          const parsedSettings = JSON.parse(saved);
          setSettings({ ...defaultSettings, ...parsedSettings });
        } catch (error) {
          console.error('Failed to parse accessibility settings:', error);
        }
      }

      // Detect user preferences
      const mediaQueries = {
        reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)'),
        highContrast: window.matchMedia('(prefers-contrast: high)'),
      };

      // Set initial values based on system preferences
      setSettings(prev => ({
        ...prev,
        reducedMotion: prev.reducedMotion || mediaQueries.reducedMotion.matches,
        highContrast: prev.highContrast || mediaQueries.highContrast.matches,
      }));

      // Listen for changes in user preferences
      const handleReducedMotionChange = (e: MediaQueryListEvent) => {
        setSettings(prev => ({ ...prev, reducedMotion: e.matches }));
      };

      const handleHighContrastChange = (e: MediaQueryListEvent) => {
        setSettings(prev => ({ ...prev, highContrast: e.matches }));
      };

      mediaQueries.reducedMotion.addEventListener('change', handleReducedMotionChange);
      mediaQueries.highContrast.addEventListener('change', handleHighContrastChange);

      return () => {
        mediaQueries.reducedMotion.removeEventListener('change', handleReducedMotionChange);
        mediaQueries.highContrast.removeEventListener('change', handleHighContrastChange);
      };
    }
  }, []);

  // Apply settings to document
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const root = document.documentElement;

      // High contrast
      if (settings.highContrast) {
        root.classList.add('high-contrast');
      } else {
        root.classList.remove('high-contrast');
      }

      // Reduced motion
      if (settings.reducedMotion) {
        root.classList.add('reduce-motion');
      } else {
        root.classList.remove('reduce-motion');
      }

      // Font size
      root.classList.remove('font-small', 'font-medium', 'font-large', 'font-xlarge');
      root.classList.add(`font-${settings.fontSize}`);

      // Enhanced focus indicators
      if (settings.focusIndicator) {
        root.classList.add('enhanced-focus');
      } else {
        root.classList.remove('enhanced-focus');
      }

      // Screen reader optimizations
      if (settings.screenReaderOptimized) {
        root.classList.add('screen-reader-optimized');
      } else {
        root.classList.remove('screen-reader-optimized');
      }

      // Save to localStorage
      localStorage.setItem('accessibility-settings', JSON.stringify(settings));
    }
  }, [settings]);

  const updateSetting = <K extends keyof AccessibilitySettings>(
    key: K,
    value: AccessibilitySettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('accessibility-settings');
    }
  };

  const announceToScreenReader = (message: string) => {
    setAnnouncements(prev => [...prev, message]);
    // Remove announcement after a delay to clean up
    setTimeout(() => {
      setAnnouncements(prev => prev.slice(1));
    }, 1000);
  };

  return (
    <AccessibilityContext.Provider
      value={{
        settings,
        updateSetting,
        resetSettings,
        announceToScreenReader,
      }}
    >
      {children}

      {/* Screen Reader Announcement Region */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        id="accessibility-announcements"
      >
        {announcements.map((announcement, index) => (
          <div key={index}>{announcement}</div>
        ))}
      </div>

      {/* Skip Links */}
      <div className="skip-links">
        <a href="#main-content" className="skip-link">
          דלג לתוכן הראשי
        </a>
        <a href="#navigation" className="skip-link">
          דלג לניווט
        </a>
        <a href="#sidebar" className="skip-link">
          דלג לסרגל צד
        </a>
      </div>
    </AccessibilityContext.Provider>
  );
}

// Helper hook for keyboard navigation
export const useKeyboardNavigation = () => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Escape key to close modals/dropdowns
      if (event.key === 'Escape') {
        const activeElement = document.activeElement as HTMLElement;
        if (activeElement && activeElement.blur) {
          activeElement.blur();
        }
      }

      // Arrow key navigation for lists and grids
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
        const activeElement = document.activeElement as HTMLElement;
        if (activeElement && activeElement.getAttribute('role') === 'option') {
          event.preventDefault();
          // Handle arrow navigation for custom components
        }
      }

      // Home/End navigation
      if (event.key === 'Home' || event.key === 'End') {
        const activeElement = document.activeElement as HTMLElement;
        if (activeElement && activeElement.closest('[role="listbox"]')) {
          event.preventDefault();
          // Navigate to first/last item
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
};