document.addEventListener('DOMContentLoaded', () => {
    // --- Step 2: Initialization ---
    let sessionTools = []; // Array for non-preset tools
    let selectedText = '';
    let selectedNode = null; // Keep track of the node where text was selected

    // --- DOM Elements ---
    const createToolModal = document.getElementById('create-tool-modal');
    const closeCreateToolModal = document.getElementById('close-create-tool-modal');
    const saveToolButton = document.getElementById('save-tool-button');
    const cancelToolButton = document.getElementById('cancel-tool-button');
    const toolNameInput = document.getElementById('tool-name-input');
    const toolPromptInput = document.getElementById('tool-prompt-input');
    const saveAsPresetCheckbox = document.getElementById('save-as-preset-checkbox');
    const gridPanel = document.querySelector('.grid-panel');

    // Create the "+ Create Tool" button
    const createToolBtn = document.createElement('button');
    createToolBtn.textContent = '+ Создать инструмент';
    createToolBtn.className = 'absolute z-10 bg-blue-600 text-white px-3 py-1 rounded-md shadow-lg text-sm';
    createToolBtn.style.display = 'none';
    document.body.appendChild(createToolBtn);

    // --- Step 3: Text Selection Handling ---
    const updateSelectionContext = () => {
        const selection = window.getSelection();
        if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
            return false;
        }

        const range = selection.getRangeAt(0);
        let parent = range.commonAncestorContainer;
        parent = parent && parent.nodeType === Node.ELEMENT_NODE ? parent : parent?.parentNode;

        if (!parent || !gridPanel.contains(parent)) {
            return false;
        }

        const answerPanel = parent.closest('.answer-panel');
        if (!answerPanel) {
            return false;
        }

        const text = selection.toString().trim();
        if (!text) {
            return false;
        }

        const hostingNode = answerPanel.closest('.semantic-node');
        if (!hostingNode) {
            return false;
        }

        selectedText = text;
        selectedNode = hostingNode;

        const rect = range.getBoundingClientRect();
        createToolBtn.style.left = `${rect.left + window.scrollX}px`;
        createToolBtn.style.top = `${rect.bottom + window.scrollY + 5}px`;
        createToolBtn.style.display = 'block';
        return true;
    };

    gridPanel.addEventListener('mouseup', () => {
        if (!updateSelectionContext()) {
            createToolBtn.style.display = 'none';
        }
    });

    document.addEventListener('selectionchange', () => {
        const selection = window.getSelection();
        if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
            createToolBtn.style.display = 'none';
            return;
        }

        let anchorNode = selection.anchorNode;
        anchorNode = anchorNode && anchorNode.nodeType === Node.ELEMENT_NODE ? anchorNode : anchorNode?.parentNode;

        if (!anchorNode || !gridPanel.contains(anchorNode)) {
            createToolBtn.style.display = 'none';
        }
    });

    document.addEventListener('mousedown', (event) => {
        if (!createToolBtn.contains(event.target)) {
            createToolBtn.style.display = 'none';
        }
    });

    // --- Step 4 & 5: Tool Creation Modal and Saving ---
    createToolBtn.addEventListener('click', () => {
        toolPromptInput.value = `Детализируй: {{selected_text}}`; // Pre-fill with template
        createToolModal.style.display = 'flex';
        createToolBtn.style.display = 'none';
    });

    closeCreateToolModal.addEventListener('click', () => createToolModal.style.display = 'none');
    cancelToolButton.addEventListener('click', () => createToolModal.style.display = 'none');

    saveToolButton.addEventListener('click', () => {
        const toolName = toolNameInput.value.trim();
        const toolPrompt = toolPromptInput.value.trim();
        const isPreset = saveAsPresetCheckbox.checked;

        if (!toolName || !toolPrompt) {
            alert('Пожалуйста, заполните все поля.');
            return;
        }

        const newTool = {
            id: `tool_${Date.now()}`,
            name: toolName,
            prompt: toolPrompt,
        };

        if (isPreset) {
            let presets = JSON.parse(localStorage.getItem('mmss_tools_presets') || '[]');
            presets.push(newTool);
            localStorage.setItem('mmss_tools_presets', JSON.stringify(presets));
            // showToast('Инструмент сохранен как пресет.', 'success');
        } else {
            sessionTools.push(newTool);
        }

        // Add the tool visually to the node
        if (selectedNode) {
            addToolButtonToNode(selectedNode, newTool);
        }

        console.log("New tool created:", newTool, "Preset:", isPreset);

        // Reset and hide modal
        createToolModal.style.display = 'none';
        toolNameInput.value = '';
        toolPromptInput.value = '';
        saveAsPresetCheckbox.checked = false;
    });

    // --- Step 8 (Refactored): Restore MemoryTools ---
    const restoreMemoryToolsButton = document.getElementById('restore-memory-tools');
    const memoryToolsPanel = document.getElementById('memory-tools-panel');
    const memoryToolButtonsContainer = memoryToolsPanel.querySelector('.memory-tool-buttons');

    restoreMemoryToolsButton.addEventListener('click', () => {
        const presets = JSON.parse(localStorage.getItem('mmss_tools_presets') || '[]');
        if (presets.length === 0) {
            alert('Нет сохраненных пресетов.');
            return;
        }

        // Clear previous buttons and show the panel
        memoryToolButtonsContainer.innerHTML = '';
        memoryToolsPanel.style.display = 'block';

        presets.forEach(preset => {
            const toolButton = document.createElement('button');
            toolButton.textContent = preset.name;
            toolButton.dataset.toolId = preset.id;

            toolButton.addEventListener('click', () => {
                if (!selectedText || !selectedNode) {
                    alert("Нет выделенного текста для применения инструмента. Сначала выделите текст в ответе агента.");
                    return;
                }
                
                const finalPrompt = preset.prompt.replace('{{selected_text}}', selectedText);

                console.log(`Applying preset tool: ${preset.name}`);
                console.log(`Node: ${selectedNode.id}`);
                console.log(`Selected Text: ${selectedText}`);
                console.log(`Final Prompt: ${finalPrompt}`);

                const agentId = selectedNode.closest('[data-agent-id]').dataset.agentId;
                if (typeof window.sendAgentRequest === 'function') {
                    window.sendAgentRequest(agentId, finalPrompt, selectedNode.id);
                } else {
                    console.error('sendAgentRequest function not found.');
                }
            });
            memoryToolButtonsContainer.appendChild(toolButton);
        });
    });

    // --- Step 10: Semantic Markup (helpLinks-forAI) ---
    // Create a single tooltip element to be reused
    const helpTooltip = document.createElement('div');
    helpTooltip.className = 'absolute z-20 px-3 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg shadow-sm opacity-0 transition-opacity duration-300';
    helpTooltip.style.pointerEvents = 'none'; // Prevent tooltip from interfering with mouse events
    document.body.appendChild(helpTooltip);

    function initializeHelpLinks(container) {
        container.querySelectorAll('.help-link').forEach(link => {
            link.addEventListener('mouseover', (event) => {
                const tooltipText = link.dataset.mmssSystem;
                if (!tooltipText) return;

                helpTooltip.textContent = tooltipText;
                helpTooltip.style.opacity = 1;

                const rect = event.target.getBoundingClientRect();
                helpTooltip.style.left = `${rect.left + window.scrollX}px`;
                helpTooltip.style.top = `${rect.bottom + window.scrollY + 5}px`;
            });

            link.addEventListener('mouseout', () => {
                helpTooltip.style.opacity = 0;
            });
        });
    }

    // Initialize for any existing content on load
    initializeHelpLinks(document.body);

    // Use a MutationObserver to initialize tooltips on new content added later
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    initializeHelpLinks(node);
                }
            });
        });
    });

    observer.observe(gridPanel, { childList: true, subtree: true });


    // --- Step 11: Orchestrator-Conductor (Create Summary Response) ---
    const createSummaryButton = document.getElementById('create-summary-response');
    createSummaryButton.addEventListener('click', async () => {
        let summaryContent = "### Исходный вопрос:\n";
        const mainQuestion = document.getElementById('question').value;
        summaryContent += `${mainQuestion}\n\n### Ответы агентов:\n`;

        document.querySelectorAll('.agent-card').forEach(card => {
            const agentTitle = card.querySelector('.agent-title').textContent;
            const answerText = card.querySelector('.answer-panel').innerText;
            if (answerText) {
                summaryContent += `\n---\n#### Агент: ${agentTitle}\n${answerText}\n`;
            }
        });

        const summaryPrompt = `
            Проанализируй следующую сессию работы оркестратора. 
            Собери ключевые идеи, выводы и сгенерированные данные в единый, структурированный итоговый отчет.
            Устрани избыточность, сохрани важные детали и представь результат в виде целостного документа.
            \n\n${summaryContent}
        `;

        console.log("Creating summary with prompt:", summaryPrompt);
        // showToast('Создание сводного отчета...', 'info');

        try {
            const response = await fetch('/orchestrate/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    agent_name: 'OMNIAGENT_UNIFIED_SYNTHESIZER',
                    prompt: summaryPrompt
                }),
            });

            if (!response.ok) throw new Error('Network response was not ok.');
            const result = await response.json();
            if (result.error) throw new Error(result.error);

            displaySummaryResponse(result.answer);
            // showToast('Сводный отчет создан.', 'success');

        } catch (error) {
            console.error('Error creating summary response:', error);
            // showToast(`Ошибка: ${error.message}`, 'error');
        }
    });

    function displaySummaryResponse(summaryHtml) {
        let summaryNode = document.getElementById('summary-response-node');
        if (!summaryNode) {
            summaryNode = document.createElement('div');
            summaryNode.id = 'summary-response-node';
            // Changed class to match agent-card and appended to gridPanel
            summaryNode.className = 'agent-card bg-gray-800 border border-purple-500'; 
            const gridPanel = document.querySelector('.grid-panel');
            gridPanel.appendChild(summaryNode);
        }

        summaryNode.innerHTML = `
            <div class="agent-header">
                <div class="agent-icon">🌀</div>
                <h2 class="agent-title">Сводный ответ</h2>
            </div>
            <div class="answer-panel mt-2">${summaryHtml}</div>
        `;
    }


    // --- Step 9: Fractal State Storage (Frontend) ---
    window.areaCreator = {
        sessionTools: sessionTools,
        getState: () => {
            const nodeToolMap = {};
            document.querySelectorAll('.semantic-node').forEach(node => {
                const nodeId = node.dataset.nodeId || node.id;
                if (!nodeId) return;

                const appliedTools = [];
                node.querySelectorAll('.context-tools button').forEach(button => {
                    appliedTools.push({
                        id: button.dataset.toolId,
                        name: button.textContent
                    });
                });

                if (appliedTools.length > 0) {
                    nodeToolMap[nodeId] = appliedTools;
                }
            });

            return {
                tools: sessionTools,
                nodeToolMap: nodeToolMap
            };
        },
        restoreState: (state) => {
            if (!state) return;

            // Restore session tools
            sessionTools = state.tools || [];

            // Restore tools on nodes
            if (state.nodeToolMap) {
                for (const nodeId in state.nodeToolMap) {
                    const node = document.getElementById(nodeId);
                    if (node) {
                        const toolsForNode = state.nodeToolMap[nodeId];
                        toolsForNode.forEach(tool => {
                            // We need the full tool object, which should be in sessionTools
                            const fullTool = sessionTools.find(t => t.id === tool.id);
                            if (fullTool) {
                                addToolButtonToNode(node, fullTool);
                            }
                        });
                    }
                }
            }
        }
    };


    // --- Step 6: Displaying Tool Buttons ---
    function addToolButtonToNode(node, tool) {
        let toolsContainer = node.querySelector('.context-tools');
        if (!toolsContainer) {
            toolsContainer = document.createElement('div');
            toolsContainer.className = 'context-tools mt-2 flex flex-wrap gap-2';
            // Insert after the content but before children
            const childrenContainer = node.querySelector('.semantic-children');
            if(childrenContainer) {
                node.insertBefore(toolsContainer, childrenContainer);
            } else {
                node.appendChild(toolsContainer);
            }
        }

        const toolButton = document.createElement('button');
        toolButton.className = 'bg-purple-600 hover:bg-purple-700 text-white px-2 py-1 rounded-md text-xs';
        toolButton.textContent = tool.name;
        toolButton.dataset.toolId = tool.id;

        // --- Step 7: Applying the Tool ---
        toolButton.addEventListener('click', () => {
             if (!selectedText) {
                alert("Нет выделенного текста для применения инструмента.");
                return;
            }
            const finalPrompt = tool.prompt.replace('{{selected_text}}', selectedText);

            console.log(`Applying tool: ${tool.name}`);
            console.log(`Node: ${node.dataset.nodeId}`);
            console.log(`Selected Text: ${selectedText}`);
            console.log(`Final Prompt: ${finalPrompt}`);

            // Find the agent associated with this node to send the request
            const agentId = node.closest('[data-agent-id]').dataset.agentId;
            if (typeof window.sendAgentRequest === 'function') {
                 // Assuming sendAgentRequest can take a target node ID to append the result
                window.sendAgentRequest(agentId, finalPrompt, node.dataset.nodeId);
            } else {
                console.error('sendAgentRequest function not found.');
                // showToast('Ошибка: функция отправки запроса не найдена.', 'error');
            }
        });

        toolsContainer.appendChild(toolButton);
    }
});