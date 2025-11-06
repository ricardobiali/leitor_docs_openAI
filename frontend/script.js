document.addEventListener("DOMContentLoaded", () => {
    const runBtn = document.getElementById("runBtn");
    const cancelBtn = document.getElementById("cancelBtn");
    const avisosContainer = document.getElementById("avisosContainer");
    const avisosContent = document.getElementById("avisosContent");
    const cancelSection = document.getElementById("cancelSection");
    const pathInput = document.getElementById("pathInput");
    const folderIcon = document.getElementById("folderIcon");
    const runSection = document.getElementById("runSection");
    const formSection = document.querySelector(".form-section");

    // 🟢 Clicar no ícone abre seletor de diretório
    folderIcon.addEventListener("click", async () => {
        const caminho = await eel.selecionar_diretorio()();
        if (caminho) {
            pathInput.value = caminho;
        }
    });

    // 🟢 Executar automação
    runBtn.addEventListener("click", async () => {
        const path = pathInput.value.trim();
        if (!path) {
            alert("Por favor, insira o caminho de rede antes de executar.");
            return;
        }

        // 🔹 Esconde o campo e botão de envio suavemente
        formSection.classList.add("hidden");
        runSection.classList.add("hidden");

        // 🔹 Mostra avisos e botão cancelar suavemente
        avisosContainer.classList.remove("hidden");
        cancelSection.classList.remove("hidden");

        avisosContent.innerHTML = `
            <li>
                <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                Executando automação
            </li>
        `;


        try {
            await eel.atualizar_requests_json(path)();
            const resultado = await eel.executar_automacao()();
            mostrarAviso(resultado);
        } catch (err) {
            mostrarAviso("Erro durante a execução da automação.");
            console.error(err);
        } finally {
            // 🔹 Restaura interface ao fim do processo
            formSection.classList.remove("hidden");
            runSection.classList.remove("hidden");
            cancelSection.classList.add("hidden");
        }
    });

    // 🟠 Cancelar execução
    cancelBtn.addEventListener("click", () => {
        mostrarAviso("Processo cancelado pelo usuário.");
        cancelSection.classList.add("hidden");
        formSection.classList.remove("hidden");
        runSection.classList.remove("hidden");
    });

    function mostrarAviso(msg) {
        avisosContainer.classList.remove("hidden");
        const li = document.createElement("li");
        li.textContent = msg;
        avisosContent.appendChild(li);
    }
});