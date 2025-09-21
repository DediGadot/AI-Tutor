/**
 * Basic test to validate Jest setup and Hebrew AI Tutor functionality
 */

describe('Hebrew AI Tutor - Basic Tests', () => {
  test('Jest setup is working', () => {
    expect(1 + 1).toBe(2);
  });

  test('Hebrew text processing', () => {
    const hebrewText = 'ברוך הבא למערכת';
    expect(hebrewText).toBe('ברוך הבא למערכת');
    expect(hebrewText.length).toBeGreaterThan(0);
  });

  test('RTL detection utility', () => {
    // Test Hebrew text detection
    const hebrewText = 'שלום עולם';
    const englishText = 'Hello World';

    // Simple RTL detection function
    const isRTL = (text) => {
      const rtlChars = /[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
      return rtlChars.test(text);
    };

    expect(isRTL(hebrewText)).toBe(true);
    expect(isRTL(englishText)).toBe(false);
  });

  test('Web Speech API mock is working', () => {
    expect(global.speechSynthesis).toBeDefined();
    expect(global.speechSynthesis.speak).toBeDefined();
    expect(global.SpeechSynthesisUtterance).toBeDefined();

    // Test creating an utterance
    const utterance = new global.SpeechSynthesisUtterance('ברוך הבא');
    expect(utterance.text).toBe('ברוך הבא');
    expect(utterance.lang).toBe('he-IL');
  });

  test('Canvas mock is working', () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    expect(ctx).toBeDefined();
    expect(ctx.fillRect).toBeDefined();
    expect(ctx.fillText).toBeDefined();

    // Test drawing operations don't throw
    expect(() => {
      ctx.fillRect(0, 0, 100, 100);
      ctx.fillText('Test', 10, 10);
    }).not.toThrow();
  });

  test('localStorage mock is working', () => {
    expect(global.localStorage).toBeDefined();
    expect(global.localStorage.setItem).toBeDefined();
    expect(global.localStorage.getItem).toBeDefined();

    // Test localStorage operations
    global.localStorage.setItem('test', 'value');
    expect(global.localStorage.setItem).toHaveBeenCalledWith('test', 'value');
  });
});