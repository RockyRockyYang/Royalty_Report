param(
  [string]$v,
  [string]$r,
  [string]$f,
  [string]$ismFile
)

$arch = $env:Processor_Architecture
Write-Host 'Architecture: ' $arch
Write-Host 'InstallShield project file:' $ismFile

if (-not($arch.Equals('x86')))
{ 
    Write-Error 'Not running on the correct Architecture'
    return $false
}

Write-Host 'Updating ' $ismFile

if (-not $ismFile)
{
    Write-Error 'ismFile is a required Parameter'
    return $false
}

if (-not $v)
{
    Write-Error 'v is a required Parameter'
    return $false
}

if (-not $r)
{
    Write-Error 'r is a required Parameter'
    return $false
}

if (-not $f)
{
    Write-Error 'f is a required Parameter'
    return $false
}

if (-not (Test-Path $ismFile))
{
    $msg = 'cannot find product specific InstallShield script:' + $ismFile
    Write-Error $msg
    return $false
}

Get-Item -Path $ismFile |
    Set-ItemProperty -Name IsReadOnly -Value $false

$installShield = new-object -comobject IswiAuto22.ISWiProject

if (!$installShield)
{
    Write-Error 'Unable to Create InstallShield Automation Object'
    return $false
}

$installShield.OpenProject($ismFile)
$productVersion = $v + '.' + $r + '.' + $f
Write-Host 'productVersion' $productVersion
$installShield.ProductVersion = $productVersion
$installShield.SaveProject()
$installShield.CloseProject()

return $true
