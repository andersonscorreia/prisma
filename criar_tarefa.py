import os
import subprocess
import sys
import getpass
import ctypes


def pedir_admin():
    """Relança o script como administrador."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Solicitando permissão de administrador...")
        params = " ".join(sys.argv)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()


def criar_tarefa_agendada(script_principal):
    usuario = getpass.getuser()

    print("\n=== Criando Tarefa Agendada ===")
    print(f"Usuário: {usuario}")
    print(f"Script principal: {script_principal}")

    if not os.path.exists(script_principal):
        print("❌ ERRO: O arquivo do script principal não foi encontrado!")
        return

    nome_tarefa = "GerenciadorImpressorasAdmin"

    comando = [
        "schtasks", "/create",
        "/tn", nome_tarefa,
        "/tr", f'"{sys.executable}" "{script_principal}"',
        "/sc", "onlogon",
        "/rl", "highest",
        "/f"
    ]

    print("\nExecutando comando:")
    print(" ".join(comando))

    resultado = subprocess.run(comando, capture_output=True, text=True)

    if resultado.returncode != 0:
        print("\n❌ ERRO AO CRIAR TAREFA:")
        print(resultado.stderr)
    else:
        print("\n✅ Tarefa criada com sucesso!")
        print(f"Execute pelo outro script usando:\n")
        print(f'   schtasks /run /tn "{nome_tarefa}"\n')


if __name__ == "__main__":
    pedir_admin()
    script = r"C:\Users\Admin\Documents\GitHub\PRISMA\printlocal.py"
    criar_tarefa_agendada(script)
