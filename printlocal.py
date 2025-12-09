import win32print
import win32api
import win32con
import os

def listar_impressoras():
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    lista = []
    for idx, p in enumerate(printers):
        lista.append((idx + 1, p[2]))
    return lista

def consultar_fila(nome):
    hPrinter = win32print.OpenPrinter(nome)
    jobs = win32print.EnumJobs(hPrinter, 0, -1, 1)
    win32print.ClosePrinter(hPrinter)
    return jobs

def limpar_fila(nome):
    hPrinter = win32print.OpenPrinter(nome)
    jobs = win32print.EnumJobs(hPrinter, 0, -1, 1)
    for job in jobs:
        try:
            win32print.SetJob(hPrinter, job["JobId"], 0, None, win32print.JOB_CONTROL_DELETE)
        except:
            pass
    win32print.ClosePrinter(hPrinter)

def cancelar_job(nome, job_id):
    hPrinter = win32print.OpenPrinter(nome)
    win32print.SetJob(hPrinter, job_id, 0, None, win32print.JOB_CONTROL_DELETE)
    win32print.ClosePrinter(hPrinter)

def pausar_impressora(nome):
    h = win32print.OpenPrinter(nome)
    info = win32print.GetPrinter(h, 2)
    info['Status'] |= win32print.PRINTER_STATUS_PAUSED
    win32print.SetPrinter(h, 2, info, 0)
    win32print.ClosePrinter(h)

def retomar_impressora(nome):
    h = win32print.OpenPrinter(nome)
    info = win32print.GetPrinter(h, 2)
    info['Status'] &= ~win32print.PRINTER_STATUS_PAUSED
    win32print.SetPrinter(h, 2, info, 0)
    win32print.ClosePrinter(h)

def pausar_job(nome, job_id):
    h = win32print.OpenPrinter(nome)
    win32print.SetJob(h, job_id, 0, None, win32print.JOB_CONTROL_PAUSE)
    win32print.ClosePrinter(h)

def retomar_job(nome, job_id):
    h = win32print.OpenPrinter(nome)
    win32print.SetJob(h, job_id, 0, None, win32print.JOB_CONTROL_RESUME)
    win32print.ClosePrinter(h)

def tornar_padrao(nome):
    win32print.SetDefaultPrinter(nome)

def configurar_impressora(nome, papel="A4", bandeja=1, colorido=True):
    # ❗ Obs: Configurações variam por modelo. Aqui é apenas exemplo base.
    h = win32print.OpenPrinter(nome)
    devmode = win32print.GetPrinter(h, 2)["pDevMode"]

    devmode.PaperSize = 9  # A4
    devmode.DefaultSource = bandeja
    devmode.Color = 1 if colorido else 2

    win32print.DocumentProperties(None, h, nome, devmode, devmode, win32con.DM_IN_BUFFER | win32con.DM_OUT_BUFFER)
    win32print.ClosePrinter(h)

def menu():
    while True:
        print("""
1 - Consultar fila
2 - Limpar fila
3 - Cancelar job específico
4 - Pausar impressora
5 - Retomar impressora
6 - Pausar job
7 - Retomar job
9 - Tornar padrão
11 - Configurações (papel, bandeja, cor)
0 - Sair
""")

        opcao = input("Escolha: ")

        if opcao == "0":
            exit()

        printers = listar_impressoras()
        for idp, nome in printers:
            print(f"[{idp}] {nome}")
        pid = int(input("Escolha a impressora: "))
        nome = printers[pid - 1][1]

        if opcao == "1":
            jobs = consultar_fila(nome)
            print(jobs)

        elif opcao == "2":
            limpar_fila(nome)
            print("Fila limpa.")

        elif opcao == "3":
            job = int(input("ID do job: "))
            cancelar_job(nome, job)

        elif opcao == "4":
            pausar_impressora(nome)

        elif opcao == "5":
            retomar_impressora(nome)

        elif opcao == "6":
            job = int(input("ID do job: "))
            pausar_job(nome, job)

        elif opcao == "7":
            job = int(input("ID do job: "))
            retomar_job(nome, job)

        elif opcao == "9":
            tornar_padrao(nome)

        elif opcao == "11":
            configurar_impressora(nome)

        else:
            print("Opção inválida.")

menu()
