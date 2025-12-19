; =============================================================================
; USER CONFIG (hier anpassen)
; =============================================================================
#define MyAppName "MindPic"
#define MyAppVersion "1.1.0"
#define MyAppExeName "MindPic.exe"

#define ProjectDir "D:\Coding\Projekte\mindpic"
#define DistDir    ProjectDir + "\dist\MindPic"

#define OutputDir  ProjectDir + "\mindpic\dist"
#define SetupName  "MindPic_Setup"

; Optional: Setup-Icon (für die Installer-EXE)
#define SetupIcon  ProjectDir + "\mindpic\assets\mindpic.ico"
; =============================================================================

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir={#OutputDir}
OutputBaseFilename={#SetupName}
SetupIconFile={#SetupIcon}
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; Flags: unchecked

[Files]
; kompletten one-dir Build kopieren (inkl. assets + DLLs + Python runtime)
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} starten"; Flags: nowait postinstall skipifsilent
