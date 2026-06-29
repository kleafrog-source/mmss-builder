console.log("orchestrator_main.js loaded");

const agents = [
    "QUANTUM_MAP",
    "META_DERIVATION",
    "FRACTAL_ENTAILMENT",
    "TEMPORAL_GENERATION",
    "GOLDEN_DERIVATION",
    "CORRECTION_ENHANCED",
    "MULTYFUNCTIONAL_SUMMARY_WRITER_OBSIDIAN",
    "OBSIDIAN_NODEFLOW_EXPORTER",
    "ULTRA_CONCISE_LINKED_SUMMARY",
    "OMNIAGENT_UNIFIED_SYNTHESIZER"
];

document.addEventListener('DOMContentLoaded', function() {
    const questionInput = document.getElementById('question');
    const gridPanel = document.querySelector('.grid-panel');
    const downloadBtn = document.getElementById('download-results');
    const saveProjectBtn = document.getElementById('save-project');
    const loadProjectBtn = document.getElementById('load-project');
    const fillPromptsBtn = document.getElementById('fill-all-prompts');
    const autoCycleBtn = document.getElementById('auto-cycle');
    const gridToggleBtn = document.getElementById('grid-toggle');
    const createSummaryBtn = document.getElementById('create-summary-response');
    const providerSelect = document.getElementById('orchestrator-provider');
    const ollamaModelSelect = document.getElementById('orchestrator-ollama-model');
    const mistralModelSelect = document.getElementById('orchestrator-mistral-model');
    const refreshOllamaModelsBtn = document.getElementById('refresh-orchestrator-models');
    const refreshMistralModelsBtn = document.getElementById('refresh-orchestrator-mistral-models');
    const projectList = document.getElementById('project-list');
    const loadProjectModal = document.getElementById('load-project-modal');
    const closeProjectModal = document.getElementById('close-project-modal');

    let agentData = {};
    let currentProjectName = '';
    let autoCycleRunning = false;
    let autoCyclePaused = false;
    let autoCycleIndex = 0;
    let retryCount = 0;

    const previewModal = document.createElement('div');
    previewModal.style.cssText = 'display:none; position:fixed; inset:0; background:rgba(0,0,0,0.72); z-index:2600; align-items:center; justify-content:center; padding:24px;';
    previewModal.innerHTML = `
        <div style="width:min(1100px,100%); max-height:85vh; background:#111827; color:#e5e7eb; border:1px solid #374151; border-radius:16px; overflow:hidden;">
            <div style="display:flex; justify-content:space-between; align-items:center; padding:16px 20px; border-bottom:1px solid #374151;">
                <strong>Prompt Preview</strong>
                <button id="orchestrator-preview-close" style="background:none; border:none; color:#e5e7eb; font-size:22px; cursor:pointer;">×</button>
            </div>
            <pre id="orchestrator-preview-content" style="margin:0; padding:20px; overflow:auto; max-height:calc(85vh - 64px); white-space:pre-wrap; word-break:break-word;"></pre>
        </div>
    `;
    document.body.appendChild(previewModal);
    previewModal.querySelector('#orchestrator-preview-close').addEventListener('click', () => {
        previewModal.style.display = 'none';
    });

    function getOperatorSymbol(agentName) {
        const symbols = {
            QUANTUM_MAP: "↦ₚ",
            META_DERIVATION: "⊢ᵠ",
            FRACTAL_ENTAILMENT: "⇛ᶠ",
            TEMPORAL_GENERATION: "⧴ᵗ",
            GOLDEN_DERIVATION: "⊢ᵍ",
            CORRECTION_ENHANCED: "↦ᶜ",
            MULTYFUNCTIONAL_SUMMARY_WRITER_OBSIDIAN: "📝",
            OBSIDIAN_NODEFLOW_EXPORTER: "📊",
            ULTRA_CONCISE_LINKED_SUMMARY: "🔗",
            OMNIAGENT_UNIFIED_SYNTHESIZER: "🌀"
        };
        return symbols[agentName] || '?';
    }

    function getOutputType(agentName) {
        const types = {
            MULTYFUNCTIONAL_SUMMARY_WRITER_OBSIDIAN: "dataview md",
            OBSIDIAN_NODEFLOW_EXPORTER: "nodeflow-list",
            ULTRA_CONCISE_LINKED_SUMMARY: "linked-summary",
            OMNIAGENT_UNIFIED_SYNTHESIZER: "unified-omni",
            QUANTUM_MAP: "markdown",
            META_DERIVATION: "markdown",
            FRACTAL_ENTAILMENT: "markdown",
            TEMPORAL_GENERATION: "markdown",
            GOLDEN_DERIVATION: "markdown",
            CORRECTION_ENHANCED: "markdown"
        };
        return types[agentName] || 'markdown';
    }

    function parseResponsePayload(answerRaw) {
        const raw = typeof answerRaw === 'string' ? answerRaw : '';
        const markerIndex = raw.lastIndexOf('--- METRICS:');
        if (markerIndex === -1) {
            return { answer: raw.trim(), metrics: {}, raw };
        }

        const answer = raw.slice(0, markerIndex).trim();
        const metricsBlock = raw.slice(markerIndex + '--- METRICS:'.length).trim();
        let metrics = {};
        const metricsMatch = metricsBlock.match(/\{[\s\S]*\}/);
        if (metricsMatch) {
            try {
                metrics = JSON.parse(metricsMatch[0]);
            } catch (error) {
                console.log('Metrics parsing warning:', error.message);
            }
        }
        return { answer: answer || raw.trim(), metrics, raw };
    }

    function renderAnswer(answerPanel, answer) {
        const value = (answer || '').trim();
        if (!value) {
            answerPanel.innerHTML = `<p class="text-sm text-amber-300">Пустой ответ. Возможные причины: обрезание по контексту, нестандартный формат, ранняя остановка модели.</p>`;
            return;
        }
        if (value.startsWith('```nodeflow-list')) {
            answerPanel.innerHTML = `<pre class="text-xs overflow-x-auto p-3 bg-gray-950 rounded">${value.replace(/```nodeflow-list|```/g, '')}</pre>`;
            return;
        }
        if (value.startsWith('```')) {
            answerPanel.innerHTML = `<pre class="text-xs overflow-x-auto p-3 bg-gray-950 rounded">${value.replace(/```/g, '')}</pre>`;
            return;
        }
        answerPanel.innerHTML = `<pre class="text-sm whitespace-pre-wrap">${value}</pre>`;
    }

    function buildPromptPreview(agentName, overridePrompt = null) {
        const card = document.getElementById(`agent-card-${agentName}`);
        const promptInput = card?.querySelector('.prompt-input');
        const prompt = (overridePrompt !== null ? overridePrompt : (promptInput ? promptInput.value : '')).trim();
        return [
            `Agent: ${agentName}`,
            `Provider: ${providerSelect?.value || 'ollama'}`,
            `Question:`,
            `${(questionInput?.value || '').trim()}`,
            '',
            'Prompt:',
            prompt
        ].join('\n');
    }

    function showPromptPreview(agentName, overridePrompt = null) {
        document.getElementById('orchestrator-preview-content').textContent = buildPromptPreview(agentName, overridePrompt);
        previewModal.style.display = 'flex';
    }

    function updateProviderUI() {
        const provider = providerSelect?.value || 'ollama';
        if (ollamaModelSelect) ollamaModelSelect.disabled = provider !== 'ollama';
        if (refreshOllamaModelsBtn) refreshOllamaModelsBtn.disabled = provider !== 'ollama';
        if (mistralModelSelect) mistralModelSelect.disabled = provider !== 'mistral';
        if (refreshMistralModelsBtn) refreshMistralModelsBtn.disabled = provider !== 'mistral';
    }

    async function saveOrchestratorProvider() {
        if (!providerSelect) return;
        const response = await fetch('/api/orchestrator/provider', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider: providerSelect.value }),
        });
        const data = await response.json();
        if (!response.ok || data.error) {
            throw new Error(data.message || data.error || 'Provider update failed');
        }
        updateProviderUI();
    }

    async function refreshModels(url, select, selectedKey) {
        const response = await fetch(url);
        const data = await response.json();
        select.innerHTML = '';
        (data.models || []).forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            option.selected = model === data[selectedKey];
            select.appendChild(option);
        });
        if (data.error) {
            throw new Error(data.error);
        }
    }

    async function saveModel(url, model) {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model }),
        });
        const data = await response.json();
        if (!response.ok || data.error) {
            throw new Error(data.message || data.error || 'Model update failed');
        }
    }

    function renderAgents() {
        gridPanel.innerHTML = '';
        agents.forEach(agentName => {
            const data = agentData[agentName] || { answer: '', metrics: {} };
            const card = document.createElement('div');
            card.className = 'agent-card';
            card.id = `agent-card-${agentName}`;
            card.dataset.branchId = `branch-${agentName}`;
            card.dataset.agentId = agentName;
            card.style.borderLeft = '4px solid #64ffda';
            card.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';

            const answerHtml = `<pre class="text-sm whitespace-pre-wrap">${(data.answer || '').trim()}</pre>`;
            const semanticNodeId = `semantic-node-${agentName}`;

            card.innerHTML = `
                <div class="agent-header">
                    <div class="agent-icon">${getOperatorSymbol(agentName)}</div>
                    <h2 class="agent-title">${agentName.replace(/_/g, ' ')}</h2>
                    <div class="agent-status" style="font-size:0.8rem; font-weight:bold; color:#8892b0;">Ready</div>
                    <div style="display:flex; gap:8px; align-items:center;">
                        <button class="preview-btn" data-agent="${agentName}" title="Показать текущий запрос целиком">👁</button>
                        <button class="agent-btn" data-agent="${agentName}">Запустить</button>
                    </div>
                </div>
                <div class="output-type">${getOutputType(agentName)}</div>
                <div class="agent-actions" style="display:flex; gap:8px; margin:0.5rem 0;">
                    <button class="copy-btn" title="Скопировать ответ" style="background:none; border:none; color:var(--accent); cursor:pointer; font-size:1.1em; padding:0 4px;">📋</button>
                    <button class="fullscreen-btn" title="Развернуть во весь экран" style="background:none; border:none; color:var(--accent); cursor:pointer; font-size:1.1em; padding:0 4px;">🔎↕</button>
                    <button class="zoom-in-btn" title="Свернуть" style="background:none; border:none; color:var(--accent); cursor:pointer; font-size:1.1em; padding:0 4px; display:none;">🔎↙</button>
                </div>
                <div class="semantic-node" id="${semanticNodeId}" data-node-id="${semanticNodeId}" data-agent-id="${agentName}">
                    <div class="answer-panel">${answerHtml}</div>
                </div>
                <div class="agent-controls">
                    <select class="prompt-type">
                        <option value="full">Full Prompt</option>
                        <option value="short">Short Prompt</option>
                    </select>
                    <textarea class="prompt-input" rows="2" placeholder="Введите промпт..."></textarea>
                </div>
            `;
            gridPanel.appendChild(card);

            card.querySelector('.agent-btn').addEventListener('click', () => window.sendAgentRequest(agentName));
            card.querySelector('.preview-btn').addEventListener('click', () => showPromptPreview(agentName));
        });
    }

    async function sendStandardAgentRequest(agentName, prompt) {
        const response = await fetch('/orchestrate/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_name: agentName, prompt, project_name: currentProjectName }),
        });
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        const result = await response.json();
        if (result.error) {
            throw new Error(result.error);
        }
        return result;
    }

    async function streamAgentRequest(agentName, prompt, answerPanel) {
        const response = await fetch('/orchestrate/send-stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_name: agentName, prompt, project_name: currentProjectName }),
        });
        if (!response.ok || !response.body) {
            throw new Error('Streaming response was not available.');
        }

        const decoder = new TextDecoder();
        const reader = response.body.getReader();
        let buffer = '';
        let finalAnswer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (!line.trim()) continue;
                const payload = JSON.parse(line);
                if (payload.type === 'error') {
                    throw new Error(payload.error || 'Streaming error');
                }
                if (payload.type === 'chunk' || payload.type === 'content' || payload.type === 'thinking') {
                    finalAnswer += payload.content || '';
                    renderAnswer(answerPanel, finalAnswer);
                }
                if (payload.type === 'done') {
                    finalAnswer = payload.response || finalAnswer;
                    return { answer: finalAnswer };
                }
            }
        }

        return { answer: finalAnswer };
    }

    window.sendAgentRequest = async function(agentName, overridePrompt = null, targetNodeId = null) {
        const card = document.getElementById(`agent-card-${agentName}`);
        if (!card) return;

        const statusEl = card.querySelector('.agent-status');
        const btn = card.querySelector('.agent-btn');
        const promptInput = card.querySelector('.prompt-input');
        const prompt = (overridePrompt !== null ? overridePrompt : (promptInput ? promptInput.value : '')).trim();
        const targetNode = targetNodeId ? document.getElementById(targetNodeId) : card.querySelector('.semantic-node');
        const answerPanel = targetNode ? targetNode.querySelector('.answer-panel') : card.querySelector('.answer-panel');
        const provider = providerSelect?.value || 'ollama';

        if (!prompt) {
            alert('Пожалуйста, введите промпт.');
            return;
        }

        statusEl.textContent = 'Обработка...';
        statusEl.style.color = '#667eea';
        card.style.borderLeft = '4px solid #667eea';
        btn.disabled = true;
        btn.textContent = '...';
        answerPanel.innerHTML = `<pre class="text-sm whitespace-pre-wrap">Connecting to ${provider}...</pre>`;

        try {
            let result;
            if (provider === 'ollama') {
                result = await streamAgentRequest(agentName, prompt, answerPanel);
            } else {
                result = await sendStandardAgentRequest(agentName, prompt);
            }

            const parsed = parseResponsePayload(result.answer);
            agentData[agentName] = { answer: parsed.answer, metrics: parsed.metrics };
            renderAnswer(answerPanel, parsed.answer);

            statusEl.textContent = 'Готово';
            statusEl.style.color = '#64ffda';
            card.style.borderLeft = '4px solid #64ffda';
            card.style.backgroundColor = 'rgba(100, 255, 218, 0.05)';
        } catch (error) {
            console.error(`Ошибка агента ${agentName}:`, error);
            console.log(`Likely causes: provider unavailable, missing model, timeout, oversized context, truncated output.`);
            answerPanel.innerHTML = `<p class="text-sm text-red-400">Ошибка: ${error.message}</p>`;
            statusEl.textContent = 'Ошибка';
            statusEl.style.color = '#f44336';
            card.style.borderLeft = '4px solid #f44336';
            card.style.backgroundColor = 'rgba(244, 67, 54, 0.05)';
        } finally {
            btn.disabled = false;
            btn.textContent = 'Запустить';
        }
    };

    async function loadProjectList() {
        const response = await fetch('/api/ai/projects');
        const projects = await response.json();
        projectList.innerHTML = '';
        if (projects.length === 0) {
            projectList.innerHTML = '<li>Нет сохранённых проектов.</li>';
            return;
        }
        projects.forEach((projectName) => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.textContent = projectName;
            a.dataset.projectName = projectName;
            li.appendChild(a);
            projectList.appendChild(li);
        });
    }

    closeProjectModal?.addEventListener('click', () => {
        loadProjectModal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === loadProjectModal) {
            loadProjectModal.style.display = 'none';
        }
    });

    loadProjectBtn?.addEventListener('click', async () => {
        try {
            await loadProjectList();
            loadProjectModal.style.display = 'block';
        } catch (error) {
            alert(`Не удалось загрузить список проектов: ${error.message}`);
        }
    });

    projectList?.addEventListener('click', async (event) => {
        if (event.target.tagName !== 'A') return;
        const projectName = event.target.dataset.projectName;
        const response = await fetch(`/api/ai/project/${projectName}`);
        const data = await response.json();
        currentProjectName = projectName;
        agentData = data.agents || {};
        questionInput.value = data.question || '';
        renderAgents();
        loadProjectModal.style.display = 'none';
    });

    fillPromptsBtn?.addEventListener('click', () => {
        const promptText = prompt("Введите текст для вставки во все промпты:");
        if (!promptText) return;
        document.querySelectorAll('.prompt-input').forEach((input) => {
            input.value = promptText;
        });
    });

    saveProjectBtn?.addEventListener('click', async () => {
        const projectName = prompt("Введите имя проекта:", `Orchestrator_Project_${new Date().toISOString().slice(0, 16).replace('T', '_')}`);
        if (!projectName) return;
        currentProjectName = projectName;

        const projectData = {
            project_name: projectName,
            question: questionInput.value,
            agents: agentData
        };

        const response = await fetch('/orchestrator/save_project', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectData)
        });
        const data = await response.json();
        if (data.error) {
            alert(`Ошибка сохранения проекта: ${data.error}`);
            return;
        }
        alert(`Проект "${data.project_name}" успешно сохранён.`);
    });

    downloadBtn?.addEventListener('click', () => {
        if (Object.keys(agentData).length === 0) {
            alert('Нет результатов для скачивания.');
            return;
        }
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(agentData, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "orchestration_results.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    });

    function cycleNextAgent() {
        if (!autoCycleRunning || autoCyclePaused) return;
        if (autoCycleIndex >= agents.length) {
            autoCycleRunning = false;
            autoCyclePaused = false;
            autoCycleBtn.textContent = '🔄 Auto Cycle';
            alert('Автоцикл завершён.');
            return;
        }

        const agentName = agents[autoCycleIndex];
        const card = document.getElementById(`agent-card-${agentName}`);
        const prompt = card?.querySelector('.prompt-input')?.value?.trim() || '';
        if (!prompt) {
            autoCycleIndex++;
            setTimeout(cycleNextAgent, 500);
            return;
        }

        window.sendAgentRequest(agentName).then(() => {
            autoCycleIndex++;
            retryCount = 0;
            setTimeout(cycleNextAgent, 1500);
        }).catch(() => {
            retryCount++;
            if (retryCount >= 4) {
                autoCycleIndex++;
                retryCount = 0;
            }
            setTimeout(cycleNextAgent, 2500);
        });
    }

    autoCycleBtn?.addEventListener('click', () => {
        if (!autoCycleRunning) {
            autoCycleRunning = true;
            autoCyclePaused = false;
            autoCycleIndex = 0;
            retryCount = 0;
            autoCycleBtn.textContent = '⏸ Приостановить';
            cycleNextAgent();
            return;
        }

        if (autoCyclePaused) {
            autoCyclePaused = false;
            autoCycleBtn.textContent = '⏸ Приостановить';
            cycleNextAgent();
        } else {
            autoCyclePaused = true;
            autoCycleBtn.textContent = '▶ Продолжить';
        }
    });

    let gridMode = 3;
    gridToggleBtn?.addEventListener('click', () => {
        gridMode = gridMode % 4 + 1;
        gridPanel.className = 'grid-panel';
        gridPanel.classList.add(`grid-${gridMode}`);
        gridToggleBtn.textContent = `🔢 Grid: ${gridMode}`;
    });

    createSummaryBtn?.addEventListener('click', async () => {
        let summaryContent = "### Исходный вопрос:\n";
        summaryContent += `${questionInput.value}\n\n### Ответы агентов:\n`;
        document.querySelectorAll('.agent-card').forEach(card => {
            const agentTitle = card.querySelector('.agent-title')?.textContent || '';
            const answerText = card.querySelector('.answer-panel')?.innerText || '';
            if (answerText.trim()) {
                summaryContent += `\n---\n#### Агент: ${agentTitle}\n${answerText}\n`;
            }
        });
        const summaryPrompt = `Проанализируй сессию оркестратора и собери единый структурированный итог.\n\n${summaryContent}`;
        await window.sendAgentRequest('OMNIAGENT_UNIFIED_SYNTHESIZER', summaryPrompt);
    });

    document.addEventListener('click', function(e) {
        const copyBtn = e.target.closest('.copy-btn');
        const fullscreenBtn = e.target.closest('.fullscreen-btn');
        const zoomOutBtn = e.target.closest('.zoom-in-btn');

        if (copyBtn) {
            const card = copyBtn.closest('.agent-card');
            const text = card.querySelector('.answer-panel')?.innerText || '';
            if (text.trim()) {
                navigator.clipboard.writeText(text);
                console.log('Ответ скопирован в буфер обмена.');
            }
            return;
        }

        if (fullscreenBtn) {
            const card = fullscreenBtn.closest('.agent-card');
            const answerPanel = card.querySelector('.answer-panel');
            answerPanel.requestFullscreen?.();
            fullscreenBtn.style.display = 'none';
            card.querySelector('.zoom-in-btn').style.display = 'inline-block';
            return;
        }

        if (zoomOutBtn) {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            }
            const card = zoomOutBtn.closest('.agent-card');
            zoomOutBtn.style.display = 'none';
            card.querySelector('.fullscreen-btn').style.display = 'inline-block';
        }
    });

    if (providerSelect) {
        providerSelect.addEventListener('change', async () => {
            try {
                await saveOrchestratorProvider();
            } catch (error) {
                alert(`Не удалось переключить provider: ${error.message}`);
            }
        });
    }
    refreshOllamaModelsBtn?.addEventListener('click', async () => {
        try {
            refreshOllamaModelsBtn.textContent = 'Refreshing...';
            await refreshModels('/api/settings/ollama/models', ollamaModelSelect, 'selected_model');
        } catch (error) {
            alert(error.message);
        } finally {
            refreshOllamaModelsBtn.textContent = 'Refresh Models';
        }
    });
    refreshMistralModelsBtn?.addEventListener('click', async () => {
        try {
            refreshMistralModelsBtn.textContent = 'Refreshing...';
            await refreshModels('/api/settings/mistral/models', mistralModelSelect, 'selected_model');
        } catch (error) {
            alert(error.message);
        } finally {
            refreshMistralModelsBtn.textContent = 'Refresh Mistral';
        }
    });
    ollamaModelSelect?.addEventListener('change', async () => {
        try {
            await saveModel('/api/settings/ollama/model', ollamaModelSelect.value);
        } catch (error) {
            alert(error.message);
        }
    });
    mistralModelSelect?.addEventListener('change', async () => {
        try {
            await saveModel('/api/settings/mistral/model', mistralModelSelect.value);
        } catch (error) {
            alert(error.message);
        }
    });

    renderAgents();
    updateProviderUI();
});
