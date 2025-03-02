import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QFileDialog, 
                            QMessageBox, QSpinBox, QComboBox, QFormLayout, QSplitter)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QClipboard, QImage
from PyQt6.QtCore import Qt, QBuffer
import qrcode
from PIL import Image
from decimal import Decimal

class GeradorPix:
    """Classe responsável pela geração de payloads PIX e QR codes."""
    
    def __init__(self):
        self.payload = {}
        
    def _adicionar_valor(self, id_campo, valor):
        """Adiciona um valor ao payload no formato ID + tamanho + valor"""
        if valor is not None:
            valor_str = str(valor)
            tamanho = f"{len(valor_str):02d}"
            self.payload[id_campo] = id_campo + tamanho + valor_str
    
    def calculate_crc16(self, data):
        """Calcula o CRC16/CCITT-FALSE manualmente"""
        crc = 0xFFFF
        polynomial = 0x1021
        
        for byte in data.encode('ascii'):
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= 0xFFFF
        
        return f"{crc:04X}"

    def gerar_payload(self, chave_pix, valor=None, txid="***", nome_merchant="N", cidade_merchant="C"):
        """Gera o payload do PIX com os campos necessários"""
        self.payload = {}
        
        self._adicionar_valor("00", "01")  # Payload Format Indicator
        
        # Merchant Account Information (26)
        merchant_account = f"0014BR.GOV.BCB.PIX01{len(chave_pix):02d}{chave_pix}"
        self._adicionar_valor("26", merchant_account)
        
        self._adicionar_valor("52", "0000")  # Merchant Category Code
        self._adicionar_valor("53", "986")   # Transaction Currency
        
        if valor is not None and valor > 0:
            valor_str = f"{valor:.2f}"
            self._adicionar_valor("54", valor_str)  # Transaction Amount
        
        self._adicionar_valor("58", "BR")    # Country Code
        self._adicionar_valor("59", nome_merchant)  # Merchant Name
        self._adicionar_valor("60", cidade_merchant)  # Merchant City
        
        # Additional Data Field (62) com subcampo 05
        txid_field = f"05{len(txid):02d}{txid}"
        self._adicionar_valor("62", txid_field)
        
        payload_sem_crc = ''.join(self.payload.values()) + "6304"
        crc_hex = self.calculate_crc16(payload_sem_crc)
        payload_completo = payload_sem_crc + crc_hex
        
        return payload_completo
    
    def gerar_qrcode_pillow(self, payload, size=300):
        """Gera um QR code usando Pillow"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        if hasattr(img, 'resize'):
            img = img.resize((size, size), Image.LANCZOS)
        return img
    
    def gerar_qrcode_pixmap(self, payload, size=300):
        """Gera um QR code e retorna como QPixmap"""
        img = self.gerar_qrcode_pillow(payload, size)
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        img.save(buffer, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.data())
        buffer.close()
        return pixmap
    
    def salvar_qrcode(self, payload, filename, size=300):
        """Salva o QR code como arquivo de imagem"""
        try:
            img = self.gerar_qrcode_pillow(payload, size)
            img.save(filename)
            return True
        except Exception as e:
            print(f"Erro ao salvar QR code: {e}")
            return False

    def parse_payload(self, payload):
        """Analisa um payload PIX e extrai seus dados"""
        result = {}
        i = 0
        while i < len(payload) - 4:
            id_campo = payload[i:i+2]
            tamanho = int(payload[i+2:i+4])
            valor = payload[i+4:i+4+tamanho]
            result[id_campo] = valor
            i += 4 + tamanho
        result["63"] = payload[-4:]
        return result

class PixGUI(QMainWindow):
    """Interface gráfica para o Gerador PIX"""
    
    def __init__(self):
        super().__init__()
        self.gerador = GeradorPix()
        self.current_payload = None
        self.is_dark_theme = False
        self.init_ui()

    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Gerador de Chaves Pix")
        self.setGeometry(100, 100, 900, 650)
        
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        self.apply_styles()

        title = QLabel("Gerador de Pix")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter, 1)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        splitter.addWidget(form_widget)
        
        form_group = QGroupBox("Dados do Pix")
        form_fields = QFormLayout()
        
        self.tipo_chave = QComboBox()
        self.tipo_chave.addItems(["E-mail", "CPF", "CNPJ", "Telefone", "Chave aleatória"])
        form_fields.addRow("Tipo de chave:", self.tipo_chave)
        
        self.chave_input = QLineEdit()
        self.chave_input.setPlaceholderText("Chave Pix (e-mail, CPF, etc.)")
        form_fields.addRow("Chave PIX:", self.chave_input)
        
        valor_layout = QHBoxLayout()
        self.valor_inteiro = QSpinBox()
        self.valor_inteiro.setRange(0, 999999)
        self.valor_inteiro.setPrefix("R$ ")
        self.valor_inteiro.setFixedWidth(130)
        self.valor_centavos = QSpinBox()
        self.valor_centavos.setRange(0, 99)
        self.valor_centavos.setSuffix(" centavos")
        self.valor_centavos.setFixedWidth(130)
        valor_layout.addWidget(self.valor_inteiro)
        valor_layout.addWidget(QLabel(","))
        valor_layout.addWidget(self.valor_centavos)
        valor_layout.addStretch()
        form_fields.addRow("Valor:", valor_layout)
        
        self.txid_input = QLineEdit()
        self.txid_input.setPlaceholderText("Identificador (txid)")
        form_fields.addRow("Identificador:", self.txid_input)
        
        info_layout = QHBoxLayout()
        self.nome_input = QLineEdit("N")
        self.nome_input.setFixedWidth(130)
        info_layout.addWidget(QLabel("Nome:"))
        info_layout.addWidget(self.nome_input)
        self.cidade_input = QLineEdit("C")
        self.cidade_input.setFixedWidth(130)
        info_layout.addWidget(QLabel("Cidade:"))
        info_layout.addWidget(self.cidade_input)
        form_fields.addRow("Informações adicionais:", info_layout)
        
        qr_size_layout = QHBoxLayout()
        self.qr_size = QSpinBox()
        self.qr_size.setRange(100, 1000)
        self.qr_size.setValue(200)
        self.qr_size.setSuffix(" px")
        qr_size_layout.addWidget(QLabel("Tamanho do QR:"))
        qr_size_layout.addWidget(self.qr_size)
        qr_size_layout.addStretch()
        form_fields.addRow("Tamanho do QR:", qr_size_layout)
        
        form_group.setLayout(form_fields)
        form_layout.addWidget(form_group)
        
        buttons_layout = QHBoxLayout()
        self.gerar_btn = QPushButton("Gerar Pix")
        self.gerar_btn.setIcon(self.style().standardIcon(QApplication.style().StandardPixmap.SP_DialogApplyButton))
        self.gerar_btn.clicked.connect(self.generate_pix)
        buttons_layout.addWidget(self.gerar_btn)
        
        self.limpar_btn = QPushButton("Limpar")
        self.limpar_btn.setIcon(self.style().standardIcon(QApplication.style().StandardPixmap.SP_DialogResetButton))
        self.limpar_btn.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.limpar_btn)
        
        self.theme_btn = QPushButton("Modo Escuro")
        self.theme_btn.clicked.connect(self.toggle_theme)
        buttons_layout.addWidget(self.theme_btn)
        
        form_layout.addLayout(buttons_layout)
        form_layout.addStretch()
        
        result_widget = QWidget()
        result_layout = QVBoxLayout(result_widget)
        splitter.addWidget(result_widget)
        
        self.qr_group = QGroupBox("QR Code")
        qr_layout = QVBoxLayout()
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumSize(200, 200)
        qr_layout.addWidget(self.qr_label)
        qr_btn_layout = QHBoxLayout()
        self.save_qr_btn = QPushButton("Salvar QR Code")
        self.save_qr_btn.setIcon(self.style().standardIcon(QApplication.style().StandardPixmap.SP_DialogSaveButton))
        self.save_qr_btn.clicked.connect(self.save_qrcode)
        self.save_qr_btn.setEnabled(False)
        qr_btn_layout.addWidget(self.save_qr_btn)
        qr_layout.addLayout(qr_btn_layout)
        self.qr_group.setLayout(qr_layout)
        result_layout.addWidget(self.qr_group)
        
        self.payload_group = QGroupBox("Pix Copia e Cola")
        payload_layout = QVBoxLayout()
        self.payload_text = QTextEdit()
        self.payload_text.setReadOnly(True)
        self.payload_text.setMinimumHeight(100)
        payload_layout.addWidget(self.payload_text)
        copy_btn = QPushButton("Copiar Código")
        copy_btn.setIcon(self.style().standardIcon(QApplication.style().StandardPixmap.SP_DialogSaveButton))
        copy_btn.clicked.connect(self.copy_payload)
        payload_layout.addWidget(copy_btn)
        self.payload_group.setLayout(payload_layout)
        result_layout.addWidget(self.payload_group)
        
        self.details_group = QGroupBox("Detalhes")
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        self.details_group.setLayout(details_layout)
        result_layout.addWidget(self.details_group)
        
        splitter.setSizes([350, 550])
        self.statusBar().showMessage("Pronto para gerar códigos PIX")

    def apply_styles(self):
        """Aplica estilos CSS à interface"""
        if self.is_dark_theme:
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; }
                QLabel { font-size: 14px; color: #e0e0e0; }
                QLineEdit, QComboBox, QSpinBox { 
                    padding: 8px; 
                    font-size: 14px; 
                    border: 1px solid #555; 
                    border-radius: 5px; 
                    background-color: #3c3c3c; 
                    color: #e0e0e0;
                }
                QComboBox::drop-down { 
                    border-left: 1px solid #555; 
                    padding: 0 5px; 
                }
                QPushButton { 
                    background-color: #4CAF50; 
                    color: white; 
                    padding: 10px; 
                    font-size: 14px; 
                    border: none; 
                    border-radius: 5px; 
                    min-width: 120px;
                }
                QPushButton:hover { background-color: #45a049; }
                QPushButton:disabled { background-color: #666; color: #999; }
                QTextEdit { 
                    font-family: 'Courier New'; 
                    font-size: 12px; 
                    border: 1px solid #555; 
                    border-radius: 5px; 
                    background-color: #3c3c3c; 
                    color: #e0e0e0;
                }
                QGroupBox { 
                    font-weight: bold; 
                    font-size: 14px; 
                    padding: 15px; 
                    margin-top: 15px; 
                    border: 1px solid #555; 
                    border-radius: 5px; 
                    background-color: #333; 
                    color: #e0e0e0;
                }
                QGroupBox::title { padding: 0 5px; color: #e0e0e0; }
                #limpar_btn { background-color: #f44336; }
                #limpar_btn:hover { background-color: #d32f2f; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #f5f5f5; }
                QLabel { font-size: 14px; color: #333; }
                QLineEdit, QComboBox, QSpinBox { 
                    padding: 8px; 
                    font-size: 14px; 
                    border: 1px solid #ccc; 
                    border-radius: 5px; 
                    background-color: #ffffff; 
                    color: #333333;
                }
                QComboBox::drop-down { 
                    border-left: 1px solid #ccc; 
                    padding: 0 5px; 
                }
                QComboBox::down-arrow { 
                    image: url(:/down-arrow);
                }
                QPushButton { 
                    background-color: #4CAF50; 
                    color: white; 
                    padding: 10px; 
                    font-size: 14px; 
                    border: none; 
                    border-radius: 5px; 
                    min-width: 120px;
                }
                QPushButton:hover { background-color: #45a049; }
                QPushButton:disabled { background-color: #cccccc; color: #666666; }
                QTextEdit { 
                    font-family: 'Courier New'; 
                    font-size: 12px; 
                    border: 1px solid #ccc; 
                    border-radius: 5px; 
                    background-color: #ffffff; 
                    color: #333333;
                }
                QGroupBox { 
                    font-weight: bold; 
                    font-size: 14px; 
                    padding: 15px; 
                    margin-top: 15px; 
                    border: 1px solid #ddd; 
                    border-radius: 5px; 
                    background-color: #ffffff;
                }
                QGroupBox::title { padding: 0 5px; color: #333; }
                #limpar_btn { background-color: #f44336; }
                #limpar_btn:hover { background-color: #d32f2f; }
            """)

    def toggle_theme(self):
        """Alterna entre tema claro e escuro"""
        self.is_dark_theme = not self.is_dark_theme
        self.theme_btn.setText("Modo Claro" if self.is_dark_theme else "Modo Escuro")
        self.apply_styles()
        self.style().polish(self)

    def validate_key(self, chave, tipo):
        """Valida a chave PIX com base no tipo selecionado"""
        chave = chave.strip()
        if tipo == "E-mail" and "@" not in chave:
            return False
        elif tipo == "CPF" and (len(chave) != 11 or not chave.isdigit()):
            return False
        elif tipo == "CNPJ" and (len(chave) != 14 or not chave.isdigit()):
            return False
        elif tipo == "Telefone" and (len(chave) < 12 or not chave.startswith("+55")):
            return False
        elif tipo == "Chave aleatória" and len(chave) > 36:
            return False
        return True

    def generate_pix(self):
        """Gera o payload e QR Code"""
        try:
            chave = self.chave_input.text().strip()
            tipo = self.tipo_chave.currentText()
            if not chave:
                self.show_error("A chave PIX é obrigatória!")
                return
            if not self.validate_key(chave, tipo):
                self.show_error(f"Chave inválida para o tipo {tipo}!")
                return
                
            valor_reais = self.valor_inteiro.value()
            valor_centavos = self.valor_centavos.value()
            valor = Decimal(f"{valor_reais}.{valor_centavos:02d}")
            
            txid = self.txid_input.text().strip() or "***"
            nome = self.nome_input.text().strip() or "N"
            cidade = self.cidade_input.text().strip() or "C"
            qr_size = self.qr_size.value()

            payload = self.gerador.gerar_payload(chave, valor, txid, nome, cidade)
            self.current_payload = payload
            
            self.payload_text.setText(payload)
            
            qr_pixmap = self.gerador.gerar_qrcode_pixmap(payload, qr_size)
            self.qr_label.setPixmap(qr_pixmap)
            
            self.save_qr_btn.setEnabled(True)
            
            self.update_details(chave, valor, txid, nome, cidade, payload)
            
            self.statusBar().showMessage("PIX gerado com sucesso!")

        except ValueError as e:
            self.show_error(f"Erro de valor: {str(e)}")
        except Exception as e:
            self.show_error(f"Erro ao gerar PIX: {str(e)}")

    def update_details(self, chave, valor, txid, nome, cidade, payload):
        """Atualiza as informações detalhadas do PIX"""
        tipo_chave = self.tipo_chave.currentText()
        parsed = self.gerador.parse_payload(payload)
        
        details = f"**Detalhes do PIX:**\n\n"
        details += f"**Tipo de chave:** {tipo_chave}\n"
        details += f"**Chave PIX:** {chave}\n"
        details += f"**Valor:** R$ {valor:.2f}\n"
        details += f"**Identificador (txid):** {txid}\n"
        details += f"**Nome do recebedor:** {nome}\n"
        details += f"**Cidade do recebedor:** {cidade}\n"
        
        details += "\n**Campos EMV Decodificados:**\n"
        for id_campo, valor in parsed.items():
            campo_nome = {
                "00": "Payload Format Indicator",
                "26": "Merchant Account Information",
                "52": "Merchant Category Code",
                "53": "Transaction Currency",
                "54": "Transaction Amount",
                "58": "Country Code",
                "59": "Merchant Name",
                "60": "Merchant City",
                "62": "Additional Data Field",
                "63": "CRC"
            }.get(id_campo, f"Unknown ({id_campo})")
            details += f"{id_campo}: {campo_nome} = {valor}\n"
        
        self.details_text.setMarkdown(details)

    def save_qrcode(self):
        """Salva o QR code em um arquivo"""
        if not self.current_payload:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Salvar QR Code", os.path.expanduser("~/pix_qrcode.png"), "Imagens (*.png *.jpg *.jpeg)"
        )
        if filename:
            size = 500
            if self.gerador.salvar_qrcode(self.current_payload, filename, size):
                self.statusBar().showMessage(f"QR Code salvo em: {filename}", 5000)
            else:
                self.show_error("Erro ao salvar o QR Code")

    def copy_payload(self):
        """Copia o payload para a área de transferência"""
        if self.current_payload:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_payload)
            self.statusBar().showMessage("Código PIX copiado para a área de transferência!", 3000)

    def clear_form(self):
        """Limpa todos os campos do formulário"""
        self.chave_input.clear()
        self.valor_inteiro.setValue(0)
        self.valor_centavos.setValue(0)
        self.txid_input.clear()
        self.nome_input.setText("N")
        self.cidade_input.setText("C")
        self.qr_size.setValue(200)
        self.payload_text.clear()
        self.details_text.clear()
        self.qr_label.clear()
        self.current_payload = None
        self.save_qr_btn.setEnabled(False)
        self.statusBar().showMessage("Formulário limpo", 3000)

    def show_error(self, message):
        """Exibe uma mensagem de erro"""
        QMessageBox.critical(self, "Erro", message)
        self.statusBar().showMessage(f"Erro: {message}", 5000)

def verificar_dependencias():
    """Verifica se as dependências necessárias estão instaladas"""
    try:
        import qrcode
        from PIL import Image
        from PyQt6 import QtWidgets
        return True
    except ImportError as e:
        print(f"Erro: {e}. Instale as dependências com: pip install PyQt6 qrcode pillow")
        return False

def main():
    """Função principal que inicia a aplicação"""
    if not verificar_dependencias():
        sys.exit(1)
    
    app = QApplication(sys.argv)
    window = PixGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()