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
                card.dataset.branchId = `branch-${agentName}`; // Add data-branch-id
                card.dataset.branchId = `branch-${agentName}`; // Add data-branch-id

                const symbol = getOperatorSymbol(agentName);
                const outputType = getOutputType(agentName);

                // Инициализируем цвет как "готово"
                card.style.borderLeft = '4px solid #64ffda'; // бирюзовый — готово
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
                        <div class="answer-panel">
                                ${answerHtml}
                                
                            </div>
                            <div class="agent-controls">
                                <button class="copy-btn" title="Скопировать ответ" style="margin-top: 0.5rem; background: none; border: none; color: var(--accent); cursor: pointer; font-size: 1.1em; padding: 0;">📋</button>
                                <select class="prompt-type">
                                    <option value="full">Full Prompt</option>
                                    <option value="short">Short Prompt</option>
                                </select>
                                
                                <textarea class="prompt-input" rows="2" placeholder="Введите промпт..."></textarea>
                         </div>
                            `;
                gridPanel.appendChild(card);

                const btn = card.querySelector('.agent-btn');
                btn.addEventListener('click', () => sendAgentRequest(agentName, card));
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
        async function sendAgentRequest(agentName, card) {
            const statusEl = card.querySelector('.agent-status');
            const answerPanel = card.querySelector('.answer-panel');
            const btn = card.querySelector('.agent-btn');
            const promptInput = card.querySelector('.prompt-input');
            const prompt = promptInput.value.trim();

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
                btn.disabled = false;
                btn.textContent = 'Запустить';
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

function cycleNextAgent() {
    if (!autoCycleRunning || autoCyclePaused) return;
    if (autoCycleIndex >= autoCycleAgents.length) {
        alert('Автоцикл завершён!');
        stopAutoCycle();
        return;
    }

    const agentName = autoCycleAgents[autoCycleIndex];
    const card = document.getElementById(`agent-card-${agentName}`);
    const promptInput = card.querySelector('.prompt-input');
    const prompt = promptInput.value.trim();

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

    fetch('/orchestrate/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_name: agentName, prompt: prompt })
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            retryCount++;
            if (retryCount >= 4) {
                alert(`Агент "${agentName}" ошибся 4 раза. Пропускаем.`);
                autoCycleIndex++;
                retryCount = 0;
                setTimeout(cycleNextAgent, 1500);
                return;
            }
            statusEl.textContent = `Ошибка (${retryCount}/4)`;
            statusEl.style.color = '#f44336';
            card.style.borderLeft = '4px solid #f44336';
            setTimeout(() => {
                btn.disabled = false;
                btn.textContent = 'Запустить';
                cycleNextAgent(); // повтор
            }, 3000);
            return;
        }

        // Успешно
        const parts = result.answer.split('--- METRICS:');
        const answer = parts[0].trim();
        const answerPanel = card.querySelector('.answer-panel');

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
        setTimeout(cycleNextAgent, 2000); // пауза 2 сек между агентами
    })
    .catch(error => {
        retryCount++;
        if (retryCount >= 4) {
            alert(`Агент "${agentName}" ошибся 4 раза. Пропускаем.`);
            autoCycleIndex++;
            retryCount = 0;
            setTimeout(cycleNextAgent, 1500);
            return;
        }
        statusEl.textContent = `Ошибка (${retryCount}/4)`;
        statusEl.style.color = '#f44336';
        card.style.borderLeft = '4px solid #f44336';
        setTimeout(() => {
            btn.disabled = false;
            btn.textContent = 'Запустить';
            cycleNextAgent();
        }, 3000);
    });
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
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('copy-btn')) {
        const answerPanel = e.target.closest('.answer-panel');
        const text = answerPanel.querySelector('pre')?.textContent || 
                     answerPanel.querySelector('p')?.textContent || 
                     '';
        if (text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('Ответ скопирован в буфер обмена!');
            }).catch(err => {
                alert('Ошибка копирования: ' + err);
            });
        }
    }
});

