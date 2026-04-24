$path = "E:\CLOUD\VS Code\Bao_gia_nhanh\Bao_Gia_Jay_Home_Truc_Quan.html"
$content = Get-Content -Path $path -Raw

$brokenDomBlock = @'
        document.addEventListener('DOMContentLoaded', () => {
            const theadTr = document.querySelector('table thead tr');
            if (theadTr) {
                theadTr.dataset.brandReady = '1';
                theadTr.innerHTML = 
                    <th width="4%" class="text-center">STT</th>
                    <th width="11%">Ma SP</th>
                    <th width="28%">Loai thiet bi / Dien giai</th>
                    <th width="11%">Thuong hieu</th>
                    <th width="6%" class="text-center">DVT</th>
                    <th width="10%" class="text-center">So luong</th>
                    <th width="14%" class="text-right">Don gia (VND)</th>
                    <th width="15%" class="text-right">Thanh tien (VND)</th>
                    <th width="5%" class="text-center print-hide action-col">Xoa</th>;
            }

            const trs = document.querySelectorAll('#quote-body tr');
'@
$fixedDomBlock = @'
        document.addEventListener('DOMContentLoaded', () => {
            const theadTr = document.querySelector('table thead tr');
            if (theadTr) {
                theadTr.dataset.brandReady = '1';
                theadTr.innerHTML = `
                    <th width="4%" class="text-center">STT</th>
                    <th width="11%">Ma SP</th>
                    <th width="28%">Loai thiet bi / Dien giai</th>
                    <th width="11%">Thuong hieu</th>
                    <th width="6%" class="text-center">DVT</th>
                    <th width="10%" class="text-center">So luong</th>
                    <th width="14%" class="text-right">Don gia (VND)</th>
                    <th width="15%" class="text-right">Thanh tien (VND)</th>
                    <th width="5%" class="text-center print-hide action-col">Xoa</th>`;
            }

            const trs = document.querySelectorAll('#quote-body tr');
'@
$content = $content.Replace($brokenDomBlock, $fixedDomBlock)

$adminOldBlock = @'
                        prods.forEach(p => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = '<td class="text-center"></td>' +
                                '<td><div class="editable-cell" contenteditable="true" spellcheck="false">' + (p.sku || '-') + '</div></td>' +
                                '<td><div class="editable-cell" contenteditable="true" spellcheck="false">' + (p.description || 'Sáº£n pháº©m') + '</div></td>' +
                                '<td><div class="editable-cell" contenteditable="true" spellcheck="false">' + (p.brand || '-') + '</div></td>' +
                                '<td class="text-center">Cai</td>' +
                                '<td class="text-center"><input type="number" min="0" class="qty" value="1"></td>' +
                                '<td class="text-right"><input type="number" min="0" class="price" value="' + (p.sell_price || 0) + '"></td>' +
                                '<td class="text-right amount">0</td>' +
                                '<td class="text-center action-col"><button class="btn-delete" onclick="deleteRow(this)" title="XÃƒÆ’Ã‚Â³a" tabindex="-1"><svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button></td>';
                        });
'@
$adminNewBlock = @'
                        prods.forEach(p => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = '<td class="text-center"></td>' +
                                '<td><div class="editable-cell" contenteditable="true" spellcheck="false">' + (p.sku || '-') + '</div></td>' +
                                '<td><div class="editable-cell" contenteditable="true" spellcheck="false">' + (p.description || 'Sáº£n pháº©m') + '</div></td>' +
                                '<td><div class="editable-cell" contenteditable="true" spellcheck="false">' + (p.brand || '-') + '</div></td>' +
                                '<td class="text-center">Cai</td>' +
                                '<td class="text-center"><input type="number" min="0" class="qty" value="1"></td>' +
                                '<td class="text-right"><input type="number" min="0" class="price" value="' + (p.sell_price || 0) + '"></td>' +
                                '<td class="text-right amount">0</td>' +
                                '<td class="text-center action-col"><button class="btn-delete" onclick="deleteRow(this)" title="XÃƒÆ’Ã‚Â³a" tabindex="-1"><svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button></td>';
                            tbody.appendChild(tr);
                        });
'@
$content = $content.Replace($adminOldBlock, $adminNewBlock)

$adminPattern = "(?s)(                        prods\.forEach\(p => \{\r?\n                            const tr = document\.createElement\('tr'\);\r?\n.*?'<td class=""text-center action-col""><button class=""btn-delete"" onclick=""deleteRow\(this\)"" title=""XÃƒÆ’Ã‚Â³a"" tabindex=""-1""><svg width=""18"" height=""18"" fill=""none"" stroke=""currentColor"" viewBox=""0 0 24 24""><path stroke-linecap=""round"" stroke-linejoin=""round"" stroke-width=""2"" d=""M19 7l-\.867 12\.142A2 2 0 0116\.138 21H7\.862a2 2 0 01-1\.995-1\.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16""></path></svg></button></td>';\r?\n)(                        \}\);)"
$content = [regex]::Replace($content, $adminPattern, '$1                            tbody.appendChild(tr);`r`n$2', 1)

$lines = [System.Collections.Generic.List[string]]::new()
$lines.AddRange([string[]]($content -split "`r?`n"))
$inAdminImport = $false
$inserted = $false
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match "prods\.forEach\(p => \{") {
        $inAdminImport = $true
    }
    if ($inAdminImport -and $lines[$i].Trim() -eq '});') {
        $prevLine = if ($i -gt 0) { $lines[$i - 1] } else { '' }
        if ($prevLine -match 'action-col' -and $prevLine -notmatch 'tbody\.appendChild\(tr\);') {
            $lines.Insert($i, '                            tbody.appendChild(tr);')
            $inserted = $true
            break
        }
    }
}
if ($inserted) {
    $content = [string]::Join("`r`n", $lines)
}

Set-Content -Path $path -Value $content -NoNewline
