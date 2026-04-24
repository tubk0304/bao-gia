$path = 'E:\CLOUD\VS Code\Bao_gia_nhanh\Bao_Gia_Jay_Home_Truc_Quan.html'
$lines = Get-Content -Path $path -Encoding UTF8

$lines[1167] = "                                '<td><div class=""editable-cell"" contenteditable=""true"" spellcheck=""false"">' + (p.brand || '-') + '</div></td>' +"
$lines[1168] = "                                '<td class=""text-center"">Cai</td>' +"
$lines[1169] = "                                '<td class=""text-center""><input type=""number"" min=""0"" class=""qty"" value=""1""></td>' +"
$lines[1170] = "                                '<td class=""text-right""><input type=""number"" min=""0"" class=""price"" value=""' + (p.sell_price || 0) + '""></td>' +"
$lines[1171] = "                                '<td class=""text-right amount"">0</td>' +"
$lines[1172] = "                                '<td class=""text-center action-col""><button class=""btn-delete"" onclick=""deleteRow(this)"" title=""XÃ³a"" tabindex=""-1""><svg width=""18"" height=""18"" fill=""none"" stroke=""currentColor"" viewBox=""0 0 24 24""><path stroke-linecap=""round"" stroke-linejoin=""round"" stroke-width=""2"" d=""M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16""></path></svg></button></td>';"

[System.IO.File]::WriteAllLines($path, $lines, [System.Text.UTF8Encoding]::new($false))
