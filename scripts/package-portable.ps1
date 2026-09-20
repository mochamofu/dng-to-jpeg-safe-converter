$ErrorActionPreference = "Stop"

$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ExecutablePath = Join-Path $ProjectRoot "dist\DNG-to-JPEG.exe"
$BuildRoot = Join-Path $ProjectRoot "build"
$PackagePath = Join-Path $BuildRoot "portable"
$DistPath = Join-Path $ProjectRoot "dist"
$ArchivePath = Join-Path $DistPath "DNG-to-JPEG-Windows-Portable.zip"
$ChecksumPath = Join-Path $DistPath "SHA256SUMS.txt"

if (-not (Test-Path -LiteralPath $ExecutablePath -PathType Leaf)) {
    throw "Build the executable first: $ExecutablePath"
}
if (-not $PackagePath.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
    [System.IO.Path]::GetFileName($PackagePath) -ne "portable") {
    throw "Refusing to package an unsafe output path: $PackagePath"
}

if (Test-Path -LiteralPath $PackagePath) {
    Remove-Item -LiteralPath $PackagePath -Recurse -Force
}
New-Item -ItemType Directory -Path $PackagePath -Force | Out-Null
New-Item -ItemType Directory -Path $DistPath -Force | Out-Null

Copy-Item -LiteralPath $ExecutablePath -Destination $PackagePath
Copy-Item -LiteralPath (Join-Path $ProjectRoot "README.md") -Destination $PackagePath
Copy-Item -LiteralPath (Join-Path $ProjectRoot "LICENSE") -Destination $PackagePath
Copy-Item -LiteralPath (Join-Path $ProjectRoot "THIRD_PARTY_NOTICES.md") -Destination $PackagePath
Copy-Item -LiteralPath (Join-Path $ProjectRoot "RELEASE_NOTES.md") -Destination $PackagePath
Copy-Item -LiteralPath (Join-Path $ProjectRoot "licenses") -Destination $PackagePath -Recurse

if (Test-Path -LiteralPath $ArchivePath) {
    Remove-Item -LiteralPath $ArchivePath -Force
}
Compress-Archive -Path (Join-Path $PackagePath "*") -DestinationPath $ArchivePath
$ArchiveHash = (Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash
"$ArchiveHash  DNG-to-JPEG-Windows-Portable.zip" | Set-Content -LiteralPath $ChecksumPath -Encoding ascii

Write-Host "Portable package complete: $ArchivePath"
Write-Host "SHA-256: $ArchiveHash"
