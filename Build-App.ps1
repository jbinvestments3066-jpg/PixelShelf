#requires -Version 5.1
[CmdletBinding()]
param([string]$OutputPath = (Join-Path $PSScriptRoot 'PixelShelf.exe'))

$ErrorActionPreference = 'Stop'
$outputFile = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputPath)
$framework = Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319'
$compiler = Join-Path $framework 'csc.exe'
if (-not (Test-Path -LiteralPath $compiler -PathType Leaf)) {
    throw 'The Windows .NET Framework 4.x C# compiler is required.'
}
$parent = [IO.Path]::GetDirectoryName($outputFile)
[void][IO.Directory]::CreateDirectory($parent)
$sources = @('PixelShelf.cs', 'Playback.cs') | ForEach-Object { Join-Path $PSScriptRoot $_ }
& $compiler /nologo /target:winexe /platform:anycpu /optimize+ "/out:$outputFile" /r:System.Windows.Forms.dll /r:System.Drawing.dll /r:System.Xml.Linq.dll $sources
if ($LASTEXITCODE -ne 0) { throw "C# compilation failed with exit code $LASTEXITCODE." }
Write-Output $outputFile
