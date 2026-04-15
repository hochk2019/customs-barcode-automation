; Inno Setup Script for Customs Barcode Automation v1.5.4
; Build with: ISCC.exe installer.iss (after PyInstaller build)

#define MyAppName "Customs Barcode Automation"
#define MyAppVersion "1.5.4"
#define MyAppPublisher "Hochk2019"
#define MyAppExeName "CustomsAutomation.exe"
#define MyAppURL "https://github.com/hochk2019/customs-barcode-automation"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName=C:\CustomsBarcodeAutomation
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=CustomsBarcodeAutomation_Setup_{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Don't require admin for portable install location
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Uninstaller settings - preserve user data
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Tạo biểu tượng trên Desktop"; GroupDescription: "Biểu tượng:"; Flags: checkedonce

[Files]
; Main application files from PyInstaller dist
Source: "dist\CustomsAutomation\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Config sample (config.ini will be auto-created on first run)
Source: "config.ini.sample"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Gỡ cài đặt {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Khởi chạy {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up logs only - keep user data
Type: filesandordirs; Name: "{app}\logs"

[Code]
// Preserve user data during uninstall - ask user
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Don't delete user config/data files automatically
    // They will remain in the install folder for manual cleanup
  end;
end;
