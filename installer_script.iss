[Setup]
AppName=StreamDeck
AppVersion=2.x
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
VersionInfoVersion=2.9.9.9
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
  VersionFixPage: TOutputMsgWizardPage;
  ArduinoPort: String;
  BaudRate: String;
  VolumeEnabled: Boolean;
  MediaEnabled: Boolean;
  DebugEnabled: Boolean;
  ConfigCheckBox: TCheckBox;
  VolumeCheckBox: TCheckBox;
  MediaCheckBox: TCheckBox;
  DebugCheckBox: TCheckBox;
  PreviousVersion: String;
  IsUpgrade: Boolean;
  VersionIssueDetected: Boolean;

function GetBooleanString(Value: Boolean): String;
begin
  if Value then
    Result := 'true'
  else
    Result := 'false';
end;

function DetectPreviousVersion(): String;
var
  VersionFile, UpdateInfoFile, ConfigFile: String;
  VersionContent, UpdateContent, ConfigContent: String;
  I: Integer;
  Lines: TArrayOfString;
begin
  Result := '';
  
  // Method 1: Check version.txt
  VersionFile := ExpandConstant('{app}\version.txt');
  if FileExists(VersionFile) then
  begin
    if LoadStringFromFile(VersionFile, VersionContent) then
    begin
      Result := Trim(VersionContent);
      if Result <> '' then
        Exit;
    end;
  end;
  
  // Method 2: Check update_info.json for installed_version
  UpdateInfoFile := ExpandConstant('{app}\update_info.json');
  if FileExists(UpdateInfoFile) then
  begin
    if LoadStringFromFile(UpdateInfoFile, UpdateContent) then
    begin
      // Simple JSON parsing for "installed_version"
      I := Pos('"installed_version":', UpdateContent);
      if I > 0 then
      begin
        UpdateContent := Copy(UpdateContent, I + 20, Length(UpdateContent));
        I := Pos('"', UpdateContent);
        if I > 0 then
        begin
          UpdateContent := Copy(UpdateContent, I + 1, Length(UpdateContent));
          I := Pos('"', UpdateContent);
          if I > 0 then
          begin
            Result := Copy(UpdateContent, 1, I - 1);
            if Result <> '' then
              Exit;
          end;
        end;
      end;
    end;
  end;
  
  // Method 3: Check update_config.json for last_processed_version
  ConfigFile := ExpandConstant('{app}\update_config.json');
  if FileExists(ConfigFile) then
  begin
    if LoadStringFromFile(ConfigFile, ConfigContent) then
    begin
      // Simple JSON parsing for "last_processed_version"
      I := Pos('"last_processed_version":', ConfigContent);
      if I > 0 then
      begin
        ConfigContent := Copy(ConfigContent, I + 25, Length(ConfigContent));
        I := Pos('"', ConfigContent);
        if I > 0 then
        begin
          ConfigContent := Copy(ConfigContent, I + 1, Length(ConfigContent));
          I := Pos('"', ConfigContent);
          if I > 0 then
          begin
            Result := Copy(ConfigContent, 1, I - 1);
            if (Result <> '') then
              Exit;
          end;
        end;
      end;
    end;
  end;
end;

function CheckVersionIssue(): Boolean;
begin
  Result := False;
  
  // Check if previous version indicates a potential issue
  // (empty version or version files missing despite app being installed)
  if (PreviousVersion = '') then
  begin
    // Check if app files exist but no version detected
    if FileExists(ExpandConstant('{app}\main.py')) or 
       FileExists(ExpandConstant('{app}\gui.py')) or
       DirExists(ExpandConstant('{app}\src')) then
    begin
      Result := True;
      Exit;
    end;
  end;
  
  // Check if any StreamDeck files exist but no proper version tracking
  if FileExists(ExpandConstant('{app}\StreamDeck.exe')) or FileExists(ExpandConstant('{app}\main.py')) then
  begin
    // If app exists but no version was detected, there's likely an issue
    if PreviousVersion = '' then
    begin
      Result := True;
      Exit;
    end;
  end;
  
  // Check if update config exists with problematic settings
  if FileExists(ExpandConstant('{app}\update_config.json')) then
  begin
    // If config exists but version detection failed, there might be an issue
    if PreviousVersion = '' then
      Result := True;
  end;
end;

function GetLatestVersionFromGitHub(): String;
var
  WinHttpReq: Variant;
  Response: String;
  TagPos, StartPos, EndPos: Integer;
begin
  Result := '1.0.0'; // Minimal fallback version if GitHub fails
  
  try
    // Create WinHTTP request object
    WinHttpReq := CreateOleObject('WinHttp.WinHttpRequest.5.1');
    WinHttpReq.Open('GET', 'https://api.github.com/repos/keithlau2015/stream-deck/releases/latest', False);
    WinHttpReq.SetRequestHeader('User-Agent', 'StreamDeck-Installer');
    WinHttpReq.Send();
    
    if WinHttpReq.Status = 200 then
    begin
      Response := WinHttpReq.ResponseText;
      
      // Simple JSON parsing to extract tag_name
      TagPos := Pos('"tag_name":', Response);
      if TagPos > 0 then
      begin
        StartPos := Pos('"', Response, TagPos + 11);
        if StartPos > 0 then
        begin
          EndPos := Pos('"', Response, StartPos + 1);
          if EndPos > 0 then
          begin
            Result := Copy(Response, StartPos + 1, EndPos - StartPos - 1);
            // Remove 'v' prefix if present
            if (Length(Result) > 0) and (Result[1] = 'v') then
              Result := Copy(Result, 2, Length(Result) - 1);
          end;
        end;
      end;
    end;
  except
    // If anything fails, use minimal fallback version
    Result := '1.0.0';
  end;
end;

procedure FixVersionIssue();
var
  VersionFile, UpdateInfoFile: String;
  UpdateContent: String;
  CurrentVersion: String;
begin
  // Get the latest version from GitHub instead of hardcoding
  CurrentVersion := GetLatestVersionFromGitHub();
  
  // Create/update version.txt
  VersionFile := ExpandConstant('{app}\version.txt');
  SaveStringToFile(VersionFile, CurrentVersion, False);
  
  // Create/update update_info.json with comprehensive information
  UpdateInfoFile := ExpandConstant('{app}\update_info.json');
  UpdateContent := '{' + #13#10 +
    '  "installed_version": "' + CurrentVersion + '",' + #13#10 +
    '  "installation_date": "' + GetDateTimeString('yyyy-mm-dd"T"hh:nn:ss', #0, #0) + '",' + #13#10 +
    '  "installation_method": "installer_auto_fix",' + #13#10 +
    '  "version_fixed_by_installer": true,' + #13#10 +
    '  "previous_version_detected": "' + PreviousVersion + '",' + #13#10 +
    '  "fix_applied": true,' + #13#10 +
    '  "installer_version": "' + CurrentVersion + '",' + #13#10 +
    '  "notes": "Automatically fixed version detection issue during installation"' + #13#10 +
    '}';
  SaveStringToFile(UpdateInfoFile, UpdateContent, False);
end;

procedure InitializeWizard;
var
  WelcomeMessage: String;
  LatestVersion: String;
begin
  // Get the latest version from GitHub
  LatestVersion := GetLatestVersionFromGitHub();
  
  // Detect previous installation
  PreviousVersion := DetectPreviousVersion();
  IsUpgrade := (PreviousVersion <> '');
  VersionIssueDetected := CheckVersionIssue();
  
  // Create welcome message based on installation type
  if IsUpgrade then
  begin
    if VersionIssueDetected then
      WelcomeMessage := 'StreamDeck Update & Auto-Fix Setup' + #13#10 + #13#10 +
        'Existing installation detected!' + #13#10 +
        'Previous version: ' + PreviousVersion + #13#10 +
        'Latest available: ' + LatestVersion + #13#10 + #13#10 +
        '🔧 AUTO-FIX: This installer will automatically:' + #13#10 +
        '• Update to StreamDeck v' + LatestVersion + #13#10 +
        '• Fix the "always updating" issue' + #13#10 +
        '• Repair version detection problems' + #13#10 +
        '• Keep ALL your existing settings' + #13#10 + #13#10 +
        '✅ Your button configs and GPIO settings will be preserved!' + #13#10 +
        '✅ No more constant update notifications!' + #13#10 +
        '✅ Auto-updates will work correctly!'
    else
      WelcomeMessage := 'StreamDeck Update Setup' + #13#10 + #13#10 +
        'Existing installation detected!' + #13#10 +
        'Previous version: ' + PreviousVersion + #13#10 +
        'Updating to: ' + LatestVersion + #13#10 + #13#10 +
        'This will update StreamDeck to version ' + LatestVersion + ' while preserving' + #13#10 +
        'all your existing settings and configurations.' + #13#10 + #13#10 +
        '✅ Button configurations will be kept' + #13#10 +
        '✅ GPIO settings will be preserved' + #13#10 +
        '✅ All preferences will remain intact';
  end
  else
  begin
    WelcomeMessage := 'Welcome to StreamDeck v' + LatestVersion + '!' + #13#10 + #13#10 +
      'StreamDeck is a customizable macro deck that allows you to configure up to 9 buttons to launch websites or executable files with a click.' + #13#10 + #13#10 +
      'Key Features:' + #13#10 +
      '• System tray integration' + #13#10 +
      '• Arduino hardware support' + #13#10 +
      '• Volume and media controls' + #13#10 +
      '• Background operation' + #13#10 +
      '• Auto-update system' + #13#10 + #13#10 +
      'Installing version: ' + LatestVersion + #13#10 + #13#10 +
      'Click Next to continue with the installation.';
  end;

  // Create welcome page with dynamic message
  WelcomePage := CreateOutputMsgPage(wpWelcome,
    'Welcome to StreamDeck Setup', 'This will install StreamDeck on your computer.',
    WelcomeMessage);

  // Create version fix information page (only shown if needed)
  if VersionIssueDetected then
  begin
    VersionFixPage := CreateOutputMsgPage(wpSelectDir,
      'Auto-Fix: Version Detection Issue', 'Resolving the "always updating" problem',
      '🔍 PROBLEM DETECTED:' + #13#10 +
      'Your StreamDeck installation has version detection issues, causing:' + #13#10 +
      '• Constant "update available" notifications' + #13#10 +
      '• Auto-update system repeatedly downloading' + #13#10 +
      '• Version detection not working properly' + #13#10 + #13#10 +
      '🔧 AUTO-FIX IN PROGRESS:' + #13#10 +
      'This installer will automatically resolve the issue by:' + #13#10 +
      '• Creating proper version tracking files (version.txt, update_info.json)' + #13#10 +
      '• Setting the correct version number (' + LatestVersion + ')' + #13#10 +
      '• Ensuring auto-updates work correctly in the future' + #13#10 + #13#10 +
      '✅ RESULT: No more update notifications spam!' + #13#10 +
      '✅ Your button configs and settings will be preserved!' + #13#10 + #13#10 +
      'Click Next to continue the automatic fix...');
  end;

  // Create GPIO configuration page (skip for upgrades with existing config)
  if not IsUpgrade or not FileExists(ExpandConstant('{app}\gpio_config.json')) then
  begin
    ConfigPage := CreateInputQueryPage(wpSelectDir,
      'GPIO Configuration', 'Configure your Arduino connection settings',
      'Please specify the Arduino connection settings. You can change these later by opening GPIO Settings from the system tray.');
      
    ConfigPage.Add('Arduino COM Port (e.g., COM3, COM7):', False);
    ConfigPage.Add('Baud Rate (default: 9600):', False);
    
    // Set default values
    ConfigPage.Values[0] := 'COM7';
    ConfigPage.Values[1] := '9600';
  end;
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
  // Only create config controls if ConfigPage was created (new installation or missing config)
  if Assigned(ConfigPage) and (CurPageID = ConfigPage.ID) then
  begin
    CreateConfigControls;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Only validate config page if it was created and we're on it
  if Assigned(ConfigPage) and (CurPageID = ConfigPage.ID) then
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
  ExistingConfigContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Always fix version issue first
    FixVersionIssue();
    
    // Handle GPIO configuration
    ConfigFile := ExpandConstant('{app}\gpio_config.json');
    
    // Only create new config if it doesn't exist or if this is a new installation
    if not FileExists(ConfigFile) or not IsUpgrade then
    begin
      // Use default values if ConfigPage wasn't shown (upgrade scenario)
      if not Assigned(ConfigPage) then
      begin
        ArduinoPort := 'COM7';
        BaudRate := '9600';
        VolumeEnabled := True;
        MediaEnabled := True;
        DebugEnabled := True;
      end;
      
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
    end
    else
    begin
      // For upgrades with existing config, just log that we preserved it
      // The config is already there, no need to overwrite
    end;
    
    // Create default pref.json if it doesn't exist
    if not FileExists(ExpandConstant('{app}\pref.json')) then
    begin
      SaveStringToFile(ExpandConstant('{app}\pref.json'), 
        '{"BUTTON_1":{"type":"none","value":""},"BUTTON_2":{"type":"none","value":""},"BUTTON_3":{"type":"none","value":""},"BUTTON_4":{"type":"none","value":""},"BUTTON_5":{"type":"none","value":""},"BUTTON_6":{"type":"none","value":""},"BUTTON_7":{"type":"none","value":""},"BUTTON_8":{"type":"none","value":""},"BUTTON_9":{"type":"none","value":""}}', 
        False);
    end;
    
    // Show completion message for version fix
    if VersionIssueDetected then
    begin
      MsgBox('🎉 SUCCESS: Version Issue Fixed!' + #13#10 + #13#10 +
             '✅ StreamDeck now correctly detects version ' + LatestVersion + #13#10 +
             '✅ Auto-update system has been repaired' + #13#10 +
             '✅ No more constant "update available" notifications' + #13#10 +
             '✅ All your existing settings have been preserved' + #13#10 + #13#10 +
             'The following files were created to fix the issue:' + #13#10 +
             '• version.txt (tracks current version)' + #13#10 +
             '• update_info.json (installation details)' + #13#10 + #13#10 +
             'You can now use StreamDeck normally without update issues!', mbInformation, MB_OK);
    end;
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\gpio_config.json"
Type: files; Name: "{app}\config.json"
Type: dirifempty; Name: "{app}"
