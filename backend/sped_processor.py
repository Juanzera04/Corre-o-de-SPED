from decimal import Decimal

# ======================================================
# 1️⃣ CÁLCULO DE PIS / COFINS
# ======================================================

def processar_sped(arquivo_entrada, arquivo_saida):

    PIS_IDX = 29
    COFINS_IDX = 35
    C175_PIS_IDX = 9
    C175_COF_IDX = 15

    TARGET_PIS_C100_IDX = 25
    TARGET_COF_C100_IDX = 26
    IDENT_IDX = 5  # Identificação da nota (C100)

    def parse_line(line):
        return line.rstrip("\n").strip("|").split("|")

    def montar_linha(campos):
        while campos and campos[-1] == "":
            campos.pop()
        return "|" + "|".join(campos) + "|\n"

    def to_float_safe(s):
        if not s:
            return None
        try:
            return float(s.replace(",", "."))
        except:
            return None

    with open(arquivo_entrada, "r", encoding="latin-1") as f:
        linhas = f.readlines()

    saida = []
    bloco_atual = []
    c100_campos = None
    total_pis = 0.0
    total_cofins = 0.0

    def salvar_bloco():
        nonlocal c100_campos, bloco_atual, total_pis, total_cofins

        if not c100_campos:
            return

        ident = c100_campos[IDENT_IDX]

        while len(c100_campos) <= TARGET_COF_C100_IDX:
            c100_campos.append("")

        if total_pis == 0 and ident in {"02", "04", "05"}:
            c100_campos[TARGET_PIS_C100_IDX] = ""
        else:
            c100_campos[TARGET_PIS_C100_IDX] = f"{total_pis:.2f}".replace(".", ",")

        if total_cofins == 0 and ident in {"02", "04", "05"}:
            c100_campos[TARGET_COF_C100_IDX] = ""
        else:
            c100_campos[TARGET_COF_C100_IDX] = f"{total_cofins:.2f}".replace(".", ",")

        saida.append(montar_linha(c100_campos))
        saida.extend(bloco_atual)

        bloco_atual.clear()
        c100_campos = None
        total_pis = total_cofins = 0.0

    for linha in linhas:
        if linha.startswith("|C100"):
            salvar_bloco()
            c100_campos = parse_line(linha)

        elif linha.startswith("|C170"):
            campos = parse_line(linha)
            pis = to_float_safe(campos[PIS_IDX] if len(campos) > PIS_IDX else "")
            cof = to_float_safe(campos[COFINS_IDX] if len(campos) > COFINS_IDX else "")
            total_pis += pis or 0
            total_cofins += cof or 0
            bloco_atual.append(linha)

        elif linha.startswith("|C175"):
            campos = parse_line(linha)
            pis = to_float_safe(campos[C175_PIS_IDX] if len(campos) > C175_PIS_IDX else "")
            cof = to_float_safe(campos[C175_COF_IDX] if len(campos) > C175_COF_IDX else "")
            total_pis += pis or 0
            total_cofins += cof or 0
            bloco_atual.append(linha)

        else:
            salvar_bloco()
            saida.append(linha)

    salvar_bloco()

    with open(arquivo_saida, "w", encoding="latin-1") as f:
        f.writelines(saida)


# ======================================================
# 2️⃣ CONSOLIDAÇÃO DE C175
# ======================================================

def processar_c175(entrada, saida):

    CST_PERMITIDOS = {'01', '02', '04', '06', '07', '08'}

    with open(entrada, "r", encoding="latin-1") as f:
        linhas = f.readlines()

    resultado = []
    bloco = []
    removidas = 0

    def consolidar(bloco):
        nonlocal removidas
        grupos = {}

        for l in bloco:
            c = l.strip().split("|")
            chave = (c[2], c[5])
            grupos.setdefault(chave, []).append(c)

        saida = []

        for linhas in grupos.values():
            if len(linhas) == 1 or linhas[0][5] not in CST_PERMITIDOS:
                saida.append("|".join(linhas[0]) + "\n")
            else:
                soma1 = sum(Decimal(l[3].replace(",", ".")) for l in linhas)
                soma2 = sum(Decimal(l[4].replace(",", ".")) for l in linhas)
                base = linhas[0]
                base[3] = f"{soma1:.2f}".replace(".", ",")
                base[4] = f"{soma2:.2f}".replace(".", ",")
                saida.append("|".join(base) + "\n")
                removidas += len(linhas) - 1

        return saida

    for l in linhas:
        if l.startswith("|C175"):
            bloco.append(l)
        else:
            if bloco:
                resultado.extend(consolidar(bloco))
                bloco.clear()
            resultado.append(l)

    if bloco:
        resultado.extend(consolidar(bloco))

    with open(saida, "w", encoding="latin-1") as f:
        f.writelines(resultado)

    return removidas
