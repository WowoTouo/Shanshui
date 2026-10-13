import re
from pathlib import Path
p=Path('D:/窝窝头的1.20.2整合包/Shanshui/.cloud/worker/worker.py')
s=p.read_text()
if 'def extract_tool_calls' in s: print('ALREADY'); exit()
a='def execute_shell(cmd: str) -> tuple[bool, str]:'
L=chr(60); G=chr(62); Q=chr(34)
f='''def extract_tool_calls(t):
 c=[]
 pat=L+'function name='+Q+'bash'+Q+G+'(.*?)'+L+'/function'+G
 for fn in re.findall(pat,t,flags=re.DOTALL):
  pat2=L+'parameter'+G+'(.*?)'+L+'/parameter'+G
  q=[x.strip() for x in re.findall(pat2,fn,flags=re.DOTALL) if x.strip()]
  if q: c.append(q[0] if len(q)==1 else ' && '.join(q))
 return c
def strip_tool_calls(t):
 t=re.sub(L+'seed:tool_call'+G+'.*?'+L+'/seed:tool_call'+G,'',t,flags=re.DOTALL)
 t=re.sub(L+'function name='+Q+'bash'+Q+G+'.*?'+L+'/function'+G,'',t,flags=re.DOTALL)
 return t.strip()
'''
s=s.replace(a,f+a,1)
p.write_text(s)
print('DONE')