// Jest setup for Hebrew AI Tutor testing
import '@testing-library/jest-dom';
import 'jest-localstorage-mock';
import 'fake-indexeddb/auto';
import 'jest-canvas-mock';

// Fix userEvent clipboard redefinition issue
Object.defineProperty(global.navigator, 'clipboard', {
  value: {
    writeText: jest.fn(),
    readText: jest.fn(),
  },
  writable: true,
  configurable: true,
});

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      locale: 'he',
      locales: ['he', 'en'],
      defaultLocale: 'he',
      push: jest.fn(),
      replace: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn(),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
    };
  },
}));

// Mock next-intl
jest.mock('next-intl', () => ({
  useTranslations: () => (key) => key,
  useLocale: () => 'he',
  useMessages: () => ({}),
  useFormatter: () => ({
    dateTime: (date) => date.toLocaleDateString('he-IL'),
    number: (num) => num.toLocaleString('he-IL'),
    relativeTime: (date) => date.toString(),
  }),
}));

// Mock Framer Motion for performance
jest.mock('framer-motion', () => ({
  motion: {
    div: 'div',
    button: 'button',
    span: 'span',
    p: 'p',
    h1: 'h1',
    h2: 'h2',
    h3: 'h3',
    ul: 'ul',
    li: 'li',
    nav: 'nav',
    header: 'header',
    footer: 'footer',
    section: 'section',
    article: 'article',
    aside: 'aside',
    main: 'main',
  },
  AnimatePresence: ({ children }) => children,
  useAnimation: () => ({
    start: jest.fn(),
    stop: jest.fn(),
    set: jest.fn(),
  }),
  useMotionValue: () => ({ get: jest.fn(), set: jest.fn() }),
  useTransform: () => ({ get: jest.fn(), set: jest.fn() }),
  useSpring: () => ({ get: jest.fn(), set: jest.fn() }),
}));

// Mock Web Speech API for TTS testing
Object.defineProperty(window, 'speechSynthesis', {
  writable: true,
  value: {
    speak: jest.fn(),
    cancel: jest.fn(),
    pause: jest.fn(),
    resume: jest.fn(),
    getVoices: jest.fn(() => [
      {
        name: 'Hebrew Voice',
        lang: 'he-IL',
        voiceURI: 'he-IL',
        localService: true,
        default: false,
      },
    ]),
    speaking: false,
    pending: false,
    paused: false,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  },
});

// Mock SpeechSynthesisUtterance
Object.defineProperty(window, 'SpeechSynthesisUtterance', {
  writable: true,
  value: jest.fn().mockImplementation((text) => ({
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
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver for scroll-based components
global.IntersectionObserver = jest.fn().mockImplementation((callback) => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
  root: null,
  rootMargin: '',
  thresholds: [],
}));

// Mock ResizeObserver for responsive components
global.ResizeObserver = jest.fn().mockImplementation((callback) => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock matchMedia for responsive design testing
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock clipboard API
Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: jest.fn(() => Promise.resolve()),
    readText: jest.fn(() => Promise.resolve('')),
  },
});

// Mock getUserMedia for potential voice input features
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: jest.fn(() =>
      Promise.resolve({
        getTracks: () => [
          {
            stop: jest.fn(),
            addEventListener: jest.fn(),
            removeEventListener: jest.fn(),
          },
        ],
      })
    ),
    enumerateDevices: jest.fn(() => Promise.resolve([])),
  },
});

// Mock HTMLCanvasElement methods for p5.js testing
HTMLCanvasElement.prototype.getContext = jest.fn((contextType) => {
  if (contextType === '2d') {
    return {
      fillRect: jest.fn(),
      clearRect: jest.fn(),
      getImageData: jest.fn(() => ({
        data: new Uint8ClampedArray(4),
      })),
      putImageData: jest.fn(),
      createImageData: jest.fn(() => []),
      setTransform: jest.fn(),
      drawImage: jest.fn(),
      save: jest.fn(),
      fillText: jest.fn(),
      restore: jest.fn(),
      beginPath: jest.fn(),
      moveTo: jest.fn(),
      lineTo: jest.fn(),
      closePath: jest.fn(),
      stroke: jest.fn(),
      translate: jest.fn(),
      scale: jest.fn(),
      rotate: jest.fn(),
      arc: jest.fn(),
      fill: jest.fn(),
      measureText: jest.fn(() => ({ width: 0 })),
      transform: jest.fn(),
      rect: jest.fn(),
      clip: jest.fn(),
    };
  }
  return null;
});

// Mock p5.js for creative coding tests
jest.mock('p5', () => {
  return jest.fn().mockImplementation(() => ({
    createCanvas: jest.fn(),
    background: jest.fn(),
    fill: jest.fn(),
    noFill: jest.fn(),
    stroke: jest.fn(),
    noStroke: jest.fn(),
    ellipse: jest.fn(),
    rect: jest.fn(),
    line: jest.fn(),
    point: jest.fn(),
    triangle: jest.fn(),
    quad: jest.fn(),
    text: jest.fn(),
    textSize: jest.fn(),
    textAlign: jest.fn(),
    textFont: jest.fn(),
    push: jest.fn(),
    pop: jest.fn(),
    translate: jest.fn(),
    rotate: jest.fn(),
    scale: jest.fn(),
    frameRate: jest.fn(),
    noLoop: jest.fn(),
    loop: jest.fn(),
    redraw: jest.fn(),
    mousePressed: jest.fn(),
    mouseReleased: jest.fn(),
    keyPressed: jest.fn(),
    keyReleased: jest.fn(),
    setup: jest.fn(),
    draw: jest.fn(),
    preload: jest.fn(),
    windowResized: jest.fn(),
    remove: jest.fn(),
    width: 800,
    height: 600,
    mouseX: 0,
    mouseY: 0,
    pmouseX: 0,
    pmouseY: 0,
    key: '',
    keyCode: 0,
    frameCount: 0,
  }));
});

// Mock Monaco Editor
jest.mock('@monaco-editor/react', () => ({
  Editor: jest.fn(({ value, onChange, onMount }) => {
    // Simple textarea mock for Monaco Editor
    const handleChange = (e) => {
      if (onChange) onChange(e.target.value);
    };

    return React.createElement('textarea', {
      'data-testid': 'monaco-editor',
      value: value || '',
      onChange: handleChange,
      style: { width: '100%', height: '400px', fontFamily: 'monospace' },
      placeholder: 'Monaco Editor Mock',
      dir: 'ltr', // Code is always LTR even in Hebrew interface
    });
  }),
  loader: {
    init: jest.fn(() => Promise.resolve()),
    config: jest.fn(),
  },
}));

// Mock Matter.js physics engine
jest.mock('matter-js', () => ({
  Engine: {
    create: jest.fn(() => ({
      world: { bodies: [] },
      timing: { timeScale: 1 },
    })),
    update: jest.fn(),
    run: jest.fn(),
  },
  World: {
    add: jest.fn(),
    remove: jest.fn(),
    clear: jest.fn(),
  },
  Bodies: {
    rectangle: jest.fn(() => ({ id: 'body-1', position: { x: 0, y: 0 } })),
    circle: jest.fn(() => ({ id: 'body-2', position: { x: 0, y: 0 } })),
  },
  Body: {
    setPosition: jest.fn(),
    setVelocity: jest.fn(),
    applyForce: jest.fn(),
  },
  Render: {
    create: jest.fn(() => ({ canvas: { width: 800, height: 600 } })),
    run: jest.fn(),
  },
  Runner: {
    create: jest.fn(),
    run: jest.fn(),
  },
  Events: {
    on: jest.fn(),
    off: jest.fn(),
  },
}));

// Global test utilities for Hebrew/RTL testing
global.testUtils = {
  // Check if text contains Hebrew characters
  containsHebrew: (text) => /[\u0590-\u05FF]/.test(text),

  // Check if element has RTL direction
  isRTL: (element) => {
    const computedStyle = window.getComputedStyle(element);
    return computedStyle.direction === 'rtl';
  },

  // Create mock Hebrew text
  createHebrewText: (length = 10) => {
    const hebrewChars = 'אבגדהוזחטיכלמנסעפצקרשת';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += hebrewChars.charAt(Math.floor(Math.random() * hebrewChars.length));
    }
    return result;
  },

  // Mock student data
  createMockStudent: () => ({
    id: 'test-student-123',
    nickname: 'דני',
    level: 2,
    xp: 150,
    streak: 5,
    badges: ['משתנים-מתחיל', 'לולאות-מתקדם'],
    theme: 'football',
    preferences: {
      voice_enabled: true,
      session_length: 20,
    },
  }),

  // Mock lesson data
  createMockLesson: () => ({
    id: 'test-lesson-1',
    title: 'כדורגל דיגיטלי',
    theme: 'football',
    duration_min: 20,
    milestones: [
      {
        id: 'milestone-1',
        goal_he: 'צור כדור שנע על המסך',
        concept: 'variables',
        xp: 20,
      },
    ],
  }),

  // Wait for Hebrew text to render
  waitForHebrewText: async (element) => {
    return new Promise((resolve) => {
      const observer = new MutationObserver(() => {
        const text = element.textContent || '';
        if (global.testUtils.containsHebrew(text)) {
          observer.disconnect();
          resolve(text);
        }
      });

      observer.observe(element, {
        childList: true,
        subtree: true,
        characterData: true,
      });

      // Fallback timeout
      setTimeout(() => {
        observer.disconnect();
        resolve(element.textContent || '');
      }, 1000);
    });
  },
};

// Console error suppression for expected warnings in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render is deprecated') ||
        args[0].includes('Warning: componentWillReceiveProps') ||
        args[0].includes('Warning: componentWillMount'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Global test setup
beforeEach(() => {
  // Clear all mocks between tests
  jest.clearAllMocks();

  // Reset localStorage
  localStorage.clear();

  // Reset sessionStorage
  sessionStorage.clear();

  // Reset document direction for RTL tests
  document.dir = 'rtl';
  document.documentElement.dir = 'rtl';
  document.documentElement.lang = 'he';

  // Reset viewport meta for responsive tests
  let viewport = document.querySelector('meta[name="viewport"]');
  if (!viewport) {
    viewport = document.createElement('meta');
    viewport.name = 'viewport';
    document.head.appendChild(viewport);
  }
  viewport.content = 'width=device-width, initial-scale=1';
});

// Global test teardown
afterEach(() => {
  // Clean up any remaining timers only if fake timers are enabled
  try {
    if (jest.isMockFunction(setTimeout)) {
      jest.runOnlyPendingTimers();
    }
  } catch (e) {
    // Ignore timer cleanup errors
  }

  // Always ensure real timers are restored
  try {
    jest.useRealTimers();
  } catch (e) {
    // Ignore if real timers are already in use
  }

  // Clean up any DOM mutations
  document.body.innerHTML = '';

  // Clean up clipboard to prevent userEvent conflicts
  try {
    if (global.navigator && global.navigator.clipboard) {
      Object.defineProperty(global.navigator, 'clipboard', {
        value: undefined,
        configurable: true,
        writable: true,
      });
    }
  } catch (e) {
    // Ignore clipboard cleanup errors
  }

  // Reset fetch mocks if using MSW
  if (global.msw) {
    global.msw.restoreHandlers();
  }
});

// Add custom matchers for Hebrew/RTL testing
expect.extend({
  toContainHebrew(received) {
    const pass = /[\u0590-\u05FF]/.test(received);
    if (pass) {
      return {
        message: () => `expected "${received}" not to contain Hebrew characters`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected "${received}" to contain Hebrew characters`,
        pass: false,
      };
    }
  },

  toHaveRTLDirection(received) {
    const computedStyle = window.getComputedStyle(received);
    const pass = computedStyle.direction === 'rtl';
    if (pass) {
      return {
        message: () => `expected element not to have RTL direction`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected element to have RTL direction, but got "${computedStyle.direction}"`,
        pass: false,
      };
    }
  },

  toBeAccessible(received) {
    // Basic accessibility checks
    const hasAriaLabel = received.hasAttribute('aria-label') || received.hasAttribute('aria-labelledby');
    const hasValidRole = !received.hasAttribute('role') || received.getAttribute('role') !== '';
    const hasValidTabIndex = !received.hasAttribute('tabindex') || parseInt(received.getAttribute('tabindex')) >= -1;

    const pass = hasAriaLabel && hasValidRole && hasValidTabIndex;

    if (pass) {
      return {
        message: () => `expected element not to be accessible`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected element to be accessible (check aria-label, role, tabindex)`,
        pass: false,
      };
    }
  },

  toMeetTargetSize(received) {
    const rect = received.getBoundingClientRect();
    const pass = rect.width >= 24 && rect.height >= 24; // WCAG 2.2 AA requirement

    if (pass) {
      return {
        message: () => `expected element not to meet target size requirements`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected element to be at least 24x24px, but got ${rect.width}x${rect.height}px`,
        pass: false,
      };
    }
  },
});