// Notes App Logic
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
loadNotes();