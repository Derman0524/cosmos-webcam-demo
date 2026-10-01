param([string]$Distro = 'Cosmos-Edge-2404')
$ErrorActionPreference = 'Stop'
& wsl.exe -d $Distro -u root --exec python3 /opt/cosmos-demo/manage_demo.py status
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect the demo in the selected WSL distro.' }
