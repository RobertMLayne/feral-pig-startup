$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$archiveDuplicates = Join-Path $root 'archive/duplicates'
New-Item -ItemType Directory -Force -Path $archiveDuplicates | Out-Null

# Move duplicate working copies into the archive before renaming the canonical files.
$workingFolders = @('docs', 'drafts', 'claims', 'roadmap', 'tracker', 'figures')
foreach ($folder in $workingFolders) {
    $folderPath = Join-Path $root $folder
    if (-not (Test-Path $folderPath)) { continue }
    Get-ChildItem -Path $folderPath -File | Where-Object { $_.Name -match '\(\d+\)' } | ForEach-Object {
        Move-Item -Path $_.FullName -Destination $archiveDuplicates -Force
    }
}

# Canonical naming convention:
#   FeralPig_<Artifact>_v<major.minor>_<YYYYMMDD>.<ext>
# Example: FeralPig_StatusProtocol_v0.4_20260903.md
$rules = @(
    @{ Path = Join-Path $root 'docs'; Match = 'PROJECT_STATUS_AND_RESUME_PROTOCOL'; NewName = 'FeralPig_StatusProtocol' },
    @{ Path = Join-Path $root 'docs'; Match = 'PATENT_RESEARCH_NOTES'; NewName = 'FeralPig_ResearchNotes' },
    @{ Path = Join-Path $root 'docs'; Match = 'Patent_Drafting_Master_Control'; NewName = 'FeralPig_MasterControl' },
    @{ Path = Join-Path $root 'drafts'; Match = 'Feral_Pig_Provisional_Patent_Application_Working_Draft'; NewName = 'FeralPig_ProvisionalDraft' },
    @{ Path = Join-Path $root 'claims'; Match = 'Feral_Pig_Provisional_Exemplary_Claims'; NewName = 'FeralPig_ExemplaryClaims' },
    @{ Path = Join-Path $root 'roadmap'; Match = 'Feral_Pig_Project_Roadmap'; NewName = 'FeralPig_Roadmap' },
    @{ Path = Join-Path $root 'tracker'; Match = 'Feral_Pig_Patent_Business_Project_Tracker'; NewName = 'FeralPig_Tracker' },
    @{ Path = Join-Path $root 'figures'; Match = 'Patent_Figures'; NewName = 'FeralPig_Figures' }
)

foreach ($rule in $rules) {
    $folder = $rule.Path
    if (-not (Test-Path $folder)) { continue }

    $files = Get-ChildItem -Path $folder -File | Where-Object { $_.Name -match $rule.Match }
    foreach ($file in $files) {
        $nameWithoutExt = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
        $version = if ($nameWithoutExt -match 'v(\d+\.\d+)') { 'v' + $Matches[1] } else { 'v0.1' }
        $dateIso = if ($nameWithoutExt -match '(\d{4})-(\d{2})-(\d{2})') { $Matches[1] + $Matches[2] + $Matches[3] } elseif ($nameWithoutExt -match '(\d{8})') { $Matches[1] } else { (Get-Date).ToString('yyyyMMdd') }
        $extension = $file.Extension
        $newName = $rule.NewName + '_' + $version + '_' + $dateIso + $extension
        $target = Join-Path $folder $newName

        if ($file.Name -ne $newName) {
            Rename-Item -Path $file.FullName -NewName $newName
        }
    }
}

# Rename root-level index to the same convention.
$canonicalIndex = Join-Path $root 'STARTUP_CANONICAL_INDEX.md'
if (Test-Path $canonicalIndex) {
    Rename-Item -Path $canonicalIndex -NewName 'FeralPig_ProjectIndex_v0.1_20260609.md' -Force
}

Write-Host 'Renaming complete.'
Write-Host 'Convention: FeralPig_<Artifact>_v<major.minor>_<YYYYMMDD>.<ext>'
