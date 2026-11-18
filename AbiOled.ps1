#requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet('Demo','Session','Text','Remove')][string]$Mode = 'Demo',
    [ValidateRange(1,86400)][int]$DurationSeconds = 30,
    [ValidateLength(1,20)][string]$Line1 = 'ABI COMPANION',
    [ValidateLength(1,20)][string]$Line2 = 'Display connected',
    [ValidatePattern('^screened(-[0-9]+x[0-9]+)?$')][string]$DeviceType = 'screened-128x52',
    [switch]$DryRun
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$gameId = 'ABI_OLED_COMPANION'
$propsPath = Join-Path $env:PROGRAMDATA 'SteelSeries\SteelSeries Engine 3\coreProps.json'

function Send-GameSense([string]$Endpoint, [hashtable]$Payload) {
    $json = $Payload | ConvertTo-Json -Depth 12 -Compress
    if ($DryRun) { Write-Output "$Endpoint $json"; return }
    $address = (Get-Content -LiteralPath $propsPath -Raw | ConvertFrom-Json).address
    if ($address -notmatch '^127\.0\.0\.1:([0-9]{1,5})$' -or [int]$Matches[1] -gt 65535) {
        throw 'SteelSeries did not advertise a valid loopback address.'
    }
    $response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "http://$address/$Endpoint" -ContentType 'application/json' -Body $json -TimeoutSec 5
    Write-Verbose "$Endpoint HTTP $($response.StatusCode)"
}

if ($Mode -eq 'Remove') {
    Send-GameSense 'remove_game' @{game=$gameId}
    Write-Output 'Removed ABI OLED Companion from SteelSeries Engine.'
    return
}

$registered = $false
try {
    Send-GameSense 'game_metadata' @{
        game=$gameId; game_display_name='ABI OLED Companion'; developer='Local companion prototype'
        deinitialize_timer_length_ms=5000
    }
    $registered = $true
    Send-GameSense 'bind_game_event' @{
        game=$gameId; event='STATUS'; min_value=0; max_value=100; value_optional=$true
        handlers=@(@{
            'device-type'=$DeviceType; zone='one'; mode='screen'
            datas=@(@{ 'length-millis'=2500; lines=@(
                @{'has-text'=$true; 'context-frame-key'='title'; bold=$true},
                @{'has-text'=$true; 'context-frame-key'='detail'}
            ) })
        })
    }
    $watch = [Diagnostics.Stopwatch]::StartNew()
    do {
        $title = $Line1
        $detail = $Line2
        if ($Mode -eq 'Demo') {
            $title = 'ABI OLED TEST'
            $detail = 'Display connected'
        } elseif ($Mode -eq 'Session') {
            $processes = @(Get-Process -Name UAGame -ErrorAction SilentlyContinue)
            if ($processes.Count -eq 0) {
                $title = 'ABI NOT RUNNING'
                $detail = 'Waiting for game'
            } else {
                $title = 'ABI RUNNING'
                try {
                    $start = $processes[0].StartTime
                    if ($null -eq $start) { throw 'Start time unavailable' }
                    $elapsed = (Get-Date) - $start
                    $detail = 'Open {0:00}:{1:00}' -f [int][math]::Floor($elapsed.TotalHours),$elapsed.Minutes
                } catch { $detail = 'Session time unknown' }
            }
        }
        Send-GameSense 'game_event' @{
            game=$gameId; event='STATUS'; data=@{value=1; frame=@{title=$title;detail=$detail}}
        }
        if ($DryRun) { break }
        Start-Sleep -Milliseconds ([int][math]::Max(1,[math]::Min(2000,($DurationSeconds-$watch.Elapsed.TotalSeconds)*1000)))
    } while ($watch.Elapsed.TotalSeconds -lt $DurationSeconds)
} finally {
    if ($registered) {
        try { Send-GameSense 'stop_game' @{game=$gameId} } catch { Write-Warning "Could not stop display: $($_.Exception.Message). It should expire after five seconds without updates." }
    }
}
