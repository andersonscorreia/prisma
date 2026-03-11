import customtkinter as ctk
import asyncio
import threading
from scanner import scan_network, get_local_network_prefix
from database import Database
from collector import coleta_dados
from sender import send_to_api, check_sync_status
from vendors import SUPPORTED_VENDORS

# =========================================================
# CONFIGURAÇÕES DE TEMA G TRIGUEIRO
# =========================================================

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

COLOR_RED = "#E3262E"
COLOR_RED_HOVER = "#C21F25"
COLOR_BG_LIGHT = "#FFFFFF"
COLOR_SIDEBAR = "#F7F7F7"
COLOR_TEXT_DARK = "#2C2C2C"
COLOR_TEXT_MUTED = "#757575"
COLOR_CARD = "#FFFFFF"
COLOR_GREEN_STATUS = "#22A669" # Verde para "Online"


class RegisteredPrinterCard(ctk.CTkFrame):
    """
    Card para a Tela Home: Mostra os detalhes e status da impressora salva.
    """
    def __init__(self, master, printer, callback_edit=None, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color="#EAEAEA", **kwargs)
        
        self.ip = printer.get("ip", "Desconhecido")
        self.nome = printer.get("nome", "Sem Nome")
        self.marca = printer.get("marca", "")
        self.callback_edit = callback_edit
        
        # --- HEADER DO CARD (Nome, IP, Status Bolinha) ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # Container de Título e Subtítulos
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left")

        title = f"{self.nome} ({self.marca})" if self.marca else self.nome
        self.lbl_title = ctk.CTkLabel(title_frame, text=title, text_color=COLOR_TEXT_DARK, font=("Segoe UI", 16, "bold"))
        self.lbl_title.pack(anchor="w")
        
        self.lbl_ip_sn = ctk.CTkLabel(title_frame, text=f"IP: {self.ip}  •  S/N: Carregando...", text_color=COLOR_TEXT_MUTED, font=("Segoe UI", 11))
        self.lbl_ip_sn.pack(anchor="w")
        
        # Bolinha de Status
        self.canvas_status = ctk.CTkCanvas(self.header_frame, width=15, height=15, bg=COLOR_CARD, highlightthickness=0)
        self.canvas_status.pack(side="right", pady=5)
        self.circle = self.canvas_status.create_oval(2, 2, 13, 13, fill="#CCCCCC", outline="")
        self.lbl_status_text = ctk.CTkLabel(self.header_frame, text="Carregando...", text_color=COLOR_TEXT_MUTED, font=("Segoe UI", 12, "bold"))
        self.lbl_status_text.pack(side="right", padx=5)

        # Botão Edit
        if self.callback_edit:
            self.btn_edit = ctk.CTkButton(self.header_frame, text="Editar", fg_color="transparent", text_color=COLOR_TEXT_DARK, hover_color="#EAEAEA", width=60, height=25, command=self.edit_action)
            self.btn_edit.pack(side="right", padx=10)

        # --- CONTEUDO DO CARD (Contador e Níveis) ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="x", padx=15, pady=(5, 15))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=2)

        # Esquerda: Contador de Páginas
        self.lbl_contador_val = ctk.CTkLabel(self.content_frame, text="--", text_color=COLOR_TEXT_DARK, font=("Segoe UI", 28, "bold"))
        self.lbl_contador_val.grid(row=0, column=0, sticky="w")
        self.lbl_contador_desc = ctk.CTkLabel(self.content_frame, text="Páginas Impressas", text_color=COLOR_TEXT_MUTED, font=("Segoe UI", 11))
        self.lbl_contador_desc.grid(row=1, column=0, sticky="wn", pady=(0, 10))

        # Direita: Barras de Toner
        self.toners_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.toners_frame.grid(row=0, column=1, rowspan=2, sticky="e")

    def edit_action(self):
        if self.callback_edit:
            self.callback_edit(self.ip, self.nome, self.marca)

    def create_toner_bar(self, color_name, hex_color, value):
        row = ctk.CTkFrame(self.toners_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        lbl = ctk.CTkLabel(row, text=color_name, width=20, anchor="w", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_DARK)
        lbl.pack(side="left")
        
        # Conversão de "N/A" para 0 na barra visual e mostra texto
        val_float = 0.0
        val_text = value
        if isinstance(value, (int, float)):
            val_float = float(value) / 100.0
            val_text = f"{value}%"
            
        pb = ctk.CTkProgressBar(row, width=100, height=8, progress_color=hex_color, fg_color="#E0E0E0")
        pb.pack(side="left", padx=5)
        pb.set(val_float)
        
        lbl_v = ctk.CTkLabel(row, text=str(val_text), font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED, width=35, anchor="e")
        lbl_v.pack(side="left")

    def schedule_update(self, data):
        """Metódo exposto para ser chamado via app.after com os resultados SNMP"""
        # Se contador == "N/A" (ou None) sumimos q ta offline
        contador = data.get("last_counter", "N/A")
        if contador == "N/A":
            self.canvas_status.itemconfig(self.circle, fill=COLOR_RED)
            self.lbl_status_text.configure(text="Offline", text_color=COLOR_RED)
            self.lbl_contador_val.configure(text="N/A", text_color=COLOR_TEXT_MUTED)
        else:
            self.canvas_status.itemconfig(self.circle, fill=COLOR_GREEN_STATUS)
            self.lbl_status_text.configure(text="Online", text_color=COLOR_GREEN_STATUS)
            self.lbl_contador_val.configure(text=str(contador), text_color=COLOR_TEXT_DARK)

        # Update S/N text
        sn = data.get("serial_number", "")
        if not sn or sn == "N/A":
            sn = "Não identificado"
        self.lbl_ip_sn.configure(text=f"IP: {self.ip}  •  S/N: {sn}")

        # Destroi barras antigas para recriar
        for widget in self.toners_frame.winfo_children():
            widget.destroy()

        toner = data.get("last_toner_data", [])
        if not toner or toner == "N/A":
            pass # Sem dados de toner
        else:
            # Toner agora é uma LISTA de dicionários: [{"color": "Black", "level": 85}, ...]
            if isinstance(toner, list):
                if len(toner) == 1:
                    # Somente PB
                    nivel = toner[0].get("level", "N/A")
                    if nivel != "N/A":
                        self.create_toner_bar("Toner", "#000000", nivel)
                else:
                    # Colorida: percorremos o array para plotar progressbars adequadas
                    cores_hex = {"Black": "#000000", "Cyan": "#00BFFF", "Magenta": "#FF00FF", "Yellow": "#FFD700", "Manutenção": "#A9A9A9"}
                    
                    for item in toner:
                        cor_name = item.get("color", "Black")
                        nivel = item.get("level", "N/A")
                        
                        if nivel != "N/A":
                            prog_color = cores_hex.get(cor_name, "#000000")
                            # Usa a primeira letra como sigla (B, C, M, Y, M)
                            sigla = cor_name[0].upper() if cor_name != "Black" else "BK"
                            if cor_name == "Manutenção": sigla = "W"
                            self.create_toner_bar(sigla, prog_color, nivel)


class ScannedPrinterCard(ctk.CTkFrame):
    """
    Card para a Tela de Scanner: Mostra IPs encontrados e permite cadastrar.
    """
    def __init__(self, master, printer_info, callback_register, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color="#EAEAEA", **kwargs)
        
        self.ip = printer_info.get("ip", "")
        self.desc = printer_info.get("sys_desc", "").strip()
        self.callback_register = callback_register
        
        if len(self.desc) > 55:
            self.desc = self.desc[:52] + "..."

        self.info_label = ctk.CTkLabel(
            self, text=f"{self.ip}  •  {self.desc}", 
            text_color=COLOR_TEXT_DARK, 
            font=("Segoe UI", 13, "bold")
        )
        self.info_label.pack(side="left", padx=15, pady=15)

        self.btn_cadastrar = ctk.CTkButton(
            self, text="Cadastrar", 
            fg_color=COLOR_RED, hover_color=COLOR_RED_HOVER, 
            corner_radius=15, font=("Segoe UI", 12, "bold"),
            width=90, height=30,
            command=self.cadastrar_action
        )
        self.btn_cadastrar.pack(side="right", padx=15, pady=15)

    def cadastrar_action(self):
        # Aciona a troca de tela para manual já preenchida
        self.callback_register(self.ip, self.desc)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Grupo GTrigueiro - Painel de Monitoramento")
        self.geometry("1000x650")
        self.configure(fg_color=COLOR_BG_LIGHT)
        self.db = Database()

        # Grid principal 1 linha x 2 colunas
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.setup_sidebar()
        
        # Frames do Container Principal
        self.main_container = ctk.CTkFrame(self, fg_color=COLOR_BG_LIGHT, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Inicializa Views Intercambiáveis
        self.view_home = self.build_home_view()
        self.view_scanner = self.build_scanner_view()
        self.view_manual = self.build_manual_view()

        # Começa na tela Home
        self.show_view("home")
        
        # Inicia Loop de Sincronização Dinâmico em Background
        self.run_background = True
        threading.Thread(target=self.background_sync_loop, daemon=True).start()

    # =========================================================
    # LOOP DINÂMICO (BACKGROUND SYNC)
    # =========================================================

    def background_sync_loop(self):
        """
        Thread separada que gerencia os tempos de coleta dinamicamente.
        Pergunta à API a cada 30 segundos sobre o status.
        """
        import time 
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Tempo que a última coleta geral foi executada
        last_sync_time = 0.0

        while self.run_background:
            try:
                # 1. Checa a API para obter o delay e o force_update
                status_coro = check_sync_status()
                status_api = loop.run_until_complete(status_coro)
                
                intervalo = status_api.get("interval", 300)
                force_update = status_api.get("force_update", False)
                
                now = time.time()
                time_since_last = now - last_sync_time
                
                # 2. Avalia: Forçar update pela API ou se o tempo total expirou
                if force_update or (time_since_last >= float(intervalo)):
                    print(f"[BACKGROUND] Iniciando sincronização. Motivo: {'Force Update' if force_update else 'Intervalo Expirado'} (Delay API={intervalo}s)")
                    
                    # Usa a função nativa já criada (rodará bloqueando esta thread, o q é perfeitamente ok)
                    printers = self.db.load()
                    if printers:
                        tarefas = [self.fetch_and_send(p) for p in printers]
                        if tarefas:
                            loop.run_until_complete(asyncio.gather(*tarefas))
                            
                            # Atualiza Tela visual também para refletir a nova coleta
                            self.after(0, self.refresh_home_list)

                    last_sync_time = time.time()
                
            except Exception as e:
                print(f"[BACKGROUND ERRO] Falha no loop de sincronia: {e}")
                
            # Sleep estático de checking. A cada 30 segundos ele analisa se deve coletar ou não baseado no status dinâmico
            time.sleep(30)
            
        loop.close()

    # =========================================================
    # SIDEBAR E ROTEAMENTO
    # =========================================================

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="GRUPO GTRIGUEIRO", 
            font=("Segoe UI Black", 18), text_color=COLOR_RED
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Botões de Navegação
        self.btn_home = ctk.CTkButton(
            self.sidebar_frame, text="📊 Dashboard", anchor="w", 
            font=("Segoe UI", 14), corner_radius=6,
            command=lambda: self.show_view("home")
        )
        self.btn_home.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_scan = ctk.CTkButton(
            self.sidebar_frame, text="🔍 Scanner", anchor="w", 
            font=("Segoe UI", 14), corner_radius=6,
            command=lambda: self.show_view("scanner")
        )
        self.btn_scan.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_manual = ctk.CTkButton(
            self.sidebar_frame, text="➕ Cadastro Manual", anchor="w", 
            font=("Segoe UI", 14), corner_radius=6,
            command=lambda: self.show_view("manual")
        )
        self.btn_manual.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

    def reset_nav_buttons(self):
        """Limpa as cores de seleção de todos os links do menu"""
        unselected = {"fg_color":"transparent", "text_color":COLOR_TEXT_DARK, "hover_color":"#E0E0E0"}
        self.btn_home.configure(**unselected)
        self.btn_scan.configure(**unselected)
        self.btn_manual.configure(**unselected)

    def show_view(self, name):
        """Alterna as views no frame principal"""
        self.reset_nav_buttons()
        # Esconde todos
        self.view_home.grid_forget()
        self.view_scanner.grid_forget()
        self.view_manual.grid_forget()

        selected = {"fg_color":COLOR_RED, "text_color":"#FFFFFF", "hover_color":COLOR_RED_HOVER}

        if name == "home":
            self.btn_home.configure(**selected)
            self.view_home.grid(row=0, column=0, sticky="nsew")
            self.refresh_home_list()
        elif name == "scanner":
            self.btn_scan.configure(**selected)
            self.view_scanner.grid(row=0, column=0, sticky="nsew")
        elif name == "manual":
            self.btn_manual.configure(**selected)
            self.form_ip.configure(state="normal")
            self.form_ip.delete(0, 'end')
            self.form_nome.delete(0, 'end')
            
            # Puxa dinamicamente a primeira marca disponivel
            first_vendor = list(SUPPORTED_VENDORS.keys())[0] if SUPPORTED_VENDORS else "Canon"
            self.form_marca.set(first_vendor)
            
            self.is_editing = False
            self.editing_ip = None
            self.lbl_manual_title.configure(text="Adicionar Impressora")
            self.btn_save_manual.configure(text="Salvar Impressora")
            self.manual_msg.configure(text="")
            self.view_manual.grid(row=0, column=0, sticky="nsew")


    # =========================================================
    # VIEW: HOME (Dashboard)
    # =========================================================

    def build_home_view(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        header_container = ctk.CTkFrame(frame, fg_color="transparent")
        header_container.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_container.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(header_container, text="Dashboard: Impressoras Vigiladas", font=("Segoe UI", 26, "bold"), text_color=COLOR_TEXT_DARK)
        lbl.grid(row=0, column=0, sticky="w")

        # Container de Botoes
        botoes_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        botoes_frame.grid(row=0, column=1, sticky="e")

        # Botão Sync Nuvem
        self.btn_sync = ctk.CTkButton(
            botoes_frame, text="☁️ Sincronizar com Nuvem", fg_color="#007BFF", hover_color="#0056b3",
            corner_radius=20, font=("Segoe UI", 13, "bold"), height=35, command=self.sync_to_cloud_action
        )
        self.btn_sync.pack(side="left", padx=(0, 10))

        # Botão Refresh
        self.btn_refresh = ctk.CTkButton(
            botoes_frame, text="Atualizar", fg_color=COLOR_RED, hover_color=COLOR_RED_HOVER,
            corner_radius=20, font=("Segoe UI", 13, "bold"), width=100, height=35, command=self.refresh_home_list
        )
        self.btn_refresh.pack(side="left")

        self.home_list_frame = ctk.CTkScrollableFrame(frame, fg_color="#F9F9F9", corner_radius=10, border_width=1, border_color="#EAEAEA")
        self.home_list_frame.grid(row=1, column=0, sticky="nsew")
        self.home_list_frame.grid_columnconfigure(0, weight=1)

        return frame

    def refresh_home_list(self):
        """Atualiza a lista visual puxando do DB JSON e dispara thread de SNMP"""
        for w in self.home_list_frame.winfo_children():
            w.destroy()
            
        printers = self.db.load()
        if not printers:
            ctk.CTkLabel(self.home_list_frame, text="Nenhuma impressora cadastrada.", font=("Segoe UI", 14), text_color=COLOR_TEXT_MUTED).grid(pady=30)
            return

        cards_and_printers = []
        for idx, p in enumerate(printers):
            card = RegisteredPrinterCard(self.home_list_frame, p, callback_edit=self.open_edit_from_card)
            card.grid(row=idx, column=0, sticky="ew", pady=6, padx=10)
            cards_and_printers.append((card, p))

        # Inicia Threading p/ fazer SNMP live update
        threading.Thread(target=self.run_live_updates, args=(cards_and_printers,), daemon=True).start()

    async def fetch_and_update(self, card, printer_data):
        """Busca dados de 1 impressora e atualiza via event loop base"""
        ip = printer_data.get("ip")
        marca = printer_data.get("marca")
        
        # Pega a árvore de OIDs baseada no nome da marca salva no JSON
        dict_marca = SUPPORTED_VENDORS.get(marca, SUPPORTED_VENDORS.get("Canon"))
            
        try:
            # Passamos o dicionário completo da impressora para pegar o nome/modelo para enviar à API
            dados = await coleta_dados(ip, dict_marca)
        except Exception:
            dados = {"last_counter": "N/A"}
            
        # Retorna p/ GUI Thread safe
        self.after(0, card.schedule_update, dados)

    def run_live_updates(self, cards_and_printers):
        """Loop local em thread separada para paralelizar updates parciais"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        tarefas = []
        for card, p in cards_and_printers:
            tarefas.append(self.fetch_and_update(card, p))
            
        if tarefas:
            loop.run_until_complete(asyncio.gather(*tarefas))
        loop.close()


    def sync_to_cloud_action(self):
        """Ação acionada pelo botão de sincronizar nuvem no Dashboard."""
        printers = self.db.load()
        if not printers:
            return
            
        self.btn_sync.configure(state="disabled", text="☁️ Sincronizando...")
        
        # Inicia Threading para rodar as rotinas http longas
        threading.Thread(target=self.run_cloud_sync, args=(printers,), daemon=True).start()

    async def fetch_and_send(self, printer_data):
        ip = printer_data.get("ip")
        marca = printer_data.get("marca")
        
        # Injetamos "nome" e "marca" textuais da DB no dicionário de mapeamento OID para a coleta
        # conseguir extrair isso e mandar à API
        dict_marca = SUPPORTED_VENDORS.get(marca, SUPPORTED_VENDORS.get("Canon")).copy()
        dict_marca["nome"] = printer_data.get("nome")
        dict_marca["marca"] = marca
        
        try:
            dados = await coleta_dados(ip, dict_marca)
            await send_to_api(dados)
        except Exception as e:
            print(f"Erro ao processar sync para {ip}: {e}")

    def run_cloud_sync(self, printers):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        tarefas = [self.fetch_and_send(p) for p in printers]
        if tarefas:
            loop.run_until_complete(asyncio.gather(*tarefas))
        loop.close()
        
        # Retorna o botão para o estado original na UI principal
        self.after(0, lambda: self.btn_sync.configure(state="normal", text="☁️ Sincronizar com Nuvem"))

    def open_edit_from_card(self, ip, nome, marca):
        """Abre a aba manual já preparada para editar uma impressora"""
        self.show_view("manual")
        
        self.form_ip.configure(state="normal")
        self.form_ip.delete(0, 'end')
        self.form_ip.insert(0, ip)
        self.form_ip.configure(state="disabled") # Trava o IP (chave primaria)
        
        self.form_nome.delete(0, 'end')
        self.form_nome.insert(0, nome)
        self.form_marca.set(marca)
        
        self.is_editing = True
        self.editing_ip = ip
        self.lbl_manual_title.configure(text="Editar Impressora (Atualizar)")
        self.btn_save_manual.configure(text="Atualizar Impressora")

    # =========================================================
    # VIEW: SCANNER
    # =========================================================

    def build_scanner_view(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(header, text="Escanear Rede Local", font=("Segoe UI", 26, "bold"), text_color=COLOR_TEXT_DARK)
        lbl.grid(row=0, column=0, sticky="w")
        
        self.prefixo_rede = get_local_network_prefix()
        sub_lbl = ctk.CTkLabel(header, text=f"Rede atual identificada: {self.prefixo_rede}.X", font=("Segoe UI", 14), text_color=COLOR_TEXT_MUTED)
        sub_lbl.grid(row=1, column=0, sticky="w")

        self.btn_start_scan = ctk.CTkButton(
            header, text="Iniciar Varredura", fg_color=COLOR_RED, hover_color=COLOR_RED_HOVER,
            corner_radius=25, font=("Segoe UI", 15, "bold"), height=45, command=self.start_scan_thread
        )
        self.btn_start_scan.grid(row=0, column=1, rowspan=2, sticky="e")

        self.scan_msg = ctk.CTkLabel(frame, text="", font=("Segoe UI", 13), text_color=COLOR_TEXT_DARK)
        self.scan_msg.grid(row=1, column=0, sticky="w", pady=(0, 10))

        self.scan_list_frame = ctk.CTkScrollableFrame(frame, fg_color="#F9F9F9", corner_radius=10, border_width=1, border_color="#EAEAEA")
        self.scan_list_frame.grid(row=2, column=0, sticky="nsew")
        self.scan_list_frame.grid_columnconfigure(0, weight=1)

        return frame

    def start_scan_thread(self):
        self.btn_start_scan.configure(state="disabled", text="Buscando...")
        self.scan_msg.configure(text="Sondando a rede. Isso levará alguns segundos...")
        for w in self.scan_list_frame.winfo_children(): w.destroy()
        threading.Thread(target=self.run_async_scan, daemon=True).start()

    def run_async_scan(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            resultados = loop.run_until_complete(scan_network(self.prefixo_rede))
            self.after(0, self.update_scan_results, resultados)
        except Exception as e:
            self.after(0, lambda: self.scan_msg.configure(text=f"Erro: {e}"))
            self.after(0, lambda: self.btn_start_scan.configure(state="normal", text="Iniciar Varredura"))
        finally:
            loop.close()

    def update_scan_results(self, resultados):
        self.btn_start_scan.configure(state="normal", text="Iniciar Varredura")
        self.scan_msg.configure(text=f"Varredura concluída. {len(resultados)} ativas encontradas.")
        for idx, res in enumerate(resultados):
            card = ScannedPrinterCard(self.scan_list_frame, res, callback_register=self.open_registration_from_scan)
            card.grid(row=idx, column=0, sticky="ew", pady=6, padx=10)

    def open_registration_from_scan(self, ip, raw_desc):
        """Ao clicar em cadastrar no frame scanner, pula para a View Manual e autocompleta"""
        self.show_view("manual")
        self.form_ip.insert(0, ip)
        
        # Tenta descobrir a marca pela desc
        desc_lower = raw_desc.lower()
        
        # Tenta adivinhar de forma mais dinamica
        matched = False
        for brand_name in SUPPORTED_VENDORS.keys():
            # Ex: compara "canon" in sys_desc text
            if brand_name.split()[0].lower() in desc_lower:
                self.form_marca.set(brand_name)
                matched = True
                break
                
        if not matched:
            # Fallback pra primeira disponível
            self.form_marca.set(list(SUPPORTED_VENDORS.keys())[0] if SUPPORTED_VENDORS else "Canon")
        
        # Coloca o cursor no campo nome para facilitar
        self.form_nome.focus()

    # =========================================================
    # VIEW: CADASTRO MANUAL
    # =========================================================

    def build_manual_view(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        self.lbl_manual_title = ctk.CTkLabel(frame, text="Adicionar Impressora", font=("Segoe UI", 26, "bold"), text_color=COLOR_TEXT_DARK)
        self.lbl_manual_title.grid(row=0, column=0, sticky="w", pady=(0, 20))

        content = ctk.CTkFrame(frame, fg_color=COLOR_CARD, corner_radius=10, border_color="#EAEAEA", border_width=1)
        content.grid(row=1, column=0, sticky="ew")
        content.grid_columnconfigure(1, weight=1)

        # Campos
        ctk.CTkLabel(content, text="Endereço IP:", text_color=COLOR_TEXT_DARK, font=("Segoe UI", 13)).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        self.form_ip = ctk.CTkEntry(content, width=250, border_color="#D1D1D1")
        self.form_ip.grid(row=0, column=1, sticky="w", padx=20, pady=(20, 5))

        ctk.CTkLabel(content, text="Marca/Modelo:", text_color=COLOR_TEXT_DARK, font=("Segoe UI", 13)).grid(row=1, column=0, sticky="w", padx=20, pady=5)
        
        # Aqui injetamos dinamicamente as opções direto do backend (vendors)
        available_brands = list(SUPPORTED_VENDORS.keys())
        
        self.form_marca = ctk.CTkOptionMenu(
            content, values=available_brands, 
            fg_color="#F0F0F0", button_color="#E0E0E0", button_hover_color="#D0D0D0",
            text_color=COLOR_TEXT_DARK, dropdown_fg_color="#FFFFFF", dropdown_text_color=COLOR_TEXT_DARK
        )
        self.form_marca.grid(row=1, column=1, sticky="w", padx=20, pady=5)

        ctk.CTkLabel(content, text="Nome Personalizado:", text_color=COLOR_TEXT_DARK, font=("Segoe UI", 13)).grid(row=2, column=0, sticky="w", padx=20, pady=(5, 30))
        self.form_nome = ctk.CTkEntry(content, width=250, placeholder_text="Ex: Setor Jurídico", border_color="#D1D1D1")
        self.form_nome.grid(row=2, column=1, sticky="w", padx=20, pady=(5, 30))

        # Botão Salvar
        self.btn_save_manual = ctk.CTkButton(
            content, text="Salvar Impressora", fg_color=COLOR_RED, hover_color=COLOR_RED_HOVER,
            corner_radius=20, font=("Segoe UI", 14, "bold"), height=40, command=self.save_printer_action
        )
        self.btn_save_manual.grid(row=3, column=0, columnspan=2, pady=(0, 25))

        self.manual_msg = ctk.CTkLabel(content, text="", text_color=COLOR_GREEN_STATUS, font=("Segoe UI", 12))
        self.manual_msg.grid(row=4, column=0, columnspan=2, pady=(0, 10))

        return frame

    def save_printer_action(self):
        v_ip = self.form_ip.get().strip()
        v_nome = self.form_nome.get().strip()
        v_marca = self.form_marca.get()

        if not v_ip or not v_nome:
            self.manual_msg.configure(text="Preencha o IP e o Nome antes de salvar.", text_color=COLOR_RED)
            return

        if getattr(self, "is_editing", False):
            # Modo Atualização
            self.db.update_printer(self.editing_ip, {"nome": v_nome, "marca": v_marca})
            self.manual_msg.configure(text=f"Impressora {v_nome} atualizada com sucesso!", text_color=COLOR_GREEN_STATUS)
        else:
            # Novo Cadastro (Validação de IP duplo)
            printers = self.db.load()
            if v_ip in [p.get("ip") for p in printers]:
                self.manual_msg.configure(text=f"Erro: O IP {v_ip} já está cadastrado!", text_color=COLOR_RED)
                return
            
            self.db.add_printer(ip=v_ip, marca=v_marca, nome=v_nome)
            self.manual_msg.configure(text=f"Impressora {v_nome} salva com sucesso!", text_color=COLOR_GREEN_STATUS)
        
        # Opcional: Voltar para a Home automaticamente ao salvar
        self.after(1000, lambda: self.show_view("home"))


if __name__ == "__main__":
    app = App()
    app.mainloop()
