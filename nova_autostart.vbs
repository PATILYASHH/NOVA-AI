Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\code\NOVA"
WshShell.Run "python nova_watchdog.py", 0, False
Set WshShell = Nothing
