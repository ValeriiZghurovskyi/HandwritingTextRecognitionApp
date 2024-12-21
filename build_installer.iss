[Setup]
AppName=Розпізнавання рукописного тексту
AppVersion={#MyAppVersion}
DefaultDirName={pf}\TextRecognition
DefaultGroupName=TextRecognition
OutputDir=Output
OutputBaseFilename=TextRecognitionSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\TextRecognition"; Filename: "{app}\main\main.exe"