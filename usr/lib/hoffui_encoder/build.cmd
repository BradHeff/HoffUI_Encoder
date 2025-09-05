@ECHO off
SETLOCAL EnableDelayedExpansion

REM ============================================================================
REM Enhanced Build Script for HoffUI FFMPEG Encoder
REM ============================================================================
REM This script builds a standalone Python application using PyInstaller
REM Automatically increments version numbers and ensures all dependencies
REM are included for standalone execution
REM ============================================================================

REM Application Configuration
SET APP_NAME="HoffUI FFMPEG Encoder"
SET MAIN_SCRIPT=main.py

REM Check if custom app name was provided as parameter
IF NOT "%1"=="" SET APP_NAME=%1

ECHO ============================================================================
ECHO Building %APP_NAME% - Standalone Executable
ECHO ============================================================================

REM Step 1: Auto-increment version number
ECHO [1/7] Auto-incrementing version number...
python auto_version_increment.py
IF ERRORLEVEL 1 (
    ECHO ERROR: Failed to increment version number
    GOTO :ERROR_EXIT
)

REM Step 2: Set DEBUG to False for production build
ECHO [2/7] Setting DEBUG mode to False...
python preBuild.py
IF ERRORLEVEL 1 (
    ECHO ERROR: Failed to set DEBUG mode
    GOTO :ERROR_EXIT
)

REM Step 3: Detect PyInstaller location
ECHO [3/7] Detecting PyInstaller installation...
SET PYINSTALLER_EXE=

REM Try common PyInstaller locations
FOR %%P IN (pyinstaller.exe) DO (
    IF EXIST "%%~$PATH:P" (
        SET PYINSTALLER_EXE=%%~$PATH:P
        GOTO :PYINSTALLER_FOUND
    )
)

REM Try user-specific paths based on your installation
IF '%username%' == 'bheffernan' (
    SET PYINSTALLER_EXE=C:\Users\bheffernan\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe
) ELSE IF '%username%' == 'bradh' (
    SET PYINSTALLER_EXE=C:\Users\bradheffernan\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe
) ELSE IF '%username%' == 'brad.heffernan' (
    SET PYINSTALLER_EXE=C:\Users\bradheffernan\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe
) ELSE (
    REM Try common PyInstaller locations for any user
    SET PYINSTALLER_CANDIDATE=C:\Users\%username%\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe
    IF EXIST "!PYINSTALLER_CANDIDATE!" (
        SET PYINSTALLER_EXE=!PYINSTALLER_CANDIDATE!
    ) ELSE (
        REM Try to find pyinstaller in PATH
        WHERE pyinstaller >nul 2>nul
        IF !ERRORLEVEL! EQU 0 (
            SET PYINSTALLER_EXE=pyinstaller
        ) ELSE (
            ECHO ERROR: PyInstaller not found. Please install it with: pip install pyinstaller
            ECHO Expected location: C:\Users\%username%\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe
            GOTO :ERROR_EXIT
        )
    )
)

:PYINSTALLER_FOUND
ECHO Found PyInstaller: %PYINSTALLER_EXE%

REM Step 4: Clean previous builds
ECHO [4/7] Cleaning previous builds...
IF EXIST "scrap\dist" RMDIR /S /Q "scrap\dist"
IF EXIST "scrap\build" RMDIR /S /Q "scrap\build"
IF EXIST "*.spec" DEL /Q "*.spec"

REM Step 5: Create directories
ECHO [5/7] Creating build directories...
IF NOT EXIST "scrap" MKDIR "scrap"
IF NOT EXIST "scrap\dist" MKDIR "scrap\dist"
IF NOT EXIST "scrap\build" MKDIR "scrap\build"

REM Step 6: Build standalone executable with comprehensive dependencies
ECHO [6/7] Building standalone executable...
ECHO Using PyInstaller: %PYINSTALLER_EXE%

"%PYINSTALLER_EXE%" ^
    --clean ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --noconsole ^
    --distpath=scrap/dist ^
    --workpath=scrap/build ^
    --name=%APP_NAME% ^
    --icon=icon.ico ^
    --version-file=version.rc ^
    --collect-all=ttkbootstrap ^
    --collect-all=tkthread ^
    --collect-all=pillow ^
    --collect-all=PIL ^
    --hidden-import=ttkbootstrap ^
    --hidden-import=ttkbootstrap.themes ^
    --hidden-import=ttkbootstrap.style ^
    --hidden-import=ttkbootstrap.toast ^
    --hidden-import=tkthread ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=threading ^
    --hidden-import=pathlib ^
    --hidden-import=signal ^
    --add-data=icon.ico;. ^
    --add-data=hoffui.png;. ^
    %MAIN_SCRIPT%

IF ERRORLEVEL 1 (
    ECHO ERROR: PyInstaller build failed
    GOTO :ERROR_EXIT
)

REM Step 7: Validate the build
ECHO [7/7] Validating the standalone executable...
python validate_build.py
IF ERRORLEVEL 1 (
    ECHO WARNING: Build validation failed - executable may not work properly
    ECHO Continuing anyway...
)

ECHO ============================================================================
ECHO Build completed successfully!
ECHO ============================================================================
ECHO Executable location: scrap\dist\%APP_NAME%.exe
ECHO ============================================================================

REM Display file size and version info
IF EXIST "scrap\dist\%APP_NAME%.exe" (
    FOR %%F IN ("scrap\dist\%APP_NAME%.exe") DO (
        ECHO File size: %%~zF bytes
    )
)

ECHO.
ECHO Build artifacts:
DIR "scrap\dist" /B
ECHO.

GOTO :SUCCESS_EXIT

:ERROR_EXIT
ECHO ============================================================================
ECHO BUILD FAILED!
ECHO ============================================================================
PAUSE
EXIT /B 1

:SUCCESS_EXIT
ECHO ============================================================================
ECHO BUILD SUCCESSFUL!
ECHO ============================================================================
EXIT /B 0
