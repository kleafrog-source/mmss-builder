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
        let agentData = {};

     
        function getOperatorSymbol(agentName) {
            const symbols = {
                "QUANTUM_MAP": "↦ₚ",
                "META_DERIVATION": "⊢ᵠ",
                "FRACTAL_ENTAILMENT": "⇛ᶠ",
                "TEMPORAL_GENERATION": "⧴ᵗ",
                "GOLDEN_DERIVATION": "⊢ᵍ",
                "CORRECTION_ENHANCED": "↦ᶜ",
                "MULTYFUNCTIONAL_SUMMARY_WRITER_OBSIDIAN": "📝",
                "OBSIDIAN_NODEFLOW_EXPORTER": "📊",
                "ULTRA_CONCISE_LINKED_SUMMARY": "🔗",
                "OMNIAGENT_UNIFIED_SYNTHESIZER": "🌀"
            };
            return symbols[agentName] || '?';
        }

        function getOutputType(agentName) {
            const types = {
                "MULTYFUNCTIONAL_SUMMARY_WRITER_OBSIDIAN": "dataview md",
                "OBSIDIAN_NODEFLOW_EXPORTER": "nodeflow-list",
                "ULTRA_CONCISE_LINKED_SUMMARY": "linked-summary",
                "OMNIAGENT_UNIFIED_SYNTHESIZER": "unified-omni",
                "QUANTUM_MAP": "markdown",
                "META_DERIVATION": "markdown",
                "FRACTAL_ENTAILMENT": "markdown",
                "TEMPORAL_GENERATION": "markdown",
                "GOLDEN_DERIVATION": "markdown",
                "CORRECTION_ENHANCED": "markdown"
            };
            return types[agentName] || 'unknown';
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

                const symbol = getOperatorSymbol(agentName);
                const outputType = getOutputType(agentName);
                const semanticNodeId = `semantic-node-${agentName}`;

                // Инициализируем цвет как "готово"
                card.style.borderLeft = '4px solid #64ffda';
                card.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';

                let answerHtml = '';
                if (data.answer && data.answer.startsWith('```nodeflow-list')) {
                    answerHtml = `<pre class="text-xs overflow-x-auto p-3 bg-gray-950 rounded">${data.answer.replace(/```nodeflow-list|```/g, '')}</pre>`;
                } else if (data.answer && data.answer.startsWith('```')) {
                    answerHtml = `<pre class="text-xs overflow-x-auto p-3 bg-gray-950 rounded">${data.answer.replace(/```/g, '')}</pre>`;
                } else {
                    answerHtml = `<p class="text-sm">${data.answer}</p>`;
                }

                card.innerHTML = `
                     <div class="agent-header">
                        <div class="agent-icon">${symbol}</div>
                        <h2 class="agent-title">${agentName.replace(/_/g, ' ')}</h2>
                        <div class="agent-status" style="font-size: 0.8rem; font-weight: bold; color: #8892b0;">Ready</div>
                        <button class="agent-btn" data-agent="${agentName}">Запустить</button>
                     </div>
                        <div class="output-type">${outputType}</div>
                        <div class="agent-actions" style="display: flex; gap: 8px; margin: 0.5rem 0;">
                            <button class="copy-btn" id="copy-btn-${agentName}" title="Скопировать ответ" style="background: none; border: none; color: var(--accent); cursor: pointer; font-size: 1.1em; padding: 0 4px;">📋</button>
                            <button class="fullscreen-btn" data-agent="${agentName}" title="Развернуть во весь экран" style="background: none; border: none; color: var(--accent); cursor: pointer; font-size: 1.1em; padding: 0 4px;">🔎➕</button>
                            <button class="zoom-in-btn" data-agent="${agentName}" title="Увеличить" style="background: none; border: none; color: var(--accent); cursor: pointer; font-size: 1.1em; padding: 0 4px; display: none;">🔎➖</button>
                        </div>
                        <div class="semantic-node" id="${semanticNodeId}" data-node-id="${semanticNodeId}" data-agent-id="${agentName}">
                            <div class="answer-panel">
                                ${answerHtml}
                            </div>
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

                const btn = card.querySelector('.agent-btn');
                btn.addEventListener('click', () => window.sendAgentRequest(agentName));
            });
        }
// Загрузка проекта
        const loadProjectModal = document.getElementById('load-project-modal');
        const closeProjectModal = document.getElementById('close-project-modal');
        const projectList = document.getElementById('project-list');

        closeProjectModal.addEventListener('click', () => {
            loadProjectModal.style.display = 'none';
        });

        window.addEventListener('click', (event) => {
            if (event.target == loadProjectModal) {
                loadProjectModal.style.display = 'none';
            }
        });

        document.getElementById('load-project').addEventListener('click', () => {
            fetch('/api/ai/projects')
                .then(response => response.json())
                .then(projects => {
                    projectList.innerHTML = ''; // Clear previous list
                    if (projects.length === 0) {
                        projectList.innerHTML = '<li>Нет сохранённых проектов.</li>';
                    } else {
                        projects.forEach(projectName => {
                            const li = document.createElement('li');
                            const a = document.createElement('a');
                            a.textContent = projectName;
                            a.dataset.projectName = projectName;
                            li.appendChild(a);
                            projectList.appendChild(li);
                        });
                    }
                    loadProjectModal.style.display = 'block';
                })
                .catch(() => alert('Не удалось загрузить список проектов.'));
        });

        projectList.addEventListener('click', (event) => {
            if (event.target.tagName === 'A') {
                const projectName = event.target.dataset.projectName;
                if (!projectName) return;

                fetch(`/api/ai/project/${projectName}`)
                    .then(response => response.json())
                    .then(data => {
                        agentData = data.agents || {};
                        questionInput.value = data.question || '';
                        renderAgents(); // This rebuilds the agent cards

                        // --- Step 9: Restore Area-Creator State ---
                        // We need a slight delay to ensure agents are rendered before we attach tools
                        setTimeout(() => {
                            if (data.areaCreatorState && window.areaCreator && typeof window.areaCreator.restoreState === 'function') {
                                window.areaCreator.restoreState(data.areaCreatorState);
                                console.log("Area-Creator state restored.");
                            }
                        }, 100);
                        // -----------------------------------------

                        loadProjectModal.style.display = 'none';
                        alert(`Проект "${projectName}" загружен.`);
                    })
                    .catch(() => alert('Проект не найден.'));
            }
        });

// Заполнить все промпты (Шаг 4 — будет ниже)
document.getElementById('fill-all-prompts').addEventListener('click', () => {
    const promptText = prompt("Введите текст для вставки во все промпты:");
    if (!promptText) return;
    document.querySelectorAll('.prompt-input').forEach(input => {
        input.value = promptText;
    });
    alert('Текст вставлен во все промпты.');
});
        window.sendAgentRequest = async function(agentName, overridePrompt = null, targetNodeId = null) {
            const card = document.getElementById(`agent-card-${agentName}`);
            if (!card) {
                console.warn(`Card for agent ${agentName} not found`);
                return;
            }
            const statusEl = card.querySelector('.agent-status');
            const btn = card.querySelector('.agent-btn');
            const promptInput = card.querySelector('.prompt-input');
            const promptSource = overridePrompt !== null ? overridePrompt : (promptInput ? promptInput.value : '');
            const prompt = promptSource.trim();
            const targetNode = targetNodeId ? document.getElementById(targetNodeId) : card.querySelector('.semantic-node');
            const answerPanel = targetNode ? targetNode.querySelector('.answer-panel') : card.querySelector('.answer-panel');

            if (!prompt) {
                alert('Пожалуйста, введите промпт.');
                return;
            }

            // Сброс статуса
            statusEl.textContent = 'Обработка...';
            statusEl.style.color = '#667eea'; // синий
            card.style.borderLeft = '4px solid #667eea'; // синий
            btn.disabled = true;
            btn.textContent = '...';

            try {
                const response = await fetch('/orchestrate/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent_name: agentName, prompt: prompt }),
                });

                if (!response.ok) throw new Error('Network response was not ok.');

                const result = await response.json();
                if (result.error) throw new Error(result.error);

                const parts = result.answer.split('--- METRICS:');
                const answer = parts[0].trim();
                let metrics = {};
                const metricsString = parts[1].match(/{.*}/s);
                if (metricsString) {
                    try {
                        metrics = JSON.parse(metricsString[0]);
                    } catch (e) {
                        console.error("Ошибка парсинга метрик:", e);
                    }
                }

                agentData[agentName] = { answer, metrics };

                // Отображение результата
                if (answer.startsWith('```nodeflow-list')) {
                    answerPanel.innerHTML = `<pre class="text-xs overflow-x-auto p-3 bg-gray-950 rounded">${answer.replace(/```nodeflow-list|```/g, '')}</pre>`;
                } else if (answer.startsWith('```')) {
                    answerPanel.innerHTML = `<pre class="text-xs overflow-x-auto p-3 bg-gray-950 rounded">${answer.replace(/```/g, '')}</pre>`;
                } else {
                    answerPanel.innerHTML = `<p class="text-sm">${answer}</p>`;
                }

                // Успешно
                statusEl.textContent = 'Готово';
                statusEl.style.color = '#64ffda'; // бирюзовый
                card.style.borderLeft = '4px solid #64ffda'; // бирюзовый
                card.style.backgroundColor = 'rgba(100, 255, 218, 0.05)';

            } catch (error) {
                console.error(`Ошибка агента ${agentName}:`, error);
                answerPanel.innerHTML = `<p class="text-sm text-red-400">Ошибка: ${error.message}</p>`;
                statusEl.textContent = 'Ошибка';
                statusEl.style.color = '#f44336'; // красный
                card.style.borderLeft = '4px solid #f44336'; // красный
                card.style.backgroundColor = 'rgba(244, 67, 54, 0.05)';
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Запустить';
                }
            }
        }

        // Загрузка из localStorage
        const savedQuestion = localStorage.getItem('orchestrator_question');
        if (savedQuestion) {
            questionInput.value = savedQuestion;
        }
        const savedProject = localStorage.getItem('orchestrator_project');
        if (savedProject) {
            agentData = JSON.parse(savedProject);
        }

        renderAgents();

        saveProjectBtn.addEventListener('click', () => {
            const projectName = prompt("Введите имя проекта:", `Orchestrator_Project_${new Date().toISOString().slice(0, 16).replace('T', '_')}`);
            if (!projectName) return;

            // --- Step 9: Get state from Area-Creator ---
            let areaCreatorState = {};
            if (window.areaCreator && typeof window.areaCreator.getState === 'function') {
                areaCreatorState = window.areaCreator.getState();
            }
            // -----------------------------------------

            const projectData = {
                project_name: projectName,
                question: questionInput.value,
                agents: agentData,
                areaCreatorState: areaCreatorState // Add the state to the project data
            };

            fetch('/orchestrator/save_project', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(projectData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`Ошибка сохранения проекта: ${data.error}`);
                } else {
                    alert(`Проект "${data.project_name}" успешно сохранён.`);
                    // Also save the main agent data to localStorage
                    localStorage.setItem('orchestrator_project', JSON.stringify(agentData));
                }
            })
            .catch(error => console.error('Ошибка сохранения проекта:', error));
        });
        let gridMode = 3;
        document.getElementById('grid-toggle').addEventListener('click', () => {
            gridMode = gridMode % 4 + 1;
            const gridPanel = document.querySelector('.grid-panel');
            gridPanel.className = 'grid-panel';
            gridPanel.classList.add(`grid-${gridMode}`);
            document.getElementById('grid-toggle').textContent = `🔢 Grid: ${gridMode}`;
        });
        downloadBtn.addEventListener('click', () => {
            console.log("Download JSON button clicked.");
            if (Object.keys(agentData).length === 0) {
                alert('Нет результатов для скачивания.');
                console.log("No data to download.");
                return;
            }
            console.log("Agent data to be downloaded:", agentData);
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(agentData, null, 2));
            console.log("Generated data URI:", dataStr);
            
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "orchestration_results.json");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
            console.log("Download triggered.");
        });
    });


    let autoCycleRunning = false;
let autoCyclePaused = false;
let autoCycleIndex = 0;
let retryCount = 0;
let autoCycleAgents = [];

function startAutoCycle() {
    if (autoCycleRunning) return;
    autoCycleRunning = true;
    autoCyclePaused = false;
    autoCycleIndex = 0;
    retryCount = 0;
    autoCycleAgents = [...agents]; // копия
    cycleNextAgent();
}

function pauseAutoCycle() {
    autoCyclePaused = true;
    document.getElementById('auto-cycle').textContent = '▶️ Продолжить';
}

function resumeAutoCycle() {
    autoCyclePaused = false;
    document.getElementById('auto-cycle').textContent = '⏸️ Приостановить';
    if (autoCycleRunning) cycleNextAgent();
}

function stopAutoCycle() {
    autoCycleRunning = false;
    autoCyclePaused = false;
    autoCycleIndex = 0;
    retryCount = 0;
    document.getElementById('auto-cycle').textContent = '🔄 Auto Cycle';
    alert('Автоцикл остановлен.');
}

async function cycleNextAgent() {
    if (!autoCycleRunning || autoCyclePaused) return;
    if (autoCycleIndex >= autoCycleAgents.length) {
        alert('Автоцикл завершён!');
        stopAutoCycle();
        return;
    }

    const agentName = autoCycleAgents[autoCycleIndex];
    const card = document.getElementById(`agent-card-${agentName}`);
    if (!card) {
        console.warn(`Карточка агента "${agentName}" не найдена. Пропускаем.`);
        autoCycleIndex++;
        setTimeout(cycleNextAgent, 0);
        return;
    }

    const promptInput = card.querySelector('.prompt-input');
    const prompt = promptInput?.value?.trim() || '';

    if (!prompt) {
        alert(`Промпт для "${agentName}" пуст. Пропускаем.`);
        autoCycleIndex++;
        setTimeout(cycleNextAgent, 1000);
        return;
    }

    const statusEl = card.querySelector('.agent-status');
    const btn = card.querySelector('.agent-btn');

    statusEl.textContent = 'Обработка...';
    statusEl.style.color = '#667eea';
    card.style.borderLeft = '4px solid #667eea';
    btn.disabled = true;
    btn.textContent = '...';

    try {
        const response = await fetch('/orchestrate/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_name: agentName, prompt })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }

        const result = await response.json();
        if (result.error) {
            throw new Error(result.error);
        }

        const answerRaw = typeof result.answer === 'string' ? result.answer : '';
        const parts = answerRaw.split('--- METRICS:');
        const answer = parts[0]?.trim() || '';
        const answerPanel = card.querySelector('.answer-panel');
        if (!answerPanel) {
            throw new Error('Не удалось найти панель ответа для вставки результата.');
        }

        if (answer.startsWith('```nodeflow-list')) {
            answerPanel.innerHTML = `<pre class="text-xs overflow-x-auto p-3 bg-gray-950 rounded">${answer.replace(/```nodeflow-list|```/g, '')}</pre>`;
        } else if (answer.startsWith('```')) {
            answerPanel.innerHTML = `<pre class="text-xs overflow-x-auto p-3 bg-gray-950 rounded">${answer.replace(/```/g, '')}</pre>`;
        } else {
            answerPanel.innerHTML = `<p class="text-sm">${answer}</p>`;
        }

        agentData[agentName] = { answer, metrics: result.metrics || {} };
        statusEl.textContent = 'Готово';
        statusEl.style.color = '#64ffda';
        card.style.borderLeft = '4px solid #64ffda';
        card.style.backgroundColor = 'rgba(100, 255, 218, 0.05)';

        autoCycleIndex++;
        retryCount = 0;
        btn.disabled = false;
        btn.textContent = 'Запустить';

        setTimeout(cycleNextAgent, 2000); // пауза 2 сек между агентами
    } catch (error) {
        console.error(`Auto Cycle error (${agentName}):`, error);
        retryCount++;
        statusEl.textContent = `Ошибка (${retryCount}/4)`;
        statusEl.style.color = '#f44336';
        card.style.borderLeft = '4px solid #f44336';
        card.style.backgroundColor = 'rgba(244, 67, 54, 0.05)';
        btn.disabled = false;
        btn.textContent = 'Запустить';

        if (retryCount >= 4) {
            console.log(`Агент "${agentName}" ошибся 4 раза. Пропускаем.`);
            autoCycleIndex++;
            retryCount = 0;
            setTimeout(cycleNextAgent, 1500);
        } else {
            setTimeout(cycleNextAgent, 3000);
        }
    }
}

document.getElementById('auto-cycle').addEventListener('click', () => {
    if (!autoCycleRunning) {
        startAutoCycle();
        document.getElementById('auto-cycle').textContent = '⏸️ Приостановить';
    } else if (autoCyclePaused) {
        resumeAutoCycle();
    } else {
        pauseAutoCycle();
    }
});
let gridMode = 3;
document.getElementById('grid-toggle').addEventListener('click', () => {
    gridMode = gridMode % 4 + 1;
    const gridPanel = document.querySelector('.grid-panel');
    gridPanel.className = 'grid-panel';
    gridPanel.classList.add(`grid-${gridMode}`);
    document.getElementById('grid-toggle').textContent = `🔢 Grid: ${gridMode}`;
});
// Обработчик копирования
// Add console panel
const consolePanel = document.createElement('div');
consolePanel.id = 'console-panel';
consolePanel.style.cssText = `
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: #1e1e1e;
    color: #f0f0f0;
    padding: 10px;
    font-family: monospace;
    overflow-y: auto;
    z-index: 1000;
    border-top: 1px solid #444;
    display: none;
`;

const consoleHeader = document.createElement('div');
consoleHeader.style.cssText = 'display: flex; justify-content: space-between; margin-bottom: 8px;';
consoleHeader.innerHTML = `
    <strong>Консоль логов</strong>
    <button id="toggle-console" style="background: #444; color: white; border: none; padding: 2px 8px; cursor: pointer;">Свернуть</button>
`;

const consoleContent = document.createElement('div');
consoleContent.id = 'console-content';
consoleContent.style.cssText = 'overflow-y: auto; height: calc(100% - 30px); font-size: 12px;';

consolePanel.appendChild(consoleHeader);
consolePanel.appendChild(consoleContent);
document.body.appendChild(consolePanel);

// Custom console.log
const originalConsoleLog = console.log;
console.log = function() {
    originalConsoleLog.apply(console, arguments);
    const message = Array.from(arguments).join(' ');
    const logEntry = document.createElement('div');
    logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logEntry.style.borderBottom = '1px solid #333';
    logEntry.style.padding = '2px 0';
    consoleContent.appendChild(logEntry);
    consoleContent.scrollTop = consoleContent.scrollHeight;
};

// Toggle console visibility
document.getElementById('toggle-console')?.addEventListener('click', function() {
    if (consolePanel.style.display === 'none') {
        consolePanel.style.display = 'block';
        this.textContent = 'Свернуть';
    } else {
        consolePanel.style.display = 'none';
        this.textContent = 'Показать логи';
    }
});

// Event delegation for all agent card interactions
document.addEventListener('click', function(e) {
    // Copy button
    if (e.target.classList.contains('copy-btn') || e.target.closest('.copy-btn')) {
        const btn = e.target.classList.contains('copy-btn') ? e.target : e.target.closest('.copy-btn');
        const card = btn.closest('.agent-card');
        const answerPanel = card.querySelector('.answer-panel');
        const text = answerPanel?.querySelector('pre')?.textContent || 
                    answerPanel?.querySelector('p')?.textContent || 
                    '';
        if (text) {
            navigator.clipboard.writeText(text).then(() => {
                console.log('Ответ скопирован в буфер обмена!');
            }).catch(err => {
                console.log('Ошибка копирования: ' + err);
            });
        }
    }
    
    // Fullscreen button
    if (e.target.classList.contains('fullscreen-btn') || e.target.closest('.fullscreen-btn')) {
        const btn = e.target.classList.contains('fullscreen-btn') ? e.target : e.target.closest('.fullscreen-btn');
        const card = btn.closest('.agent-card');
        const answerPanel = card.querySelector('.answer-panel');
        
        // Toggle fullscreen
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            answerPanel.requestFullscreen().catch(err => {
                console.log('Ошибка при переходе в полноэкранный режим:', err);
            });
        }
        
        // Toggle button visibility
        btn.style.display = 'none';
        const zoomOutBtn = card.querySelector('.zoom-in-btn');
        zoomOutBtn.style.display = 'inline-block';
    }
    
    // Zoom out button
    if (e.target.classList.contains('zoom-in-btn') || e.target.closest('.zoom-in-btn')) {
        const btn = e.target.classList.contains('zoom-in-btn') ? e.target : e.target.closest('.zoom-in-btn');
        const card = btn.closest('.agent-card');
        const fullscreenBtn = card.querySelector('.fullscreen-btn');
        
        if (document.fullscreenElement) {
            document.exitFullscreen();
        }
        
        // Toggle button visibility
        btn.style.display = 'none';
        fullscreenBtn.style.display = 'inline-block';
    }
});

// Handle fullscreen change events
document.addEventListener('fullscreenchange', () => {
    const fullscreenElements = document.querySelectorAll('.agent-card');
    fullscreenElements.forEach(card => {
        const fullscreenBtn = card.querySelector('.fullscreen-btn');
        const zoomOutBtn = card.querySelector('.zoom-in-btn');
        
        if (!document.fullscreenElement) {
            fullscreenBtn.style.display = 'inline-block';
            zoomOutBtn.style.display = 'none';
        }
    });
});

