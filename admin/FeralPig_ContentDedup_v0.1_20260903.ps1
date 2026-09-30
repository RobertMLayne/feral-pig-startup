$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$activeFolders = @('admin','docs','drafts','claims','roadmap','tracker','figures','reference_materials')

function Get-DocumentRank {
    param([string]$Path)

    $lower = $Path.ToLowerInvariant()
    $rank = 0
    if ($lower -match '\\docs\\') { $rank += 100 }
    elseif ($lower -match '\\drafts\\') { $rank += 90 }
    elseif ($lower -match '\\claims\\') { $rank += 80 }
    elseif ($lower -match '\\roadmap\\') { $rank += 70 }
    elseif ($lower -match '\\tracker\\') { $rank += 60 }
    elseif ($lower -match '\\figures\\') { $rank += 50 }
    elseif ($lower -match '\\reference_materials\\') { $rank += 40 }
    elseif ($lower -match '\\admin\\') { $rank += 20 }
    else { $rank += 10 }

    if ($lower -match 'ferlpig_') { $rank += 25 }
    if ($lower -match 'v0\.[0-9]+') { $rank += 5 }
    if ($lower -match '\d{8}') { $rank += 2 }
    if ($lower -match 'archive') { $rank -= 50 }

    $version = 0.0
    if ($lower -match 'v(\d+(?:\.\d+)?)') { $version = [double]$Matches[1] }
    $date = 0
    if ($lower -match '(\d{8})') { $date = [int]$Matches[1] }

    return [pscustomobject]@{
        Rank = $rank
        Version = $version
        Date = $date
        Path = $Path
    }
}

# Build a content-based hash map
$hashMap = @{}
$files = Get-ChildItem -Path $root -Recurse -File | Where-Object {
    $_.FullName -notmatch '\\archive\\generated-export\\' -and
    $_.FullName -notmatch '\\\.git\\' -and
    $_.Name -ne 'Startup.code-workspace'
}

foreach ($file in $files) {
    $hash = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash
    if (-not $hashMap.ContainsKey($hash)) { $hashMap[$hash] = @() }
    $hashMap[$hash] += $file.FullName
}

$deleted = 0
$kept = @()

foreach ($group in $hashMap.Values | Where-Object { $_.Count -gt 1 }) {
    $canonical = ($group | Sort-Object {
        (Get-DocumentRank $_).Rank
    }, {
        (Get-DocumentRank $_).Version
    }, {
        (Get-DocumentRank $_).Date
    } | Select-Object -Last 1)

    $kept += $canonical

    foreach ($path in $group) {
        if ($path -eq $canonical) { continue }
        try {
            Remove-Item -Path $path -Force
            $deleted++
            Write-Host "DELETED duplicate: $path"
        }
        catch {
            Write-Host "FAILED to delete duplicate: $path"
        }
    }
}

Write-Host "CONTENT_DEDUP_COMPLETE"
Write-Host "KEPT_CANONICAL_COUNT: $($kept.Count)"
Write-Host "DELETED_DUPLICATES: $deleted"
