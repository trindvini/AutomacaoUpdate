import pandas as pd
import pyautogui
import time
import pyperclip
import pytesseract
import cv2
import numpy as np
import winsound
import keyboard  # Necessário: pip install keyboard
import sys
from datetime import datetime
from tkinter import (
    filedialog,
    Tk,
    Toplevel,
    Label,
    Entry,
    Button,
    Frame,
    Scrollbar,
    Listbox,
)

# --- CONFIGURAÇÃO OCR ---
# Caminho do executável do Tesseract no seu computador
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\vinicius.trindade\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)

# --- CONFIGURAÇÃO GERAL E COORDENADAS ---
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

# Coordenadas Base para OCR e Busca de Grupo
X_AREA_INI, Y_AREA_INI = 5, 226
X_AREA_FIM, Y_AREA_FIM = 810, 425

# --- COORDENADAS DE FLAGS (Cálculo para as linhas de lojas) ---
X_CHECKBOX = 1663
Y_PRIMEIRA_FLAG = 154
Y_ULTIMA_FLAG = 969
ALTURA_LINHA_PIXELS = (Y_ULTIMA_FLAG - Y_PRIMEIRA_FLAG) / 52
OFFSET_CORRECAO = ALTURA_LINHA_PIXELS

# Coordenadas de Arraste para selecionar a lista
X_TOPO_LISTA, Y_TOPO_LISTA = 233, 156
X_BASE_LISTA, Y_BASE_LISTA = 243, 972

# --- COORDENADAS DE INCLUSÃO (Botões da Linx) ---
BTN_INCLUIR = (859, 939)
BTN_MAXIMIZAR = (1160, 359)
CAMPO_GRUPO = (263, 57)
CAMPO_DESCRICAO = (261, 92)

# Cores da Linx (roxo e laranja) para o tema visual
THEME_BG = "#5B2585"  # roxo escuro
THEME_FG = "#FFFFFF"  # branco para texto
BTN_BG = "#FF6600"  # laranja para botões
BTN_FG = "#FFFFFF"  # texto nos botões
CANCEL_BG = "#FF0000"  # vermelho para botão encerrar

# Estado global de pausa
paused = False


def log_terminal_e_arquivo(mensagem):
    """Exibe a mensagem no terminal e salva no arquivo log_processamento.txt."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    msg_formatada = f"[{timestamp}] {mensagem}"
    print(msg_formatada)
    with open("log_processamento.txt", "a", encoding="utf-8") as f:
        f.write(msg_formatada + "\n")


def verificar_pausa():
    """Verifica se a tecla 'P' foi pressionada para pausar a automação."""
    global paused
    if keyboard.is_pressed("p"):
        inicio = time.time()
        while keyboard.is_pressed("p"):
            if time.time() - inicio >= 1.0:
                paused = not paused
                if paused:
                    log_terminal_e_arquivo("!!! SISTEMA PAUSADO PELO USUÁRIO !!!")
                    winsound.Beep(440, 500)
                else:
                    log_terminal_e_arquivo(">>> SISTEMA RETOMADO <<<")
                    winsound.Beep(880, 500)
                time.sleep(0.5)
                break
            time.sleep(0.1)

    while paused:
        time.sleep(0.1)
        if keyboard.is_pressed("p"):
            inicio = time.time()
            while keyboard.is_pressed("p"):
                if time.time() - inicio >= 1.0:
                    paused = False
                    log_terminal_e_arquivo(">>> SISTEMA RETOMADO <<<")
                    winsound.Beep(880, 500)
                    time.sleep(0.5)
                    break
                time.sleep(0.1)


def esta_marcado(x, y):
    """Verifica se a checkbox na tela já está preenchida."""
    try:
        pyautogui.moveTo(x, y)
        time.sleep(0.2)
        pix = pyautogui.pixel(int(x), int(y))
        if pix[0] > 240 and pix[1] > 240 and pix[2] > 240:
            return False
        return True
    except:
        return False


def localizar_centro_do_grupo_ocr(texto_alvo, minucioso=False):
    """Usa OCR para encontrar o nome do grupo na tela."""
    pyautogui.moveTo(X_AREA_FIM + 50, Y_AREA_FIM + 50)
    screenshot = pyautogui.screenshot(
        region=(
            X_AREA_INI,
            Y_AREA_INI,
            X_AREA_FIM - X_AREA_INI,
            Y_AREA_FIM - Y_AREA_INI,
        )
    )
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fator = 3 if minucioso else 2
    img_res = cv2.resize(gray, None, fx=fator, fy=fator, interpolation=cv2.INTER_CUBIC)
    if minucioso:
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        img_res = cv2.filter2D(img_res, -1, kernel)
    dados_ocr = pytesseract.image_to_data(
        img_res, lang="por", config="--psm 6", output_type=pytesseract.Output.DICT
    )
    alvo_str = str(texto_alvo).strip().lower()
    for i, raw in enumerate(dados_ocr["text"]):
        texto = str(raw or "").strip()
        if texto.lower() == alvo_str:
            log_terminal_e_arquivo(f"OCR encontrou correspondência exata: '{texto}'")
            return X_AREA_INI + (dados_ocr["left"][i] // fator) + (
                dados_ocr["width"][i] // (fator * 2)
            ), Y_AREA_INI + (dados_ocr["top"][i] // fator) + (
                dados_ocr["height"][i] // (fator * 2)
            )
    return None


# --- FUNÇÕES DE INTERFACE ---


def center_window(win, width=400, height=300):
    """Centraliza as janelas na tela."""
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = int((screen_w - width) / 2)
    y = int((screen_h - height) / 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


def custom_alert(root, message, title=""):
    """Alerta personalizado com o tema Linx."""
    dlg = Tk() if root is None else Toplevel(root)
    dlg.title(title)
    dlg.configure(bg=THEME_BG)
    lbl = Label(dlg, text=message, bg=THEME_BG, fg=THEME_FG, wraplength=400)
    lbl.pack(padx=20, pady=20)
    btn = Button(dlg, text="OK", command=dlg.destroy, bg=BTN_BG, fg=BTN_FG)
    btn.pack(pady=10)
    dlg.bind("<Return>", lambda e: dlg.destroy())
    center_window(dlg, width=450, height=200)

    dlg.lift()
    dlg.attributes("-topmost", True)
    dlg.grab_set()
    btn.focus_force()
    dlg.wait_window()


def ask_yes_no_cancel(root, title, message):
    """Janela de decisão com três opções."""
    result = {"value": None}
    try:
        root_visible = bool(root.winfo_viewable())
    except Exception:
        root_visible = False
    is_temp_root = not root_visible
    dlg = Tk() if is_temp_root else Toplevel(root)
    dlg.title(title)
    dlg.configure(bg=THEME_BG)

    lbl = Label(
        dlg, text=message, bg=THEME_BG, fg=THEME_FG, wraplength=420, justify="left"
    )
    lbl.pack(padx=20, pady=20)
    frame = Frame(dlg, bg=THEME_BG)
    frame.pack(pady=(0, 20))

    def set_true():
        result["value"] = True
        dlg.destroy()

    def set_false():
        result["value"] = False
        dlg.destroy()

    def set_cancel():
        result["value"] = None
        dlg.destroy()

    btn_yes = Button(
        frame,
        text="Buscar de novo",
        command=set_true,
        bg=BTN_BG,
        fg=BTN_FG,
        font=("Arial", 10),
    )
    btn_no = Button(
        frame,
        text="Incluir grupo",
        command=set_false,
        bg=BTN_BG,
        fg=BTN_FG,
        font=("Arial", 10),
    )
    btn_cancel = Button(
        frame,
        text="Encerrar",
        command=set_cancel,
        bg=CANCEL_BG,
        fg=BTN_FG,
        font=("Arial", 10),
    )
    btn_yes.pack(side="left", padx=5)
    btn_no.pack(side="left", padx=5)
    btn_cancel.pack(side="left", padx=5)

    buttons = [btn_yes, btn_no, btn_cancel]
    current_button = [0]

    def navigate_buttons(direction):
        current_button[0] = (current_button[0] + direction) % len(buttons)
        buttons[current_button[0]].focus_set()

    def on_key(event):
        if event.keysym in ["Left", "Prior"]:
            navigate_buttons(-1)
        elif event.keysym in ["Right", "Next"]:
            navigate_buttons(1)
        elif event.keysym == "Return":
            buttons[current_button[0]].invoke()

    dlg.bind("<Left>", on_key)
    dlg.bind("<Right>", on_key)
    dlg.bind("<Prior>", on_key)
    dlg.bind("<Next>", on_key)
    dlg.bind("<Return>", on_key)

    center_window(dlg, width=500, height=220)
    if not is_temp_root:
        try:
            dlg.transient(root)
        except Exception:
            pass
    dlg.lift()
    try:
        dlg.attributes("-topmost", True)
    except Exception:
        pass
    try:
        dlg.grab_set()
    except Exception:
        pass
    btn_yes.focus_force()
    try:
        if is_temp_root:
            dlg.wait_window()
        else:
            root.update()
            root.wait_window(dlg)
    finally:
        if is_temp_root:
            try:
                dlg.destroy()
            except Exception:
                pass
    return result["value"]


# --- INÍCIO DO SCRIPT ---
root = Tk()
root.withdraw()
caminho_arquivo = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
root.update()
if not caminho_arquivo:
    root.destroy()
    exit()

df = pd.read_excel(caminho_arquivo)
df["Codigo_loja"] = (
    df["Codigo_loja"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
)

if "Descrição do Grupo" not in df.columns:
    log_terminal_e_arquivo(
        "ERRO: Coluna 'Descrição do Grupo' não encontrada na planilha."
    )
    root.destroy()
    exit()

lista_grupos = list(df["Grupo"].unique())
if not lista_grupos:
    custom_alert(root, "Nenhum grupo encontrado na planilha.", "Erro")
    root.destroy()
    exit()

root.title("Sistema de Automação - Inclusão de Lojas")
root.configure(bg=THEME_BG)
center_window(root, width=600, height=400)

header = Label(
    root,
    text="Grupos Carregados da Planilha",
    bg=THEME_BG,
    fg=THEME_FG,
    font=("Arial", 14, "bold"),
)
header.pack(pady=10)

frame_grupos = Frame(root, bg=THEME_BG)
frame_grupos.pack(fill="both", expand=True, padx=10, pady=10)

listbox_grupos = Listbox(
    frame_grupos, bg="white", fg="black", font=("Arial", 10), height=10
)
scrollbar = Scrollbar(frame_grupos, orient="vertical", command=listbox_grupos.yview)
listbox_grupos.config(yscrollcommand=scrollbar.set)
listbox_grupos.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

for idx, grp in enumerate(lista_grupos):
    listbox_grupos.insert("end", f"{idx} - {grp}")

frame_selecao = Frame(root, bg=THEME_BG)
frame_selecao.pack(pady=10)

label_selecao = Label(
    frame_selecao,
    text="Digite o número do grupo:",
    bg=THEME_BG,
    fg=THEME_FG,
    font=("Arial", 10),
)
label_selecao.pack(side="left", padx=5)

entry_grupo = Entry(frame_selecao, width=10, font=("Arial", 10))
entry_grupo.pack(side="left", padx=5)

frame_botoes = Frame(root, bg=THEME_BG)
frame_botoes.pack(pady=10)

indice_inicio = None


def iniciar_automacao():
    global indice_inicio
    try:
        indice_inicio = int(entry_grupo.get())
        if 0 <= indice_inicio < len(lista_grupos):
            root.withdraw()
            root.quit()
        else:
            custom_alert(
                root,
                f"Por favor, digite um número entre 0 e {len(lista_grupos) - 1}",
                "Número Inválido",
            )
            indice_inicio = None
    except ValueError:
        custom_alert(root, "Por favor, digite um número válido", "Erro")


entry_grupo.bind("<Return>", lambda e: iniciar_automacao())


def on_group_select(evt):
    sel = evt.widget.curselection()
    if sel:
        entry_grupo.delete(0, "end")
        entry_grupo.insert(0, str(sel[0]))


listbox_grupos.bind("<<ListboxSelect>>", on_group_select)

btn_iniciar = Button(
    frame_botoes,
    text="Iniciar Automação",
    command=iniciar_automacao,
    bg=BTN_BG,
    fg=BTN_FG,
    font=("Arial", 10),
    padx=10,
)
btn_iniciar.pack(side="left", padx=5)


def encerrar():
    root.destroy()
    sys.exit(0)


btn_encerrar = Button(
    frame_botoes,
    text="Encerrar",
    command=encerrar,
    bg=CANCEL_BG,
    fg=BTN_FG,
    font=("Arial", 10),
    padx=10,
)
btn_encerrar.pack(side="left", padx=5)


def on_closing():
    global indice_inicio
    if indice_inicio is None:
        root.destroy()
        sys.exit(0)
    else:
        root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.deiconify()
entry_grupo.focus_force()
root.mainloop()

if indice_inicio is None:
    root.destroy()
    exit()

grupos_para_processar = lista_grupos[indice_inicio:]

# Cria o arquivo de log limpo no início
with open("log_processamento.txt", "w", encoding="utf-8") as f:
    f.write(f"Início da Sessão: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

log_terminal_e_arquivo(f"Sessão iniciada. {len(df)} registros carregados.")
time.sleep(2)
tentativa_minuciosa = False

for grupo in grupos_para_processar:
    if pd.isna(grupo):
        continue
    grupo_str = str(grupo).strip()
    desc_grupo = str(df[df["Grupo"] == grupo]["Descrição do Grupo"].iloc[0]).strip()
    lojas_excel = df[df["Grupo"] == grupo]["Codigo_loja"].tolist()
    # Criamos um set de lojas pendentes para este grupo
    lojas_pendentes = set(lojas_excel)

    marcadas_agora, ja_estavam_marcadas, nao_encontradas = [], [], []
    log_terminal_e_arquivo("=" * 50)
    log_terminal_e_arquivo(f"PROCESSANDO GRUPO: {grupo_str}")
    log_terminal_e_arquivo("=" * 50)

    ponto_grupo = None
    fluxo_inclusao = False

    while True:
        verificar_pausa()
        pyautogui.click(164, 168)
        pyautogui.click(155, 203)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        pyperclip.copy(grupo_str)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")

        ponto_grupo = localizar_centro_do_grupo_ocr(
            grupo_str, minucioso=tentativa_minuciosa
        )

        if ponto_grupo:
            pyautogui.click(ponto_grupo)
            time.sleep(0.4)
            pyautogui.click(966, 944)
            time.sleep(2)
            pyautogui.click(BTN_MAXIMIZAR)
            time.sleep(0.8)
            tentativa_minuciosa = False
            break
        else:
            if not tentativa_minuciosa:
                tentativa_minuciosa = True
                log_terminal_e_arquivo(
                    f"Tentativa normal falhou para '{grupo_str}', executando busca minuciosa."
                )
                continue

            msg = f"Grupo '{grupo_str}' não localizado.\n\nEscolha uma opção:"
            escolha = ask_yes_no_cancel(root, "Tente outra forma", msg)

            if escolha is True:
                tentativa_minuciosa = True
                continue
            elif escolha is False:
                log_terminal_e_arquivo(
                    f"Iniciando fluxo de INCLUSÃO para o grupo: {grupo_str}"
                )
                pyautogui.click(BTN_INCLUIR)
                time.sleep(0.4)
                pyautogui.click(BTN_MAXIMIZAR)
                time.sleep(0.8)
                pyautogui.click(CAMPO_GRUPO)
                pyperclip.copy(grupo_str)
                pyautogui.hotkey("ctrl", "v")
                pyautogui.click(CAMPO_DESCRICAO)
                pyperclip.copy(desc_grupo)
                pyautogui.hotkey("ctrl", "v")
                fluxo_inclusao = True
                break
            else:
                confirmar = ask_yes_no_cancel(
                    root, "Confirmar Encerrar", "Deseja realmente encerrar a automação?"
                )
                if confirmar:
                    root.destroy()
                    sys.exit(0)
                else:
                    continue

    if ponto_grupo or fluxo_inclusao:
        # --- NOVO FLUXO DE BUSCA POR FRAME ---
        pyautogui.click(X_TOPO_LISTA, Y_TOPO_LISTA)
        pyautogui.press("home")
        time.sleep(0.5)

        previous_text = None
        for t in range(72):
            verificar_pausa()

            # Se não houver mais lojas pendentes, encerramos a busca neste grupo
            if not lojas_pendentes:
                break

            pyperclip.copy("")
            pyautogui.moveTo(X_TOPO_LISTA, Y_TOPO_LISTA)
            pyautogui.mouseDown(button="left")
            pyautogui.moveTo(X_BASE_LISTA, Y_BASE_LISTA, duration=0.1)
            pyautogui.moveRel(-5, 0, duration=0.03)
            pyautogui.moveRel(10, 0, duration=0.03)
            pyautogui.moveRel(-5, 0, duration=0.03)
            pyautogui.mouseUp(button="left")
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.1)

            texto_bloco = pyperclip.paste() or ""
            if previous_text is not None and texto_bloco == previous_text:
                break
            previous_text = texto_bloco

            if texto_bloco:
                linhas_na_tela = texto_bloco.splitlines()
                # Para cada linha capturada no frame atual, testamos todas as lojas pendentes
                for idx_linha, linha_texto in enumerate(linhas_na_tela):
                    # Fazemos uma cópia da lista para poder remover itens enquanto iteramos
                    for cod_loja in list(lojas_pendentes):
                        if cod_loja in linha_texto:
                            y_clique = (
                                Y_PRIMEIRA_FLAG
                                + (idx_linha * ALTURA_LINHA_PIXELS)
                                + OFFSET_CORRECAO
                            )

                            if esta_marcado(X_CHECKBOX, y_clique):
                                log_terminal_e_arquivo(
                                    f"  [JÁ MARCADA] Loja: {cod_loja}"
                                )
                                ja_estavam_marcadas.append(cod_loja)
                            else:
                                pyautogui.click(X_CHECKBOX, int(y_clique))
                                log_terminal_e_arquivo(
                                    f"  [ACHADA/OK]  Loja: {cod_loja}"
                                )
                                marcadas_agora.append(cod_loja)
                                winsound.Beep(800, 100)

                            # Remove das pendentes pois já foi processada neste grupo
                            lojas_pendentes.remove(cod_loja)

            # Após checar todas as lojas na tela atual, descemos para a próxima
            if lojas_pendentes:
                pyautogui.press("pagedown")
                time.sleep(0.1)

        # Ao final do scroll, o que restou em lojas_pendentes são as não encontradas
        for cod_restante in lojas_pendentes:
            log_terminal_e_arquivo(f"  [NÃO ACHADA] Loja: {cod_restante}")
            nao_encontradas.append(cod_restante)

        msg_resumo = (
            f"Grupo {grupo_str} Finalizado\n\n"
            f"✅ Marcadas agora: {len(marcadas_agora)}\n"
            f"⚪ Já estavam marcadas: {len(ja_estavam_marcadas)}\n"
            f"❌ Não encontradas: {len(nao_encontradas)}"
        )
        log_terminal_e_arquivo("-" * 30)
        log_terminal_e_arquivo(f"RESUMO GRUPO {grupo_str} CONCLUÍDO")
        log_terminal_e_arquivo("-" * 30)
        custom_alert(root, msg_resumo, title="Resumo do Grupo")

log_terminal_e_arquivo(">>> PROCESSO CONCLUÍDO COM SUCESSO <<<")
root.destroy()