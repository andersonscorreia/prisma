#pip install pywin32
import win32print

def listar_impressoras_windows():
    """Lista todas as impressoras instaladas no Windows."""
    try:
        impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        nomes_impressoras = [impressora[2] for impressora in impressoras]
        return nomes_impressoras
    except Exception as e:
        print(f"Ocorreu um erro ao listar as impressoras: {e}")
        return []

if __name__ == "__main__":
    print("Impressoras instaladas no Windows:")
    for impressora in listar_impressoras_windows():
        print(impressora)