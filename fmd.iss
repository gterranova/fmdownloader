; -- Example1.iss --
; Demonstrates copying 3 files and creating an icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=FileMaker Downloader
AppVerName=FileMaker Downloader 1.0 (beta)
DefaultDirName={pf}\FileMaker Downloader
DefaultGroupName=FileMaker Downloader
;UninstallDisplayIcon={app}\earthwp.ico
Compression=lzma
SolidCompression=yes
;OutputDir=userdocs:Inno Setup Examples Output

[Files]
Source: "dist/*"; DestDir: "{app}"

[Icons]
Name: "{group}\FileMaker Downloader"; Filename: "{app}\prompt.bat"; WorkingDir: "{app}"
Name: "{group}\Uninstall FileMaker Downloader"; Filename: "{uninstallexe}"

;[UninstallDelete]
;Type: files; Name: "{app}\pywallpaper.bmp"
;Type: files; Name: "{app}\cache\*"
;Type: files; Name: "{app}\graphics\*"
