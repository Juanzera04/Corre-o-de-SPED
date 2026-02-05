import customtkinter as ctk
from tkinter import filedialog
import os
from collections import defaultdict

# CFOPs que precisam de ajuste
CFOPS_AJUSTE = ["1403", "1910", "1911", "1102", "2102", "2911", "2910", "2403"]

def to_float(s):
    try:
        s = str(s).strip()
        if s == "":
            return 0.0
        # remove separador de milhar e converte vírgula
        return float(s.replace(".", "").replace(",", "."))
    except:
        return 0.0

def atualizar_status(mensagem):
    terminal.configure(state="normal")
    terminal.delete("1.0", "end")
    terminal.insert("end", mensagem)
    terminal.configure(state="disabled")

def split_normalized(line):
    # divide e remove o primeiro item vazio se a linha começa com '|'
    parts = line.split("|")
    if len(parts) and parts[0] == "":
        parts = parts[1:]
    return parts

def join_from_normalized(parts):
    # reconstrói linha com '|' inicial (para manter formato original)
    return "|" + "|".join(parts)

def ajustar_sped(caminho_entrada, pasta_saida=""):
    try:
        atualizar_status("Ajustando o Bloco C...")

        with open(caminho_entrada, "r", encoding="latin-1") as f:
            linhas_raw = [ln.rstrip("\n") for ln in f]

        saida = []
        i = 0
        nota_cont = 0

        while i < len(linhas_raw):
            raw = linhas_raw[i]
            parts = split_normalized(raw)

            # início de nota
            if len(parts) > 0 and parts[0] == "C100":
                nota_cont += 1
                bloco_raw = [raw]
                bloco_parts = [parts]
                i += 1
                while i < len(linhas_raw):
                    if linhas_raw[i].startswith("|C100|"):
                        break
                    bloco_raw.append(linhas_raw[i])
                    bloco_parts.append(split_normalized(linhas_raw[i]))
                    i += 1

                # valor total da nota (C100 -> coluna 12 -> índice 11)
                try:
                    valor_total_nota = to_float(bloco_parts[0][11])
                except:
                    valor_total_nota = 0.0

                # soma total dos produtos (todas as C190 -> coluna 5 -> índice 4)
                soma_produtos = 0.0
                for bp in bloco_parts:
                    if len(bp) > 0 and bp[0] == "C190":
                        soma_produtos += to_float(bp[4])

                diff = soma_produtos - valor_total_nota

                # se já bate, não faz ajuste nenhum na nota
                if abs(diff) < 0.02:
                    # manter bloco original
                    saida.extend(bloco_raw)
                    continue

                # para cada CFOP de interesse, calculamos os totais e aplicamos ajuste
                # (ajuste será distribuído proporcionalmente entre os C190 desse CFOP)
                # primeiro vamos construir lookup de índices no bloco
                c190_indices_por_cfop = defaultdict(list)  # cfop -> list of (idx_in_bloco, valor)
                c197_totais_por_cfop = defaultdict(float)  # cfop -> soma impostos

                for idx, bp in enumerate(bloco_parts):
                    if len(bp) > 0 and bp[0] == "C190":
                        cfop = bp[2] if len(bp) > 2 else ""
                        valor = to_float(bp[4]) if len(bp) > 4 else 0.0
                        c190_indices_por_cfop[cfop].append((idx, valor))
                    if len(bp) > 0 and bp[0] == "C197":
                        codigo = bp[1] if len(bp) > 1 else ""
                        cfop = bp[2] if len(bp) > 2 else ""
                        # exceção SP90090104 para 1102 e 2102
                        if cfop in ["1102", "2102"] and codigo == "SP90090104":
                            continue
                        imposto = to_float(bp[6]) if len(bp) > 6 else 0.0
                        c197_totais_por_cfop[cfop] += imposto

                # agora aplicar ajuste por cfop
                # se diff > 0 -> soma_produtos > nota -> devemos SUBTRAIR impostos
                # se diff < 0 -> soma_produtos < nota -> devemos SOMAR impostos
                operacao = "subtrair" if diff > 0 else "somar"

                # vamos montar o bloco_parts atualizado (cópia mutável)
                bloco_parts_novo = [list(x) for x in bloco_parts]

                for cfop in CFOPS_AJUSTE:
                    c190_list = c190_indices_por_cfop.get(cfop, [])
                    imposto_total = c197_totais_por_cfop.get(cfop, 0.0)

                    if not c190_list or imposto_total == 0:
                        continue  # nada a fazer para este CFOP

                    soma_cfop_produtos = sum(v for _, v in c190_list)
                    if soma_cfop_produtos == 0:
                        continue

                    # distribuímos proporcionalmente o imposto entre as linhas C190 desse CFOP
                    for idx_in_bloco, valor_orig in c190_list:
                        proporcao = valor_orig / soma_cfop_produtos if soma_cfop_produtos else 0
                        delta = imposto_total * proporcao
                        if diff > 0:
                            # produtos maiores que nota -> subtrair
                            novo_val = valor_orig - delta
                            acao = "subtraindo"
                        else:
                            # produtos menores que nota -> somar
                            novo_val = valor_orig + delta
                            acao = "somando"

                        # atualizar valor (índice 4 no normalized parts)
                        bloco_parts_novo[idx_in_bloco][4] = f"{round(novo_val,2):.2f}".replace(".", ",")

                    # opcional: atualizar soma_produtos local (não estritamente necessário)
                    # mas mantemos para possível log
                # reconstruir linhas do bloco a partir de bloco_parts_novo
                for bp in bloco_parts_novo:
                    linha_nova = join_from_normalized(bp)
                    saida.append(linha_nova)

                # status resumido (uma linha)
                if diff > 0:
                    atualizar_status(f"Nota {nota_cont}: produtos maiores que nota (R$ {diff:.2f}) → subtraindo impostos por CFOP")
                else:
                    atualizar_status(f"Nota {nota_cont}: produtos menores que nota (R$ {abs(diff):.2f}) → somando impostos por CFOP")

            else:
                # linha fora de C100 (mantém como está)
                saida.append(raw)
                i += 1

        # linha em branco final
        saida.append("")

        # salvar
        if not pasta_saida:
            pasta_saida = os.path.dirname(caminho_entrada)
        nome_saida = os.path.join(pasta_saida, f"AJUSTADO_{os.path.basename(caminho_entrada)}")

        with open(nome_saida, "w", encoding="latin-1") as f:
            f.write("\n".join(saida))

        atualizar_status(f"SPED ajustado salvo em:\n{nome_saida}")

    except Exception as e:
        atualizar_status(f"[ERRO] {e}")

def selecionar_arquivo():
    caminho = filedialog.askopenfilename(
        title="Selecione o arquivo SPED",
        filetypes=[("Arquivos TXT", "*.txt")]
    )
    if caminho:
        ajustar_sped(caminho)

# --- Interface ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Ajustar SPED - Bloco C (Soma/Subtrai por CFOP)")
app.geometry("760x430")

titulo = ctk.CTkLabel(app, text="Ajuste Automático do SPED (Soma/Subtrai Impostos por CFOP)", font=("Arial", 18, "bold"))
titulo.pack(pady=14)

botao = ctk.CTkButton(app, text="Ajustar SPED", command=selecionar_arquivo, width=220, height=44)
botao.pack(pady=12)

terminal = ctk.CTkTextbox(app, height=90, width=720, font=("Consolas", 11))
terminal.pack(pady=10)
terminal.configure(state="disabled")

assinatura = ctk.CTkLabel(app, text="by: Juan Rodrigues", font=("Arial", 10, "italic"))
assinatura.pack(side="right", padx=10, pady=5)

app.mainloop()
