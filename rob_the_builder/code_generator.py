"""
Code Generator for Rob the Builder

Generates actual working code for apps based on templates.
"""

from typing import Dict, List
from .app_templates import AppSpec


class CodeGenerator:
    """Generates code for various app platforms."""

    def generate(self, spec: AppSpec) -> Dict[str, str]:
        """
        Generate code files for an app.

        Args:
            spec: App specification

        Returns:
            Dictionary mapping filenames to file contents
        """
        if spec.platform == 'web':
            return self._generate_web_app(spec)
        else:
            raise ValueError(f"Unsupported platform: {spec.platform}")

    def _generate_web_app(self, spec: AppSpec) -> Dict[str, str]:
        """Generate HTML/CSS/JS web app."""
        if spec.app_type == 'todolist':
            return self._generate_todo_app(spec)
        elif spec.app_type == 'calculator':
            return self._generate_calculator_app(spec)
        elif spec.app_type == 'notes':
            return self._generate_notes_app(spec)
        elif spec.app_type == 'simplegame':
            return self._generate_simple_game(spec)
        else:
            raise ValueError(f"Unknown app type: {spec.app_type}")

    def _generate_todo_app(self, spec: AppSpec) -> Dict[str, str]:
        """Generate a todo list app."""
        color = spec.customizations.get('color', 'blue')

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{spec.name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="app-container">
        <header>
            <h1>{spec.name}</h1>
            <p>{spec.description}</p>
        </header>

        <div class="add-task-section">
            <input type="text" id="taskInput" placeholder="What do you need to do?" />
            <button id="addButton" class="btn-primary">Add Task</button>
        </div>

        <div class="task-list-section">
            <ul id="taskList"></ul>
        </div>

        <div class="actions-section">
            <button id="clearCompleted" class="btn-secondary">Clear Completed</button>
            <span id="taskCounter">0 tasks</span>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>'''

        css = f'''* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: linear-gradient(135deg, #{self._get_color_hex(color)} 0%, #667eea 100%);
    min-height: 100vh;
    padding: 20px;
}}

.app-container {{
    max-width: 600px;
    margin: 0 auto;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    padding: 30px;
}}

header {{
    text-align: center;
    margin-bottom: 30px;
}}

header h1 {{
    color: #{self._get_color_hex(color)};
    font-size: 2.5em;
    margin-bottom: 10px;
}}

header p {{
    color: #666;
    font-size: 1.1em;
}}

.add-task-section {{
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}}

#taskInput {{
    flex: 1;
    padding: 15px;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    font-size: 1em;
    transition: border-color 0.3s;
}}

#taskInput:focus {{
    outline: none;
    border-color: #{self._get_color_hex(color)};
}}

.btn-primary {{
    padding: 15px 30px;
    background: #{self._get_color_hex(color)};
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1em;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}}

.btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}}

.btn-primary:active {{
    transform: translateY(0);
}}

.task-list-section {{
    min-height: 200px;
    margin-bottom: 20px;
}}

#taskList {{
    list-style: none;
}}

.task-item {{
    display: flex;
    align-items: center;
    padding: 15px;
    background: #f9f9f9;
    border-radius: 10px;
    margin-bottom: 10px;
    transition: all 0.3s;
}}

.task-item:hover {{
    background: #f0f0f0;
    transform: translateX(5px);
}}

.task-item.completed {{
    opacity: 0.6;
}}

.task-item input[type="checkbox"] {{
    width: 20px;
    height: 20px;
    margin-right: 15px;
    cursor: pointer;
}}

.task-text {{
    flex: 1;
    font-size: 1.1em;
}}

.task-item.completed .task-text {{
    text-decoration: line-through;
    color: #999;
}}

.delete-btn {{
    padding: 8px 15px;
    background: #ff4757;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9em;
    transition: background 0.3s;
}}

.delete-btn:hover {{
    background: #ff3838;
}}

.actions-section {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 20px;
    border-top: 2px solid #e0e0e0;
}}

.btn-secondary {{
    padding: 10px 20px;
    background: #95a5a6;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9em;
    transition: background 0.3s;
}}

.btn-secondary:hover {{
    background: #7f8c8d;
}}

#taskCounter {{
    color: #666;
    font-weight: 500;
}}'''

        js = '''// Todo List App Logic
let tasks = [];

// Load tasks from localStorage
function loadTasks() {
    const saved = localStorage.getItem('tasks');
    if (saved) {
        tasks = JSON.parse(saved);
        renderTasks();
    }
}

// Save tasks to localStorage
function saveTasks() {
    localStorage.setItem('tasks', JSON.stringify(tasks));
}

// Render all tasks
function renderTasks() {
    const taskList = document.getElementById('taskList');
    taskList.innerHTML = '';

    tasks.forEach((task, index) => {
        const li = document.createElement('li');
        li.className = `task-item ${task.completed ? 'completed' : ''}`;

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = task.completed;
        checkbox.addEventListener('change', () => toggleTask(index));

        const span = document.createElement('span');
        span.className = 'task-text';
        span.textContent = task.text;

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', () => deleteTask(index));

        li.appendChild(checkbox);
        li.appendChild(span);
        li.appendChild(deleteBtn);
        taskList.appendChild(li);
    });

    updateCounter();
}

// Add new task
function addTask() {
    const input = document.getElementById('taskInput');
    const text = input.value.trim();

    if (text) {
        tasks.push({ text, completed: false });
        input.value = '';
        saveTasks();
        renderTasks();
    }
}

// Toggle task completion
function toggleTask(index) {
    tasks[index].completed = !tasks[index].completed;
    saveTasks();
    renderTasks();
}

// Delete task
function deleteTask(index) {
    tasks.splice(index, 1);
    saveTasks();
    renderTasks();
}

// Clear completed tasks
function clearCompleted() {
    tasks = tasks.filter(task => !task.completed);
    saveTasks();
    renderTasks();
}

// Update task counter
function updateCounter() {
    const counter = document.getElementById('taskCounter');
    const activeCount = tasks.filter(task => !task.completed).length;
    counter.textContent = `${activeCount} task${activeCount !== 1 ? 's' : ''}`;
}

// Event listeners
document.getElementById('addButton').addEventListener('click', addTask);
document.getElementById('taskInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addTask();
});
document.getElementById('clearCompleted').addEventListener('click', clearCompleted);

// Load tasks on startup
loadTasks();'''

        return {
            'index.html': html,
            'style.css': css,
            'app.js': js,
            'README.md': f'# {spec.name}\n\n{spec.description}\n\n## How to Use\n\n1. Open `index.html` in a web browser\n2. Add tasks using the input field\n3. Check off tasks when complete\n4. Delete tasks or clear all completed tasks\n\nYour tasks are saved automatically!'
        }

    def _generate_calculator_app(self, spec: AppSpec) -> Dict[str, str]:
        """Generate a calculator app."""
        color = spec.customizations.get('color', 'blue')

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{spec.name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="calculator">
        <header>
            <h1>{spec.name}</h1>
        </header>

        <div class="display" id="display">0</div>

        <div class="buttons">
            <button class="btn btn-function" onclick="clearDisplay()">C</button>
            <button class="btn btn-function" onclick="backspace()">←</button>
            <button class="btn btn-function" onclick="appendOperator('/')">÷</button>
            <button class="btn btn-operator" onclick="appendOperator('*')">×</button>

            <button class="btn btn-number" onclick="appendNumber('7')">7</button>
            <button class="btn btn-number" onclick="appendNumber('8')">8</button>
            <button class="btn btn-number" onclick="appendNumber('9')">9</button>
            <button class="btn btn-operator" onclick="appendOperator('-')">−</button>

            <button class="btn btn-number" onclick="appendNumber('4')">4</button>
            <button class="btn btn-number" onclick="appendNumber('5')">5</button>
            <button class="btn btn-number" onclick="appendNumber('6')">6</button>
            <button class="btn btn-operator" onclick="appendOperator('+')">+</button>

            <button class="btn btn-number" onclick="appendNumber('1')">1</button>
            <button class="btn btn-number" onclick="appendNumber('2')">2</button>
            <button class="btn btn-number" onclick="appendNumber('3')">3</button>
            <button class="btn btn-equals" onclick="calculate()" style="grid-row: span 2">=</button>

            <button class="btn btn-number" onclick="appendNumber('0')" style="grid-column: span 2">0</button>
            <button class="btn btn-number" onclick="appendNumber('.')">.</button>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>'''

        css = f'''* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #{self._get_color_hex(color)} 0%, #667eea 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}}

.calculator {{
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    padding: 20px;
    width: 100%;
    max-width: 400px;
}}

header {{
    text-align: center;
    margin-bottom: 20px;
}}

header h1 {{
    color: #{self._get_color_hex(color)};
    font-size: 1.8em;
}}

.display {{
    background: #f5f5f5;
    border-radius: 10px;
    padding: 30px 20px;
    text-align: right;
    font-size: 2.5em;
    font-weight: 300;
    margin-bottom: 20px;
    min-height: 80px;
    word-wrap: break-word;
    overflow-wrap: break-word;
}}

.buttons {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}}

.btn {{
    padding: 25px;
    font-size: 1.5em;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
}}

.btn:active {{
    transform: scale(0.95);
}}

.btn-number {{
    background: #f0f0f0;
    color: #333;
}}

.btn-number:hover {{
    background: #e0e0e0;
}}

.btn-operator {{
    background: #{self._get_color_hex(color)};
    color: white;
}}

.btn-operator:hover {{
    opacity: 0.9;
}}

.btn-function {{
    background: #95a5a6;
    color: white;
}}

.btn-function:hover {{
    background: #7f8c8d;
}}

.btn-equals {{
    background: #27ae60;
    color: white;
    font-size: 2em;
}}

.btn-equals:hover {{
    background: #229954;
}}'''

        js = '''// Calculator App Logic
let currentDisplay = '0';
let previousValue = null;
let operator = null;
let shouldResetDisplay = false;

function updateDisplay() {
    document.getElementById('display').textContent = currentDisplay;
}

function clearDisplay() {
    currentDisplay = '0';
    previousValue = null;
    operator = null;
    shouldResetDisplay = false;
    updateDisplay();
}

function backspace() {
    if (currentDisplay.length > 1) {
        currentDisplay = currentDisplay.slice(0, -1);
    } else {
        currentDisplay = '0';
    }
    updateDisplay();
}

function appendNumber(num) {
    if (shouldResetDisplay) {
        currentDisplay = num;
        shouldResetDisplay = false;
    } else {
        if (currentDisplay === '0' && num !== '.') {
            currentDisplay = num;
        } else if (num === '.' && currentDisplay.includes('.')) {
            return;
        } else {
            currentDisplay += num;
        }
    }
    updateDisplay();
}

function appendOperator(op) {
    if (operator !== null && !shouldResetDisplay) {
        calculate();
    }

    previousValue = parseFloat(currentDisplay);
    operator = op;
    shouldResetDisplay = true;
}

function calculate() {
    if (operator === null || previousValue === null) {
        return;
    }

    const current = parseFloat(currentDisplay);
    let result;

    switch (operator) {
        case '+':
            result = previousValue + current;
            break;
        case '-':
            result = previousValue - current;
            break;
        case '*':
            result = previousValue * current;
            break;
        case '/':
            if (current === 0) {
                alert('Cannot divide by zero!');
                clearDisplay();
                return;
            }
            result = previousValue / current;
            break;
        default:
            return;
    }

    currentDisplay = result.toString();
    operator = null;
    previousValue = null;
    shouldResetDisplay = true;
    updateDisplay();
}

// Keyboard support
document.addEventListener('keydown', (e) => {
    if (e.key >= '0' && e.key <= '9' || e.key === '.') {
        appendNumber(e.key);
    } else if (e.key === '+' || e.key === '-' || e.key === '*' || e.key === '/') {
        appendOperator(e.key);
    } else if (e.key === 'Enter' || e.key === '=') {
        calculate();
    } else if (e.key === 'Backspace') {
        backspace();
    } else if (e.key === 'Escape') {
        clearDisplay();
    }
});

updateDisplay();'''

        return {
            'index.html': html,
            'style.css': css,
            'app.js': js,
            'README.md': f'# {spec.name}\n\n{spec.description}\n\n## How to Use\n\n1. Open `index.html` in a web browser\n2. Click buttons or use your keyboard\n3. Perform calculations\n\nKeyboard shortcuts:\n- Numbers and operators work as expected\n- Enter or = to calculate\n- Backspace to delete\n- Escape to clear'
        }

    def _generate_notes_app(self, spec: AppSpec) -> Dict[str, str]:
        """Generate a notes app."""
        color = spec.customizations.get('color', 'blue')

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{spec.name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="app-container">
        <header>
            <h1>{spec.name}</h1>
            <p>{spec.description}</p>
        </header>

        <div class="toolbar">
            <button id="newNoteBtn" class="btn-primary">+ New Note</button>
            <input type="text" id="searchInput" placeholder="Search notes..." />
        </div>

        <div class="main-content">
            <div class="notes-sidebar">
                <div id="notesList"></div>
            </div>

            <div class="editor-area">
                <div class="editor-header">
                    <input type="text" id="noteTitle" placeholder="Note title..." />
                    <button id="deleteNoteBtn" class="btn-delete">Delete</button>
                </div>
                <textarea id="noteContent" placeholder="Start writing..."></textarea>
                <div class="editor-footer">
                    <span id="charCount">0 characters</span>
                    <span id="lastSaved">Not saved</span>
                </div>
            </div>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>'''

        css = f'''* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f5f5;
    height: 100vh;
    overflow: hidden;
}}

.app-container {{
    height: 100vh;
    display: flex;
    flex-direction: column;
}}

header {{
    background: linear-gradient(135deg, #{self._get_color_hex(color)} 0%, #667eea 100%);
    color: white;
    padding: 20px 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}}

header h1 {{
    font-size: 2em;
    margin-bottom: 5px;
}}

header p {{
    opacity: 0.9;
}}

.toolbar {{
    background: white;
    padding: 15px 30px;
    display: flex;
    gap: 15px;
    align-items: center;
    border-bottom: 1px solid #e0e0e0;
}}

.btn-primary {{
    padding: 10px 20px;
    background: #{self._get_color_hex(color)};
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: transform 0.2s;
}}

.btn-primary:hover {{
    transform: translateY(-2px);
}}

#searchInput {{
    flex: 1;
    padding: 10px 15px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1em;
}}

#searchInput:focus {{
    outline: none;
    border-color: #{self._get_color_hex(color)};
}}

.main-content {{
    flex: 1;
    display: flex;
    overflow: hidden;
}}

.notes-sidebar {{
    width: 300px;
    background: white;
    border-right: 1px solid #e0e0e0;
    overflow-y: auto;
}}

.note-item {{
    padding: 15px 20px;
    border-bottom: 1px solid #e0e0e0;
    cursor: pointer;
    transition: background 0.2s;
}}

.note-item:hover {{
    background: #f9f9f9;
}}

.note-item.active {{
    background: #e8f4ff;
    border-left: 3px solid #{self._get_color_hex(color)};
}}

.note-item-title {{
    font-weight: 600;
    margin-bottom: 5px;
}}

.note-item-preview {{
    font-size: 0.9em;
    color: #666;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

.note-item-date {{
    font-size: 0.8em;
    color: #999;
    margin-top: 5px;
}}

.editor-area {{
    flex: 1;
    display: flex;
    flex-direction: column;
    background: white;
}}

.editor-header {{
    padding: 20px 30px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    gap: 15px;
    align-items: center;
}}

#noteTitle {{
    flex: 1;
    font-size: 1.5em;
    font-weight: 600;
    border: none;
    padding: 10px;
}}

#noteTitle:focus {{
    outline: none;
    background: #f9f9f9;
    border-radius: 5px;
}}

.btn-delete {{
    padding: 10px 20px;
    background: #ff4757;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;
}}

.btn-delete:hover {{
    background: #ff3838;
}}

#noteContent {{
    flex: 1;
    padding: 30px;
    border: none;
    font-size: 1.1em;
    line-height: 1.6;
    resize: none;
    font-family: inherit;
}}

#noteContent:focus {{
    outline: none;
}}

.editor-footer {{
    padding: 15px 30px;
    border-top: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    color: #666;
    font-size: 0.9em;
}}

.empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #999;
}}

.empty-state h2 {{
    margin-bottom: 10px;
}}'''

        js = '''// Notes App Logic
let notes = [];
let currentNoteId = null;
let autoSaveTimer = null;

// Load notes from localStorage
function loadNotes() {
    const saved = localStorage.getItem('notes');
    if (saved) {
        notes = JSON.parse(saved);
        renderNotesList();
        if (notes.length > 0) {
            selectNote(notes[0].id);
        }
    }
}

// Save notes to localStorage
function saveNotes() {
    localStorage.setItem('notes', JSON.stringify(notes));
    document.getElementById('lastSaved').textContent = 'Saved ' + new Date().toLocaleTimeString();
}

// Render notes list
function renderNotesList() {
    const notesList = document.getElementById('notesList');
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();

    const filteredNotes = notes.filter(note =>
        note.title.toLowerCase().includes(searchTerm) ||
        note.content.toLowerCase().includes(searchTerm)
    );

    if (filteredNotes.length === 0) {
        notesList.innerHTML = '<div class="empty-state"><p>No notes yet</p></div>';
        return;
    }

    notesList.innerHTML = filteredNotes.map(note => `
        <div class="note-item ${note.id === currentNoteId ? 'active' : ''}"
             onclick="selectNote('${note.id}')">
            <div class="note-item-title">${note.title || 'Untitled'}</div>
            <div class="note-item-preview">${note.content.substring(0, 50)}</div>
            <div class="note-item-date">${new Date(note.updatedAt).toLocaleDateString()}</div>
        </div>
    `).join('');
}

// Create new note
function createNote() {
    const note = {
        id: Date.now().toString(),
        title: '',
        content: '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };

    notes.unshift(note);
    saveNotes();
    renderNotesList();
    selectNote(note.id);
}

// Select a note
function selectNote(noteId) {
    saveCurrentNote();

    currentNoteId = noteId;
    const note = notes.find(n => n.id === noteId);

    if (note) {
        document.getElementById('noteTitle').value = note.title;
        document.getElementById('noteContent').value = note.content;
        updateCharCount();
        renderNotesList();
    }
}

// Save current note
function saveCurrentNote() {
    if (!currentNoteId) return;

    const note = notes.find(n => n.id === currentNoteId);
    if (note) {
        note.title = document.getElementById('noteTitle').value;
        note.content = document.getElementById('noteContent').value;
        note.updatedAt = new Date().toISOString();
    }
}

// Auto-save with debounce
function scheduleAutoSave() {
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
        saveCurrentNote();
        saveNotes();
        renderNotesList();
    }, 1000);
}

// Delete current note
function deleteCurrentNote() {
    if (!currentNoteId) return;

    if (confirm('Delete this note?')) {
        notes = notes.filter(n => n.id !== currentNoteId);
        currentNoteId = null;
        document.getElementById('noteTitle').value = '';
        document.getElementById('noteContent').value = '';
        saveNotes();
        renderNotesList();

        if (notes.length > 0) {
            selectNote(notes[0].id);
        }
    }
}

// Update character count
function updateCharCount() {
    const content = document.getElementById('noteContent').value;
    document.getElementById('charCount').textContent = `${content.length} characters`;
}

// Event listeners
document.getElementById('newNoteBtn').addEventListener('click', createNote);
document.getElementById('deleteNoteBtn').addEventListener('click', deleteCurrentNote);
document.getElementById('noteTitle').addEventListener('input', scheduleAutoSave);
document.getElementById('noteContent').addEventListener('input', () => {
    updateCharCount();
    scheduleAutoSave();
});
document.getElementById('searchInput').addEventListener('input', renderNotesList);

// Load notes on startup
loadNotes();'''

        return {
            'index.html': html,
            'style.css': css,
            'app.js': js,
            'README.md': f'# {spec.name}\n\n{spec.description}\n\n## How to Use\n\n1. Open `index.html` in a web browser\n2. Click "New Note" to create a note\n3. Type your content - it saves automatically\n4. Search notes using the search bar\n5. Click on notes in the sidebar to switch between them\n\nYour notes are saved automatically and persist between sessions!'
        }

    def _generate_simple_game(self, spec: AppSpec) -> Dict[str, str]:
        """Generate a simple game (collect stars, avoid obstacles)."""
        color = spec.customizations.get('color', 'blue')

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{spec.name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="game-container">
        <header>
            <h1>{spec.name}</h1>
            <div class="score-display">
                <span>Score: <span id="score">0</span></span>
                <span>High Score: <span id="highScore">0</span></span>
            </div>
        </header>

        <canvas id="gameCanvas" width="800" height="600"></canvas>

        <div id="gameOver" class="game-over hidden">
            <h2>Game Over!</h2>
            <p>Final Score: <span id="finalScore">0</span></p>
            <button id="restartBtn" class="btn-primary">Play Again</button>
        </div>

        <div class="instructions">
            <p>Use arrow keys or WASD to move</p>
            <p>Collect ⭐ stars! Avoid 🔴 obstacles!</p>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>'''

        css = f'''* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #{self._get_color_hex(color)} 0%, #667eea 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}}

.game-container {{
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    padding: 20px;
    max-width: 840px;
}}

header {{
    text-align: center;
    margin-bottom: 20px;
}}

header h1 {{
    color: #{self._get_color_hex(color)};
    font-size: 2.5em;
    margin-bottom: 10px;
}}

.score-display {{
    display: flex;
    justify-content: center;
    gap: 30px;
    font-size: 1.2em;
    font-weight: 600;
    color: #333;
}}

#gameCanvas {{
    border: 3px solid #{self._get_color_hex(color)};
    border-radius: 10px;
    display: block;
    margin: 0 auto;
    background: #f0f8ff;
}}

.instructions {{
    text-align: center;
    margin-top: 15px;
    color: #666;
}}

.instructions p {{
    margin: 5px 0;
}}

.game-over {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 40px 60px;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
    text-align: center;
    z-index: 1000;
}}

.game-over.hidden {{
    display: none;
}}

.game-over h2 {{
    color: #{self._get_color_hex(color)};
    font-size: 2.5em;
    margin-bottom: 20px;
}}

.game-over p {{
    font-size: 1.5em;
    margin-bottom: 30px;
    color: #333;
}}

.btn-primary {{
    padding: 15px 40px;
    background: #{self._get_color_hex(color)};
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1.2em;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s;
}}

.btn-primary:hover {{
    transform: scale(1.05);
}}'''

        js = '''// Simple Game Logic
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game state
let gameRunning = true;
let score = 0;
let highScore = parseInt(localStorage.getItem('highScore')) || 0;

// Player
const player = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    size: 30,
    speed: 5,
    color: '#4CAF50'
};

// Stars (collectibles)
let stars = [];

// Obstacles
let obstacles = [];

// Input handling
const keys = {};
document.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
});
document.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
});

// Create star
function createStar() {
    return {
        x: Math.random() * (canvas.width - 30) + 15,
        y: Math.random() * (canvas.height - 30) + 15,
        size: 20,
        collected: false
    };
}

// Create obstacle
function createObstacle() {
    return {
        x: Math.random() * (canvas.width - 30) + 15,
        y: Math.random() * (canvas.height - 30) + 15,
        size: 25,
        speedX: (Math.random() - 0.5) * 3,
        speedY: (Math.random() - 0.5) * 3
    };
}

// Initialize game objects
function initGame() {
    stars = [];
    obstacles = [];

    for (let i = 0; i < 5; i++) {
        stars.push(createStar());
    }

    for (let i = 0; i < 3; i++) {
        obstacles.push(createObstacle());
    }
}

// Update player position
function updatePlayer() {
    if (keys['arrowup'] || keys['w']) {
        player.y = Math.max(player.size / 2, player.y - player.speed);
    }
    if (keys['arrowdown'] || keys['s']) {
        player.y = Math.min(canvas.height - player.size / 2, player.y + player.speed);
    }
    if (keys['arrowleft'] || keys['a']) {
        player.x = Math.max(player.size / 2, player.x - player.speed);
    }
    if (keys['arrowright'] || keys['d']) {
        player.x = Math.min(canvas.width - player.size / 2, player.x + player.speed);
    }
}

// Update obstacles
function updateObstacles() {
    obstacles.forEach(obstacle => {
        obstacle.x += obstacle.speedX;
        obstacle.y += obstacle.speedY;

        // Bounce off walls
        if (obstacle.x <= 0 || obstacle.x >= canvas.width) {
            obstacle.speedX *= -1;
        }
        if (obstacle.y <= 0 || obstacle.y >= canvas.height) {
            obstacle.speedY *= -1;
        }
    });
}

// Check collisions
function checkCollisions() {
    // Check star collisions
    stars.forEach(star => {
        if (!star.collected) {
            const dx = player.x - star.x;
            const dy = player.y - star.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < (player.size / 2 + star.size / 2)) {
                star.collected = true;
                score += 10;
                document.getElementById('score').textContent = score;
                stars.push(createStar());
            }
        }
    });

    // Check obstacle collisions
    obstacles.forEach(obstacle => {
        const dx = player.x - obstacle.x;
        const dy = player.y - obstacle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < (player.size / 2 + obstacle.size / 2)) {
            endGame();
        }
    });
}

// Draw everything
function draw() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw player
    ctx.fillStyle = player.color;
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.size / 2, 0, Math.PI * 2);
    ctx.fill();

    // Draw stars
    stars.forEach(star => {
        if (!star.collected) {
            ctx.font = `${star.size}px Arial`;
            ctx.fillText('⭐', star.x - star.size / 2, star.y + star.size / 2);
        }
    });

    // Draw obstacles
    obstacles.forEach(obstacle => {
        ctx.font = `${obstacle.size}px Arial`;
        ctx.fillText('🔴', obstacle.x - obstacle.size / 2, obstacle.y + obstacle.size / 2);
    });
}

// Game loop
function gameLoop() {
    if (!gameRunning) return;

    updatePlayer();
    updateObstacles();
    checkCollisions();
    draw();

    requestAnimationFrame(gameLoop);
}

// End game
function endGame() {
    gameRunning = false;

    if (score > highScore) {
        highScore = score;
        localStorage.setItem('highScore', highScore);
        document.getElementById('highScore').textContent = highScore;
    }

    document.getElementById('finalScore').textContent = score;
    document.getElementById('gameOver').classList.remove('hidden');
}

// Restart game
function restartGame() {
    gameRunning = true;
    score = 0;
    document.getElementById('score').textContent = score;
    player.x = canvas.width / 2;
    player.y = canvas.height / 2;

    initGame();
    document.getElementById('gameOver').classList.add('hidden');
    gameLoop();
}

document.getElementById('restartBtn').addEventListener('click', restartGame);
document.getElementById('highScore').textContent = highScore;

// Start game
initGame();
gameLoop();'''

        return {
            'index.html': html,
            'style.css': css,
            'app.js': js,
            'README.md': f'# {spec.name}\n\n{spec.description}\n\n## How to Play\n\n1. Open `index.html` in a web browser\n2. Use arrow keys or WASD to move your character (green circle)\n3. Collect stars (⭐) to earn points\n4. Avoid red obstacles (🔴)\n5. Try to beat your high score!\n\nGood luck!'
        }

    def _get_color_hex(self, color_name: str) -> str:
        """Convert color name to hex code."""
        color_map = {
            'red': 'e74c3c',
            'blue': '3498db',
            'green': '2ecc71',
            'yellow': 'f1c40f',
            'purple': '9b59b6',
            'pink': 'ff69b4',
            'orange': 'e67e22',
            'teal': '1abc9c',
            'cyan': '00bcd4',
            'lime': 'cddc39',
            'navy': '2c3e50',
        }
        return color_map.get(color_name.lower(), '3498db')
