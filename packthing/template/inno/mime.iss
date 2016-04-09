[Tasks]
Name: ${EXTENSION}Association; Description: "Associate ""${EXTENSION}"" extension"; GroupDescription: "File extensions:"

[Registry]
Root: HKCR; Subkey: ".${EXTENSION}";              ValueType: string; ValueName: ""; ValueData: "${TYPE}";        Flags: uninsdeletevalue;   Tasks: ${EXTENSION}Association 
Root: HKCR; Subkey: "${TYPE}";                    ValueType: string; ValueName: ""; ValueData: "${DESCRIPTION}"; Flags: uninsdeletekey;     Tasks: ${EXTENSION}Association 
Root: HKCR; Subkey: "${TYPE}\DefaultIcon";        ValueType: string; ValueName: ""; ValueData: "{app}\${EXECUTABLE}.EXE,0";                 Tasks: ${EXTENSION}Association 
Root: HKCR; Subkey: "${TYPE}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\${EXECUTABLE}.EXE"" ""%1""";        Tasks: ${EXTENSION}Association 
