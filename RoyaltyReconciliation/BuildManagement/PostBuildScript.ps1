<#-----------------------------------------------------------#
 |                    Postbuild Script                       |
 |                      DO NOT EDIT                          |
 #-----------------------------------------------------------#>
param(
    [string]$buildConfig = 'Release',
    [string]$isvNextBuildStr = 'Not Set'
)

Invoke-Expression "c:\BuildManagement\Scripts\IMOPostTestScript.ps1 $buildConfig $isvNextBuildStr"
