@echo off
cd /d "%~dp0"
set PYTHONW=C:\Users\cmbc\AppData\Local\Doubao\User Data\sandbox_runtime\bases\c98c5042338ed152c6f10ecd8591889f\python\pythonw.exe
if exist "%PYTHONW%" (
  start "" "%PYTHONW%" "%~dp0AIP-Admin.pyw"
) else (
  start "" python "%~dp0AIP-Admin.pyw"
)
