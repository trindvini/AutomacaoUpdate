# 🤖 Automação Linx: Vínculo de Lojas e Grupos v1.0.0

Esta ferramenta automatiza o processo manual e repetitivo de associar códigos de lojas a grupos dentro do sistema Linx. Utilizando técnicas de RPA (Robotic Process Automation) e Visão Computacional, o script garante precisão e alta performance, eliminando o erro humano e reduzindo drasticamente o tempo de operação.
<br /><br />
## ✨ Funcionalidades Principais

- Busca por OCR (Reconhecimento Óptico de Caracteres): Localiza dinamicamente os grupos na tela através do Tesseract OCR, adaptando-se a diferentes resoluções.
- Varredura Inteligente por Frame: Diferente de automações lineares, este bot analisa o quadro atual da tela e marca todas as lojas pendentes de uma só vez antes de realizar o scroll, otimizando o fluxo.
- Interface Gráfica (GUI): Janelas interativas em Tkinter para seleção de arquivos, escolha de grupos e exibição de resumos detalhados.
- Sistema de Log Robusto: Gera registros em tempo real no terminal e em arquivo .txt, permitindo auditoria total de quais lojas foram marcadas, quais já estavam ativas e quais não foram localizadas.
- Controle de Fluxo: Atalhos de teclado para pausa imediata (P) e tratamento de exceções (Fail-safe).
<br /><br />
## 📋 Pré-requisitos
### Antes de rodar o projeto, você precisará ter:
- Python 3.x instalado.
- Tesseract OCR instalado no Windows.
<br /><br />
### Nota: 
O caminho padrão configurado no código é C:\Users\(SEU USUARIO)\AppData\Local\Programs\Tesseract-OCR\tesseract.exe. Caso o seu seja diferente, ajuste a variável pytesseract.tesseract_cmd (ajuste o (SEU USUARIO) pelo nome do usuário do seu pc).
<br /><br />
## 🚀 Instalação
### Clone o repositório:
git clone https://github.com/seu-usuario/automacao-linx-lojas.git

### Navegue até a pasta:
cd automacao-linx-lojas

### Instale as dependências:
pip install -r requirements.txt
<br /><br />
## 🛠️ Como Usar
### Prepare sua planilha Excel com as colunas: Grupo, Descrição do Grupo e Codigo_loja.
### Execute o script:
python main.py
### Selecione o arquivo Excel quando solicitado.
### Escolha o grupo inicial na lista da interface gráfica.
### Atenção: Deixe a tela do Linx visível e maximizada. O bot assumirá o controle do mouse e teclado.
### Dica: Pressione 'P' por 1 segundo se precisar pausar a execução.
<br />

## ⚙️ Detalhes Técnicos
### Lógica de Busca: 
O bot utiliza o método PageDown para navegar na lista de lojas. Ele compara o conteúdo da área de transferência (Ctrl+C) para detectar o fim da lista (EOF), evitando loops infinitos.

### Cálculo de Coordenadas: 
O sistema utiliza cálculos baseados em offsets para clicar precisamente nas checkboxes laterais, independente da quantidade de linhas visíveis por página.
Lógica de Busca: O bot utiliza o método PageDown para navegar na lista de lojas. Ele compara o conteúdo da área de transferência (Ctrl+C) para detectar o fim da lista (EOF), evitando loops infinitos.

### Cálculo de Coordenadas: 
O sistema utiliza cálculos baseados em offsets para clicar precisamente nas checkboxes laterais, independente da quantidade de linhas visíveis por página.
<br /><br />
---
#### Desenvolvido por Vinícius Trindade - Focado em eficiência e automação de processos.
---
