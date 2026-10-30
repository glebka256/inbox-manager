Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get current directory
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Check for virtual environments and run silently
If fso.FileExists(currentDir & "\.venv\Scripts\pythonw.exe") Then
    WshShell.Run """" & currentDir & "\.venv\Scripts\pythonw.exe"" """ & currentDir & "\visual_advanced_gui.py""", 0, False
ElseIf fso.FileExists(currentDir & "\gmail_ai_env\Scripts\pythonw.exe") Then
    WshShell.Run """" & currentDir & "\gmail_ai_env\Scripts\pythonw.exe"" """ & currentDir & "\visual_advanced_gui.py""", 0, False
Else
    WshShell.Run "pythonw.exe """ & currentDir & "\visual_advanced_gui.py""", 0, False
End If