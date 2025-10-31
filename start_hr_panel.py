#!/usr/bin/env python3
"""
Start the HR Control Panel web interface

This starts the web-based HR Control Panel that allows you to:
1. Input job details (title, description, skills)
2. Specify number of candidates
3. Start the complete automated workflow:
   - Source candidates
   - Generate MCQ questions
   - Send onboarding emails
   - Auto-MCQ generation when form submitted
   - Auto-feedback when MCQ completed
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("\n" + "=" * 80)
    print("STARTING HR CONTROL PANEL")
    print("=" * 80)
    print("\nWhat this does:")
    print("   - Web interface to start recruitment workflow")
    print("   - Complete automation from job input to feedback emails")
    print("   - No terminal commands needed after starting!")
    print("\nAccess at: http://localhost:3000")
    print("\nRequired:")
    print("   - Onboarding form server (port 5000)")
    print("   - MCQ form server (port 5001)")
    print("\nMake sure both form servers are running!")
    print("=" * 80 + "\n")
    
    # Run the HR control panel
    try:
        script_path = Path(__file__).parent / "hr_control_panel.py"
        subprocess.run([sys.executable, str(script_path)], check=True)
    except KeyboardInterrupt:
        print("\n\n✅ HR Control Panel stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
