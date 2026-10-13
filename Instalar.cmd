@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Instale Python 3.12 com Tcl/Tk pelo site python.org e tente novamente.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto :failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed
echo Instalacao concluida. Abra Abrir.cmd para iniciar.
pause
exit /b 0
:failed
echo A instalacao falhou. Confira as mensagens acima.
pause
exit /b 1
