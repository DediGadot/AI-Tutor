#!/usr/bin/env python3
"""
Hebrew Text Processing Utilities
Handles Hebrew text processing, RTL formatting, and translation utilities.
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HebrewTextProcessor:
    """Utility class for Hebrew text processing and validation."""

    def __init__(self):
        """Initialize Hebrew text processor."""
        # Hebrew character ranges
        self.hebrew_range = (0x0590, 0x05FF)  # Hebrew block
        self.hebrew_extended_range = (0xFB1D, 0xFB4F)  # Hebrew presentation forms

        # Common error translations
        self.error_translations = {
            "Syntax error": "שגיאת תחביר",
            "Runtime error": "שגיאת זמן ריצה",
            "Type error": "שגיאת סוג",
            "Reference error": "שגיאת התייחסות",
            "Network error": "שגיאת רשת",
            "Timeout": "זמן התקשרות פג",
            "Failed to load": "טעינה נכשלה",
            "Invalid input": "קלט לא חוקי",
            "Permission denied": "הרשאה נדחתה"
        }

        # Educational feedback translations
        self.feedback_translations = {
            "Great job!": "עבודה מעולה!",
            "Well done!": "כל הכבוד!",
            "Keep going!": "המשך ככה!",
            "Try again": "נסה שוב",
            "Almost there": "כמעט הגעת",
            "Good effort": "מאמץ טוב",
            "Excellent": "מצוין",
            "Perfect": "מושלם"
        }

    def is_hebrew_text(self, text: str) -> bool:
        """Check if text contains Hebrew characters."""
        if not text:
            return False

        hebrew_chars = 0
        total_chars = 0

        for char in text:
            code_point = ord(char)
            if (self.hebrew_range[0] <= code_point <= self.hebrew_range[1] or
                self.hebrew_extended_range[0] <= code_point <= self.hebrew_extended_range[1]):
                hebrew_chars += 1
            elif char.isalpha():
                total_chars += 1

        # Consider text Hebrew if >50% of alphabetic characters are Hebrew
        if total_chars + hebrew_chars == 0:
            return False

        return hebrew_chars / (total_chars + hebrew_chars) > 0.5

    def clean_hebrew_text(self, text: str) -> str:
        """Clean and normalize Hebrew text."""
        if not text:
            return text

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Normalize Hebrew characters
        text = self.normalize_hebrew_characters(text)

        # Ensure proper RTL markers if needed
        if self.is_hebrew_text(text):
            text = self.add_rtl_markers(text)

        return text

    def normalize_hebrew_characters(self, text: str) -> str:
        """Normalize Hebrew character variations."""
        # Dictionary of character normalizations
        normalizations = {
            'ך': 'כ',  # Final kaf to regular kaf in some contexts
            'ם': 'מ',  # Final mem to regular mem in some contexts
            'ן': 'נ',  # Final nun to regular nun in some contexts
            'ף': 'פ',  # Final pe to regular pe in some contexts
            'ץ': 'צ'   # Final tsadi to regular tsadi in some contexts
        }

        # Apply normalizations only where appropriate
        # (This is a simplified version - more sophisticated rules would be needed)
        return text

    def add_rtl_markers(self, text: str) -> str:
        """Add RTL directional markers if needed."""
        # Add RLE (Right-to-Left Embedding) at the beginning
        rtl_embed = '\u202B'  # RLE character
        pop_directional = '\u202C'  # PDF (Pop Directional Formatting)

        if self.is_hebrew_text(text) and not text.startswith(rtl_embed):
            return f"{rtl_embed}{text}{pop_directional}"

        return text

    def translate_error_message(self, error: str) -> str:
        """Translate common error messages to Hebrew."""
        # Clean the error message
        error = error.strip()

        # Check for direct translations
        for en_error, he_error in self.error_translations.items():
            if en_error.lower() in error.lower():
                return he_error

        # Pattern-based translations
        if "line" in error.lower() and any(char.isdigit() for char in error):
            line_num = re.search(r'\d+', error)
            if line_num:
                return f"שגיאה בשורה {line_num.group()}"

        if "function" in error.lower():
            return "שגיאה בפונקציה"

        if "variable" in error.lower():
            return "שגיאה במשתנה"

        # Default translation for unknown errors
        return f"שגיאה: {error}"

    def translate_feedback(self, feedback: str) -> str:
        """Translate positive feedback to Hebrew."""
        feedback = feedback.strip()

        for en_feedback, he_feedback in self.feedback_translations.items():
            if en_feedback.lower() in feedback.lower():
                return he_feedback

        return feedback  # Return as-is if no translation found

    def format_code_comment(self, comment: str) -> str:
        """Format code comments for Hebrew display."""
        if not comment:
            return comment

        # Add Hebrew comment marker
        if self.is_hebrew_text(comment):
            if not comment.startswith('// '):
                comment = f"// {comment}"

            # Ensure RTL formatting
            comment = self.add_rtl_markers(comment)

        return comment

    def validate_hebrew_input(self, input_text: str) -> Dict[str, Any]:
        """Validate Hebrew text input for common issues."""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }

        if not input_text:
            validation_result["warnings"].append("קלט ריק")
            return validation_result

        # Check for mixed RTL/LTR issues
        if self.has_mixed_direction_issues(input_text):
            validation_result["warnings"].append("טקסט מכיל ערבוב של כיוונים")

        # Check for encoding issues
        if self.has_encoding_issues(input_text):
            validation_result["errors"].append("בעיות קידוד בטקסט")
            validation_result["valid"] = False

        return validation_result

    def has_mixed_direction_issues(self, text: str) -> bool:
        """Check if text has problematic mixed direction formatting."""
        # Simplified check - in production, this would be more sophisticated
        hebrew_chars = sum(1 for char in text if self.is_hebrew_character(char))
        latin_chars = sum(1 for char in text if char.isascii() and char.isalpha())

        # If both Hebrew and Latin characters are present in significant amounts
        total_alpha = hebrew_chars + latin_chars
        if total_alpha > 0:
            hebrew_ratio = hebrew_chars / total_alpha
            return 0.2 < hebrew_ratio < 0.8  # Mixed content

        return False

    def has_encoding_issues(self, text: str) -> bool:
        """Check for text encoding issues."""
        try:
            # Try to encode/decode to check for issues
            text.encode('utf-8').decode('utf-8')
            return False
        except UnicodeError:
            return True

    def is_hebrew_character(self, char: str) -> bool:
        """Check if a single character is Hebrew."""
        if not char:
            return False

        code_point = ord(char)
        return (self.hebrew_range[0] <= code_point <= self.hebrew_range[1] or
                self.hebrew_extended_range[0] <= code_point <= self.hebrew_extended_range[1])

    def extract_hebrew_words(self, text: str) -> list:
        """Extract Hebrew words from mixed text."""
        if not text:
            return []

        # Pattern to match Hebrew words
        hebrew_word_pattern = r'[\u0590-\u05FF\uFB1D-\uFB4F]+'
        hebrew_words = re.findall(hebrew_word_pattern, text)

        return hebrew_words

    def format_milestone_description(self, description: str) -> str:
        """Format milestone descriptions for optimal Hebrew display."""
        if not description:
            return description

        # Clean the text
        description = self.clean_hebrew_text(description)

        # Add appropriate formatting for educational content
        if self.is_hebrew_text(description):
            # Ensure proper punctuation
            if not description.endswith(('.', '!', '?', ':')):
                description += '.'

            # Add RTL formatting
            description = self.add_rtl_markers(description)

        return description

    def create_rtl_safe_json(self, data: Dict[str, Any]) -> str:
        """Create JSON that's safe for RTL display."""
        import json

        # Process Hebrew strings in the data
        processed_data = self._process_data_for_rtl(data)

        # Create JSON with proper Unicode handling
        json_str = json.dumps(
            processed_data,
            ensure_ascii=False,
            indent=2,
            separators=(',', ': ')
        )

        return json_str

    def _process_data_for_rtl(self, data: Any) -> Any:
        """Recursively process data to make Hebrew strings RTL-safe."""
        if isinstance(data, dict):
            return {key: self._process_data_for_rtl(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._process_data_for_rtl(item) for item in data]
        elif isinstance(data, str):
            if self.is_hebrew_text(data):
                return self.clean_hebrew_text(data)
            return data
        else:
            return data

    def get_text_direction(self, text: str) -> str:
        """Determine the primary text direction (rtl or ltr)."""
        if not text:
            return 'ltr'

        return 'rtl' if self.is_hebrew_text(text) else 'ltr'