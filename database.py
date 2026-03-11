import json
import os
from typing import List, Dict

DB_FILE = "impressoras_cadastradas.json"

class Database:
    """
    Gerenciador simples de banco de dados baseado em arquivo JSON local.
    """
    def __init__(self, filename=DB_FILE):
        self.filename = filename
        self._ensure_exists()

    def _ensure_exists(self):
        """
        Garante que o arquivo JSON existe. Se não existir, cria com lista vazia.
        """
        if not os.path.exists(self.filename):
            self.save([])

    def load(self) -> List[Dict]:
        """
        Carrega as impressoras salvas.
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[DB ERROR] Falha ao carregar {self.filename}: {e}")
            return []

    def save(self, data: List[Dict]):
        """
        Salva a lista completa no arquivo JSON.
        """
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[DB ERROR] Falha ao salvar em {self.filename}: {e}")

    def add_printer(self, ip: str, marca: str, nome: str, status="Online") -> bool:
        """
        Adiciona uma nova impressora. Retorna False se o IP já existir.
        """
        printers = self.load()
        
        # Verifica duplicidade rigorosa
        if any(p.get("ip") == ip for p in printers):
            return False
            
        printers.append({
            "ip": ip,
            "marca": marca,
            "nome": nome,
            "status": status
        })
        
        self.save(printers)
        return True

    def update_printer(self, ip: str, new_data: dict):
        """
        Atualiza dados de uma impressora existente no JSON baseada no IP.
        """
        printers = self.load()
        for p in printers:
            if p.get("ip") == ip:
                p.update(new_data)
                break
        self.save(printers)

    def delete_printer(self, ip: str):
        """
        Deleta a impressora que possuir o parâmetro IP exato.
        """
        printers = self.load()
        printers = [p for p in printers if p.get("ip") != ip]
        self.save(printers)
