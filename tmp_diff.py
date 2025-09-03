import difflib
p1='tmp_export/export_email.html'
p2='tmp_export/export_email_fixed.html'
A=open(p1,encoding='utf-8',errors='ignore').read().splitlines()
B=open(p2,encoding='utf-8').read().splitlines()
ud=list(difflib.unified_diff(A[:400],B[:400],fromfile=p1,tofile=p2,lineterm=''))
for i,l in enumerate(ud):
    if i>200: break
    print(l)
print('...diff truncated...')
