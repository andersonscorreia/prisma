# tela.py
import sys
import json
import os
from functools import partial

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QScrollArea, QFrame, QMessageBox,
    QStackedWidget, QComboBox, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon

# ---------- TENTA IMPORTAR SEU MÓDULO SNMP ----------
# Seu módulo principal que contém coleta_dados(ip, impressora_dict)
try:
    from snmp import coleta_dados, canon, richo, epson_color  # noqa: F401
    SNMP_AVAILABLE = True
except Exception:
    coleta_dados = None
    canon = richo = epson_color = None
    SNMP_AVAILABLE = False

# ---------- CONFIGS ----------
JSON_FILE = "impressoras.json"
SIDEBAR_EXPANDED = 220
SIDEBAR_COLLAPSED = 50


# ---------- UTIL JSON ----------
def carregar_impressoras():
    """Retorna dict {'impressoras': [...]}. Corrige formatos diversos."""
    if not os.path.exists(JSON_FILE):
        data = {"impressoras": []}
        salvar_impressoras(data)
        return data

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"impressoras": []}
        salvar_impressoras(data)
        return data

    if isinstance(data, list):
        return {"impressoras": data}
    if isinstance(data, dict) and "impressoras" in data and isinstance(data["impressoras"], list):
        return data

    # formato inesperado -> reset
    data = {"impressoras": []}
    salvar_impressoras(data)
    return data


def salvar_impressoras(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------- UI HELPERS ----------
def mk_label(text, bold=False, size=11):
    lbl = QLabel(text)
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    lbl.setFont(font)
    return lbl


# ---------- CARD WIDGET ----------
class CardImpressora(QFrame):
    def __init__(self, impressora: dict, app_window):
        super().__init__()
        self.impressora = impressora
        self.app_window = app_window
        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card {
                background: #ffffff;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 10px;
            }
            QLabel { color: #222; }
            QPushButton { padding: 6px 10px; }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Header: nome + IP badge
        header = QHBoxLayout()
        nome = mk_label(self.impressora.get("nome", "<sem nome>"), bold=True, size=12)
        header.addWidget(nome)
        header.addStretch()
        ip_badge = mk_label(self.impressora.get("ip", "-"), size=10)
        ip_badge.setStyleSheet("color: #555;")
        header.addWidget(ip_badge)
        layout.addLayout(header)

        # Info line
        info = QHBoxLayout()
        modelo = mk_label(f"Modelo: {self.impressora.get('modelo', '-')}", size=10)
        marca = mk_label(f"Marca: {self.impressora.get('marca', '-')}", size=10)
        info.addWidget(modelo)
        info.addStretch()
        info.addWidget(marca)
        layout.addLayout(info)

        # Buttons row
        row = QHBoxLayout()
        btn_consultar = QPushButton("Consultar")
        btn_editar = QPushButton("Editar")
        btn_detalhes = QPushButton("Detalhes")
        btn_excluir = QPushButton("Excluir")

        btn_consultar.clicked.connect(self.consultar)
        btn_editar.clicked.connect(self.editar)
        btn_detalhes.clicked.connect(self.detalhes)
        btn_excluir.clicked.connect(self.excluir)

        # small style
        for b in (btn_consultar, btn_editar, btn_detalhes, btn_excluir):
            b.setCursor(Qt.PointingHandCursor)
            b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        row.addWidget(btn_consultar)
        row.addWidget(btn_detalhes)
        row.addWidget(btn_editar)
        row.addStretch()
        row.addWidget(btn_excluir)
        layout.addLayout(row)

    def consultar(self):
        # abre a página de resultado e faz coleta SNMP (se disponível)
        self.app_window.abrir_resultado(self.impressora)

    def editar(self):
        self.app_window.abrir_cadastro(editando=self.impressora)

    def detalhes(self):
        # mostra a página de detalhes com dados locais (e tenta SNMP)
        self.app_window.abrir_detalhes(self.impressora)

    def excluir(self):
        data = carregar_impressoras()
        before = len(data["impressoras"])
        data["impressoras"] = [i for i in data["impressoras"] if i.get("ip") != self.impressora.get("ip")]
        if len(data["impressoras"]) < before:
            salvar_impressoras(data)
            QMessageBox.information(self, "Removido", "Impressora removida com sucesso.")
            self.app_window.home.atualizar_lista()
        else:
            QMessageBox.warning(self, "Aviso", "Impressora não encontrada.")


# ---------- PÁGINA HOME ----------
class PaginaHome(QWidget):
    def __init__(self, app_window):
        super().__init__()
        self.app_window = app_window
        self._build_ui()
        self.atualizar_lista()

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(14, 14, 14, 14)
        v.setSpacing(12)

        title = mk_label("Impressoras Cadastradas", bold=True, size=14)
        v.addWidget(title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(12)
        self.container_layout.setContentsMargins(6, 6, 6, 6)
        self.scroll.setWidget(self.container)
        v.addWidget(self.scroll)
        v.addStretch()

    def atualizar_lista(self):
        # limpa container
        for i in reversed(range(self.container_layout.count())):
            w = self.container_layout.takeAt(i).widget()
            if w:
                w.deleteLater()

        data = carregar_impressoras()
        impressoras = data.get("impressoras", [])

        if not impressoras:
            vazio = mk_label("Nenhuma impressora cadastrada.", size=11)
            vazio.setStyleSheet("color: #666;")
            self.container_layout.addWidget(vazio)
            return

        for imp in impressoras:
            card = CardImpressora(imp, self.app_window)
            self.container_layout.addWidget(card)


# ---------- PÁGINA CADASTRO ----------
class PaginaCadastro(QWidget):
    def __init__(self, app_window):
        super().__init__()
        self.app_window = app_window
        self.editing_item = None
        self.test_ok = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = mk_label("Cadastrar / Editar Impressora", bold=True, size=14)
        layout.addWidget(title)

        # inputs
        self.in_nome = QLineEdit()
        self.in_nome.setPlaceholderText("Nome da impressora")
        self.in_modelo = QLineEdit()
        self.in_modelo.setPlaceholderText("Modelo (opcional)")
        self.in_ip = QLineEdit()
        self.in_ip.setPlaceholderText("Endereço IP (ex: 192.168.0.10)")

        self.combo_marca = QComboBox()
        self.combo_marca.addItem("Canon", "canon")
        self.combo_marca.addItem("Ricoh", "richo")
        self.combo_marca.addItem("Epson Colorida", "epson_color")

        layout.addWidget(mk_label("Nome"))
        layout.addWidget(self.in_nome)
        layout.addWidget(mk_label("Modelo"))
        layout.addWidget(self.in_modelo)
        layout.addWidget(mk_label("IP"))
        layout.addWidget(self.in_ip)
        layout.addWidget(mk_label("Marca"))
        layout.addWidget(self.combo_marca)

        # action buttons
        row = QHBoxLayout()
        self.btn_test = QPushButton("Testar Conexão (SNMP)")
        self.btn_save = QPushButton("Salvar")
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_save.setEnabled(False)  # somente após teste ok

        self.btn_test.clicked.connect(self.on_test)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_cancel.clicked.connect(self.on_cancel)

        row.addWidget(self.btn_test)
        row.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        row.addWidget(self.btn_save)
        row.addWidget(self.btn_cancel)
        layout.addLayout(row)

    def carregar_para_edicao(self, item):
        self.editing_item = item
        self.in_nome.setText(item.get("nome", ""))
        self.in_modelo.setText(item.get("modelo", ""))
        self.in_ip.setText(item.get("ip", ""))
        marca = item.get("marca", "")
        idx = self.combo_marca.findData(marca)
        if idx >= 0:
            self.combo_marca.setCurrentIndex(idx)
        self.test_ok = False
        self.btn_save.setEnabled(False)

    def limpar_campos(self):
        self.editing_item = None
        self.in_nome.clear()
        self.in_modelo.clear()
        self.in_ip.clear()
        self.combo_marca.setCurrentIndex(0)
        self.test_ok = False
        self.btn_save.setEnabled(False)

    def on_cancel(self):
        self.limpar_campos()
        self.app_window.abrir_home()

    def on_test(self):
        ip = self.in_ip.text().strip()
        if not ip:
            QMessageBox.warning(self, "Aviso", "Digite o IP antes de testar.")
            return

        if not SNMP_AVAILABLE:
            QMessageBox.information(self, "SNMP indisponível",
                                    "SNMP indisponível (arquivo snmp.py ausente ou com erro).")
            return

        marca = self.combo_marca.currentData()
        if marca == "canon":
            imp_def = canon
        elif marca == "richo":
            imp_def = richo
        else:
            imp_def = epson_color

        try:
            # coleta_dados é síncrona no seu código original (cria seu próprio loop)
            coleta_dados(ip, imp_def)
            QMessageBox.information(self, "Conexão OK", "Conexão SNMP OK!")
            self.test_ok = True
            self.btn_save.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Falha SNMP", f"Erro ao testar SNMP:\n{e}")
            self.test_ok = False
            self.btn_save.setEnabled(False)

    def on_save(self):
        if not self.test_ok:
            QMessageBox.warning(self, "Aviso", "Execute o teste SNMP com sucesso antes de salvar.")
            return

        nome = self.in_nome.text().strip()
        modelo = self.in_modelo.text().strip()
        ip = self.in_ip.text().strip()
        marca = self.combo_marca.currentData()

        if not nome or not ip:
            QMessageBox.warning(self, "Erro", "Preencha pelo menos Nome e IP.")
            return

        data = carregar_impressoras()
        impressoras = data.get("impressoras", [])

        if self.editing_item:
            orig_ip = self.editing_item.get("ip")
            updated = False
            for idx, it in enumerate(impressoras):
                if it.get("ip") == orig_ip:
                    impressoras[idx] = {"nome": nome, "modelo": modelo, "ip": ip, "marca": marca}
                    updated = True
                    break
            if not updated:
                impressoras.append({"nome": nome, "modelo": modelo, "ip": ip, "marca": marca})
        else:
            # evita duplicação por IP
            if any(it.get("ip") == ip for it in impressoras):
                QMessageBox.warning(self, "Erro", "Já existe uma impressora com este IP.")
                return
            impressoras.append({"nome": nome, "modelo": modelo, "ip": ip, "marca": marca})

        data["impressoras"] = impressoras
        salvar_impressoras(data)
        QMessageBox.information(self, "OK", "Impressora salva.")
        self.limpar_campos()
        self.app_window.home.atualizar_lista()
        self.app_window.abrir_home()


# ---------- PÁGINA DETALHES ----------
class PaginaDetalhes(QWidget):
    def __init__(self, app_window):
        super().__init__()
        self.app_window = app_window
        self.current_item = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.title = mk_label("Detalhes da Impressora", bold=True, size=14)
        layout.addWidget(self.title)

        self.info_area = QVBoxLayout()
        layout.addLayout(self.info_area)

        # action buttons
        row = QHBoxLayout()
        self.btn_refresh = QPushButton("Atualizar SNMP")
        self.btn_back = QPushButton("Voltar")
        self.btn_refresh.clicked.connect(self.on_refresh)
        self.btn_back.clicked.connect(self.app_window.abrir_home)
        row.addWidget(self.btn_refresh)
        row.addStretch()
        row.addWidget(self.btn_back)
        layout.addLayout(row)

    def show_item(self, item: dict):
        self.current_item = item
        # limpar
        for i in reversed(range(self.info_area.count())):
            w = self.info_area.takeAt(i).widget()
            if w:
                w.deleteLater()

        # mostra dados locais
        self.info_area.addWidget(mk_label(f"Nome: {item.get('nome', '')}", size=11))
        self.info_area.addWidget(mk_label(f"Modelo (local): {item.get('modelo', '-')}", size=11))
        self.info_area.addWidget(mk_label(f"IP: {item.get('ip', '-')}", size=11))
        self.info_area.addWidget(mk_label(f"Marca: {item.get('marca', '-')}", size=11))

        # tenta trazer SNMP imediatamente (não obrigatório)
        if SNMP_AVAILABLE:
            try:
                # faz coleta e mostra resumo
                marca = item.get("marca")
                if marca == "canon":
                    imp_def = canon
                elif marca == "richo":
                    imp_def = richo
                else:
                    imp_def = epson_color

                resultado = coleta_dados(item.get("ip"), imp_def)
                self._show_snmp(resultado)
            except Exception as e:
                self.info_area.addWidget(mk_label(f"SNMP falhou: {e}", size=10))
        else:
            self.info_area.addWidget(mk_label("SNMP não disponível (módulo ausente).", size=10))

    def _show_snmp(self, dados: dict):
        # dados pode ser o dicionário retornado pelo seu coleta_dados
        self.info_area.addWidget(mk_label("---- Dados SNMP ----", bold=True, size=11))
        # exibe chaves principais (ajuste conforme seu retorno)
        for k, v in dados.items():
            self.info_area.addWidget(mk_label(f"{k}: {v}", size=10))

    def on_refresh(self):
        if not self.current_item:
            return
        if not SNMP_AVAILABLE:
            QMessageBox.information(self, "SNMP indisponível", "Arquivo snmp.py não carregado.")
            return
        try:
            marca = self.current_item.get("marca")
            if marca == "canon":
                imp_def = canon
            elif marca == "richo":
                imp_def = richo
            else:
                imp_def = epson_color
            resultado = coleta_dados(self.current_item.get("ip"), imp_def)
            # limpa SNMP anterior e mostra novo
            # remove trailing SNMP lines first
            # (simpler: clear all and re-show local + SNMP)
            self.show_item(self.current_item)
        except Exception as e:
            QMessageBox.critical(self, "Erro SNMP", f"Erro ao atualizar SNMP:\n{e}")


# ---------- MAIN WINDOW ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PRISMA - Gerenciamento de Impressoras")
        self.resize(1200, 700)
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(SIDEBAR_EXPANDED)
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(8, 8, 8, 8)
        side_layout.setSpacing(8)

        # Toggle (≡)
        self.btn_toggle = QPushButton("≡")
        self.btn_toggle.setObjectName("btn_toggle")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        self.btn_toggle.setFixedHeight(36)
        side_layout.addWidget(self.btn_toggle)

        # Menu buttons
        self.btn_home = QPushButton("Home")
        self.btn_home.setObjectName("btn_home")
        self.btn_home.clicked.connect(self.abrir_home)

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setObjectName("btn_cadastrar")
        self.btn_cadastrar.clicked.connect(lambda: self.abrir_cadastro(None))

        self.btn_resultados = QPushButton("Resultados")
        self.btn_resultados.setObjectName("btn_resultados")
        self.btn_resultados.clicked.connect(lambda: self.stack.setCurrentIndex(3))  # reserve index

        for b in (self.btn_home, self.btn_cadastrar, self.btn_resultados):
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(34)
            side_layout.addWidget(b)

        side_layout.addStretch()
        self.sidebar.setLayout(side_layout)

        # Content area (stack)
        self.stack = QStackedWidget()
        self.home = PaginaHome(self)
        self.cadastro = PaginaCadastro(self)
        self.detalhes = PaginaDetalhes(self)
        # index layout:
        # 0 -> home
        # 1 -> cadastro
        # 2 -> detalhes
        # 3 -> resultados (opcional)
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.cadastro)
        self.stack.addWidget(self.detalhes)
        self.stack.addWidget(QWidget())  # placeholder for resultados se quiser

        main.addWidget(self.sidebar)
        main.addWidget(self.stack, 1)

        # animation
        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.sidebar_collapsed = False

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #f4f6f8; }
            QWidget#sidebar { background: #2f3b52; color: #fff; }
            QPushButton#btn_toggle { color: #fff; background: transparent; border: none; font-size:18px; }
            QPushButton { color: #fff; background: #44526a; border: none; border-radius:6px; padding-left:10px; text-align:left; }
            QPushButton:hover { background: #576b85; }
            QLabel { color: #222; font-family: 'Segoe UI'; }
        """)

    # ---------- Navigation helpers ----------
    def abrir_home(self):
        self.home.atualizar_lista()
        self.stack.setCurrentIndex(0)

    def abrir_cadastro(self, editando=None):
        if isinstance(editando, dict):
            self.cadastro.carregar_para_edicao(editando)
        else:
            self.cadastro.limpar_campos()
        self.stack.setCurrentIndex(1)

    def abrir_detalhes(self, item: dict):
        self.detalhes.show_item(item)
        self.stack.setCurrentIndex(2)

    def abrir_resultado(self, item: dict):
        # Reuso: abre detalhes que já tenta SNMP
        self.abrir_detalhes(item)

    # ---------- sidebar toggle ----------
    def toggle_sidebar(self):
        if self.sidebar_collapsed:
            start, end = SIDEBAR_COLLAPSED, SIDEBAR_EXPANDED
        else:
            start, end = SIDEBAR_EXPANDED, SIDEBAR_COLLAPSED

        self.anim.stop()
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.start()

        # hide/restore texts on collapse/expand
        if not self.sidebar_collapsed:
            # collapse -> hide texts except toggle
            for b in (self.btn_home, self.btn_cadastrar, self.btn_resultados):
                b.setProperty("storedText", b.text())
                b.setText("")
                b.setToolTip(b.property("storedText"))
        else:
            # expand -> restore texts
            for b in (self.btn_home, self.btn_cadastrar, self.btn_resultados):
                txt = b.property("storedText")
                if txt:
                    b.setText(txt)
                    b.setToolTip("")

        self.sidebar_collapsed = not self.sidebar_collapsed


# ---------- RUN ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
