$ErrorActionPreference = 'Stop'
$compiler = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../.runtime/tectonic/tectonic.exe'))
if (-not (Test-Path -LiteralPath $compiler)) {
    throw "Project compiler missing: $compiler. Alternatively upload latex-source.zip to Overleaf and select XeLaTeX."
}
Push-Location -LiteralPath $PSScriptRoot
try {
    & $compiler 'paper.tex' '--outdir' '..' '--keep-logs'
    if ($LASTEXITCODE -ne 0) { throw "LaTeX compilation failed; see output/pdf/paper.log." }
    Write-Host "PDF: $([IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../paper.pdf')))"
} finally {
    Pop-Location
}
