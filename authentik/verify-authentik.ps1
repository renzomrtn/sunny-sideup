$ErrorActionPreference = "Stop"

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

$DbName = Get-EnvValue "AUTHENTIK_POSTGRES_DB" $DbName
$DbUser = Get-EnvValue "AUTHENTIK_POSTGRES_USER" $DbUser

Write-Host "Checking Authentik database readiness..."
Invoke-Checked "docker" @("exec", "authentik_db", "pg_isready", "-h", "127.0.0.1", "-U", $DbUser, "-d", $DbName)

Write-Host ""
Write-Host "Users:"
Invoke-Checked "docker" @("exec", "authentik_db", "psql", "-h", "127.0.0.1", "-U", $DbUser, "-d", $DbName, "-P", "pager=off", "-c", "SELECT id, username, email, name, is_active, type, last_login, password_change_date, CASE WHEN password IS NULL OR password='' THEN 'empty' WHEN password LIKE '!%' THEN 'unusable' ELSE split_part(password, '$', 1) END AS password_status_or_algorithm FROM authentik_core_user ORDER BY id;")

Write-Host ""
Write-Host "Applications and OAuth providers:"
Invoke-Checked "docker" @("exec", "authentik_db", "psql", "-h", "127.0.0.1", "-U", $DbUser, "-d", $DbName, "-P", "pager=off", "-c", "SELECT a.name AS application, a.slug, p.name AS provider_name, o.client_id, CASE WHEN o.client_secret IS NULL OR o.client_secret='' THEN 'missing' ELSE 'present' END AS client_secret_status, o._redirect_uris FROM authentik_core_application a LEFT JOIN authentik_core_provider p ON p.id=a.provider_id LEFT JOIN authentik_providers_oauth2_oauth2provider o ON o.provider_ptr_id=a.provider_id ORDER BY a.name;")

Write-Host ""
Write-Host "Admin group membership:"
Invoke-Checked "docker" @("exec", "authentik_db", "psql", "-h", "127.0.0.1", "-U", $DbUser, "-d", $DbName, "-P", "pager=off", "-c", "SELECT u.username, g.name AS group_name, g.is_superuser FROM authentik_core_user u LEFT JOIN authentik_core_user_ak_groups ug ON ug.user_id=u.id LEFT JOIN authentik_core_group g ON g.group_uuid=ug.group_id ORDER BY u.id, g.name;")
