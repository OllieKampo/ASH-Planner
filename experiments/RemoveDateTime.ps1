param([Parameter(Mandatory=$True, Position=0, HelpMessage="Path to folder containing experimental results.")] [string] $path)

Get-ChildItem -Path "$($path)\*" -File | Rename-Item -NewName { $_.Name -replace "_([0-9-]){10}_([0-9-]){8}_", "_" }