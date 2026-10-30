Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get parent directory (main project folder)
launchersDir = fso.GetParentFolderName(WScript.ScriptFullName)
currentDir = fso.GetParentFolderName(launchersDir)

' Check for virtual environments
If fso.FileExists(currentDir & "\.venv\Scripts\pythonw.exe") Then
    pythonPath = currentDir & "\.venv\Scripts\pythonw.exe"
ElseIf fso.FileExists(currentDir & "\gmail_ai_env\Scripts\pythonw.exe") Then
    pythonPath = currentDir & "\gmail_ai_env\Scripts\pythonw.exe"
Else
    MsgBox "Error: No virtual environment found!" & vbCrLf & "Please run setup first.", vbCritical, "Gmail AI Manager"
    WScript.Quit
End If

' Launch Visual Dashboard without showing command window
WshShell.Run """" & pythonPath & """ """ & currentDir & "\visual_advanced_gui.py""", 0, False