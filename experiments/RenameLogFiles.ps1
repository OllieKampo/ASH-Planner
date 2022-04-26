param([Parameter(Mandatory=$True, Position=0, HelpMessage="Path to folder containing log files.")] [string] $path)

Get-ChildItem -Path "$($path)\*" -Include "*.log*" -File | Rename-Item -NewName { $_.Name -replace ".(log).(?<number>[0-9]{1,2})", ".`${number}`.log" }