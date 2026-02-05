def processar_sped(arquivo_entrada, arquivo_saida):

    PIS_IDX = 29       # índice 0-based no C170
    COFINS_IDX = 35    # índice 0-based no C170
    C175_PIS_IDX = 9     # coluna 10
    C175_COF_IDX = 15    # coluna 16

    TARGET_PIS_C100_IDX = 25   # onde escrever no C100
    TARGET_COF_C100_IDX = 26

    def parse_line(line):
        return line.rstrip("\n").strip("|").split("|")

    def montar_linha(campos):
        return "|" + "|".join(campos) + "|\n"

    def to_float_safe(s):
        if s is None:
            return None
        s = s.replace(",", ".").strip()
        if s == "":
            return None
        try:
            return float(s)
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
        nonlocal c100_campos, bloco_atual, total_pis, total_cofins, saida

        if c100_campos is None:
            return

        tamanho_necessario = TARGET_COF_C100_IDX + 1
        if len(c100_campos) < tamanho_necessario:
            c100_campos += [""] * (tamanho_necessario - len(c100_campos))

        if total_pis > 0:
            c100_campos[TARGET_PIS_C100_IDX] = f"{total_pis:.2f}".replace(".", ",")
        else:
            c100_campos[TARGET_PIS_C100_IDX] = ""

        if total_cofins > 0:
            c100_campos[TARGET_COF_C100_IDX] = f"{total_cofins:.2f}".replace(".", ",")
        else:
            c100_campos[TARGET_COF_C100_IDX] = ""


        # Garantir três campos vazios no final do C100
        c100_campos += ["", ""]

        saida.append(montar_linha(c100_campos))


        for c170 in bloco_atual:
            saida.append(c170)

        bloco_atual = []
        c100_campos = None
        total_pis = 0.0
        total_cofins = 0.0

    for linha in linhas:
        if linha.startswith("|C100"):
            salvar_bloco()
            c100_campos = parse_line(linha)
            bloco_atual = []
            total_pis = 0.0
            total_cofins = 0.0

        elif linha.startswith("|C170"):
            campos = parse_line(linha)

            max_needed = max(PIS_IDX, COFINS_IDX)
            if len(campos) <= max_needed:
                campos += [""] * (max_needed + 1 - len(campos))

            pis = to_float_safe(campos[PIS_IDX])
            cof = to_float_safe(campos[COFINS_IDX])

            if pis is not None:
                total_pis += pis
            if cof is not None:
                total_cofins += cof

            bloco_atual.append(linha)

        elif linha.startswith("|C175"):
            campos = parse_line(linha)

            max_needed = max(C175_PIS_IDX, C175_COF_IDX)
            if len(campos) <= max_needed:
                campos += [""] * (max_needed + 1 - len(campos))

            pis = to_float_safe(campos[C175_PIS_IDX])
            cof = to_float_safe(campos[C175_COF_IDX])

            if pis is not None:
                total_pis += pis
            if cof is not None:
                total_cofins += cof

            bloco_atual.append(linha)

        else:
            salvar_bloco()
            saida.append(linha)

    salvar_bloco()

    with open(arquivo_saida, "w", encoding="latin-1") as f:
        f.writelines(saida)
