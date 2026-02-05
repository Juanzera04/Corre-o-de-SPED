const API = "https://sped-6762.onrender.com";

// Inicialização da página
window.addEventListener('load', () => {
    // Teste de conexão
    fetch(`${API}/health`)
        .then(response => {
            if (response.ok) {
                console.log("✅ Backend conectado");
                atualizarStatusBackend(true);
            } else {
                console.warn("⚠️ Backend com problemas");
                atualizarStatusBackend(false);
            }
        })
        .catch(() => {
            console.error("❌ Backend offline");
            atualizarStatusBackend(false);
        });
    
    // Configurar listeners para os inputs de arquivo
    configurarInputsArquivo();
});

function atualizarStatusBackend(online) {
    const titulo = document.querySelector('.titulo-principal');
    if (!titulo) return;
    
    if (online) {
        titulo.innerHTML += ' <span style="font-size: 0.8rem; color: #10b981;">(Online)</span>';
    } else {
        titulo.innerHTML += ' <span style="font-size: 0.8rem; color: #ef4444;">(Offline)</span>';
    }
}

function configurarInputsArquivo() {
    const inputs = ['pisFile', 'c175File'];
    
    inputs.forEach(id => {
        const input = document.getElementById(id);
        const infoDiv = document.getElementById(id.replace('File', 'Info'));
        
        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                const file = this.files[0];
                infoDiv.innerHTML = `
                    <i class="fas fa-file-alt"></i>
                    <strong>Arquivo selecionado:</strong><br>
                    ${file.name}<br>
                    <small>(${(file.size / 1024).toFixed(2)} KB)</small>
                `;
                infoDiv.classList.add('mostrar');
            } else {
                infoDiv.classList.remove('mostrar');
            }
        });
    });
}

function processarPisCofins(inputId) {
    const input = document.getElementById(inputId);
    if (!input.files.length) {
        mostrarStatus('pisStatus', 'Por favor, selecione um arquivo primeiro', 'erro');
        return;
    }

    const btn = document.getElementById('btnPis');
    const btnIcon = document.getElementById('pisIcon');
    const btnText = document.getElementById('pisText');
    
    const form = new FormData();
    form.append("file", input.files[0]);

    // Atualizar estado do botão
    btn.disabled = true;
    btnIcon.innerHTML = '<div class="loader"></div>';
    btnText.textContent = 'Processando...';
    
    mostrarStatus('pisStatus', 'Processando arquivo, aguarde...', 'processo');

    fetch(`${API}/corrigir`, {
        method: "POST",
        body: form
    })
    .then(response => {
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
        mostrarStatus('pisStatus', 'Arquivo processado com sucesso! Iniciando download...', 'sucesso');
        download(blob, "SPED_corrigido.txt");
    })
    .catch(e => {
        console.error("Erro:", e);
        mostrarStatus('pisStatus', `Erro: ${e.message}`, 'erro');
    })
    .finally(() => {
        btn.disabled = false;
        btnIcon.innerHTML = '<i class="fas fa-cogs icone"></i>';
        btnText.textContent = 'Processar PIS/COFINS';
    });
}

function processarC175(inputId) {
    const input = document.getElementById(inputId);
    if (!input.files.length) {
        mostrarStatus('c175Status', 'Por favor, selecione um arquivo primeiro', 'erro');
        return;
    }

    const btn = document.getElementById('btnC175');
    const btnIcon = document.getElementById('c175Icon');
    const btnText = document.getElementById('c175Text');
    
    const form = new FormData();
    form.append("file", input.files[0]);

    btn.disabled = true;
    btnIcon.innerHTML = '<div class="loader"></div>';
    btnText.textContent = 'Processando...';
    
    mostrarStatus('c175Status', 'Consolidando registros C175...', 'processo');

    fetch(`${API}/consolidar-c175`, {
        method: "POST",
        body: form
    })
    .then(response => {
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
        mostrarStatus('c175Status', 'C175 consolidados com sucesso! Iniciando download...', 'sucesso');
        download(blob, "SPED_C175.txt");
    })
    .catch(e => {
        console.error("Erro:", e);
        mostrarStatus('c175Status', `Erro: ${e.message}`, 'erro');
    })
    .finally(() => {
        btn.disabled = false;
        btnIcon.innerHTML = '<i class="fas fa-compress-alt icone"></i>';
        btnText.textContent = 'Consolidar C175';
    });
}

function mostrarStatus(elementId, mensagem, tipo) {
    const element = document.getElementById(elementId);
    element.textContent = mensagem;
    element.className = `status ${tipo} mostrar`;
    
    // Auto-esconder mensagens de sucesso após 5 segundos
    if (tipo === 'sucesso') {
        setTimeout(() => {
            element.classList.remove('mostrar');
        }, 5000);
    }
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