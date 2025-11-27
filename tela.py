import customtkinter as ctk
from tkinter import messagebox
from snmp import coleta_dados, canon, richo, epson
import json
import os

# Aparência
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Arquivo para salvar impressoras
ARQUIVO_IMPRESSORAS = "impressoras.json"

# Carrega impressoras do arquivo
if os.path.exists(ARQUIVO_IMPRESSORAS):
    with open(ARQUIVO_IMPRESSORAS, "r") as f:
        impressoras_cadastradas = json.load(f)
else:
    impressoras_cadastradas = []

# --- Tela de Cadastro --- #
class CadastroImpressora(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Cadastro de Impressora")
        self.geometry("400x300")

        self.label_ip = ctk.CTkLabel(self, text="IP da Impressora:")
        self.label_ip.pack(pady=(20,5))
        self.entry_ip = ctk.CTkEntry(self, width=200)
        self.entry_ip.pack()

        self.label_marca = ctk.CTkLabel(self, text="Marca da Impressora:")
        self.label_marca.pack(pady=(20,5))
        self.combo_marca = ctk.CTkComboBox(self, values=["Canon","Richo","Epson"])
        self.combo_marca.pack()

        self.btn_testar = ctk.CTkButton(self, text="Testar Conexão", command=self.testar_conexao)
        self.btn_testar.pack(pady=10)

        self.btn_salvar = ctk.CTkButton(self, text="Salvar", command=self.salvar_impressora)
        self.btn_salvar.pack(pady=10)

    def testar_conexao(self):
        ip = self.entry_ip.get()
        marca_str = self.combo_marca.get()
        if not ip or not marca_str:
            messagebox.showerror("Erro", "Preencha IP e Marca")
            return
        impressora = self.get_dicionario_marca(marca_str)
        try:
            dados = coleta_dados(ip, impressora)
            messagebox.showinfo("Sucesso", f"Conexão OK!\nContador: {dados['contador']}\nToner: {dados['nivel_toner']}%")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na conexão: {e}")

    def salvar_impressora(self):
        ip = self.entry_ip.get()
        marca_str = self.combo_marca.get()
        if not ip or not marca_str:
            messagebox.showerror("Erro", "Preencha IP e Marca")
            return
        impressoras_cadastradas.append({"ip": ip, "marca": marca_str})
        with open(ARQUIVO_IMPRESSORAS, "w") as f:
            json.dump(impressoras_cadastradas, f, indent=4)
        self.master.atualizar_lista()
        self.destroy()

    def get_dicionario_marca(self, marca_str):
        if marca_str.lower() == "canon":
            return canon
        elif marca_str.lower() == "richo":
            return richo
        elif marca_str.lower() == "epson":
            return epson
        else:
            raise ValueError("Marca inválida")


# --- Tela Principal --- #
class PrinterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Monitor de Impressoras SNMP")
        self.geometry("700x500")

        self.label = ctk.CTkLabel(self, text="Impressoras Cadastradas:")
        self.label.pack(pady=(10,5))

        # Scroll frame para mostrar impressoras como painel do Windows
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=650, height=300)
        self.scroll_frame.pack(pady=10)

        self.btn_cadastrar = ctk.CTkButton(self, text="Cadastrar Impressora", command=self.abrir_cadastro)
        self.btn_cadastrar.pack(pady=10)

        self.output_text = ctk.CTkTextbox(self, width=650, height=120)
        self.output_text.pack(pady=10)

        self.atualizar_lista()

    def atualizar_lista(self):
        # Limpa scroll frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for imp in impressoras_cadastradas:
            card = ctk.CTkFrame(self.scroll_frame, width=600, height=60, corner_radius=10)
            card.pack(pady=5, padx=10, fill="x")

            lbl = ctk.CTkLabel(card, text=f"{imp['marca']} - {imp['ip']}", anchor="w")
            lbl.pack(side="left", padx=10, pady=10, fill="x", expand=True)

            btn_consultar = ctk.CTkButton(card, text="Consultar", width=100,
                                           command=lambda ip=imp['ip'], marca=imp['marca']: self.consultar_impressora(ip, marca))
            btn_consultar.pack(side="right", padx=10, pady=10)

    def abrir_cadastro(self):
        CadastroImpressora(self)

    def consultar_impressora(self, ip, marca):
        # Pega o dicionário certo
        if marca.lower() == "canon":
            impressora = canon
        elif marca.lower() == "richo":
            impressora = richo
        else:
            impressora = epson
        try:
            dados = coleta_dados(ip, impressora)
            self.output_text.delete("0.0", ctk.END)
            for k,v in dados.items():
                self.output_text.insert(ctk.END, f"{k}: {v}\n")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao coletar dados: {e}")


if __name__ == "__main__":
    app = PrinterApp()
    app.mainloop()
