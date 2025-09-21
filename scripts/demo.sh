#!/bin/bash
# Demo script for the Hebrew AI Tutor CLI Tool
# Shows the tool's capabilities without actually starting long-running services

set -e

echo "🚀 Hebrew AI Tutor CLI Tool Demo"
echo "================================="
echo

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run: python -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Make sure script is executable
chmod +x scripts/tutor.py

echo
echo "📋 1. Help and Usage"
echo "-------------------"
python scripts/tutor.py --help | head -20
echo "... (truncated for demo)"

echo
echo "📊 2. Environment Validation"
echo "----------------------------"
python scripts/tutor.py config --validate

echo
echo "🔍 3. Service Status (nothing running yet)"
echo "-----------------------------------------"
python scripts/tutor.py status --json

echo
echo "💚 4. Health Check (unhealthy because nothing is running)"
echo "--------------------------------------------------------"
python scripts/tutor.py health --json

echo
echo "⚙️  5. Configuration Display"
echo "----------------------------"
python scripts/tutor.py config

echo
echo "🧪 6. Test Suite Results"
echo "------------------------"
echo "Running comprehensive test suite..."
python -m pytest scripts/test_tutor_cli.py -v --tb=short | grep -E "(PASSED|FAILED|===.*===)" | tail -10

echo
echo "🎯 7. Advanced Features"
echo "-----------------------"
echo "Verbose status with debug logging:"
python scripts/tutor.py --verbose --log-level DEBUG status 2>&1 | head -5

echo
echo "JSON health output piped to jq (if available):"
if command -v jq &> /dev/null; then
    python scripts/tutor.py health --json | jq '.services.frontend.status'
else
    python scripts/tutor.py health --json | grep -o '"status":"[^"]*"' | head -1
fi

echo
echo "🎉 Demo Complete!"
echo "================="
echo
echo "Next steps:"
echo "1. ./scripts/tutor.py start --dev    # Start development servers"
echo "2. ./scripts/tutor.py status --watch # Monitor in real-time"
echo "3. ./scripts/tutor.py test           # Run all tests"
echo "4. ./scripts/tutor.py stop           # Stop all services"
echo
echo "For full documentation: cat scripts/README.md"