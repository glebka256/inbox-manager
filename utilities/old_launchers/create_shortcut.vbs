Set WshShell = CreateObject("WScript.Shell")
Set oShellLink = WshShell.CreateShortcut("Gmail AI Manager.lnk")
oShellLink.TargetPath = "cmd.exe"
oShellLink.Arguments = "/c ""cd /d """ & WshShell.CurrentDirectory & """ && call gmail_ai_env\Scripts\activate.bat && python gmail_ai_gui.py && pause"""
oShellLink.WorkingDirectory = WshShell.CurrentDirectory
oShellLink.WindowStyle = 1
oShellLink.Description = "Gmail AI Manager - Email Classification System"
oShellLink.Save