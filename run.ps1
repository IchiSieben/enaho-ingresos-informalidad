<#
.SYNOPSIS
    Corre un script de src/ dejando la salida en logs/, separando stdout y stderr.

.DESCRIPTION
    Convencion heredada del proyecto SIS-diabetes:
      1. `python -u` -> sin buffer: si la maquina se cuelga a mitad de un
         entrenamiento, el log muestra en que fase murio.
      2. Start-Process -RedirectStandard* -> escritura directa a archivo,
         seguible durante la corrida (el `>` de PowerShell vuelca al final).
    Usa el interprete del venv del proyecto. Los logs no se versionan.

.EXAMPLE
    .\run.ps1 04_torneo_regresion
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Script
)

$ErrorActionPreference = 'Stop'
$raiz = $PSScriptRoot

if (-not $Script.EndsWith('.py')) { $Script = "$Script.py" }

$rutaScript = Join-Path $raiz "src\$Script"
if (-not (Test-Path $rutaScript)) { throw "No existe $rutaScript" }

$dirLogs = Join-Path $raiz 'logs'
if (-not (Test-Path $dirLogs)) { New-Item -ItemType Directory $dirLogs | Out-Null }

$base = [IO.Path]::GetFileNameWithoutExtension($Script)
$rutaLog = Join-Path $dirLogs "$base.log"
$rutaErr = Join-Path $dirLogs "$base.err"

$python = Join-Path $raiz '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = (Get-Command python).Source }

Write-Host "Ejecutando : $rutaScript"
Write-Host "Interprete : $python"
Write-Host "stdout     -> $rutaLog"
Write-Host "stderr     -> $rutaErr"
Write-Host ("-" * 60)

$inicio = Get-Date
$proc = Start-Process -FilePath $python `
                      -ArgumentList @('-u', ('"{0}"' -f $rutaScript)) `
                      -WorkingDirectory $raiz `
                      -RedirectStandardOutput $rutaLog `
                      -RedirectStandardError $rutaErr `
                      -NoNewWindow -PassThru -Wait

$dur = (Get-Date) - $inicio
Write-Host ("-" * 60)
Write-Host ("Terminado en {0:hh\:mm\:ss} con codigo {1}" -f $dur, $proc.ExitCode)

if ($proc.ExitCode -ne 0) {
    Write-Host "`nUltimas lineas de $rutaErr :" -ForegroundColor Red
    Get-Content $rutaErr -Tail 20
}
exit $proc.ExitCode
