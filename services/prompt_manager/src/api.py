"""FastAPI endpoints for Prompt Manager Service."""

import httpx
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .config import settings
from .storage import storage, Prompt, PromptMetadata


app = FastAPI(
    title="Prompt Manager",
    description="Локальное хранилище и управление MMSS промптами",
    version="0.1.0"
)


# ======== API Models ========

class PromptCreateRequest(BaseModel):
    """Request to create new prompt."""
    name: str
    description: str = ""
    mmss_structure: Dict[str, Any]
    category: str = "general"
    tags: List[str] = []


class PromptUpdateRequest(BaseModel):
    """Request to update prompt."""
    name: Optional[str] = None
    description: Optional[str] = None
    mmss_structure: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class OptimizeRequest(BaseModel):
    """Request to optimize prompt."""
    population_size: int = 10
    iterations: int = 20
    objective: str = "quality"


class PromptListResponse(BaseModel):
    """List of prompts response."""
    prompts: List[PromptMetadata]
    total: int


class ImportMMSSRequest(BaseModel):
    """Request to import MMSS structure."""
    mmss_structure: Dict[str, Any]
    category: str = "imported"
    tags: List[str] = []


# ======== HTML UI ========

HTML_UI = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Manager - MMSS Prompt Database</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; font-size: 1.1em; }
        .grid {
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 20px;
        }
        .sidebar {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            height: fit-content;
        }
        .main {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
            margin-bottom: 10px;
            transition: all 0.3s;
        }
        .btn:hover { background: #5568d3; transform: translateY(-2px); }
        .btn-secondary { background: #48bb78; }
        .btn-secondary:hover { background: #38a169; }
        .btn-danger { background: #f56565; }
        .btn-danger:hover { background: #e53e3e; }
        .search-box {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .search-box:focus { outline: none; border-color: #667eea; }
        .category-filter {
            width: 100%;
            padding: 10px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .prompt-list {
            max-height: 600px;
            overflow-y: auto;
        }
        .prompt-item {
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .prompt-item:hover {
            border-color: #667eea;
            background: #f7fafc;
        }
        .prompt-item.active {
            border-color: #667eea;
            background: #edf2f7;
        }
        .prompt-name {
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 5px;
        }
        .prompt-meta {
            font-size: 0.85em;
            color: #718096;
        }
        .tag {
            display: inline-block;
            background: #e2e8f0;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-right: 5px;
        }
        .detail-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
        }
        .detail-title { font-size: 1.8em; color: #2d3748; }
        .detail-actions { display: flex; gap: 10px; }
        .detail-actions .btn { width: auto; }
        .section {
            margin-bottom: 25px;
        }
        .section-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .json-viewer {
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            max-height: 500px;
            overflow-y: auto;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value { font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal.active { display: flex; }
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 12px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .form-group { margin-bottom: 15px; }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #4a5568;
        }
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
        }
        .form-group textarea {
            min-height: 200px;
            font-family: 'Monaco', 'Menlo', monospace;
        }
        .close-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 24px;
            cursor: pointer;
            color: #718096;
        }
        .optimization-history {
            margin-top: 20px;
        }
        .history-item {
            padding: 15px;
            border-left: 4px solid #667eea;
            background: #f7fafc;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
        }
        .history-date { font-size: 0.85em; color: #718096; }
        .history-score {
            font-size: 1.2em;
            font-weight: bold;
            color: #48bb78;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #718096;
        }
        .empty-state h3 { margin-bottom: 10px; color: #4a5568; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📦 Prompt Manager</h1>
            <p class="subtitle">Локальное хранилище MMSS промптов с GEPA оптимизацией</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="totalPrompts">0</div>
                <div class="stat-label">Всего промптов</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="optimizedCount">0</div>
                <div class="stat-label">Оптимизировано</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="categoriesCount">0</div>
                <div class="stat-label">Категорий</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="sidebar">
                <button class="btn" onclick="openCreateModal()">+ Новый промпт</button>
                <button class="btn btn-secondary" onclick="openImportModal()">📥 Импорт MMSS</button>
                
                <input type="text" class="search-box" id="searchBox" placeholder="🔍 Поиск промптов..." onkeyup="filterPrompts()">
                
                <select class="category-filter" id="categoryFilter" onchange="filterPrompts()">
                    <option value="">Все категории</option>
                </select>
                
                <div class="prompt-list" id="promptList">
                    <div class="empty-state">
                        <p>Загрузка...</p>
                    </div>
                </div>
            </div>
            
            <div class="main" id="detailPanel">
                <div class="empty-state">
                    <h3>Выберите промпт</h3>
                    <p>Или создайте новый для начала работы</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Create Modal -->
    <div class="modal" id="createModal">
        <div class="modal-content" style="position: relative;">
            <span class="close-btn" onclick="closeModal('createModal')">&times;</span>
            <h2>Создать новый промпт</h2>
            <form id="createForm" onsubmit="createPrompt(event)">
                <div class="form-group">
                    <label>Название (pkg)</label>
                    <input type="text" name="name" required placeholder="MY_AWESOME_PROMPT">
                </div>
                <div class="form-group">
                    <label>Описание</label>
                    <input type="text" name="description" placeholder="Краткое описание промпта">
                </div>
                <div class="form-group">
                    <label>Категория</label>
                    <select name="category">
                        <option value="general">Общее</option>
                        <option value="code">Код</option>
                        <option value="writing">Тексты</option>
                        <option value="analysis">Анализ</option>
                        <option value="chat">Чат</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>MMSS Структура (JSON)</label>
                    <textarea name="mmss_structure" required placeholder='{\n  "pkg": "...",\n  "ver": "1.0.0",\n  "ops": [...]\n}'></textarea>
                </div>
                <button type="submit" class="btn">Создать</button>
            </form>
        </div>
    </div>
    
    <!-- Import Modal -->
    <div class="modal" id="importModal">
        <div class="modal-content" style="position: relative;">
            <span class="close-btn" onclick="closeModal('importModal')">&times;</span>
            <h2>Импорт MMSS JSON</h2>
            <form id="importForm" onsubmit="importMMSS(event)">
                <div class="form-group">
                    <label>MMSS JSON</label>
                    <textarea name="mmss_json" required placeholder="Вставьте MMSS структуру..." style="min-height: 300px;"></textarea>
                </div>
                <div class="form-group">
                    <label>Категория</label>
                    <select name="category">
                        <option value="imported">Импортировано</option>
                        <option value="general">Общее</option>
                        <option value="code">Код</option>
                        <option value="writing">Тексты</option>
                    </select>
                </div>
                <button type="submit" class="btn">Импортировать</button>
            </form>
        </div>
    </div>
    
    <script>
        let prompts = [];
        let currentPrompt = null;
        
        async function loadPrompts() {
            const response = await fetch('/api/prompts');
            const data = await response.json();
            prompts = data.prompts;
            renderPromptList();
            updateStats();
            updateCategories();
        }
        
        function renderPromptList() {
            const list = document.getElementById('promptList');
            const search = document.getElementById('searchBox').value.toLowerCase();
            const category = document.getElementById('categoryFilter').value;
            
            let filtered = prompts.filter(p => {
                const matchesSearch = p.name.toLowerCase().includes(search) || 
                                     p.description.toLowerCase().includes(search);
                const matchesCategory = !category || p.category === category;
                return matchesSearch && matchesCategory;
            });
            
            if (filtered.length === 0) {
                list.innerHTML = '<div class="empty-state"><p>Нет промптов</p></div>';
                return;
            }
            
            list.innerHTML = filtered.map(p => `
                <div class="prompt-item ${currentPrompt?.metadata.id === p.id ? 'active' : ''}" 
                     onclick="selectPrompt('${p.id}')">
                    <div class="prompt-name">${p.name}</div>
                    <div class="prompt-meta">
                        v${p.version} | ${p.category} | ${new Date(p.updated_at).toLocaleDateString()}
                    </div>
                    ${p.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                </div>
            `).join('');
        }
        
        function filterPrompts() {
            renderPromptList();
        }
        
        async function selectPrompt(id) {
            const response = await fetch(`/api/prompts/${id}`);
            currentPrompt = await response.json();
            renderDetail();
            renderPromptList();
        }
        
        function renderDetail() {
            if (!currentPrompt) return;
            
            const p = currentPrompt;
            const hasHistory = p.optimization_history?.length > 0;
            const lastOptimized = hasHistory ? p.optimization_history[p.optimization_history.length - 1] : null;
            
            document.getElementById('detailPanel').innerHTML = `
                <div class="detail-header">
                    <div>
                        <div class="detail-title">${p.metadata.name}</div>
                        <p style="color: #718096; margin-top: 5px;">${p.metadata.description || 'Нет описания'}</p>
                    </div>
                    <div class="detail-actions">
                        <button class="btn btn-secondary" onclick="optimizePrompt()">⚡ Оптимизировать</button>
                        <button class="btn" onclick="exportPrompt('mmss')">📤 MMSS</button>
                        <button class="btn btn-danger" onclick="deletePrompt()">🗑 Удалить</button>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">Информация</div>
                    <p><strong>ID:</strong> ${p.metadata.id}</p>
                    <p><strong>Версия:</strong> ${p.metadata.version}</p>
                    <p><strong>Категория:</strong> ${p.metadata.category}</p>
                    <p><strong>Создан:</strong> ${new Date(p.metadata.created_at).toLocaleString()}</p>
                    <p><strong>Обновлен:</strong> ${new Date(p.metadata.updated_at).toLocaleString()}</p>
                    ${p.metadata.tags.length ? `<p><strong>Теги:</strong> ${p.metadata.tags.map(t => `<span class="tag">${t}</span>`).join('')}</p>` : ''}
                </div>
                
                ${lastOptimized ? `
                <div class="section">
                    <div class="section-title">Последняя оптимизация</div>
                    <div class="history-item">
                        <div class="history-score">Fitness: ${lastOptimized.fitness_score?.toFixed(3) || 'N/A'}</div>
                        <div class="history-date">${new Date(lastOptimized.timestamp).toLocaleString()}</div>
                        <p>Итераций: ${lastOptimized.iterations}</p>
                        ${lastOptimized.improvements?.length ? `
                            <p>Улучшения:</p>
                            <ul>${lastOptimized.improvements.map(i => `<li>${i}</li>`).join('')}</ul>
                        ` : ''}
                    </div>
                </div>
                ` : ''}
                
                <div class="section">
                    <div class="section-title">MMSS Структура</div>
                    <div class="json-viewer"><pre>${JSON.stringify(p.mmss_structure, null, 2)}</pre></div>
                </div>
                
                ${hasHistory ? `
                <div class="section optimization-history">
                    <div class="section-title">История оптимизаций (${p.optimization_history.length})</div>
                    ${p.optimization_history.slice().reverse().map((h, i) => `
                        <div class="history-item">
                            <div class="history-score">#${p.optimization_history.length - i} | Fitness: ${h.fitness_score?.toFixed(3) || 'N/A'}</div>
                            <div class="history-date">${new Date(h.timestamp).toLocaleString()}</div>
                        </div>
                    `).join('')}
                </div>
                ` : ''}
            `;
        }
        
        function updateStats() {
            document.getElementById('totalPrompts').textContent = prompts.length;
            const optimized = prompts.filter(p => (p.optimization_history?.length || 0) > 0).length;
            document.getElementById('optimizedCount').textContent = optimized;
            const categories = new Set(prompts.map(p => p.category)).size;
            document.getElementById('categoriesCount').textContent = categories;
        }
        
        function updateCategories() {
            const cats = [...new Set(prompts.map(p => p.category))];
            const select = document.getElementById('categoryFilter');
            select.innerHTML = '<option value="">Все категории</option>' + 
                cats.map(c => `<option value="${c}">${c}</option>`).join('');
        }
        
        function openCreateModal() {
            document.getElementById('createModal').classList.add('active');
        }
        
        function openImportModal() {
            document.getElementById('importModal').classList.add('active');
        }
        
        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }
        
        async function createPrompt(e) {
            e.preventDefault();
            const form = e.target;
            const mmss = JSON.parse(form.mmss_structure.value);
            
            const response = await fetch('/api/prompts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: form.name.value,
                    description: form.description.value,
                    category: form.category.value,
                    mmss_structure: mmss
                })
            });
            
            if (response.ok) {
                closeModal('createModal');
                form.reset();
                await loadPrompts();
            }
        }
        
        async function importMMSS(e) {
            e.preventDefault();
            const form = e.target;
            const mmss = JSON.parse(form.mmss_json.value);
            
            const response = await fetch('/api/prompts/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mmss_structure: mmss,
                    category: form.category.value
                })
            });
            
            if (response.ok) {
                closeModal('importModal');
                form.reset();
                await loadPrompts();
            }
        }
        
        async function optimizePrompt() {
            if (!currentPrompt) return;
            
            const btn = document.querySelector('.detail-actions .btn-secondary');
            btn.textContent = '⏳ Оптимизация...';
            btn.disabled = true;
            
            try {
                const response = await fetch(`/api/prompts/${currentPrompt.metadata.id}/optimize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        population_size: 10,
                        iterations: 20,
                        objective: 'quality'
                    })
                });
                
                if (response.ok) {
                    await selectPrompt(currentPrompt.metadata.id);
                }
            } finally {
                btn.textContent = '⚡ Оптимизировать';
                btn.disabled = false;
            }
        }
        
        async function exportPrompt(format) {
            if (!currentPrompt) return;
            const response = await fetch(`/api/prompts/${currentPrompt.metadata.id}/export?format=${format}`);
            const data = await response.json();
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentPrompt.metadata.name}_${format}.json`;
            a.click();
        }
        
        async function deletePrompt() {
            if (!currentPrompt || !confirm('Удалить этот промпт?')) return;
            
            await fetch(`/api/prompts/${currentPrompt.metadata.id}`, { method: 'DELETE' });
            currentPrompt = null;
            document.getElementById('detailPanel').innerHTML = `
                <div class="empty-state">
                    <h3>Выберите промпт</h3>
                </div>
            `;
            await loadPrompts();
        }
        
        // Initialize
        loadPrompts();
    </script>
</body>
</html>
"""


# ======== API Endpoints ========

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web UI."""
    return HTML_UI


@app.get("/api/prompts", response_model=PromptListResponse)
async def list_prompts(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """List all prompts with optional filtering."""
    prompts = await storage.list_prompts(category=category, search=search)
    return PromptListResponse(prompts=prompts, total=len(prompts))


@app.post("/api/prompts", response_model=Prompt)
async def create_prompt(request: PromptCreateRequest):
    """Create new prompt."""
    import uuid
    from datetime import datetime
    
    metadata = PromptMetadata(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        version="1.0.0",
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        tags=request.tags,
        category=request.category
    )
    
    prompt = Prompt(
        metadata=metadata,
        mmss_structure=request.mmss_structure
    )
    
    return await storage.save_prompt(prompt)


@app.get("/api/prompts/{prompt_id}", response_model=Prompt)
async def get_prompt(prompt_id: str):
    """Get prompt by ID."""
    prompt = await storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@app.put("/api/prompts/{prompt_id}", response_model=Prompt)
async def update_prompt(prompt_id: str, request: PromptUpdateRequest):
    """Update prompt."""
    prompt = await storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if request.name:
        prompt.metadata.name = request.name
    if request.description:
        prompt.metadata.description = request.description
    if request.mmss_structure:
        prompt.mmss_structure = request.mmss_structure
    if request.category:
        prompt.metadata.category = request.category
    if request.tags:
        prompt.metadata.tags = request.tags
    
    return await storage.save_prompt(prompt)


@app.delete("/api/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """Delete prompt."""
    success = await storage.delete_prompt(prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"message": "Prompt deleted"}


@app.post("/api/prompts/import", response_model=Prompt)
async def import_mmss(request: ImportMMSSRequest):
    """Import MMSS structure as new prompt."""
    return await storage.import_mmss(
        mmss_structure=request.mmss_structure,
        category=request.category,
        tags=request.tags
    )


@app.get("/api/prompts/{prompt_id}/export")
async def export_prompt(prompt_id: str, format: str = "mmss"):
    """Export prompt in specified format."""
    result = await storage.export_prompt(prompt_id, format)
    if not result:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return result


@app.post("/api/prompts/{prompt_id}/optimize")
async def optimize_prompt(prompt_id: str, request: OptimizeRequest):
    """Optimize prompt using Optimizer Service."""
    prompt = await storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Call Optimizer Service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.optimizer_url}/optimize-mmss",
                json={
                    "mmss_structure": prompt.mmss_structure,
                    "prompt_name": prompt.metadata.name,
                    "target_field": "content",
                    "config": {
                        "population_size": request.population_size,
                        "iterations": request.iterations,
                        "mutation_rate": 0.1,
                        "crossover_rate": 0.7,
                        "elitism": 1
                    },
                    "wait_for_result": True
                },
                timeout=120.0
            )
            response.raise_for_status()
            result = response.json()
        
        # Save optimization result
        if result.get("result"):
            opt_result = result["result"]
            
            # Update MMSS structure with optimized version
            if "optimized_mmss" in opt_result:
                prompt.mmss_structure = opt_result["optimized_mmss"]
            elif "optimized_prompt" in opt_result:
                # Try to parse optimized prompt as MMSS
                try:
                    import json
                    parsed = json.loads(opt_result["optimized_prompt"])
                    if isinstance(parsed, dict) and "pkg" in parsed:
                        prompt.mmss_structure = parsed
                except:
                    pass
            
            # Save updated prompt
            await storage.save_prompt(prompt)
            
            # Add to history
            await storage.add_optimization_result(prompt_id, opt_result)
            
            # Return updated prompt
            return await storage.get_prompt(prompt_id)
        
        return await storage.get_prompt(prompt_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "service": "prompt_manager",
        "storage_path": str(settings.data_dir),
        "optimizer_connected": False  # Check optimizer
    }
