param([string]$Distro = 'Cosmos-Edge-2404')
$ErrorActionPreference = 'Stop'
& wsl.exe -d $Distro -u root --exec python3 /opt/cosmos-demo/manage_demo.py start
if ($LASTEXITCODE -ne 0) { throw 'Demo startup failed. Inspect /opt/cosmos-demo/backend.log and webui.log inside the selected WSL distro.' }
Start-Process 'http://localhost:8090'
