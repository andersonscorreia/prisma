import customtkinter as ctk
from tkinter import messagebox
import json
import os

from snmp import coleta_dados, canon, richo, epson_color


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ARQUIVO_IMPRESSORAS = "impressoras.json"


# ============================================================
# Funções auxiliares
# ============================================================

def carregar_impressoras():
    if os.path.exists(ARQUIVO_IMPRESSORAS):
        with open(ARQUIVO_IMPRESSORAS, "r") as f:
            return json.load(f)
    return []


def salvar_impressoras(lista):
    with open(ARQUIVO_IMPRESSORAS, "w") as f:
        json.dump(lista, f, indent=4)


# ============================================================
# Barra visual de TONER / MANUTENÇÃO
# ============================================================

class TonerBar(ctk.CTkFrame):
    def __init__(self, master, cor_nome, nivel):
        super().__init__(master, fg_color="transparent")

        cores = {
            "bk": "#000000",
            "c":  "#0095FF",
            "m":  "#FF00AA",
            "y":  "#FFD300",
            "🛠️": "#FF8800"
        }

        # Nome da cor
        ctk.CTkLabel(
            self, 
            text=f"{cor_nome.upper()}:", 
            width=60
        ).pack(side="left", padx=5)

        # Barra
        barra = ctk.CTkProgressBar(self, width=155, height=10, corner_radius=5)
        barra.pack(side="left", padx=5)

        try:
            valor = float(nivel) / 100
        except:
            valor = 0

        barra.set(max(0, min(valor, 1)))
        barra.configure(progress_color=cores.get(cor_nome, "#AAAAAA"))

        # Porcentagem grande e destacada
        ctk.CTkLabel(
            self,
            text=f"{nivel}%",
            width=55,
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF"
        ).pack(side="left", padx=(10, 0))


# ============================================================
# CARD DA IMPRESSORA
# ============================================================

from PIL import Image

class CardImpressora(ctk.CTkFrame):
    CARD_WIDTH = 400
    CARD_HEIGHT = 320

    def __init__(self, master, app, impressora):
        super().__init__(
            master,
            width=self.CARD_WIDTH,
            height=self.CARD_HEIGHT,
            corner_radius=15,
            fg_color="#1f1f1f"
        )

        self.grid_propagate(False)
        self.pack_propagate(False)

        self.app = app
        self.impressora = impressora
        self.ip = impressora["ip"]
        self.marca = impressora["marca"]
        self.nome = impressora["nome"]

        # -------------------------
        # IMAGEM PNG CENTRALIZADA
        # -------------------------
        img_frame = ctk.CTkFrame(self, fg_color="transparent")
        img_frame.pack(pady=(8, 4), fill="x")

        try:
            self.img = ctk.CTkImage(
                light_image=Image.open("icons/impressora.png"),  # caminho correto
                size=(70, 70)
            )

            ctk.CTkLabel(img_frame, image=self.img, text="").pack(anchor="center")

        except Exception as e:
            print("Erro ao carregar imagem:", e)
            ctk.CTkLabel(
                img_frame, text="🖨️", font=("Arial", 40)
            ).pack(anchor="center")

        # Nome da impressora
        ctk.CTkLabel(
            self,
            text=self.nome,
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 4))

        # Área de toner
        toner_area = ctk.CTkFrame(self, fg_color="#262626", corner_radius=12)
        toner_area.pack(pady=5, padx=12, fill="x")

        try:
            dados = coleta_dados(self.ip, self.get_dic())
            toners = dados.get("toner", {})

            if not toners:
                ctk.CTkLabel(toner_area, text="Sem dados SNMP", text_color="red").pack()
            else:
                ordem = ["bk", "c", "m", "y"]
                for cor in ordem:
                    if cor in toners:
                        TonerBar(toner_area, cor, toners[cor]).pack(
                            anchor="w", pady=2, padx=8
                        )

                # Caixa de manutenção
                manut = (
                    dados.get("manutencao")
                    or toners.get("manutencao")
                    or toners.get("maintenance")
                )

                if manut is not None:
                    TonerBar(toner_area, "🛠️", manut).pack(
                        anchor="w", pady=2, padx=8
                    )

        except Exception as e:
            print("Erro SNMP:", e)
            ctk.CTkLabel(
                toner_area, text="Falha na coleta SNMP", text_color="red"
            ).pack()

    # -------------------------
    # RETORNA O DICIONÁRIO SNMP CORRETO
    # -------------------------
    def get_dic(self):
        m = self.marca.lower()
        if m == "canon":
            return canon
        if m == "richo":
            return richo
        return epson_color
# ============================================================
# HOME
# ============================================================

class FrameHome(ctk.CTkFrame):

    def __init__(self, app, parent):
        super().__init__(parent)
        self.app = app

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", pady=(10, 5))

        ctk.CTkLabel(topo, text="Impressoras", font=("Arial", 25, "bold")).pack(side="left", padx=20)

        # BOTÃO ATUALIZAR TUDO
        ctk.CTkButton(
            topo,
            text="🔄 Atualizar Tudo",
            width=150,
            fg_color="#2a80ff",
            command=self.atualizar_lista
        ).pack(side="right", padx=20)

        self.scroll = ctk.CTkScrollableFrame(self, width=900, height=420)
        self.scroll.pack(pady=10)

    def atualizar_lista(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        colunas = 3
        for i, imp in enumerate(self.app.impressoras):
            card = CardImpressora(self.scroll, self.app, imp)
            card.grid(row=i // colunas, column=i % colunas, padx=15, pady=15)


# ============================================================
# CADASTRO
# ============================================================

class FrameCadastro(ctk.CTkFrame):
    def __init__(self, app, parent):
        super().__init__(parent)
        self.app = app

        ctk.CTkLabel(self, text="Cadastrar Impressora", font=("Arial", 22, "bold")).pack(pady=20)

        self.entry_nome = ctk.CTkEntry(self, width=300, placeholder_text="Nome (ex: Recepção)")
        self.entry_nome.pack(pady=10)

        self.entry_ip = ctk.CTkEntry(self, width=300, placeholder_text="IP da impressora")
        self.entry_ip.pack(pady=10)

        self.combo_marca = ctk.CTkComboBox(self, values=["Canon", "Richo", "Epson Color"], width=300)
        self.combo_marca.pack(pady=10)

        ctk.CTkButton(self, text="Testar Conexão", command=self.testar).pack(pady=10)
        ctk.CTkButton(self, text="Salvar Impressora", command=self.salvar).pack(pady=10)

    def get_dic(self, marca):
        marca = marca.lower()
        if marca == "canon":
            return canon
        if marca == "richo":
            return richo
        return epson_color

    def testar(self):
        try:
            dic = self.get_dic(self.combo_marca.get())
            dados = coleta_dados(self.entry_ip.get(), dic)
            messagebox.showinfo("Conectada!", f"Serial: {dados['numero_serie']}")
        except:
            messagebox.showerror("Falha", "Não conectou via SNMP")

    def salvar(self):
        nome = self.entry_nome.get().strip()
        ip = self.entry_ip.get().strip()
        marca = self.combo_marca.get()

        if not nome or not ip:
            messagebox.showerror("Erro", "Preencha todos os dados")
            return

        self.app.impressoras.append({
            "nome": nome,
            "ip": ip,
            "marca": marca
        })

        salvar_impressoras(self.app.impressoras)

        messagebox.showinfo("OK", "Impressora cadastrada!")
        self.entry_nome.delete(0, "end")
        self.entry_ip.delete(0, "end")


# ============================================================
# APLICATIVO PRINCIPAL
# ============================================================

class PrinterApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Monitor SNMP - Impressoras")
        self.geometry("1080x650")

        self.sidebar_aberta = True
        self.impressoras = carregar_impressoras()

        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.btn_menu = ctk.CTkButton(self.sidebar, text="☰", width=40, command=self.toggle_sidebar)
        self.btn_menu.pack(pady=10)

        self.btn_home = ctk.CTkButton(self.sidebar, text="📄 Impressoras", command=self.mostrar_home)
        self.btn_home.pack(pady=10, fill="x")

        self.btn_cad = ctk.CTkButton(self.sidebar, text="➕ Cadastrar", command=self.mostrar_cadastro)
        self.btn_cad.pack(pady=10, fill="x")

        self.container = ctk.CTkFrame(self)
        self.container.pack(side="right", fill="both", expand=True)

        self.frame_home = FrameHome(self, self.container)
        self.frame_cadastro = FrameCadastro(self, self.container)

        self.mostrar_home()

    def toggle_sidebar(self):
        if self.sidebar_aberta:
            self.sidebar.configure(width=50)
            self.btn_home.pack_forget()
            self.btn_cad.pack_forget()
        else:
            self.sidebar.configure(width=180)
            self.btn_home.pack(pady=10, fill="x")
            self.btn_cad.pack(pady=10, fill="x")

        self.sidebar_aberta = not self.sidebar_aberta

    def mostrar_home(self):
        self.frame_cadastro.pack_forget()
        self.frame_home.atualizar_lista()
        self.frame_home.pack(fill="both", expand=True)

    def mostrar_cadastro(self):
        self.frame_home.pack_forget()
        self.frame_cadastro.pack(fill="both", expand=True)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    app = PrinterApp()
    app.mainloop()
