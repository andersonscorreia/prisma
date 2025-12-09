import subprocess

subprocess.run('schtasks /run /tn "GerenciadorImpressorasAdmin"', shell=True)
