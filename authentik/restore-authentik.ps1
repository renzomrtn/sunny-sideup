$ErrorActionPreference = "Stop"

$BackupPath = Join-Path $PSScriptRoot "backups\authentik.dump"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$EnvPath = Join-Path $RepoRoot ".env"
$DbName = "authentik"
$DbUser = "authentik"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Command,
        [Parameter(Mandatory = $true)]
        [string[]] $Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Command $($Arguments -join ' ')"
    }
}

function Get-EnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,
        [Parameter(Mandatory = $true)]
        [string] $Default
    )

    if (-not (Test-Path $EnvPath)) {
        return $Default
    }

    $Line = Get-Content $EnvPath | Where-Object { $_ -match "^$Name=" } | Select-Object -First 1
    if (-not $Line) {
        return $Default
    }

    return ($Line -replace "^$Name=", "").Trim()
}

if (-not (Test-Path $BackupPath)) {
    throw "Backup not found: $BackupPath"
}

$DbName = Get-EnvValue "AUTHENTIK_POSTGRES_DB" $DbName
$DbUser = Get-EnvValue "AUTHENTIK_POSTGRES_USER" $DbUser

Write-Host "Stopping Authentik services..."
Invoke-Checked "docker" @("compose", "stop", "authentik-server", "authentik-worker")

Write-Host "Starting Authentik database..."
Invoke-Checked "docker" @("compose", "up", "-d", "authentik-db")

Write-Host "Waiting for Authentik database to accept connections..."
$Ready = $false
for ($i = 1; $i -le 60; $i++) {
    & docker @("exec", "authentik_db", "pg_isready", "-h", "127.0.0.1", "-U", $DbUser, "-d", $DbName) *> $null
    if ($LASTEXITCODE -eq 0) {
        $Ready = $true
        break
    }
    Start-Sleep -Seconds 1
}

if (-not $Ready) {
    throw "Authentik database did not become ready within 60 seconds."
}

Write-Host "Copying dump into Authentik database container..."
Invoke-Checked "docker" @("cp", $BackupPath, "authentik_db:/tmp/authentik.dump")

Write-Host "Resetting Authentik database..."
Invoke-Checked "docker" @("exec", "authentik_db", "psql", "-h", "127.0.0.1", "-U", $DbUser, "-d", "postgres", "-c", "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DbName';")
Invoke-Checked "docker" @("exec", "authentik_db", "dropdb", "-h", "127.0.0.1", "-U", $DbUser, "--if-exists", $DbName)
Invoke-Checked "docker" @("exec", "authentik_db", "createdb", "-h", "127.0.0.1", "-U", $DbUser, $DbName)

Write-Host "Restoring Authentik database..."
Invoke-Checked "docker" @("exec", "authentik_db", "pg_restore", "-h", "127.0.0.1", "-U", $DbUser, "-d", $DbName, "/tmp/authentik.dump")

Write-Host "Starting Authentik services..."
Invoke-Checked "docker" @("compose", "up", "-d", "authentik-server", "authentik-worker")

Write-Host "Restore complete. Open http://localhost:9000 and check Applications."
