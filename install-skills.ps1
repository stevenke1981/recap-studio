# Copy the recap-* skills into the user's Claude Code skills directory.
param([string]$Target = (Join-Path $HOME ".claude/skills"))

$src = Join-Path $PSScriptRoot "skills"
New-Item -ItemType Directory -Force $Target | Out-Null
Get-ChildItem $src -Directory -Filter "recap-*" | ForEach-Object {
    $dest = Join-Path $Target $_.Name
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    Copy-Item -Recurse $_.FullName $dest
    Write-Host "installed $($_.Name) -> $dest"
}
