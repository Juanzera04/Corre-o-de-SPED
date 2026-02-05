const API = "https://sped-6762.onrender.com";

// Teste de conexão quando a página carrega
window.addEventListener('load', async () => {
    try {
        console.log("Testando conexão com backend...");
        const response = await fetch(`${API}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log("✅ Backend conectado:", data);
        } else {
            console.warn("⚠️ Backend respondeu com erro:", response.status);
        }
    } catch (error) {
        console.error("❌ Não foi possível conectar ao backend:", error);
        alert("Atenção: Backend não está respondendo. Verifique se o serviço está online.");
    }
});

function processarPisCofins(inputId) {
    const input = document.getElementById(inputId);
    if (!input.files.length) {
        alert("Selecione um arquivo");
        return;
    }

    const form = new FormData();
    form.append("file", input.files[0]);

    // Feedback visual
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = "Processando...";
    btn.disabled = true;

    console.log(`Enviando ${input.files[0].name} para ${API}/corrigir`);
    
    fetch(`${API}/corrigir`, {
        method: "POST",
        body: form
    })
    .then(response => {
        console.log("Status:", response.status);
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`Erro ${response.status}: ${text}`);
            });
        }
        return response.blob();
    })
    .then(blob => {
        if (blob.size === 0) {
            throw new Error("Arquivo retornado está vazio");
        }
        console.log("Download iniciado, tamanho:", blob.size);
        download(blob, "SPED_corrigido.txt");
    })
    .catch(e => {
        console.error("Erro:", e);
        alert(`Erro: ${e.message}`);
    })
    .finally(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    });
}

function processarC175(inputId) {
    const input = document.getElementById(inputId);
    if (!input.files.length) {
        alert("Selecione um arquivo");
        return;
    }

    const form = new FormData();
    form.append("file", input.files[0]);

    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = "Processando...";
    btn.disabled = true;

    console.log(`Enviando ${input.files[0].name} para ${API}/consolidar-c175`);
    
    fetch(`${API}/consolidar-c175`, {
        method: "POST",
        body: form
    })
    .then(response => {
        console.log("Status:", response.status);
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`Erro ${response.status}: ${text}`);
            });
        }
        return response.blob();
    })
    .then(blob => {
        if (blob.size === 0) {
            throw new Error("Arquivo retornado está vazio");
        }
        console.log("Download iniciado, tamanho:", blob.size);
        download(blob, "SPED_C175.txt");
    })
    .catch(e => {
        console.error("Erro:", e);
        alert(`Erro: ${e.message}`);
    })
    .finally(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    });
}

function download(blob, nome) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = nome;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
}