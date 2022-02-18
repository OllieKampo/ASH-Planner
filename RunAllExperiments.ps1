param([Parameter(Mandatory=$True, Position=0, HelpMessage="Path to folder containing experimental configurations.")] [string] $path)

Get-ChildItem -Path "$($path)\*" -Include *.config -File | Resolve-Path -Relative | ForEach-Object { Start-Process Python -ArgumentList "./Launch.py --config=$($_) -ao experiment -op experiment -cfn -dpos -disp_fig False" -Wait -NoNewWindow };