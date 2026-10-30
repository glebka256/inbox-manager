@echo off
REM Activate Virtual Environment and run Gmail AI Manager
echo Activating Gmail AI Manager virtual environment...
cd /d "c:\Users\Sean Fitz\OneDrive\Desktop\Email_Scraper"
call .venv\Scripts\activate.bat
echo.
echo Virtual environment activated!
echo You can now run:
echo   python Gmail_scraper.py
echo   python rule_based_classifier.py
echo   python test_gmail_connection.py
echo   python examples.py
echo.
cmd /k