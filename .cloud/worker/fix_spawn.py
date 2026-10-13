from pathlib import Path
p=Path('D:/窝窝头的1.20.2整合包/Shanshui/.cloud/worker/worker.py')
s=p.read_text()
o='        proj, item = plan'
if o in s:
 s=s.replace(o,'        proj, item, sig = plan',1)
 p.write_text(s)
 print('SPAWN_FIXED')
else:
 print('NOT_FOUND')