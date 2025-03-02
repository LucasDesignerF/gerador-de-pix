# Gerador de Pix 🎉

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)  
![License](https://img.shields.io/badge/License-MIT-green.svg)  
![Author](https://img.shields.io/badge/Author-LucasDesignerF-orange.svg)

Bem-vindo ao **Gerador de Pix**, um aplicativo Python com interface gráfica moderna que cria chaves Pix "Copia e Cola" e QR Codes válidos para transações no sistema Pix do Banco Central do Brasil! 🚀 Desenvolvido com paixão por **[LucasDesignerF](https://github.com/LucasDesignerF)**, este projeto é perfeito para quem precisa gerar Pix de forma rápida, prática e confiável.

---

## 📜 Sobre o Projeto

O **Gerador de Pix** é uma ferramenta desktop construída com `PyQt6`, que permite:
- Gerar payloads Pix no padrão EMV BRCode.
- Criar QR Codes escaneáveis por aplicativos de banco.
- Copiar o código "Copia e Cola" para uso direto em apps financeiros.
- Personalizar chaves Pix (e-mail, CPF, CNPJ, telefone, chave aleatória), valores, identificadores (txid), nome do recebedor e cidade.
- Alternar entre temas claro e escuro para uma experiência visual agradável.

Testado e validado com sucesso em aplicativos de banco e no site **[pix.nascent.com.br](https://pix.nascent.com.br)**! ✅

---

## ✨ Funcionalidades

- **Interface Moderna**: Layout dividido com formulário e resultados, estilizado com temas claro/escuro. 🌞🌙
- **Validação de Chaves**: Suporta diferentes tipos de chaves Pix com verificação básica (ex.: e-mail precisa ter "@"). 🔑
- **Geração de QR Code**: QR Codes ajustáveis (100 a 1000px) salváveis como imagem PNG. 📸
- **Copia e Cola**: Copie o payload Pix com um clique para usar em apps de banco. 📋
- **Detalhes Técnicos**: Exibe os campos EMV decodificados do payload gerado. 📊
- **Robustez**: Tratamento de erros com mensagens claras e status na barra inferior. 🚨

---

## 🚀 Como Usar

### Pré-requisitos
- **Python**: Versão 3.7 ou superior instalado.
- **Dependências**: Listadas no `requirements.txt`.

### Instalação
1. Clone o repositório do GitHub:
   ```bash
   git clone https://github.com/LucasDesignerF/gerador-de-pix.git
   cd gerador-de-pix
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute o aplicativo:
   ```bash
   python main.py
   ```

---

### Uso Básico
1. Abra o aplicativo e preencha os campos no formulário:
   - **Tipo de Chave**: Escolha entre "E-mail", "CPF", "CNPJ", "Telefone" ou "Chave aleatória".
   - **Chave PIX**: Insira sua chave (ex.: `seu.email@example.com`).
   - **Valor**: Defina o valor em reais e centavos (ex.: R$ 10,00).
   - **Identificador (txid)**: Um ID único para a transação (ex.: `testepix`).
   - **Nome e Cidade**: Opcional (padrão: `N` e `C`).
   - **Tamanho do QR**: Ajuste o tamanho do QR Code (padrão: 200px).

2. Clique em **"Gerar Pix"**! 🎉
   - O payload "Copia e Cola" aparecerá na caixa de texto.
   - O QR Code será exibido ao lado.
   - Detalhes do payload serão mostrados abaixo.

3. **Copiar ou Salvar**:
   - Clique em "Copiar Código" para copiar o payload para a área de transferência. 📋
   - Clique em "Salvar QR Code" para salvar o QR como imagem PNG. 💾

4. Teste o resultado:
   - Use o "Copia e Cola" ou escaneie o QR Code em um aplicativo de banco (ex.: Nubank, Banco do Brasil). 🏦

---

## 📋 Exemplo de Uso

**Entrada**:
- Tipo de Chave: E-mail
- Chave PIX: `fortes.barman@gmail.com`
- Valor: R$ 10,00
- Txid: `testepix`
- Nome: `N`
- Cidade: `C`

**Saída** (Payload):
```
00020126450014BR.GOV.BCB.PIX0123fortes.barman@gmail.com520400005303986540510.005802BR5901N6001C62120508testepix6304909F
```

**QR Code**: Gerado e exibido na interface, pronto para escaneamento! 📲

---

## 🛠️ Dependências

O projeto utiliza as seguintes bibliotecas (listadas no `requirements.txt`):
```plaintext
PyQt6>=6.6.1
qrcode>=7.4.2
pillow>=10.2.0
```

Instale com:
```bash
pip install -r requirements.txt
```

---

## 🎨 Interface

- **Tema Claro**: Fundo claro (#f5f5f5) com texto escuro (#333333) e botões verdes (#4CAF50). 🌞
- **Tema Escuro**: Fundo escuro (#2b2b2b) com texto claro (#e0e0e0) e botões verdes (#4CAF50). 🌙
- **Botões**:
  - "Gerar Pix": Cria o payload e QR Code. ✅
  - "Limpar": Reseta o formulário. 🧹
  - "Modo Escuro/Claro": Alterna entre temas. 🔄
  - "Copiar Código": Copia o payload. 📋
  - "Salvar QR Code": Salva o QR como imagem. 💾

---

## 🧑‍💻 Autor

Desenvolvido por **[LucasDesignerF](https://github.com/LucasDesignerF)** 👨‍💻  
- Perfil no GitHub: [github.com/LucasDesignerF](https://github.com/LucasDesignerF)  
- Contato: Sinta-se à vontade para abrir uma issue ou me enviar uma mensagem! 📬

---

## 📝 Licença

Este projeto está licenciado sob a **[Licença MIT](LICENSE)**. Veja o arquivo `LICENSE` para mais detalhes. 📜

---

## 🤝 Contribuições

Quer ajudar a melhorar o Gerador de Pix? 🌟
1. Faça um fork do repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-ideia`).
3. Commit suas mudanças (`git commit -m "Adiciona nova funcionalidade"`).
4. Push para o repositório (`git push origin feature/nova-ideia`).
5. Abra um Pull Request! 🚀

Sugestões de melhorias:
- Suporte a valores sem casas decimais (ex.: `10` em vez de `10.00`).
- Exportação do QR Code como PDF.
- Validação mais rígida para nome e cidade.

---

## 🚨 Solução de Problemas

- **Erro ao executar**: Certifique-se de que todas as dependências estão instaladas (`pip install -r requirements.txt`).
- **QR Code não funciona**: Verifique se o payload é válido em **[pix.nascent.com.br](https://pix.nascent.com.br)**.
- **Dúvidas**: Abra uma issue no GitHub! 📢

---

## ⭐ Agradecimentos

Obrigado por usar o Gerador de Pix! Este projeto foi criado com ❤️ para facilitar transações Pix no Brasil. Se gostou, deixe uma estrela no repositório! 🌟

Feito por **[LucasDesignerF](https://github.com/LucasDesignerF)** em 2025. 🇧🇷
