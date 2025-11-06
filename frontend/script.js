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

    // variável para controlar o elemento do spinner
    let spinnerItem = null;

    folderIcon.addEventListener("click", async () => {
        const caminho = await eel.selecionar_diretorio()();
        if (caminho) pathInput.value = caminho;
    });

    runBtn.addEventListener("click", async () => {
        const path = pathInput.value.trim();
        if (!path) {
            alert("Por favor, insira o caminho de rede antes de executar.");
            return;
        }

        // esconder formulário
        formSection.classList.add("hidden");
        runSection.classList.add("hidden");

        // mostrar container e cancel
        avisosContainer.classList.remove("hidden");
        cancelSection.classList.remove("hidden");

        // limpar mensagens antigas (opcional)
        // avisosContent.innerHTML = "";

        showSpinner("Executando automação...");

        try {
            await eel.atualizar_requests_json(path)();
            const resultado = await eel.executar_automacao()();

            // garantimos que o spinner suma antes de mostrar o resultado
            hideSpinner();
            mostrarAviso(resultado);
        } catch (err) {
            hideSpinner();
            mostrarAviso("Erro durante a execução da automação.");
            console.error(err);
        } finally {
            // restaurar interface
            formSection.classList.remove("hidden");
            runSection.classList.remove("hidden");
            cancelSection.classList.add("hidden");
        }
    });

    cancelBtn.addEventListener("click", () => {
        hideSpinner();
        mostrarAviso("Processo cancelado pelo usuário.");
        cancelSection.classList.add("hidden");
        formSection.classList.remove("hidden");
        runSection.classList.remove("hidden");
    });

    function mostrarAviso(msg) {
        // remove spinner caso ainda exista
        hideSpinner();

        avisosContainer.classList.remove("hidden");
        const li = document.createElement("li");
        li.textContent = msg;
        avisosContent.appendChild(li);
    }

    function showSpinner(text = "Carregando...") {
        // se já existe, atualiza o texto
        if (spinnerItem) {
            const textNode = spinnerItem.querySelector(".spinner-text");
            if (textNode) textNode.textContent = text;
            return;
        }

        spinnerItem = document.createElement("li");
        spinnerItem.classList.add("spinner-item");
        // marca com data-attr para identificação se quiser inspecionar
        spinnerItem.setAttribute("data-spinner", "true");

        spinnerItem.innerHTML = `
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status" aria-hidden="true"></div>
            <span class="spinner-text">${text}</span>
        `;

        // adiciona no começo para que fique visível
        avisosContent.insertBefore(spinnerItem, avisosContent.firstChild);
        avisosContainer.classList.remove("hidden");
    }

    function hideSpinner() {
        if (!spinnerItem) {
            // tenta localizar por seletor caso o elemento tenha vindo de outro lugar
            const possible = avisosContent.querySelector('[data-spinner="true"], .spinner-item');
            if (possible) possible.remove();
            return;
        }

        spinnerItem.remove();
        spinnerItem = null;
    }
});
