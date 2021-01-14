import os
import subprocess
import smb_settings
from .smb_settings import smb


def mkdir(name):
	if ' ' in name or len(name) == 0: return False
	cmd = smb + ['"mkdir ' + name +'"']
	print('executing command:',' '.join(cmd))
	out = subprocess.check_output(cmd)
	return out


