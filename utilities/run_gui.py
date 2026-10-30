#!/usr/bin/env python3
"""
Simple Python launcher for Gmail AI Manager
This can be run directly with Python if batch files don't work
"""

import os
import sys
import subprocess
import platform

def main():
    print("=" * 50)
    print("Gmail AI Manager - Python Launcher")
    print("=" * 50)
    print()
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"Working directory: {script_dir}")
    print()
    
    # Check if GUI file exists
    gui_file = os.path.join(script_dir, "..", "launchers", "gmail_ai_gui.py")
    if not os.path.exists(gui_file):
        print("ERROR: gmail_ai_gui.py not found!")
        print(f"Looking for: {gui_file}")
        input("Press Enter to exit...")
        return
    
    # Check virtual environment
    if platform.system() == "Windows":
        venv_python = os.path.join(script_dir, "gmail_ai_env", "Scripts", "python.exe")
        venv_activate = os.path.join(script_dir, "gmail_ai_env", "Scripts", "activate.bat")
    else:
        venv_python = os.path.join(script_dir, "gmail_ai_env", "bin", "python")
        venv_activate = os.path.join(script_dir, "gmail_ai_env", "bin", "activate")
    
    if os.path.exists(venv_python):
        print("✓ Using virtual environment Python")
        python_cmd = venv_python
    else:
        print("⚠ Virtual environment not found, using system Python")
        python_cmd = sys.executable
    
    print(f"Python executable: {python_cmd}")
    print()
    
    # Launch GUI
    print("Launching Gmail AI Manager GUI...")
    print("(Close this window after the GUI opens)")
    print()
    
    try:
        # Run the GUI
        result = subprocess.run([python_cmd, gui_file], 
                              cwd=script_dir,
                              check=False)
        
        if result.returncode == 0:
            print("✓ GUI closed normally")
        else:
            print(f"⚠ GUI exited with code: {result.returncode}")
            
    except Exception as e:
        print(f"ERROR launching GUI: {e}")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()