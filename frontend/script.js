document.getElementById("btnEnviar").addEventListener("click", async () => {

    const fileInput = document.getElementById("fileInput");
    const mensagem = document.getElementById("mensagem");
    const downloadLink = document.getElementById("downloadLink");

    if (!fileInput.files.length) {
        mensagem.textContent = "Selecione um arquivo primeiro.";
        return;
    }

    mensagem.textContent = "Enviando, aguarde...";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    // ---- ALTERE A URL AQUI ----
    const API_URL = "https://sped-6762.onrender.com";

    const response = await fetch(API_URL, {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        mensagem.textContent = "Erro ao processar o arquivo.";
        return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    downloadLink.href = url;
    downloadLink.style.display = "block";

    mensagem.textContent = "Arquivo processado com sucesso!";
});
