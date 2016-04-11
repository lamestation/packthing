[Setup]

AppID=${APPID}
AppName=${NAME}
AppVersion=${VERSION}
AppPublisher=${ORGANIZATION}
AppPublisherURL=${WEBSITE}
AppSupportURL=${WEBSITE}
AppUpdatesURL=${WEBSITE}
DefaultDirName={pf}\${NAME}
DefaultGroupName=${NAME}
SourceDir=${SOURCEDIR}
OutputDir=${OUTDIR}
OutputBaseFilename=${PACKAGENAME}
Compression=lzma/Max
SolidCompression=true
AlwaysShowDirOnReadyPage=true
UserInfoPage=no
UsePreviousUserInfo=no
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=no
WizardImageFile="${BANNER}"
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{cm:UninstallProgram,${NAME}}"; Filename: "{uninstallexe}";

