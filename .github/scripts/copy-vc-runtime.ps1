param(
    [string]$Path = ".",
    [object]$Extensions = @(".exe", ".dll"),
    [object]$AdditionalDirs
)

$ErrorActionPreference = "Stop"

# Ensure we are running inside a properly initialized MSVC environment.
if (-not $env:VCToolsRedistDir -or -not $env:VSCMD_ARG_TGT_ARCH) {
    throw "MSVC environment is not initialized (Developer Command Prompt required)"
}

# Converts a string separated by commas or newlines into an array.
function ConvertTo-StringArray {
    param([object]$Value)

    if ($null -eq $Value) {
        return @()
    }

    # Already an array (PowerShell-native usage)
    if ($Value -is [System.Array]) {
        return $Value | Where-Object { $_ -and $_.Trim() -ne "" }
    }

    # Normalize string input (newline or comma separated)
    $text = $Value.ToString()

    return $text -split "[`r`n,]" |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -ne "" }
}

# Extract dependent DLLs using dumpbin.
function Get-Dependencies {
    param([string]$Exe)

    $out = & dumpbin /dependents $Exe

    $dlls = @()
    foreach ($l in $out) {
        if ($l -match "^\s+([a-zA-Z0-9_\-\.]+\.dll)$") {
            $dlls += $matches[1]
        }
    }
    return $dlls
}

# --- Main execution ---

$runtimeDir = Join-Path $env:VCToolsRedistDir $env:VSCMD_ARG_TGT_ARCH

Write-Host "Searching for VC++ runtime DLLs in $runtimeDir"

$runtimeDlls = @{}
Get-ChildItem -Path $runtimeDir -Recurse -Filter "*.dll" | ForEach-Object {
    $name = $_.Name.ToLower()
    if (-not $runtimeDlls.ContainsKey($name)) {
        $runtimeDlls[$name] = $_
    }
}

$count = $runtimeDlls.Count
Write-Host "::group::Found $count VC++ runtime DLL(s)"
$runtimeDlls.Values | Sort-Object -Property FullName | ForEach-Object {
    Write-Host $_.FullName
}
Write-Host "::endgroup::"


$dirs = @($Path)
$dirs += ConvertTo-StringArray $AdditionalDirs
$dirs = $dirs | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique

$exts = ConvertTo-StringArray $Extensions | ForEach-Object { "*" + $_.ToLower() }

$dependentDlls = New-Object System.Collections.Generic.HashSet[string]
foreach ($dir in $dirs) {
    Write-Host "::group::Scanning $dir for dependencies"
    Get-ChildItem -Path $dir -File -Recurse -Include $exts -ErrorAction SilentlyContinue | ForEach-Object {
        $file = $_.FullName
        Write-Host "Analyzing dependencies of $file" 
        $deps = Get-Dependencies $file
        foreach ($dep in $deps) {
            $name = $dep.ToLower()
            if (-not $dependentDlls.Contains($name)) {
                $dependentDlls.Add($name) | Out-Null
            }
        }
    }
    Write-Host "::endgroup::"
}

$count = $dependentDlls.Count
Write-Host "::group::Found $count dependencies"
$dependentDlls | Sort-Object | ForEach-Object {
    Write-Host $_
}
Write-Host "::endgroup::"

Write-Host "Copying required VC++ runtime DLLs"

$count = 0
foreach ($depDll in $dependentDlls) {
    if ($runtimeDlls.Contains($depDll)) {
        $runDll = $runtimeDlls[$depDll]
        Write-Host "Copying $($runDll.Name)"
        Copy-Item $runDll.FullName -Destination $Path -Force
        $count += 1
    }
}

Write-Host "Copied $count DLL(s)"
