import re

with open('e:\\duong tan khoa\\Bao_Gia_Jay_Home_Truc_Quan.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add <th> to header
header_target = '<th width="19%" class="text-right">Thành tiền (VNĐ)</th>'
header_replace = header_target + '\n                    <th width="5%" class="text-center print-hide">Xóa</th>'
content = content.replace(header_target, header_replace)

# Modify colspan="7" to colspan="8"
content = content.replace('colspan="7"', 'colspan="8"')

# Add delete button to all normal rows
# A normal row ends with: <td class="text-right amount">0</td>\n                </tr>
row_target = r'(<td class="text-right amount">[\d\.\,]*</td>\s*)</tr>'
btn_html = r'\1    <td class="text-center action-col print-hide"><button class="btn-delete" onclick="deleteRow(this)" title="Xóa" tabindex="-1" style="background:none; border:none; color:#ef4444; cursor:pointer;"><svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button></td>\n                </tr>'
content = re.sub(row_target, btn_html, content)

with open('e:\\duong tan khoa\\Bao_Gia_Jay_Home_Truc_Quan.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML modified successfully.")
