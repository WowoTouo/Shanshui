#!/usr/bin/env python3
import re
from pathlib import Path
P=Path('/home/agent/worker/worker.py')
s=P.read_text()
c=0
if 'def extract_tool_calls' not in s:
 a='def execute_shell(cmd: str) -> tuple[bool, str]:'
 if s.count(a)!=1: raise SystemExit('A1')
 f='''
def extract_tool_calls(t): cmds=[]
