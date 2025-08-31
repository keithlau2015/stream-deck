[Setup]
AppName=StreamDeck
AppVersion=2.0
AppPublisher=StreamDeck Team
AppPublisherURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppSupportURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppUpdatesURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
DefaultDirName={autopf}\StreamDeck
DefaultGroupName=StreamDeck
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=StreamDeck_Setup
SetupIconFile=assets/icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardImageFile=assets/installer_image.bmp
WizardSmallImageFile=assets/installer_small.bmp
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
DisableDirPage=no
DisableReadyPage=no
DisableFinishedPage=no
ShowLanguageDialog=no
UninstallDisplayIcon={app}\StreamDeck.exe
UninstallDisplayName=StreamDeck
VersionInfoVersion=2.0.0.0
VersionInfoCompany=StreamDeck Team
VersionInfoDescription=StreamDeck - Customizable Macro Deck
VersionInfoCopyright=© 2024 StreamDeck Team

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startup"; Description: "Start StreamDeck when Windows starts"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
Source: "dist\StreamDeck.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\console_deck_v2_arduino_code\*"; DestDir: "{app}\arduino_code"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\StreamDeck"; Filename: "{app}\StreamDeck.exe"; IconFilename: "{app}\StreamDeck.exe"
Name: "{group}\Configure GPIO"; Filename: "{app}\StreamDeck.exe"; Parameters: "--config-gpio"; IconFilename: "{app}\StreamDeck.exe"
Name: "{group}\Readme"; Filename: "{app}\README.md"; IconFilename: "{app}\StreamDeck.exe"
Name: "{group}\Uninstall StreamDeck"; Filename: "{uninstallexe}"; IconFilename: "{uninstallexe}"
Name: "{autodesktop}\StreamDeck"; Filename: "{app}\StreamDeck.exe"; Tasks: desktopicon; IconFilename: "{app}\StreamDeck.exe"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\StreamDeck"; Filename: "{app}\StreamDeck.exe"; Tasks: quicklaunchicon; IconFilename: "{app}\StreamDeck.exe"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "StreamDeck"; ValueData: """{app}\StreamDeck.exe"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\StreamDeck.exe"; Description: "{cm:LaunchProgram,StreamDeck}"; Flags: nowait postinstall skipifsilent

[Code]
var
  WelcomePage: TOutputMsgWizardPage;
  ConfigPage: TInputQueryWizardPage;
  ArduinoPort: String;
  BaudRate: String;
  VolumeEnabled: Boolean;
  MediaEnabled: Boolean;
  DebugEnabled: Boolean;
  ConfigCheckBox: TCheckBox;
  VolumeCheckBox: TCheckBox;
  MediaCheckBox: TCheckBox;
  DebugCheckBox: TCheckBox;

function GetBooleanString(Value: Boolean): String;
begin
  if Value then
    Result := 'true'
  else
    Result := 'false';
end;

procedure InitializeWizard;
begin
  // Create welcome page with custom message
  WelcomePage := CreateOutputMsgPage(wpWelcome,
    'Welcome to StreamDeck Setup', 'This will install StreamDeck on your computer.',
    'StreamDeck is a customizable macro deck that allows you to configure up to 9 buttons to launch websites or executable files with a click.' + #13#10 + #13#10 +
    'Features:' + #13#10 +
    '• System tray integration' + #13#10 +
    '• Arduino hardware support' + #13#10 +
    '• Volume and media controls' + #13#10 +
    '• Background operation' + #13#10 + #13#10 +
    'Click Next to continue with the installation.');

  // Create GPIO configuration page
  ConfigPage := CreateInputQueryPage(wpSelectDir,
    'GPIO Configuration', 'Configure your Arduino connection settings',
    'Please specify the Arduino connection settings. You can change these later by opening GPIO Settings from the system tray.');
    
  ConfigPage.Add('Arduino COM Port (e.g., COM3, COM7):', False);
  ConfigPage.Add('Baud Rate (default: 9600):', False);
  
  // Set default values
  ConfigPage.Values[0] := 'COM7';
  ConfigPage.Values[1] := '9600';
    
  // We'll create all the controls manually in CreateConfigControls procedure
end;

procedure CreateConfigControls;
var
  FeaturesLabel: TLabel;
  CurrentTop: Integer;
begin
  // Position checkboxes below the existing input fields with more spacing
  CurrentTop := ConfigPage.Edits[1].Top + ConfigPage.Edits[1].Height + 30;
  
  // Create features label
  FeaturesLabel := TLabel.Create(ConfigPage);
  FeaturesLabel.Parent := ConfigPage.Surface;
  FeaturesLabel.Left := ConfigPage.Edits[0].Left;
  FeaturesLabel.Top := CurrentTop;
  FeaturesLabel.Caption := 'Enable Features:';
  FeaturesLabel.Font.Style := [fsBold];
  CurrentTop := CurrentTop + 25;
  
  // Create checkboxes for feature configuration
  VolumeCheckBox := TCheckBox.Create(ConfigPage);
  VolumeCheckBox.Parent := ConfigPage.Surface;
  VolumeCheckBox.Left := ConfigPage.Edits[0].Left;
  VolumeCheckBox.Top := CurrentTop;
  VolumeCheckBox.Width := ConfigPage.SurfaceWidth - 40;
  VolumeCheckBox.Caption := 'Enable Volume Control';
  VolumeCheckBox.Checked := True;
  CurrentTop := CurrentTop + 25;
  
  MediaCheckBox := TCheckBox.Create(ConfigPage);
  MediaCheckBox.Parent := ConfigPage.Surface;
  MediaCheckBox.Left := ConfigPage.Edits[0].Left;
  MediaCheckBox.Top := CurrentTop;
  MediaCheckBox.Width := ConfigPage.SurfaceWidth - 40;
  MediaCheckBox.Caption := 'Enable Media Controls';
  MediaCheckBox.Checked := True;
  CurrentTop := CurrentTop + 25;
  
  DebugCheckBox := TCheckBox.Create(ConfigPage);
  DebugCheckBox.Parent := ConfigPage.Surface;
  DebugCheckBox.Left := ConfigPage.Edits[0].Left;
  DebugCheckBox.Top := CurrentTop;
  DebugCheckBox.Width := ConfigPage.SurfaceWidth - 40;
  DebugCheckBox.Caption := 'Enable Debug Logging';
  DebugCheckBox.Checked := True;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = ConfigPage.ID then
  begin
    CreateConfigControls;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = ConfigPage.ID then
  begin
    // Get values from input query page
    ArduinoPort := ConfigPage.Values[0];
    BaudRate := ConfigPage.Values[1];
    VolumeEnabled := VolumeCheckBox.Checked;
    MediaEnabled := MediaCheckBox.Checked;
    DebugEnabled := DebugCheckBox.Checked;
    
    // Validate COM port
    if (Length(ArduinoPort) < 3) or (Copy(ArduinoPort, 1, 3) <> 'COM') then
    begin
      MsgBox('Please enter a valid COM port (e.g., COM3, COM7).', mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Validate baud rate - simple check for common values
    if (BaudRate <> '9600') and (BaudRate <> '115200') and (BaudRate <> '57600') and (BaudRate <> '38400') and (BaudRate <> '19200') then
    begin
      MsgBox('Please enter a valid baud rate (9600, 19200, 38400, 57600, or 115200).', mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  ConfigContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Create gpio_config.json with user settings
    ConfigFile := ExpandConstant('{app}\gpio_config.json');
    ConfigContent := '{' + #13#10 +
      '    "arduino": {' + #13#10 +
      '        "port": "' + ArduinoPort + '",' + #13#10 +
      '        "baudrate": ' + BaudRate + ',' + #13#10 +
      '        "timeout": 1' + #13#10 +
      '    },' + #13#10 +
      '    "volume": {' + #13#10 +
      '        "enabled": ' + GetBooleanString(VolumeEnabled) + ',' + #13#10 +
      '        "default_value": 0' + #13#10 +
      '    },' + #13#10 +
      '    "media": {' + #13#10 +
      '        "enabled": ' + GetBooleanString(MediaEnabled) + #13#10 +
      '    },' + #13#10 +
      '    "debug": {' + #13#10 +
      '        "enabled": ' + GetBooleanString(DebugEnabled) + ',' + #13#10 +
      '        "log_level": "INFO"' + #13#10 +
      '    }' + #13#10 +
      '}';
    
    SaveStringToFile(ConfigFile, ConfigContent, False);
    
    // Create default pref.json if it doesn't exist
    if not FileExists(ExpandConstant('{app}\pref.json')) then
    begin
      SaveStringToFile(ExpandConstant('{app}\pref.json'), 
        '{"1":{"type":"none","value":""},"2":{"type":"none","value":""},"3":{"type":"none","value":""},"4":{"type":"none","value":""},"5":{"type":"none","value":""},"6":{"type":"none","value":""},"7":{"type":"none","value":""},"8":{"type":"none","value":""},"9":{"type":"none","value":""}}', 
        False);
    end;
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\gpio_config.json"
Type: files; Name: "{app}\config.json"
Type: dirifempty; Name: "{app}"
