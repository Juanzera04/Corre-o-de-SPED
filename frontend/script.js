// Mensagem ao selecionar arquivo
document.getElementById("fileInput").addEventListener("change", () => {
    const msg = document.getElementById("arquivo-msg");
    msg.textContent = "Arquivo selecionado ✔️";
});

const API_URL = "https://sped-6762.onrender.com/corrigir";
const MAX_TENTATIVAS = 3;

async function enviarArquivo(formData, tentativa = 1) {
    const mensagem = document.getElementById("mensagem");
    const loader = document.getElementById("loader");
    const downloadLink = document.getElementById("downloadLink");

    try {
        mensagem.textContent =
            tentativa === 1
                ? "Inicializando servidor, aguarde alguns segundos…"
                : `Servidor acordando… tentativa ${tentativa} de ${MAX_TENTATIVAS}`;

        loader.style.display = "block";

        const response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Resposta inválida");
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        downloadLink.href = url;
        downloadLink.style.display = "block";

        mensagem.textContent = "Arquivo processado com sucesso!";
        loader.style.display = "none";

    } catch (err) {
        if (tentativa < MAX_TENTATIVAS) {
            // espera alguns segundos antes de tentar novamente
            setTimeout(() => {
                enviarArquivo(formData, tentativa + 1);
            }, 5000);
        } else {
            mensagem.textContent =
                "O servidor demorou para responder. Tente novamente em alguns instantes.";
            loader.style.display = "none";
        }
    }
}

document.getElementById("btnEnviar").addEventListener("click", () => {
    const fileInput = document.getElementById("fileInput");
    const mensagem = document.getElementById("mensagem");
    const downloadLink = document.getElementById("downloadLink");

    if (!fileInput.files.length) {
        mensagem.textContent = "Selecione um arquivo primeiro.";
        return;
    }

    downloadLink.style.display = "none";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    enviarArquivo(formData);
});
