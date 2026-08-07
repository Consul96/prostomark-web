# ProstoMark Sign Agent (Windows + CryptoPro CSP)
# Исходящий опрос backend, подпись точных байтов через cryptcp.exe, возврат CMS Base64.
# НЕ логирует полный КМ/токен/закрытый ключ.

$ErrorActionPreference = 'Stop'

$AgentApiKey  = $env:AGENT_API_KEY
$BackendUrl   = ($env:BACKEND_URL   ?? 'https://app.prostomark.ru/api/v1/marking').TrimEnd('/')
$CryptcpPath  = $env:CRYPTCP_PATH   ?? 'C:\Program Files\Crypto Pro\CSP\cryptcp.exe'
$PollSeconds  = [int]($env:SIGN_AGENT_POLL_SECONDS ?? '5')

if (-not $AgentApiKey) { throw 'AGENT_API_KEY is required' }

$Headers = @{ 'X-Agent-Api-Key' = $AgentApiKey }

function Get-Sha256Base64([byte[]]$bytes) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    return ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
}

function Invoke-Sign([byte[]]$payload, [bool]$detached, [string]$thumbprint) {
    $tmpIn  = [System.IO.Path]::GetTempFileName()
    $tmpOut = "$tmpIn.sig"
    try {
        [System.IO.File]::WriteAllBytes($tmpIn, $payload)
        $detachArg = if ($detached) { '-detached' } else { '' }
        # cryptcp формирует CMS-подпись по отпечатку сертификата (thumbprint).
        & $CryptcpPath -sign $detachArg -thumbprint $thumbprint -der $tmpIn $tmpOut | Out-Null
        $sig = [System.IO.File]::ReadAllBytes($tmpOut)
        return [Convert]::ToBase64String($sig)
    } finally {
        Remove-Item -Force -ErrorAction SilentlyContinue $tmpIn, $tmpOut
    }
}

Write-Host "Sign Agent started; backend=$BackendUrl poll=${PollSeconds}s"

while ($true) {
    try {
        Invoke-RestMethod -Method Post -Uri "$BackendUrl/sign-agent/heartbeat" -Headers $Headers | Out-Null
        $job = Invoke-RestMethod -Method Get -Uri "$BackendUrl/sign-agent/next-job" -Headers $Headers

        if ($null -ne $job.job_id) {
            $payload = [Convert]::FromBase64String($job.payload_base64)
            $localHash = Get-Sha256Base64 $payload
            if ($localHash -ne $job.payload_sha256) {
                Invoke-RestMethod -Method Post -Uri "$BackendUrl/sign-agent/error" -Headers $Headers `
                    -ContentType 'application/json' `
                    -Body (@{ job_id = $job.job_id; error = 'payload hash mismatch' } | ConvertTo-Json)
            } else {
                $detached = ($job.sign_type -eq 'detached')
                $thumb = if ($job.certificate_thumbprint) { $job.certificate_thumbprint } else { $env:CERT_THUMBPRINT }
                $signature = Invoke-Sign $payload $detached $thumb
                Invoke-RestMethod -Method Post -Uri "$BackendUrl/sign-agent/result" -Headers $Headers `
                    -ContentType 'application/json' `
                    -Body (@{ job_id = $job.job_id; signature_base64 = $signature; payload_sha256 = $localHash } | ConvertTo-Json)
                # payload не сохраняем дольше операции.
                Remove-Variable payload, signature -ErrorAction SilentlyContinue
            }
        }
    } catch {
        Write-Warning "iteration error: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds $PollSeconds
}
