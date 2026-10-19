Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "d:\AGI"
WshShell.Run "cmd /c d:\AGI\START_SERVER.bat", 0, False
