; Bulletin Builder - Inno Setup Script
; Creates a professional Windows installer with Start Menu shortcuts and uninstaller

#define MyAppName "Bulletin Builder"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Lake Almanor Community Church"
#define MyAppURL "https://github.com/LogunLACC/bulletin_builder"
#define MyAppExeName "bulletin.exe"

[Setup]
; Basic application information
AppId={{8F3B4C2D-1A5E-4F7B-9C3D-2E6A8B4C1D7F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=BulletinBuilder-{#MyAppVersion}-Setup
; TODO: Add icon file - SetupIconFile=..\assets\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}

; Visual settings
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

; Minimum Windows version
MinVersion=10.0.17763

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "..\dist\bulletin\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; All files and subdirectories from dist\bulletin\
Source: "..\dist\bulletin\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; _internal directory with all dependencies
Source: "..\dist\bulletin\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; Templates and assets
Source: "..\dist\bulletin\templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\bulletin\components\*"; DestDir: "{app}\components"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\bulletin\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration
Source: "..\dist\bulletin\config.ini.default"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "README.txt"
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion; DestName: "LICENSE.txt"

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\README"; Filename: "{app}\README.txt"

; Desktop shortcut (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch shortcut (optional, Windows 7 and below)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to launch the app after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up user data directories (optional - commented out by default to preserve user drafts)
; Type: filesandordirs; Name: "{app}\user_drafts"
; Type: filesandordirs; Name: "{app}\config.ini"

[Code]
// Custom functions for the installer

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Add any pre-installation checks here
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create user_drafts directory if it doesn't exist
    if not DirExists(ExpandConstant('{app}\user_drafts')) then
      CreateDir(ExpandConstant('{app}\user_drafts'));
      
    // Create user_drafts\AutoSave directory
    if not DirExists(ExpandConstant('{app}\user_drafts\AutoSave')) then
      CreateDir(ExpandConstant('{app}\user_drafts\AutoSave'));
      
    // Copy default config if user config doesn't exist
    if not FileExists(ExpandConstant('{app}\config.ini')) then
      FileCopy(ExpandConstant('{app}\config.ini.default'), 
               ExpandConstant('{app}\config.ini'), False);
  end;
end;

function InitializeUninstall(): Boolean;
var
  Response: Integer;
begin
  Response := MsgBox('Do you want to keep your bulletins and settings?' + #13#10 + 
                     '(Located in user_drafts folder and config.ini)', 
                     mbConfirmation, MB_YESNO);
  
  if Response = IDNO then
  begin
    // Delete user data if user chose not to keep it
    DelTree(ExpandConstant('{app}\user_drafts'), True, True, True);
    DeleteFile(ExpandConstant('{app}\config.ini'));
  end;
  
  Result := True;
end;
