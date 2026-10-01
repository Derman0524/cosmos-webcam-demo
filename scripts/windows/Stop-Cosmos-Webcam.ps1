param([string]$Distro = 'Cosmos-Edge-2404')
$ErrorActionPreference = 'Stop'
& wsl.exe -d $Distro -u root --exec python3 /opt/cosmos-demo/manage_demo.py stop
if ($LASTEXITCODE -ne 0) { throw 'Demo shutdown was not confirmed. Inspect the status inside the selected WSL distro.' }
