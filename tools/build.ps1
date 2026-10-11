param(
    [string]$Toolchain = $env:PICO_TOOLCHAIN_PATH,
    [string]$CMake = $env:CMAKE_COMMAND,
    [string]$Ninja = $env:NINJA_COMMAND,
    [string]$Python = 'python',
    [string]$BuildDir = 'build',
    [switch]$Offline,
    [switch]$Prepared
)
$ErrorActionPreference='Stop'
$buildArgs = @((Join-Path $PSScriptRoot 'build.py'), '--build-dir', $BuildDir)
if ($Toolchain) { $buildArgs += @('--toolchain', $Toolchain) }
if ($CMake) { $buildArgs += @('--cmake', $CMake) }
if ($Ninja) { $buildArgs += @('--ninja', $Ninja) }
if ($Offline) { $buildArgs += '--offline' }
if ($Prepared) { $buildArgs += '--prepared' }
& $Python @buildArgs
if ($LASTEXITCODE) { throw 'PicoConsole build failed' }
