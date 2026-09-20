param(
    [Parameter(Mandatory = $true)]
    [string]$Destination
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$ExifToolVersion = "13.59"
$ArchiveName = "exiftool-$($ExifToolVersion)_64.zip"
$DownloadUrl = "https://master.dl.sourceforge.net/project/exiftool/${ArchiveName}?viasf=1"
$ExpectedSha256 = "44B512B25AF500724BA579D0A53C8FC5851628B692DD5E5D94AE4A15C2CBA9EC"

$DestinationPath = [System.IO.Path]::GetFullPath($Destination)
$DestinationRoot = [System.IO.Path]::GetPathRoot($DestinationPath)
if ($DestinationPath -eq $DestinationRoot -or [System.IO.Path]::GetFileName($DestinationPath) -ne "exiftool") {
    throw "For safety, Destination must end with an 'exiftool' directory."
}

$WorkRoot = Join-Path ([System.IO.Path]::GetTempPath()) "dng-to-jpeg-exiftool-$([guid]::NewGuid())"
$ArchivePath = Join-Path $WorkRoot $ArchiveName
$ExtractPath = Join-Path $WorkRoot "expanded"

try {
    New-Item -ItemType Directory -Path $WorkRoot | Out-Null
    Write-Host "Downloading official ExifTool $ExifToolVersion (64-bit)..."
    & curl.exe -L --fail --retry 3 $DownloadUrl -o $ArchivePath
    if ($LASTEXITCODE -ne 0) {
        throw "ExifTool download failed with exit code $LASTEXITCODE."
    }

    $ActualSha256 = (Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash
    if ($ActualSha256 -ne $ExpectedSha256) {
        throw "ExifTool SHA-256 mismatch. Expected $ExpectedSha256 but got $ActualSha256."
    }

    New-Item -ItemType Directory -Path $ExtractPath | Out-Null
    Expand-Archive -LiteralPath $ArchivePath -DestinationPath $ExtractPath
    $SourcePath = Join-Path $ExtractPath "exiftool-$($ExifToolVersion)_64"
    if (-not (Test-Path -LiteralPath (Join-Path $SourcePath "exiftool(-k).exe") -PathType Leaf)) {
        throw "The downloaded ExifTool archive has an unexpected layout."
    }

    if (Test-Path -LiteralPath $DestinationPath) {
        Remove-Item -LiteralPath $DestinationPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
    Copy-Item -Path (Join-Path $SourcePath "*") -Destination $DestinationPath -Recurse -Force
    Rename-Item -LiteralPath (Join-Path $DestinationPath "exiftool(-k).exe") -NewName "exiftool.exe"

    $BundledExecutable = Join-Path $DestinationPath "exiftool.exe"
    $DetectedVersion = (& $BundledExecutable -ver | Select-Object -First 1).Trim()
    if ($DetectedVersion -ne $ExifToolVersion) {
        throw "Bundled ExifTool validation failed. Expected $ExifToolVersion but got $DetectedVersion."
    }

    Write-Host "ExifTool $DetectedVersion verified and prepared at $DestinationPath"
}
finally {
    if (Test-Path -LiteralPath $WorkRoot) {
        Remove-Item -LiteralPath $WorkRoot -Recurse -Force
    }
}
