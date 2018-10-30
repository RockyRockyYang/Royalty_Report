<#----------------------------------------------------#
 |             Delphi DUnitX Test Script              |
 |             -------------------------              |
 |                                                    |
 |       This script will run all DUnitX projects in  |
 |       your repository, capture their results, and  |
 |       publish those results to TFS.                |
 |                                                    |
 #----------------------------------------------------#>

function Modify-DUnitResults
{
    $currentTime = Get-Date -format "HH:mm:ss"
    $resultFile = get-childitem -path $binaryDirectory -filter 'dunitx-results.xml' -recurse
    $xmlResults = [xml](get-content $resultFile.FullName)
    $xmlResults."test-results".time = $currentTime.ToString()

    $xmlResults.Save($resultFile.FullName)
}

function Modify-TrxResults
{
    $computerName = $env:ComputerName
    $userName = $env:Username
    foreach($o in $input)
    {
        Write-host 'Updating:' $o.FullName
        $TmpFile = $o.FullName + ".tmp"

        get-content $o.FullName |
            %{$_ -replace "COMPUTERNAMENEEDED\\USERNAMENEEDED", "$computerName\$userName" } |
            %{$_ -replace "USERNAMENEEDED@COMPUTERNAMENEEDED", "$userName@$computerName" } | out-file $TmpFile -encoding utf8

         move-item $TmpFile $o.FullName -force

        $xmlResults = [xml](get-content $o.FullName)
        #$oldId = $xmlResults.TestRun.id
        #$newId = $oldId.Substring(0, 24)
        $newId = [guid]::NewGuid().ToString()

        $outDirectory = Split-Path $o.FullName
        $configurationFlavor = Split-Path $outDirectory -Leaf
        $configurationPlatform = Split-Path (Split-Path $outDirectory) -Leaf

        if ($configurationPlatform -eq "Win32")
        {
            $appendedId += "32"
        }
        elseif ($configurationPlatform -eq "Win64")
        {
            $appendedId += "64"
        }

        if ($configurationFlavor -eq "Release")
        {
            $appendedId += "ab"
        }
        elseif ($configurationFlavor -eq "Debug")
        {
            $appendedId += "cd"
        }

        $newId += $appendedId
        $xmlResults.TestRun.id = $newId

        $xmlResults.Save($o.FullName)
    }
}

function Modify-AllTrxResults
{
    get-childitem -path $binaryDirectory -filter "*.trx" -recurse | Modify-TrxResults;
}

#$o is the dpr file retrieved from Check-ProjectForTests
function Create-TrxResult($o, $exeFile)
{
    $dunitResult = get-childitem -path $binaryDirectory -filter 'dunitx-results.xml' -recurse
    $dunitResult = $dunitResult.FullName
    $pathToXslt = "C:\installs\Delphi\nxslt3\NUnitToMSTest.xslt"

    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($o.FullName)
    $outputPath = Split-Path $exeFile.FullName

    & "C:\installs\Delphi\nxslt3\nxslt3.exe" $dunitResult $pathToXslt -o "$outputPath\$fileName.trx"

    rm $dunitResult
}

function Check-ProjectForTests
{
    foreach($o in $input)
    {
        $dprName = $o.name
        #Checking if its a DUnitX test by checking for Key words.
        #If it has a Test runner and a DUnit Logger, then it MUST be a test, otherwise there is no reason for having both.
        if($dprName.Contains('Test') -or $dprName.Contains('test'))
        {
            $fileName = [System.IO.Path]::GetFileNameWithoutExtension($o.FullName)
            $fileName = "$fileName.exe"
            $exeFile = get-childitem -path $binaryDirectory -filter $fileName -recurse
            $oldPath = $pwd

            foreach($project in $exeFile)
            {
			          Write-Host $project.FullName
                Write-Host "Running $project for test execution."
				        cd $project.DirectoryName
                & $project.FullName
                Modify-DUnitResults
                Create-TrxResult $o $project
				        cd $oldPath
            }
        }
    }
}

function Run-AllTests
{
    get-childitem -path $sourceDirectory -Include *.dpr -recurse | Check-ProjectForTests;
}

function Publish-TrxResults
{
    $buildNumber = $Env:TF_BUILD_BUILDNUMBER

    $buildCollectionUri = $Env:TF_BUILD_COLLECTIONURI
    $publishUri = $buildCollectionUri
    # -split "/tfs/"
    #$publishUri = $publishUri[0]
    #$publishUri += "/tfs"

    $buildDirectory = $Env:TF_BUILD_BUILDDIRECTORY
    $teamProjectName = Split-Path (Split-Path $buildDirectory) -Leaf

    foreach($o in $input)
    {
        $outDirectory = Split-Path $o.FullName
        $configurationFlavor = Split-Path $outDirectory -Leaf
        $configurationPlatform = Split-Path (Split-Path $outDirectory) -Leaf
        $resultFile = $o.FullName

        Write-Host "Publishing $resultFile to $publishUri with BuildNumber: $buildNumber, and configuration $configurationPlatform|$configurationFlavor."
        & "C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\IDE\mstest.exe" /publish:$publishUri /publishbuild:$buildNumber /PublishResultsFile:$resultFile /teamproject:$teamProjectName /platform:$configurationPlatform /flavor:$configurationFlavor
    }
}

function Publish-AllTrxResults
{
    get-childitem -path $binaryDirectory -filter '*.trx' -recurse | Publish-TrxResults;
}

function Check-TestResult
{
    foreach($o in $input)
    {
        $trxContent = [string](get-content $o.FullName)
        if($trxContent.Contains('outcome="Failed"'))
        {
            Write-Error "There are failed tests"
            exit 1
        }
    }
}

function Check-AllTestResult
{
    get-childitem -path $binaryDirectory -filter '*.trx' -recurse | Check-TestResult;
}

$binaryDirectory = $Env:TF_BUILD_BINARIESDIRECTORY

$sourceDirectory = $Env:TF_BUILD_SOURCESDIRECTORY

Run-AllTests
Modify-AllTrxResults
Publish-AllTrxResults

Check-AllTestResult
