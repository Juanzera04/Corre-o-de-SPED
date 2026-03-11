import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Processador SPED C110")
        self.geometry("600x350")
        self.resizable(False, False)

        self.arquivo_path = None

        # Título
        self.titulo = ctk.CTkLabel(
            self,
            text="Processador de SPED",
            font=("Arial", 22, "bold")
        )
        self.titulo.pack(pady=20)

        # Botão selecionar arquivo
        self.btn_selecionar = ctk.CTkButton(
            self,
            text="Selecionar Arquivo",
            command=self.selecionar_arquivo
        )
        self.btn_selecionar.pack(pady=10)

        # Label do arquivo
        self.label_arquivo = ctk.CTkLabel(
            self,
            text="Nenhum arquivo selecionado",
            wraplength=500
        )
        self.label_arquivo.pack(pady=5)

        # Botão processar
        self.btn_processar = ctk.CTkButton(
            self,
            text="Processar",
            command=self.processar_arquivo,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.btn_processar.pack(pady=20)

        # Barra de progresso
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=10)

        # Status
        self.status = ctk.CTkLabel(self, text="")
        self.status.pack()

    def selecionar_arquivo(self):
        path = filedialog.askopenfilename(
            filetypes=[("Arquivos SPED", "*.txt")]
        )

        if path:
            self.arquivo_path = path
            self.label_arquivo.configure(text=path)

    def processar_arquivo(self):
        if not self.arquivo_path:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return

        self.progress.set(0)
        self.status.configure(text="Processando...")

        # 🔹 Define nome de saída com sufixo CORRIGIDO
        pasta = os.path.dirname(self.arquivo_path)
        nome_original = os.path.splitext(os.path.basename(self.arquivo_path))[0]
        arquivo_saida = os.path.join(pasta, f"{nome_original}_CORRIGIDO.txt")

        codigos_c110 = set()

        # 🔹 Detecta encoding automaticamente
        try:
            arquivo_teste = open(self.arquivo_path, "r", encoding="utf-8")
            arquivo_teste.read()
            arquivo_teste.close()
            encoding_usado = "utf-8"
        except UnicodeDecodeError:
            encoding_usado = "cp1252"

        # Conta linhas
        with open(self.arquivo_path, "r", encoding=encoding_usado) as f:
            total_linhas = sum(1 for _ in f)

        with open(self.arquivo_path, "r", encoding=encoding_usado) as entrada, \
            open(arquivo_saida, "w", encoding="utf-8") as saida:

            for i, linha in enumerate(entrada):
                linha = linha.strip()

                if linha.startswith("|C100|"):
                    codigos_c110.clear()
                    saida.write(linha + "\n")

                elif linha.startswith("|C110|"):
                    partes = linha.split("|")

                    if len(partes) > 2:
                        codigo = partes[2]

                        if codigo not in codigos_c110:
                            codigos_c110.add(codigo)
                            saida.write(linha + "\n")
                    else:
                        saida.write(linha + "\n")

                else:
                    saida.write(linha + "\n")

                # Atualiza barra
                if i % 1000 == 0:
                    self.progress.set(i / total_linhas)
                    self.update_idletasks()

        self.progress.set(1)
        self.status.configure(text="Processamento concluído ✅")

        messagebox.showinfo(
            "Sucesso",
            f"Arquivo processado!\nSalvo em:\n{arquivo_saida}"
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()