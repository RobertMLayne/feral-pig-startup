param(
    [Parameter(Mandatory=$true)][string]$QueryName,
    [Parameter(Mandatory=$true)][ValidateSet('A','AAAA','CNAME','TXT')][string]$QueryType
)

# Read-only resolver adapter. Values arrive as arguments rather than shell code.
try {
    $records = @(Resolve-DnsName -Name $QueryName -Type $QueryType -Server 1.1.1.1 -DnsOnly -ErrorAction Stop)
    $answers = @($records | ForEach-Object {
        if ($_.Type -eq 'A') { @{name=$_.Name; type=1; data=$_.IPAddress} }
        elseif ($_.Type -eq 'AAAA') { @{name=$_.Name; type=28; data=$_.IPAddress} }
        elseif ($_.Type -eq 'CNAME') { @{name=$_.Name; type=5; data=$_.NameHost} }
        elseif ($_.Type -eq 'TXT') { @{name=$_.Name; type=16; data=($_.Strings -join '')} }
    })
    @{Status=0; Answer=$answers} | ConvertTo-Json -Depth 5 -Compress
} catch {
    $code = $_.Exception.NativeErrorCode
    if ($code -eq 9003) { @{Status=3} | ConvertTo-Json -Compress }
    elseif ($code -eq 9501) { @{Status=0; Answer=@()} | ConvertTo-Json -Compress }
    else { @{Status=-1; error=$_.Exception.Message} | ConvertTo-Json -Compress }
}
