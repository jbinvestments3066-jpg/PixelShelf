#requires -Version 5.1
[CmdletBinding()]
param([ValidateRange(1,86400)][int]$DurationSeconds, [switch]$DryRun, [switch]$Stop,
    [ValidatePattern('^[a-z][a-z0-9_]*$')][string]$SceneId='penguin', [switch]$ReportStop)
$ErrorActionPreference = 'Stop'
$signalName = if ($SceneId -eq 'penguin') { 'Local\AbiOledPenguinStop' } else { 'Local\Shelf_' + $SceneId }
if ($Stop) {
    try { $running = [Threading.EventWaitHandle]::OpenExisting($signalName) }
    catch [Threading.WaitHandleCannotBeOpenedException] { return }
    try { $null = $running.Set() } finally { $running.Dispose() }
    return
}
$frameSize = 832
$file = if ($SceneId -eq 'penguin') { 'Shore.frames' } else { "films/$SceneId.frames" }
$frames = [IO.File]::ReadAllBytes((Join-Path $PSScriptRoot $file))
$frameCount = if ($SceneId -eq 'penguin') { 1800 } else { 1200 }
if ($frames.Length -ne ($frameCount * $frameSize)) { throw "Incomplete film: $file" }
$buffer = [byte[]]::new($frameSize)
if ($DryRun) { Write-Output "$SceneId ready: $frameCount frames at 10 fps (128 x 52 pixels)."; return }

$props = Join-Path $env:PROGRAMDATA 'SteelSeries\SteelSeries Engine 3\coreProps.json'
$address = (Get-Content -Raw -LiteralPath $props | ConvertFrom-Json).address
if ($address -notmatch '^127\.0\.0\.1:\d{1,5}$') { throw 'No local SteelSeries Engine address.' }
$client = [Net.WebClient]::new()
$client.Proxy = $null
$client.Headers['Content-Type'] = 'application/json'
$base = 'http://' + $address
$game = 'ABI_OLED_COMPANION'
$eventName = 'PENGUIN'
$lease = [Threading.Mutex]::new($false,'Local\PixelShelfDisplayLease')
try { $acquired = $lease.WaitOne(0) } catch [Threading.AbandonedMutexException] { $acquired = $true }
if (!$acquired) { $lease.Dispose(); $client.Dispose(); throw 'Another shelf film is playing.' }
$created = $false
$signal = [Threading.EventWaitHandle]::new($false,'ManualReset',$signalName,[ref]$created)
if (!$created) { $signal.Dispose(); $client.Dispose(); $lease.ReleaseMutex(); $lease.Dispose(); throw 'This film is already playing.' }
function Send-Payload($route, $body) {
    $client.Headers['Content-Type'] = 'application/json'
    try { $null = $client.UploadString($base+'/'+$route,'POST',$body) }
    catch [Net.WebException] {
        $response = $_.Exception.Response
        if ($null -eq $response) { throw }
        $reader = [IO.StreamReader]::new($response.GetResponseStream())
        try { throw "$route returned $([int]$response.StatusCode): $($reader.ReadToEnd())" }
        finally { $reader.Dispose(); $response.Dispose() }
    }
}
try {
    Send-Payload 'game_metadata' (@{game=$game;game_display_name='ABI OLED Companion';developer='Local companion prototype';deinitialize_timer_length_ms=5000} | ConvertTo-Json -Compress)
    $handler = @{'device-type'='screened-128x52';zone='one';mode='screen';datas=@(@{'has-text'=$false;'image-data'=[int[]]$frames[0..831]})}
    Send-Payload 'bind_game_event' (@{game=$game;event=$eventName;value_optional=$true;handlers=@($handler)} | ConvertTo-Json -Depth 10 -Compress)
    $clock = [Diagnostics.Stopwatch]::StartNew()
    $lastPixels = ''
    $lastSent = -1000
    while (!$signal.WaitOne(0) -and (!$DurationSeconds -or $clock.Elapsed.TotalSeconds -lt $DurationSeconds)) {
        $tick = [long][Math]::Floor($clock.ElapsedMilliseconds / 100)
        [Array]::Copy($frames, ($tick % $frameCount)*$frameSize, $buffer, 0, $frameSize)
        $pixels = $buffer -join ','
        if ($lastPixels -cne $pixels -or $tick-$lastSent -ge 20) {
            Send-Payload 'game_event' ('{"game":"ABI_OLED_COMPANION","event":"PENGUIN","data":{"value":1,"frame":{"image-data-128x52":['+$pixels+']}}}')
            $lastPixels = $pixels
            $lastSent = $tick
        }
        $wait = ($tick+1)*100 - $clock.ElapsedMilliseconds
        if ($wait -gt 0) { Start-Sleep -Milliseconds $wait }
    }
    $interrupted = $signal.WaitOne(0)
} finally {
    try { Send-Payload 'stop_game' '{"game":"ABI_OLED_COMPANION"}' } finally {
        $client.Dispose(); $lease.ReleaseMutex(); $lease.Dispose(); $signal.Dispose()
    }
}
if ($ReportStop -and $interrupted) { exit 2 }
