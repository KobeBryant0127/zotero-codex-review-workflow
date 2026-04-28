# Check whether Word and Zotero-related processes/add-ins are available on Windows.
Write-Host "== Running processes containing zotero or winword =="
Get-Process | Where-Object { $_.ProcessName -match 'zotero|winword' } | Select-Object ProcessName,Id,Path | Format-Table -AutoSize

Write-Host "`n== Word COM add-ins =="
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $true
    foreach($a in $word.AddIns){
        [pscustomobject]@{Name=$a.Name; Installed=$a.Installed; Path=$a.Path}
    } | Format-Table -AutoSize
    $word.Quit()
} catch {
    Write-Error "Cannot start Microsoft Word via COM. Is Word installed? $_"
}
