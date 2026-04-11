"""
Flask Web Application for MMSS System
Многоуровневая Мета-Семантическая Система - Веб-интерфейс
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from mmss_activator import MMSSSystem
from mmss_core.fractal_reassembly import FractalReassemblyEngine
from mmss_core.temporal_navigator import TemporalNavigator
from mmss_game.game_types import EmotionalTrigger
from mmss_core.context_weaver import ContextWeaver
from mmss_core.prompt_generator import MMSSPromptGenerator
from mmss_core.ai.mistral import MistralNeMoAPI, MistralAPIError
from mmss_game.game_engine import MMSSGameEngine
from mmss_game.game_types import GameType, GameDifficulty
from mmss_core.orchestrator_core import MMSOrchestrator
from dotenv import load_dotenv
import json
import os
from datetime import datetime
import re
import subprocess
import xml.etree.ElementTree as ET

# Загрузка переменных окружения из .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mmss-system-secret-key-change-in-production')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
TASKS_FILE = os.path.join(os.path.dirname(__file__), 'TASKS.md')

def load_config():
    """Loads configuration from config.json or returns default if not found/invalid."""
    default_config = {
        "theme": "light", 
        "custom_theme_css": None,
        "mistral_model": "mistral-small-latest" # Default model
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with default config to ensure new keys are present
                return {**default_config, **config}
        except json.JSONDecodeError:
            print(f"Error decoding config.json. Using default config.")
        except Exception as e:
            print(f"Error loading config.json: {e}. Using default config.")
    return default_config

def save_config(config):
    """Saves the current configuration to config.json."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving config.json: {e}")

# Load initial configuration
app_config = load_config()

# Define the directory for saving sent prompts
CHATS_SENDEN_DIR = os.path.join(os.path.dirname(__file__), 'mmss_core', 'ai', 'chats', 'senden')
os.makedirs(CHATS_SENDEN_DIR, exist_ok=True) # Ensure the directory exists

#--- Task Functions ---
def read_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        tree = ET.parse(TASKS_FILE)
        root = tree.getroot()
        tasks = []
        for task_elem in root.findall('task'):
            task = {
                'id': task_elem.find('id').text,
                'title': task_elem.find('title').text,
                'description': task_elem.find('description').text,
                'status': task_elem.find('status').text,
                'comments': [comment.text for comment in task_elem.find('comments').findall('comment')]
            }
            tasks.append(task)
        return tasks
    except ET.ParseError:
        return []

def write_tasks(tasks):
    root = ET.Element('tasks')
    for task_dict in tasks:
        task_elem = ET.SubElement(root, 'task')
        ET.SubElement(task_elem, 'id').text = task_dict['id']
        ET.SubElement(task_elem, 'title').text = task_dict['title']
        ET.SubElement(task_elem, 'description').text = task_dict['description']
        ET.SubElement(task_elem, 'status').text = task_dict['status']
        comments_elem = ET.SubElement(task_elem, 'comments')
        for comment_text in task_dict.get('comments', []):
            ET.SubElement(comments_elem, 'comment').text = comment_text
    tree = ET.ElementTree(root)
    tree.write(TASKS_FILE, encoding='utf-8', xml_declaration=True)

# Добавляем фильтр для JSON в шаблонах
@app.template_filter('tojsonfilter')
def tojson_filter(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

# Инициализация системы MMSS
mmss_system = MMSSSystem()
mmss_activated = False
prompt_generator = MMSSPromptGenerator()
game_engine = MMSSGameEngine()

# Инициализация Mistral API (опционально, только если ключ установлен)
mistral_api = None
mistral_api_error = None
try:
    api_key = os.environ.get("MISTRAL_API_KEY")
    if api_key and api_key.strip() and api_key != "your_mistral_api_key_here":
        # Pass the model from config to the constructor
        mistral_api = MistralNeMoAPI(model=app_config.get('mistral_model'))
        print(f"✓ Mistral API инициализирован успешно с моделью: {mistral_api.model}")
    else:
        mistral_api_error = "MISTRAL_API_KEY не установлен в .env файле"
        print(f"⚠ {mistral_api_error}")
except ValueError as e:
    mistral_api_error = str(e)
    print(f"⚠ Mistral API не инициализирован: {mistral_api_error}")
except Exception as e:
    mistral_api_error = str(e)
    print(f"⚠ Ошибка инициализации Mistral API: {mistral_api_error}")


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', mmss_activated=mmss_activated, theme=app_config['theme'], custom_theme_css=app_config['custom_theme_css'])


@app.route('/activate', methods=['GET', 'POST'])
def activate():
    """Активация MMSS системы"""
    global mmss_activated
    
    if request.method == 'POST':
        domain = request.form.get('domain', 'Финансовый Анализ')
        result = mmss_system.activate_all(domain=domain)
        mmss_activated = result['all_systems_operational']
        
        if mmss_activated:
            flash('MMSS система успешно активирована!', 'success')
        else:
            flash('Ошибка активации некоторых компонентов', 'warning')
        
        return jsonify(result)
    
    return render_template('activate.html', theme=app_config['theme'], custom_theme_css=app_config['custom_theme_css'])


@app.route('/api/activate', methods=['POST'])
def api_activate():
    """API endpoint для активации"""
    global mmss_activated
    data = request.get_json()
    domain = data.get('domain', 'Финансовый Анализ')
    
    result = mmss_system.activate_all(domain=domain)
    mmss_activated = result['all_systems_operational']
    
    return jsonify(result)


@app.route('/pfr', methods=['GET', 'POST'])
def pfr():
    """PFR - Практическая Фрактальная Пересборка"""
    if request.method == 'POST':
        if request.is_json:
            # If it's an AJAX request with JSON, delegate to api_pfr
            return api_pfr()
        try:
            problem_data = {
                "area": float(request.form.get('area', 1.0)),
                "S": float(request.form.get('S', 0.8)),
                "Xi_topo": float(request.form.get('Xi_topo', 0.9)),
                "user_request": request.form.get('user_request', ''),
                "data_corpus": request.form.get('data_corpus', ''),
                "W": float(request.form.get('W', 0.95)),
                "Psi_opt": float(request.form.get('Psi_opt', 0.9)),
                "delta_V": float(request.form.get('delta_V', 0.6)),
                "delta_S": float(request.form.get('delta_S', 0.4)),
                "cost": float(request.form.get('cost', 1.2))
            }
            domain = request.form.get('domain', 'Финансовый Анализ')
            
            result = mmss_system.execute_pfr_reassembly(domain, problem_data)
            return render_template('pfr_result.html', result=result, problem_data=problem_data)
        except Exception as e:
            flash(f'Ошибка выполнения PFR: {str(e)}', 'error')
            return redirect(url_for('pfr'))
    
    return render_template('pfr.html', mmss_activated=mmss_activated, theme=app_config['theme'])


@app.route('/api/pfr', methods=['POST'])
def api_pfr():
    """API endpoint для PFR"""
    data = request.get_json()
    domain = data.get('domain', 'Финансовый Анализ')
    problem_data = data.get('problem_data', {})
    
    result = mmss_system.execute_pfr_reassembly(domain, problem_data)
    return jsonify(result)


@app.route('/frp', methods=['GET', 'POST'])
def frp():
    """FRP - Темпоральная Навигация"""
    if request.method == 'POST':
        if request.is_json:
            # If it's an AJAX request with JSON, delegate to api_frp
            return api_frp()
        try:
            scenario_data = {
                "chaos_level": float(request.form.get('chaos_level', 0.5)),
                "plot_loss": request.form.get('plot_loss') == 'on',
                "scenario_signature": request.form.get('scenario_signature', ''),
                "iteration_index": int(request.form.get('iteration_index', 1)),
                "previous_iteration": int(request.form.get('previous_iteration', 0)),
                "emotional_state": request.form.get('emotional_state', ''),
                "intention": request.form.get('intention', 'continue')
            }
            
            result = mmss_system.execute_temporal_navigation(scenario_data)
            return render_template('frp_result.html', result=result, scenario_data=scenario_data)
        except Exception as e:
            flash(f'Ошибка выполнения FRP: {str(e)}', 'error')
            return redirect(url_for('frp'))
    
    return render_template('frp.html', mmss_activated=mmss_activated, theme=app_config['theme'])


@app.route('/api/frp', methods=['POST'])
def api_frp():
    """API endpoint для FRP"""
    data = request.get_json()
    scenario_data = data.get('scenario_data', {})
    
    result = mmss_system.execute_temporal_navigation(scenario_data)
    return jsonify(result)


@app.route('/ammss', methods=['GET', 'POST'])
def ammss():
    """A-MMSS - Плетение Контекста"""
    if request.method == 'POST':
        if request.is_json:
            # If it's an AJAX request with JSON, delegate to api_ammss
            return api_ammss()
        try:
            context_data = {
                "R_T": float(request.form.get('R_T', 1.0)),
                "S_1_mean": float(request.form.get('S_1_mean', 0.3)),
                "S_1_var": float(request.form.get('S_1_var', 0.05)),
                "beta": float(request.form.get('beta', 0.5)),
                "Xi_topo_2": float(request.form.get('Xi_topo_2', 0.95)),
                "N_2": float(request.form.get('N_2', 0.05)),
                "C_val_2": float(request.form.get('C_val_2', 0.1)),
                "Phi_meta_self": float(request.form.get('Phi_meta_self', 1.0)),
                "lambda": float(request.form.get('lambda', 0.1)),
                "Cost_eth_1_sum": float(request.form.get('Cost_eth_1_sum', 0.8)),
                "Phi_fractal_field": float(request.form.get('Phi_fractal_field', 0.98)),
                "Psi_co_2": float(request.form.get('Psi_co_2', 0.95)),
                "resonance": float(request.form.get('resonance', 1.0)),
                "Phi_universal_cohesion": float(request.form.get('Phi_universal_cohesion', 0.98)),
                "absolute_contextuality": float(request.form.get('absolute_contextuality', 0.95)),
                "S_2": float(request.form.get('S_2', 0.0))
            }
            
            result = mmss_system.execute_context_weaving(context_data)
            return render_template('ammss_result.html', result=result, context_data=context_data)
        except Exception as e:
            flash(f'Ошибка выполнения A-MMSS: {str(e)}', 'error')
            return redirect(url_for('ammss'))
    
    return render_template('ammss.html', mmss_activated=mmss_activated, theme=app_config['theme'])


@app.route('/api/ammss', methods=['POST'])
def api_ammss():
    """API endpoint для A-MMSS"""
    data = request.get_json()
    context_data = data.get('context_data', {})
    
    result = mmss_system.execute_context_weaving(context_data)
    return jsonify(result)


@app.route('/status')
def status():
    """Статус системы"""
    status_info = mmss_system.get_system_status()
    return jsonify(status_info)


@app.route('/dashboard')
def dashboard():
    """Дашборд с обзором системы"""
    status_info = mmss_system.get_system_status()
    return render_template('dashboard.html', status=status_info, mmss_activated=mmss_activated, theme=app_config['theme'], custom_theme_css=app_config['custom_theme_css'])


@app.route('/prompt-generator', methods=['GET', 'POST'])
def prompt_generator_page():
    """Генератор промптов MMSS для нейросетей"""
    if request.method == 'POST':
        try:
            config = {
                'prompt_type': request.form.get('prompt_type', 'full'),
                'domain': request.form.get('domain', ''),
                'task_context': request.form.get('task_context', ''),
                'role_description': request.form.get('role_description', ''),
                'instructions': request.form.get('instructions', ''),
                'expected_result': request.form.get('expected_result', ''),
                'ethical_constraints': request.form.get('ethical_constraints', ''),
                'enable_pfr': request.form.get('enable_pfr') == 'on',
                'enable_frp': request.form.get('enable_frp') == 'on',
                'enable_ammss': request.form.get('enable_ammss') == 'on',
                'target_eta_r': request.form.get('target_eta_r') == 'on',
                'target_value': request.form.get('target_value') == 'on',
                'target_coherence': request.form.get('target_coherence') == 'on',
                'target_cohesion': request.form.get('target_cohesion') == 'on',
                'chaos_level': request.form.get('chaos_level', ''),
                'plot_loss': request.form.get('plot_loss', ''),
                'emotional_state': request.form.get('emotional_state', ''),
                'export_format': request.form.get('export_format', 'text')
            }
            
            prompt_type = config['prompt_type']
            generated_prompt = prompt_generator.generate_specialized_prompt(prompt_type, config)
            formatted_prompt = prompt_generator.generate_export_format(
                generated_prompt, 
                config['export_format']
            )
            
            return render_template('prompt_result.html', 
                                 prompt=formatted_prompt,
                                 original_prompt=generated_prompt,
                                 config=config, theme=app_config['theme'], custom_theme_css=app_config['custom_theme_css'])
        except Exception as e:
            flash(f'Ошибка генерации промпта: {str(e)}', 'error')
            return redirect(url_for('prompt_generator_page'))
    
    return render_template('prompt_generator.html', mmss_activated=mmss_activated, theme=app_config['theme'], custom_theme_css=app_config['custom_theme_css'])


@app.route('/api/prompt-generator', methods=['POST'])
def api_prompt_generator():
    """API endpoint для генерации промптов"""
    data = request.get_json()
    config = data.get('config', {})
    prompt_type = config.get('prompt_type', 'full')
    export_format = config.get('export_format', 'text')
    
    generated_prompt = prompt_generator.generate_specialized_prompt(prompt_type, config)
    formatted_prompt = prompt_generator.generate_export_format(generated_prompt, export_format)
    
    return jsonify({
        'prompt': formatted_prompt,
        'original_prompt': generated_prompt,
        'config': config
    })


@app.route('/game', methods=['GET'])
def game():
    """Страница выбора игры"""
    return render_template('game.html', mmss_activated=mmss_activated, theme=app_config['theme'], custom_theme_css=app_config['custom_theme_css'])


@app.route('/game/start', methods=['POST'])
def game_start():
    """Начать новую игру"""
    data = request.get_json() or request.form
    game_type_str = data.get('game_type', 'pfr_puzzle')
    difficulty_str = data.get('difficulty', 'medium')
    
    try:
        game_type = GameType(game_type_str)
        difficulty = GameDifficulty(difficulty_str)
    except ValueError:
        return jsonify({"error": "Неверный тип игры или сложность"}), 400
    
    result = game_engine.start_game(game_type, difficulty)
    return jsonify(result)


@app.route('/game/move', methods=['POST'])
def game_move():
    """Выполнить действие в игре"""
    data = request.get_json() or request.form
    action_id = data.get('action_id')
    parameters = data.get('parameters')
    
    if not action_id:
        return jsonify({"error": "Не указано действие"}), 400
    
    result = game_engine.make_move(action_id, parameters)
    return jsonify(result)


@app.route('/game/next-level', methods=['POST'])
def game_next_level():
    """Перейти на следующий уровень"""
    result = game_engine.next_level()
    return jsonify(result)


@app.route('/game/leaderboard', methods=['GET'])
def game_leaderboard():
    """Таблица лидеров"""
    leaderboard = game_engine.get_leaderboard()
    return jsonify({"leaderboard": leaderboard})


@app.route('/game/play/<game_type>', methods=['GET'])
def game_play(game_type):
    """Страница игры"""
    try:
        game_type_enum = GameType(game_type)
        return render_template('game_play.html', 
                             game_type=game_type,
                             game_type_enum=game_type_enum,
                             mmss_activated=mmss_activated, theme=app_config['theme'], custom_theme_css=app_config['custom_theme_css'])
    except ValueError:
        flash('Неверный тип игры', 'error')
        return redirect(url_for('game'))


@app.route('/ai', methods=['GET', 'POST'])
def ai_assistant():
    """AI ассистент с генерацией промптов и отправкой в Mistral"""
    mistral_available = mistral_api is not None
    return render_template('ai_assistant.html', 
                         mmss_activated=mmss_activated,
                         mistral_available=mistral_available,
                         mistral_error=mistral_api_error, theme=app_config['theme'], custom_theme_css=app_config['custom_theme_css'])


@app.route('/api/ai/generate-and-send', methods=['POST'])
def ai_generate_and_send():
    """Генерация промпта и отправка в Mistral AI"""
    if not mistral_api:
        return jsonify({"error": "Mistral API не инициализирован. Проверьте MISTRAL_API_KEY в .env файле"}), 400
    
    try:
        data = request.get_json()
        if not data:
            data = request.form.to_dict()
        
        user_query = data.get('user_query', '').strip()
        prompt_config = data.get('prompt_config', {}) or {}
        auto_generate_prompt = data.get('auto_generate_prompt', True)
        custom_prompt = data.get('custom_prompt', '').strip()
        
        if not user_query and not custom_prompt:
            return jsonify({"error": "Не указан запрос пользователя"}), 400
        
        # Генерация промпта MMSS (если включено)
        if auto_generate_prompt and user_query:
            # Используем user_query как контекст задачи
            prompt_config['task_context'] = user_query
            if not prompt_config.get('domain'):
                prompt_config['domain'] = 'Научные исследования'  # По умолчанию
            
            # Установка значений по умолчанию для компонентов
            if 'enable_pfr' not in prompt_config:
                prompt_config['enable_pfr'] = True
            if 'enable_frp' not in prompt_config:
                prompt_config['enable_frp'] = True
            if 'enable_ammss' not in prompt_config:
                prompt_config['enable_ammss'] = True
            
            generated_prompt = prompt_generator.generate_specialized_prompt(
                prompt_config.get('prompt_type', 'full'),
                prompt_config
            )
            
            # Комбинируем промпт с запросом пользователя
            full_prompt = f"{generated_prompt}\n\n## Задача пользователя:\n{user_query}"
        else:
            full_prompt = custom_prompt or user_query

        # Save the full prompt to a file
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
            filename = os.path.join(CHATS_SENDEN_DIR, f"prompt_{timestamp}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_prompt)
        except Exception as e:
            print(f"Error saving prompt: {e}") # Log error but don't block the request
        
        # Отправка в Mistral
        history = data.get('history', [])
        if not isinstance(history, list):
            history = []
        
        # Отправка в Mistral
        print(f"[AI] Отправка запроса в Mistral API...")
        print(f"[AI] Промпт (первые 200 символов): {full_prompt[:200]}...")
        
        response = mistral_api.get_response(full_prompt, history=history)
        
        print(f"[AI] Получен ответ от Mistral (длина: {len(response) if response else 0})")
        
        if not response or not response.strip():
            return jsonify({"error": "Пустой ответ от Mistral API. Проверьте API ключ и попробуйте снова."}), 500
        
        return jsonify({
            "status": "success",
            "response": response,
            "prompt_used": full_prompt,
            "prompt_generated": auto_generate_prompt,
            "model": mistral_api.model
        })
        
    except MistralAPIError as e:
        import traceback
        print(f"MistralAPIError: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"Ошибка Mistral API: {str(e)}"}), 500
    except Exception as e:
        import traceback
        print(f"Exception in ai_generate_and_send: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"Ошибка: {str(e)}"}), 500


@app.route('/api/ai/generate-prompt-only', methods=['POST'])
def ai_generate_prompt_only():
    """Только генерация промпта без отправки в AI"""
    data = request.get_json() or request.form
    user_query = data.get('user_query', '')
    prompt_config = data.get('prompt_config', {})
    
    if not user_query:
        return jsonify({"error": "Не указан запрос пользователя"}), 400
    
    try:
        prompt_config['task_context'] = user_query
        if not prompt_config.get('domain'):
            prompt_config['domain'] = 'Научные исследования'
        
        generated_prompt = prompt_generator.generate_specialized_prompt(
            prompt_config.get('prompt_type', 'full'),
            prompt_config
        )
        
        # Комбинируем промпт с запросом пользователя
        full_prompt = f"{generated_prompt}\n\n## Задача пользователя:\n{user_query}"
        
        return jsonify({
            "status": "success",
            "prompt": full_prompt,
            "config": prompt_config
        })
        
    except Exception as e:
        return jsonify({"error": f"Ошибка генерации промпта: {str(e)}"}), 500


@app.route('/api/settings/theme', methods=['POST'])
def update_theme():
    """API endpoint to update the theme setting."""
    global app_config
    data = request.get_json()
    new_theme = data.get('theme')
    if new_theme in ['light', 'dark']:
        app_config['theme'] = new_theme
        save_config(app_config)
        return jsonify({"status": "success", "theme": new_theme})
    return jsonify({"status": "error", "message": "Invalid theme"}), 400


@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    """Displays the settings page and handles settings updates."""
    global app_config
    if request.method == 'POST':
        # Update theme
        new_theme = request.form.get('theme')
        if new_theme in ['light', 'dark']:
            app_config['theme'] = new_theme

        # Update Mistral model
        new_model = request.form.get('mistral_model')
        if new_model:
            app_config['mistral_model'] = new_model
            # Update the running mistral_api instance if it exists
            if mistral_api:
                mistral_api.model = new_model
                print(f"[Settings] Mistral model updated to: {new_model}")

        save_config(app_config)
        flash('Настройки успешно сохранены!', 'success')
        return redirect(url_for('settings_page'))

    # GET request: display the page
    mistral_models = []
    if mistral_api:
        try:
            mistral_models = mistral_api.list_models()
        except MistralAPIError as e:
            flash(f'Не удалось получить список моделей Mistral: {e}', 'danger')

    return render_template('settings.html', 
                         config=app_config, 
                         mistral_models=mistral_models,
                         selected_model=app_config.get('mistral_model'),
                         theme=app_config['theme'], 
                         custom_theme_css=app_config['custom_theme_css'])


@app.route('/settings/save', methods=['POST'])
def save_settings():
    """Saves updated settings from the settings page."""
    global app_config
    try:
        new_config = request.get_json()
        if not isinstance(new_config, dict):
            return jsonify({"status": "error", "message": "Invalid JSON format"}), 400
        
        # Update app_config with new values
        app_config.update(new_config)
        save_config(app_config)
        
        # If theme was changed, update the theme in the session/frontend
        if 'theme' in new_config and new_config['theme'] != app_config.get('theme'):
            # This part is handled by the theme.js, which also calls the /api/settings/theme endpoint
            # So, we just need to ensure the config is saved.
            pass

        return jsonify({"status": "success", "message": "Настройки успешно сохранены!"})
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Неверный формат JSON."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/tasks')
def tasks_page():
    """Displays the tasks page."""
    tasks = read_tasks()
    return render_template('tasks.html', tasks=tasks, theme=app_config['theme'], custom_theme_css=app_config.get('custom_theme_css'))


@app.route('/tasks/add', methods=['POST'])
def add_task():
    """Adds a new task."""
    tasks = read_tasks()
    new_task = {
        'id': f'TASK-{len(tasks) + 1}',
        'title': request.form.get('task_description'),
        'description': request.form.get('task_description'),
        'status': 'todo',
        'comments': []
    }
    tasks.append(new_task)
    write_tasks(tasks)
    flash('Task added successfully!', 'success')
    return redirect(url_for('tasks_page'))


@app.route('/tasks/delete', methods=['POST'])
def delete_task():
    """Deletes a task."""
    tasks = read_tasks()
    task_id_to_delete = request.form.get('task_id')
    tasks = [task for task in tasks if task['id'] != task_id_to_delete]
    write_tasks(tasks)
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks_page'))


@app.route('/tasks/update_status', methods=['POST'])
def update_task_status():
    """Updates the status of a task."""
    tasks = read_tasks()
    data = request.get_json()
    task_id = data.get('task_id')
    new_status = data.get('new_status')
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            break
    write_tasks(tasks)
    return jsonify({'status': 'success'})


@app.route('/tasks/edit', methods=['POST'])
def edit_task():
    """Edits a task."""
    tasks = read_tasks()
    data = request.get_json()
    task_id = data.get('task_id')
    new_description = data.get('description')
    for task in tasks:
        if task['id'] == task_id:
            task['description'] = new_description
            task['title'] = new_description.splitlines()[0] # Use first line as title
            break
    write_tasks(tasks)
    return jsonify({'status': 'success'})


PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'mmss_core', 'ai', 'projects')

CUSTOM_THEMES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'custom_themes')
os.makedirs(CUSTOM_THEMES_DIR, exist_ok=True)

@app.route('/api/settings/upload_custom_theme', methods=['POST'])
def upload_custom_theme():
    global app_config
    if 'custom_css_file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['custom_css_file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    if file and file.filename.endswith('.css'):
        filename = "custom_theme.css" # Standardize filename
        filepath = os.path.join(CUSTOM_THEMES_DIR, filename)
        try:
            file.save(filepath)
            app_config['custom_theme_css'] = url_for('static', filename=f'custom_themes/{filename}')
            save_config(app_config)
            return jsonify({"status": "success", "message": "Custom theme uploaded and applied!"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to save file: {str(e)}"}), 500
    
    return jsonify({"status": "error", "message": "Invalid file type. Only .css files are allowed."}), 400

@app.route('/api/settings/clear_custom_theme', methods=['POST'])
def clear_custom_theme():
    global app_config
    try:
        if app_config.get('custom_theme_css'):
            # Optionally delete the file from disk
            filename = os.path.basename(app_config['custom_theme_css'])
            filepath = os.path.join(CUSTOM_THEMES_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            app_config['custom_theme_css'] = None
            save_config(app_config)
            return jsonify({"status": "success", "message": "Custom theme cleared!"}), 200
        return jsonify({"status": "success", "message": "No custom theme to clear."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to clear custom theme: {str(e)}"}), 500

@app.route('/api/ai/projects', methods=['GET'])
def list_projects():
    """List saved AI assistant projects."""
    # ✅ ИЗМЕНЕНО: Теперь ищем в правильной папке
    PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'mmss_core', 'ai', 'projects', 'orchestrator')
    if not os.path.exists(PROJECTS_DIR):
        os.makedirs(PROJECTS_DIR)
    projects = [f.replace('.json', '') for f in os.listdir(PROJECTS_DIR) if f.endswith('.json')]
    return jsonify(projects)

@app.route('/api/ai/projects/save', methods=['POST'])
def save_project():
    """Save an AI assistant project."""
    data = request.get_json()
    project_name = data.get('project_name')
    if not project_name or not project_name.strip():
        return jsonify({"error": "Project name is required"}), 400

    # Sanitize project name to prevent directory traversal
    project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    if not project_name:
        return jsonify({"error": "Invalid project name"}), 400

    file_path = os.path.join(PROJECTS_DIR, f"{project_name}.json")
    
    project_data = {
        "history": data.get('history', []),
        "settings": data.get('settings', {})
    }

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=4)
        return jsonify({"status": "success", "project_name": project_name})
    except Exception as e:
        return jsonify({"error": f"Failed to save project: {str(e)}"}), 500

@app.route('/api/ai/project/<project_name>', methods=['GET'])
@app.route('/api/ai/project/<project_name>', methods=['GET'])
def load_project(project_name):
    # ✅ ИЗМЕНЕНО: Используем ту же папку
    PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'mmss_core', 'ai', 'projects', 'orchestrator')
    project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    file_path = os.path.join(PROJECTS_DIR, f"{project_name}.json")
    if not os.path.exists(file_path):
        return jsonify({"error": "Project not found"}), 404
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        return jsonify(project_data)
    except Exception as e:
        return jsonify({"error": f"Failed to load project: {str(e)}"}), 500


@app.route('/api/tasks/run', methods=['POST'])
def run_task_in_terminal():

    """Simulates running a task in a terminal and returns dummy output."""

    data = request.get_json()

    task_id = data.get('task_id')



    # Placeholder for actual task execution logic

    # In a real scenario, you would fetch the task by ID, get its command,

    # execute it using subprocess, and capture stdout/stderr.

    if task_id:

        # Simulate some output

        output = f"Executing task {task_id}...\n"

        output += "This is a simulated console output.\n"

        output += "Command completed successfully.\n"

        return jsonify({"status": "success", "output": output})

    else:

        return jsonify({"status": "error", "message": "Task ID not provided"}), 400



@app.route('/orchestrator')
def orchestrator():
    """Renders the MMSS Orchestrator page."""
    return render_template('orchestrator_v2.html', theme=app_config['theme'], custom_theme_css=app_config.get('custom_theme_css'))

@app.route('/orchestrate/send', methods=['POST'])
def orchestrate_send():
    """Handles sending a prompt for a single agent to the Mistral API (LIVE MODE ONLY)."""
    data = request.get_json()
    agent_name = data.get('agent_name')
    prompt = data.get('prompt')

    if not agent_name or not prompt:
        return jsonify({"error": "Agent name and prompt are required"}), 400

    try:
        # Инициализируем оркестратор
        orchestrator = MMSOrchestrator()
        
        # Проверяем, доступен ли Mistral
        if orchestrator.mistral_api_error:
            return jsonify({"error": f"Mistral API error: {orchestrator.mistral_api_error}"}), 500
        
        if not orchestrator.mistral_api:
            return jsonify({"error": "Mistral API not initialized. Check MISTRAL_API_KEY in .env"}), 500

        # ГЕНЕРИРУЕМ КОРРЕКТНЫЙ PROMPT ДЛЯ АГЕНТА
        agents = orchestrator.get_agents()
        agent_config = next((a for a in agents if a['name'] == agent_name), None)
        if not agent_config:
            return jsonify({"error": f"Agent {agent_name} not found in config"}), 404

        system_prompt = orchestrator.generate_prompt(agent_config, prompt)
        print(f"[Orchestrator] Sending to Mistral: {system_prompt[:200]}...")

        # ОТПРАВЛЯЕМ В MISTRAL — ТОЛЬКО LIVE
        response = orchestrator.send_prompt_to_mistral(system_prompt)

        # Сохраняем лог
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
            filename = os.path.join(CHATS_SENDEN_DIR, f"prompt_{timestamp}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"--- PROMPT ---\n{system_prompt}\n\n--- RESPONSE ---\n{response}")
        except Exception as e:
            print(f"Error saving orchestrator chat log: {e}")

        # ВАЖНО: Mistral **не возвращает** метрики автоматически
        # Поэтому мы ВРУЧНУЮ ДОБАВЛЯЕМ СТРОКУ " --- METRICS: {...}"
        # Это нужно для парсинга на фронтенде
        metrics_stub = {
            "V": 0.99,
            "N": 0.98,
            "S": 0.01,
            "D_f": 9.0,
            "G_S": 150.0,
            "R_T": 2.618
        }
        final_response = f"{response} --- METRICS: {json.dumps(metrics_stub, ensure_ascii=False)}"

        return jsonify({"answer": final_response})
    except MistralAPIError as e:
        return jsonify({"error": f"Mistral API error: {str(e)}"}), 500
    except Exception as e:
        import traceback
        print(f"Unexpected error in /orchestrate/send: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"Internal error: {str(e)}"}), 500



@app.route('/orchestrator/save_project', methods=['POST'])
def save_orchestrator_project():
    """Saves the orchestrator project."""
    data = request.get_json()
    project_name = data.get('project_name', f"Orchestrator_Project_{datetime.now().strftime('%Y-%m-%d_%H-%M')}")
    
    # Sanitize project name
    project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    if not project_name:
        return jsonify({"error": "Invalid project name"}), 400

    projects_dir = os.path.join(os.path.dirname(__file__), 'mmss_core', 'ai', 'projects', 'orchestrator')
    os.makedirs(projects_dir, exist_ok=True)
    file_path = os.path.join(projects_dir, f"{project_name}.json")

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return jsonify({"status": "success", "project_name": project_name})
    except Exception as e:
        return jsonify({"error": f"Failed to save project: {str(e)}"}), 500


if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)


