param(
    [Parameter(Mandatory=$true)][string]$CudaPython,
    [Parameter(Mandatory=$true)][string]$ModelDir,
    [string]$QuantoDir,
    [string]$OutputDir = 'research/market/measurements',
    [ValidateSet('bf16','int4')][string]$Group = 'bf16'
)

# Serialize real GPU work; preserve every existing result and unrelated process.
# CUDA-reported free and nvidia-smi-reported free differ on this host. Use the
# additional conservative nvidia-smi guard; neither number is a capacity guarantee.
$ErrorActionPreference = 'Stop'
$env:HF_HUB_DISABLE_PROGRESS_BARS = '1'
$env:TQDM_DISABLE = '1'
$env:TOKENIZERS_PARALLELISM = 'false'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
if($Group -eq 'int4') {
    if(-not $QuantoDir -or -not (Test-Path -LiteralPath $QuantoDir)) {
        throw 'INT4 group requires the separately inspected temporary Quanto package.'
    }
    $env:PYTHONPATH = $QuantoDir
}

$cells = if($Group -eq 'bf16') {
    @(@{Cell='D1';Prompt=256;Active=1}, @{Cell='D2';Prompt=2048;Active=1}, @{Cell='D3';Prompt=2048;Active=2})
} else {
    @(@{Cell='D4';Prompt=2048;Active=1}, @{Cell='D5';Prompt=2048;Active=2})
}
$ledgerPath = Join-Path $OutputDir "mr09-$Group-execution-ledger.json"
$ledger = @()
foreach($cell in $cells) {
    foreach($repetition in 1..3) {
        $resultPath = Join-Path $OutputDir "mr09-$($cell.Cell)-r$repetition.json"
        if(Test-Path -LiteralPath $resultPath) {
            Write-Output "Preserved existing $resultPath"
            continue
        }
        $freeCsv = & nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits
        if($LASTEXITCODE -ne 0 -or @($freeCsv).Count -ne 1) {
            throw 'Need one valid nvidia-smi free-memory sample; no execution permitted.'
        }
        $freeMiB = [int]($freeCsv.Trim())
        $entry = [ordered]@{Cell=$cell.Cell;Repetition=$repetition;PreflightUtc=[DateTime]::UtcNow.ToString('o');
            SmiFreeMiB=$freeMiB;SmiQuery='nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits';
            Cache=$Group;PromptTokens=$cell.Prompt;ActiveSequences=$cell.Active;QueuedRequests=0}
        if($freeMiB -lt 2048) {
            $entry.Status='unexecuted'
            $entry.Reason='nvidia-smi free-memory guard below2048MiB; preserve other workloads'
            $ledger += $entry
            $ledger | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ledgerPath -Encoding utf8
            throw 'Memory guard stopped matrix; no process was evicted.'
        }
        Write-Output "Starting $($cell.Cell) r$repetition; nvidia-smi free=$freeMiB MiB"
        $entry.Status='running'
        $ledger += $entry
        $ledger | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ledgerPath -Encoding utf8
        & $CudaPython scripts/mr09_measure.py --model-dir $ModelDir --output $resultPath `
            --cell $cell.Cell --repetition $repetition --prompt-tokens $cell.Prompt `
            --active-sequences $cell.Active --cache $Group
        $processExitCode = $LASTEXITCODE
        $entry.ProcessExitCode=$processExitCode
        if(Test-Path -LiteralPath $resultPath) {
            $runResult = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json -AsHashtable
            $entry.Status=$runResult.status
        } else {
            $entry.Status='runtime_error'
            $entry.Reason='measurement process returned no result; retain process exit code'
        }
        $ledger | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ledgerPath -Encoding utf8
        if($processExitCode -ne 0 -or $entry.Status -ne 'success') {
            throw "Matrix stopped after $($cell.Cell) r$repetition outcome=$($entry.Status); no hidden configuration retry."
        }
    }
}
