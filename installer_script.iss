[Setup]
AppName=StreamDeck
AppVersion=2.0
AppPublisher=Null Point Interactive Team
AppPublisherURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppSupportURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppUpdatesURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
DefaultDirName={autopf}\StreamDeck
DefaultGroupName=StreamDeck
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=StreamDeck_Setup_v3
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardImageFile=assets\installer_image.bmp
WizardSmallImageFile=assets\installer_small.bmp
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
DisableDirPage=no
DisableReadyPage=no
DisableFinishedPage=no
ShowLanguageDialog=no
UninstallDisplayIcon={app}\StreamDeck.exe
UninstallDisplayName=StreamDeck
VersionInfoVersion=2.0.0.0
VersionInfoCompany=Null Point Interactive Team
VersionInfoDescription=StreamDeck - Customizable Macro Deck
VersionInfoCopyright=© 2024 Null Point Interactive Team

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Start StreamDeck when Windows starts"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
Source: "dist\StreamDeck.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "gpio_config_template.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\gpio_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\console_deck_v2_arduino_code\*"; DestDir: "{app}\arduino_code"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\StreamDeck"; Filename: "{app}\StreamDeck.exe"
Name: "{group}\Configure GPIO"; Filename: "{app}\StreamDeck.exe"; Parameters: "--config-gpio"
Name: "{group}\Uninstall StreamDeck"; Filename: "{uninstallexe}"
Name: "{autodesktop}\StreamDeck"; Filename: "{app}\StreamDeck.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "StreamDeck"; ValueData: """{app}\StreamDeck.exe"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\StreamDeck.exe"; Description: "{cm:LaunchProgram,StreamDeck}"; Flags: nowait postinstall skipifsilent

[Code]
var
  ConfigPage: TInputQueryWizardPage;
  ArduinoPort: String;
  BaudRate: String;

procedure InitializeWizard;
begin
  ConfigPage := CreateInputQueryPage(wpWelcome,
    'GPIO Configuration', 'Configure your Arduino connection settings',
    'Please specify the Arduino connection settings. You can change these later by running StreamDeck with --config-gpio parameter.');
    
  ConfigPage.Add('Arduino COM Port (e.g., COM3, COM7):', False);
  ConfigPage.Add('Baud Rate (default: 9600):', False);
  
  // Set default values
  ConfigPage.Values[0] := 'COM7';
  ConfigPage.Values[1] := '9600';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = ConfigPage.ID then
  begin
    ArduinoPort := ConfigPage.Values[0];
    BaudRate := ConfigPage.Values[1];
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  ConfigContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Create gpio_config.json after installation
    ConfigFile := ExpandConstant('{app}\gpio_config.json');
    ConfigContent := '{\n' +
      '    "arduino": {\n' +
      '        "port": "' + ArduinoPort + '",\n' +
      '        "baudrate": ' + BaudRate + ',\n' +
      '        "timeout": 1\n' +
      '    },\n' +
      '    "volume": {\n' +
      '        "enabled": true,\n' +
      '        "default_value": 0\n' +
      '    },\n' +
      '    "media": {\n' +
      '        "enabled": true\n' +
      '    },\n' +
      '    "debug": {\n' +
      '        "enabled": true,\n' +
      '        "log_level": "INFO"\n' +
      '    }\n' +
      '}';
    
    SaveStringToFile(ConfigFile, ConfigContent, False);
  end;
end;