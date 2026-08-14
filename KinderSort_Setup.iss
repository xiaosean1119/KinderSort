; KinderSort 1.0 Installer

[Setup]
AppName=KinderSort
AppVersion=1.0
DefaultDirName={autopf}\KinderSort
DefaultGroupName=KinderSort
OutputDir=installer
OutputBaseFilename=KinderSort_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "C:\xampp\htdocs\tutorial2\KinderSort\dist\KinderSort.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\KinderSort"; Filename: "{app}\KinderSort.exe"
Name: "{autodesktop}\KinderSort"; Filename: "{app}\KinderSort.exe"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"