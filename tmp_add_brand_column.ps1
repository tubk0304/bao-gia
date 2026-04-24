$path = 'E:\CLOUD\VS Code\Bao_gia_nhanh\Bao_Gia_Jay_Home_Truc_Quan.html'
$text = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

$helper = @'
        function createQuoteRowHtml(product = {}) {
            const sku = product.sku || '-';
            const description = product.description || 'Thiet bi moi';
            const brand = product.brand || '-';
            const unit = product.unit || 'Cai';
            const qty = product.qty ?? 1;
            const price = product.price ?? product.sell_price ?? 0;

            return `
                <td class="text-center"></td>
                <td><div class="editable-cell" contenteditable="true" spellcheck="false">${sku}</div></td>
                <td><div class="editable-cell" contenteditable="true" spellcheck="false">${description}</div></td>
                <td><div class="editable-cell" contenteditable="true" spellcheck="false">${brand}</div></td>
                <td class="text-center">${unit}</td>
                <td class="text-center"><input type="number" min="0" class="qty" value="${qty}"></td>
                <td class="text-right"><input type="number" min="0" class="price" value="${price}"></td>
                <td class="text-right amount">0</td>
                <td class="text-center action-col">
                    <button class="btn-delete" onclick="deleteRow(this)" title="Xoa" tabindex="-1">
                        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </td>
            `;
        }
'@

$text = [regex]::Replace($text, 'function deleteRow\(btn\) \{', "$helper`r`n        function deleteRow(btn) {", 1)

$text = [regex]::Replace($text, '(?s)function addRow\(\) \{.*?calculate\(\);\}', @'
function addRow() {
            const tbody = document.getElementById('quote-body');
            const tr = document.createElement('tr');
            tr.innerHTML = createQuoteRowHtml();
            tbody.appendChild(tr);
            calculate();}
'@, 1)

$text = $text -replace '<td colspan="8">', '<td colspan="9">'
$text = $text -replace 'cTd\.colSpan = 8;', 'cTd.colSpan = 9;'

$text = [regex]::Replace($text, '(?s)function addRowToCategory\(btn\) \{.*?calculate\(\);\}', @'
function addRowToCategory(btn) {
            const currentCatRow = btn.closest('tr.category-row');
            let nextRow = currentCatRow.nextElementSibling;
            while(nextRow && !nextRow.classList.contains('category-row')) {
                nextRow = nextRow.nextElementSibling;
            }
            
            const tbody = document.getElementById('quote-body');
            const tr = document.createElement('tr');
            tr.innerHTML = createQuoteRowHtml();
            
            if(nextRow) {
                tbody.insertBefore(tr, nextRow);
            } else {
                tbody.appendChild(tr);
            }
            
            calculate();}
'@, 1)

$text = $text -replace 'if\(tds\.length >= 6\)', 'if(tds.length >= 7)'
$text = $text -replace "const isDesc = e.target === tds\[2\]\.querySelector\('\.editable-cell'\);", "const isDesc = e.target === tds[2].querySelector('.editable-cell');`r`n                        const isBrand = e.target === tds[3].querySelector('.editable-cell');"
$text = $text -replace 'if\(isSku \|\| isDesc\)', 'if(isSku || isDesc || isBrand)'
$text = $text -replace "tds\[2\]\.querySelector\('\.editable-cell'\)\.textContent = item\.description;\s*const priceInput = tds\[5\]\.querySelector\('\.price'\);", "tds[2].querySelector('.editable-cell').textContent = item.description;`r`n                                            tds[3].querySelector('.editable-cell').textContent = item.brand || '-';`r`n                                            const priceInput = tds[6].querySelector('.price');"

$text = [regex]::Replace($text, '(?s)window\.insertProductFromPicker = function\(p\) \{.*?setTimeout\(\(\) => msg\.remove\(\), 2000\);\s*\};', @'
window.insertProductFromPicker = function(p) {
                if(!window.activeCategoryRow) return;
                
                let nextRow = window.activeCategoryRow.nextElementSibling;
                while(nextRow && !nextRow.classList.contains('category-row')) {
                    nextRow = nextRow.nextElementSibling;
                }
                
                const tr = document.createElement('tr');
                tr.innerHTML = createQuoteRowHtml(p);
                
                const tbody = document.getElementById('quote-body');
                if(nextRow) {
                    tbody.insertBefore(tr, nextRow);
                } else {
                    tbody.appendChild(tr);
                }
                
                calculate();
                const msg = document.createElement('div');
                msg.textContent = 'Inserted: ' + (p.sku || p.description);
                msg.style.cssText = 'position:fixed; bottom:20px; right:20px; background:#10b981; color:white; padding:10px 20px; border-radius:6px; z-index:10001; font-family: Inter, sans-serif; font-size: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);';
                document.body.appendChild(msg);
                setTimeout(() => msg.remove(), 2000);
            };
'@, 1)

$text = $text -replace 'catTr\.innerHTML = ''<td colspan="8">', 'catTr.innerHTML = ''<td colspan="9">'
$text = $text -replace "'<td><div class=""editable-cell"" contenteditable=""true"" spellcheck=""false"">' \+ \(p\.description \|\| 'Sáº£n pháº©m'\) \+ '</div></td>' \+\s*'<td class=""text-center"">CÃ¡i</td>' \+", "'<td><div class=""editable-cell"" contenteditable=""true"" spellcheck=""false"">' + (p.description || 'San pham') + '</div></td>' +`r`n                                '<td><div class=""editable-cell"" contenteditable=""true"" spellcheck=""false"">' + (p.brand || '-') + '</div></td>' +`r`n                                '<td class=""text-center"">Cai</td>' +"

$text = [regex]::Replace($text, "document\.addEventListener\('DOMContentLoaded', \(\) => \{", @'
document.addEventListener('DOMContentLoaded', () => {
            const theadTr = document.querySelector('table thead tr');
            if (theadTr && !theadTr.dataset.brandReady) {
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
                    <th width="5%" class="text-center print-hide">Xoa</th>`;
            }
'@, 1)

[System.IO.File]::WriteAllText($path, $text, [System.Text.UTF8Encoding]::new($false))
