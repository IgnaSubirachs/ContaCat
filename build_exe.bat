@echo off
echo Building ERP Catala Desktop Application...
echo.

pyinstaller erp.spec --clean --noconfirm

echo.
echo Build complete! Executable is in dist\ERP_Catala\
