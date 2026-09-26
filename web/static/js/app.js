/**
 * Unlimited AI Voice Generator - Web UI Controller
 * Developed by badarbukhari.me
 * High-performance, Apple-grade interface with custom Cupertino dropdowns
 */

const API_BASE = (window.location.protocol === 'http:' || window.location.protocol === 'https:') 
    ? '' 
    : 'http://127.0.0.1:7860';

// Premium SVG Icons (Crisp Feather/Lucide vector stroke format - Zero Emojis)
const ICONS = {
    play: `<svg class="icon sm" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="5 3 19 12 5 21 5 3"/></svg>`,
    pause: `<svg class="icon sm" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`,
    download: `<svg class="icon sm" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>`,
    trash: `<svg class="icon sm" viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>`,
    mic: `<svg class="icon sm" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>`,
    clock: `<svg class="icon sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
    check: `<svg class="icon sm" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>`,
    sun: `<svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`,
    moon: `<svg class="icon" viewBox="0 0 24 24"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>`
};

// Application State
const state = {
    voices: [],
    languages: [],
    countries: [],
    filteredVoices: [],
    selectedVoice: null,
    favorites: JSON.parse(localStorage.getItem('speechma_favs') || '["voice-107", "voice-110", "voice-1", "voice-5"]'),
    previewAudio: new Audio(),
    activeAudioPlayer: new Audio(),
    activePlayingFilename: null,
    previewingVoiceId: null,
    isGenerating: false,
    selectedGender: 'all',
    selectedLanguage: 'all', // Default: All Languages
    selectedCountry: 'all',  // Default: All Countries
    searchQuery: '',
    history: []
};

// Helper: Format Time (mm:ss)
function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

// DOM Elements Cache
const el = {};

function initElements() {
    el.ttsText = document.getElementById('ttsText');
    el.charCount = document.getElementById('charCount');
    el.wordCount = document.getElementById('wordCount');
    el.readTime = document.getElementById('readTime');
    el.batchBadge = document.getElementById('batchBadge');
    el.fileInput = document.getElementById('fileInput');
    el.uploadBtn = document.getElementById('uploadBtn');
    el.cleanBtn = document.getElementById('cleanBtn');
    el.pasteBtn = document.getElementById('pasteBtn');
    el.clearBtn = document.getElementById('clearBtn');
    el.generateBtn = document.getElementById('generateBtn');
    el.generateText = document.getElementById('generateText');
    el.effectsToggleBtn = document.getElementById('effectsToggleBtn');
    el.effectsDrawer = document.getElementById('effectsDrawer');
    el.pitchSlider = document.getElementById('pitchSlider');
    el.pitchVal = document.getElementById('pitchVal');
    el.rateSlider = document.getElementById('rateSlider');
    el.rateVal = document.getElementById('rateVal');
    el.resetPitch = document.getElementById('resetPitch');
    el.resetRate = document.getElementById('resetRate');
    el.customFilename = document.getElementById('customFilename');
    el.progressBox = document.getElementById('progressBox');
    el.progressMessage = document.getElementById('progressMessage');
    
    // Voice Section
    el.selectedVoicePill = document.getElementById('selectedVoicePill');
    el.voiceCountBadge = document.getElementById('voiceCountBadge');
    el.voiceSearchInput = document.getElementById('voiceSearchInput');
    el.genderBtns = document.querySelectorAll('.segmented-pill-btn');
    el.voiceGrid = document.getElementById('voiceGrid');

    // Apple Custom Dropdowns
    el.langDropdown = document.getElementById('langDropdown');
    el.langDropdownTrigger = document.getElementById('langDropdownTrigger');
    el.langDropdownSelected = document.getElementById('langDropdownSelected');
    el.langDropdownMenu = document.getElementById('langDropdownMenu');
    el.langSearchInput = document.getElementById('langSearchInput');
    el.langDropdownList = document.getElementById('langDropdownList');

    el.countryDropdown = document.getElementById('countryDropdown');
    el.countryDropdownTrigger = document.getElementById('countryDropdownTrigger');
    el.countryDropdownSelected = document.getElementById('countryDropdownSelected');
    el.countryDropdownMenu = document.getElementById('countryDropdownMenu');
    el.countrySearchInput = document.getElementById('countrySearchInput');
    el.countryDropdownList = document.getElementById('countryDropdownList');

    // History Section
    el.historyCountBadge = document.getElementById('historyCountBadge');
    el.generatedAudioList = document.getElementById('generatedAudioList');
    el.themeToggleBtn = document.getElementById('themeToggleBtn');
    el.themeIcon = document.getElementById('themeIcon');
}

// App Initialization
async function init() {
    initElements();
    setupTheme();
    setupDropdowns();
    setupEventListeners();
    updateTextMetrics();

    // Fetch initial datasets
    fetchStatus();
    await fetchLanguages();
    await fetchVoices();
    fetchHistory();
}

// Light Mode by default, persistent with localStorage
function setupTheme() {
    const saved = localStorage.getItem('speechma_theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    if (el.themeToggleBtn) {
        el.themeToggleBtn.innerHTML = saved === 'dark' ? ICONS.moon : ICONS.sun;
    }
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('speechma_theme', next);
    if (el.themeToggleBtn) {
        el.themeToggleBtn.innerHTML = next === 'dark' ? ICONS.moon : ICONS.sun;
    }
}

// System Status Check
async function fetchStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/status`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const badge = document.getElementById('tessBadge');
        if (badge) {
            badge.className = "pill-badge active-badge";
            badge.innerHTML = `<svg class="icon sm" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg><span>0.4ms Native OCR</span>`;
        }
    } catch (err) {
        console.warn("Status error:", err);
    }
}

// Fetch Languages & Countries and populate Apple Dropdowns
async function fetchLanguages() {
    try {
        const res = await fetch(`${API_BASE}/api/languages`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        
        state.languages = data.languages || [];
        state.countries = data.countries || [];

        renderLanguageDropdown();
        renderCountryDropdown();
    } catch (err) {
        console.warn("Languages fetch error:", err);
    }
}

// Populate Custom Apple Dropdown: Languages
function renderLanguageDropdown(filterTerm = '') {
    if (!el.langDropdownList) return;
    const term = filterTerm.toLowerCase().trim();

    let itemsHtml = `
        <div class="dropdown-item ${state.selectedLanguage === 'all' ? 'active' : ''}" data-value="all">
            <span>All Languages</span>
            ${state.selectedLanguage === 'all' ? ICONS.check : ''}
        </div>
    `;

    const filtered = state.languages.filter(l => !term || l.language.toLowerCase().includes(term));
    
    filtered.forEach(l => {
        const isSelected = state.selectedLanguage.toLowerCase() === l.language.toLowerCase();
        itemsHtml += `
            <div class="dropdown-item ${isSelected ? 'active' : ''}" data-value="${l.language}">
                <span>${l.language} (${l.count})</span>
                ${isSelected ? ICONS.check : ''}
            </div>
        `;
    });

    el.langDropdownList.innerHTML = itemsHtml;

    // Attach click events
    el.langDropdownList.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const val = item.dataset.value;
            state.selectedLanguage = val;
            el.langDropdownSelected.textContent = val === 'all' ? 'All Languages' : val;
            closeAllDropdowns();
            renderLanguageDropdown();
            filterAndRenderVoices();
        });
    });
}

// Populate Custom Apple Dropdown: Countries
function renderCountryDropdown(filterTerm = '') {
    if (!el.countryDropdownList) return;
    const term = filterTerm.toLowerCase().trim();

    let itemsHtml = `
        <div class="dropdown-item ${state.selectedCountry === 'all' ? 'active' : ''}" data-value="all">
            <span>All Countries</span>
            ${state.selectedCountry === 'all' ? ICONS.check : ''}
        </div>
    `;

    const filtered = state.countries.filter(c => !term || c.toLowerCase().includes(term));

    filtered.forEach(c => {
        const isSelected = state.selectedCountry.toLowerCase() === c.toLowerCase();
        itemsHtml += `
            <div class="dropdown-item ${isSelected ? 'active' : ''}" data-value="${c}">
                <span>${c}</span>
                ${isSelected ? ICONS.check : ''}
            </div>
        `;
    });

    el.countryDropdownList.innerHTML = itemsHtml;

    // Attach click events
    el.countryDropdownList.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const val = item.dataset.value;
            state.selectedCountry = val;
            el.countryDropdownSelected.textContent = val === 'all' ? 'All Countries' : val;
            closeAllDropdowns();
            renderCountryDropdown();
            filterAndRenderVoices();
        });
    });
}

// Dropdown interactions (Apple Cupertino behavior)
function closeAllDropdowns() {
    if (el.langDropdown) el.langDropdown.classList.remove('open');
    if (el.countryDropdown) el.countryDropdown.classList.remove('open');
}

function setupDropdowns() {
    // Language Dropdown toggle
    if (el.langDropdownTrigger) {
        el.langDropdownTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = el.langDropdown.classList.contains('open');
            closeAllDropdowns();
            if (!isOpen) {
                el.langDropdown.classList.add('open');
                if (el.langSearchInput) {
                    el.langSearchInput.value = '';
                    renderLanguageDropdown();
                    setTimeout(() => el.langSearchInput.focus(), 50);
                }
            }
        });
    }

    // Country Dropdown toggle
    if (el.countryDropdownTrigger) {
        el.countryDropdownTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = el.countryDropdown.classList.contains('open');
            closeAllDropdowns();
            if (!isOpen) {
                el.countryDropdown.classList.add('open');
                if (el.countrySearchInput) {
                    el.countrySearchInput.value = '';
                    renderCountryDropdown();
                    setTimeout(() => el.countrySearchInput.focus(), 50);
                }
            }
        });
    }

    // Search filter inside Language Dropdown
    if (el.langSearchInput) {
        el.langSearchInput.addEventListener('input', (e) => {
            renderLanguageDropdown(e.target.value);
        });
        el.langSearchInput.addEventListener('click', (e) => e.stopPropagation());
    }

    // Search filter inside Country Dropdown
    if (el.countrySearchInput) {
        el.countrySearchInput.addEventListener('input', (e) => {
            renderCountryDropdown(e.target.value);
        });
        el.countrySearchInput.addEventListener('click', (e) => e.stopPropagation());
    }

    // Close on click outside or Esc key
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.apple-dropdown')) {
            closeAllDropdowns();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAllDropdowns();
        }
    });
}

// Fetch Voices Catalog
async function fetchVoices() {
    try {
        const res = await fetch(`${API_BASE}/api/voices`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        state.voices = data.voices || [];

        // Select default voice (Andrew Multilingual or first)
        const defaultVoice = state.voices.find(v => v.id === 'voice-107') || state.voices[0];
        selectVoice(defaultVoice);

        filterAndRenderVoices();
    } catch (err) {
        console.error("Voices fetch error:", err);
        if (el.voiceGrid) {
            el.voiceGrid.innerHTML = `<div style="text-align:center; padding:3rem; color:var(--text-muted); grid-column:1/-1;">Failed to load voices. Ensure server is running.</div>`;
        }
    }
}

// Select Voice
function selectVoice(voice) {
    if (!voice) return;
    state.selectedVoice = voice;
    if (el.selectedVoicePill) {
        el.selectedVoicePill.textContent = voice.name;
    }
    document.querySelectorAll('.voice-card').forEach(card => {
        if (card.dataset.id === voice.id) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
}

// Filter and Render Voice Cards (4-Column Apple Grid Layout)
function filterAndRenderVoices() {
    const q = state.searchQuery.toLowerCase().trim();
    const l = state.selectedLanguage;
    const c = state.selectedCountry;
    const g = state.selectedGender;

    state.filteredVoices = state.voices.filter(v => {
        if (g === 'fav' && !state.favorites.includes(v.id)) return false;
        if (g !== 'all' && g !== 'fav' && v.gender.toLowerCase() !== g.toLowerCase()) return false;
        if (l !== 'all' && v.language.toLowerCase() !== l.toLowerCase()) return false;
        if (c !== 'all' && (v.country || '').toLowerCase() !== c.toLowerCase()) return false;

        if (q) {
            const nameMatch = v.name.toLowerCase().includes(q);
            const idMatch = v.id.toLowerCase().includes(q);
            const langMatch = v.language.toLowerCase().includes(q);
            const countryMatch = (v.country || '').toLowerCase().includes(q);
            if (!nameMatch && !idMatch && !langMatch && !countryMatch) return false;
        }
        return true;
    });

    if (el.voiceCountBadge) {
        el.voiceCountBadge.textContent = `${state.filteredVoices.length} voices`;
    }

    if (!el.voiceGrid) return;
    el.voiceGrid.innerHTML = '';

    const subset = state.filteredVoices.slice(0, 120);

    if (subset.length === 0) {
        el.voiceGrid.innerHTML = `<div style="text-align:center; padding:3rem; color:var(--text-muted); grid-column:1/-1;">No voices match your filters.</div>`;
        return;
    }

    subset.forEach(v => {
        const isSelected = state.selectedVoice && state.selectedVoice.id === v.id;
        const isPlaying = state.previewingVoiceId === v.id;

        const card = document.createElement('div');
        card.className = 'voice-card' + (isSelected ? ' selected' : '');
        card.dataset.id = v.id;

        card.innerHTML = `
            <div class="voice-card-header">
                <div class="voice-card-name" title="${v.name}">${v.name}</div>
                <button class="circular-preview-btn ${isPlaying ? 'playing' : ''}" data-id="${v.id}" title="Preview Voice">
                    ${isPlaying ? ICONS.pause : ICONS.play}
                </button>
            </div>
            <div class="card-tags-row">
                <span class="apple-tag">${v.gender}</span>
                <span class="apple-tag">${v.language}</span>
            </div>
            <div class="voice-card-footer">
                <span title="${v.country || 'Global'}">${v.country || 'Global'}</span>
            </div>
        `;

        // Card click selects voice
        card.addEventListener('click', (e) => {
            if (e.target.closest('.circular-preview-btn')) return;
            selectVoice(v);
        });

        // Circle button previews audio
        const playBtn = card.querySelector('.circular-preview-btn');
        playBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            playVoicePreview(v, playBtn);
        });

        el.voiceGrid.appendChild(card);
    });
}

// Voice Preview Player
function playVoicePreview(voice, btnElement) {
    if (state.previewingVoiceId === voice.id && !state.previewAudio.paused) {
        state.previewAudio.pause();
        state.previewingVoiceId = null;
        if (btnElement) {
            btnElement.classList.remove('playing');
            btnElement.innerHTML = ICONS.play;
        }
        return;
    }

    state.previewAudio.src = voice.preview_url || `https://speechma.com/assets/audio/previews/${voice.id}.mp3`;
    state.previewingVoiceId = voice.id;

    document.querySelectorAll('.circular-preview-btn').forEach(btn => {
        btn.classList.remove('playing');
        btn.innerHTML = ICONS.play;
    });

    if (btnElement) {
        btnElement.classList.add('playing');
        btnElement.innerHTML = ICONS.pause;
    }

    state.previewAudio.play().catch(err => {
        console.warn("Preview error:", err);
        if (btnElement) {
            btnElement.classList.remove('playing');
            btnElement.innerHTML = ICONS.play;
        }
    });

    state.previewAudio.onended = () => {
        state.previewingVoiceId = null;
        if (btnElement) {
            btnElement.classList.remove('playing');
            btnElement.innerHTML = ICONS.play;
        }
    };
}

// Textarea Metrics - NEVER show 2000 character limit, show Unlimited
function updateTextMetrics() {
    if (!el.ttsText) return;
    const text = el.ttsText.value;
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;

    // Auto RTL for Urdu/Arabic/Persian
    const isRTL = /[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/.test(text.slice(0, 100));
    el.ttsText.setAttribute('dir', isRTL ? 'rtl' : 'ltr');

    // Reading time calculation (~140 words per minute)
    const readSecs = Math.round((words / 140) * 60);
    const readMins = Math.floor(readSecs / 60);
    const remSecs = readSecs % 60;
    const timeText = readMins > 0 ? `~${readMins}m ${remSecs}s read` : `~${remSecs}s read`;

    if (el.charCount) {
        el.charCount.textContent = `${chars.toLocaleString()} characters • Unlimited`;
    }
    if (el.wordCount) {
        el.wordCount.textContent = `${words.toLocaleString()} words`;
    }
    if (el.readTime) {
        el.readTime.textContent = timeText;
    }

    // Parallel turbo batch indicator for long text
    if (el.batchBadge) {
        if (chars > 1800) {
            const chunks = Math.ceil(chars / 1800);
            el.batchBadge.style.display = 'inline-flex';
            el.batchBadge.textContent = `⚡ Fast Parallel Mode (~${chunks} Chunks)`;
        } else {
            el.batchBadge.style.display = 'none';
        }
    }
}

// Clean and Format Text
function cleanTextContent() {
    if (!el.ttsText) return;
    let t = el.ttsText.value;
    if (!t.trim()) return;

    t = t.replace(/^#{1,6}\s+/gm, '')
         .replace(/^\s*[-*+]\s+/gm, '')
         .replace(/\*\*(.*?)\*\*/g, '$1')
         .replace(/\*(.*?)\*/g, '$1')
         .replace(/[ \t]+/g, ' ')
         .replace(/\n{3,}/g, '\n\n')
         .trim();

    el.ttsText.value = t;
    updateTextMetrics();
}

// Fetch Generation History
async function fetchHistory() {
    try {
        const res = await fetch(`${API_BASE}/api/history`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        state.history = data.history || [];
        renderHistory();
    } catch (err) {
        console.warn("History fetch failed:", err);
    }
}

// Render Generated Audio Library
function renderHistory() {
    if (el.historyCountBadge) {
        el.historyCountBadge.textContent = `${state.history.length} audios`;
    }
    if (!el.generatedAudioList) return;

    el.generatedAudioList.innerHTML = '';

    if (state.history.length === 0) {
        el.generatedAudioList.innerHTML = `<div style="text-align:center; padding:3rem; color:var(--text-muted);">No generated audios yet. Type text and click Generate Audio!</div>`;
        return;
    }

    state.history.forEach(item => {
        const card = document.createElement('div');
        card.className = 'generated-audio-item';
        const audioUrl = `${API_BASE}${item.url}`;
        const downloadUrl = `${API_BASE}${item.download_url}`;
        const cleanId = item.filename.replace(/[^a-zA-Z0-9]/g, '_');
        const isCurrentPlaying = state.activePlayingFilename === item.filename && !state.activeAudioPlayer.paused;

        card.innerHTML = `
            <div class="item-filename-title">${item.filename}</div>
            <div class="item-meta-bar">
                <span>${ICONS.mic} Voice</span>
                <span>${ICONS.clock} ${item.created_at}</span>
                <span class="apple-tag">${item.size_formatted}</span>
            </div>
            <div class="audio-waveform-scrubber">
                <div class="waveform-bg-track" data-file="${item.filename}">
                    <div class="waveform-fill-progress" id="fill_${cleanId}"></div>
                </div>
                <div class="waveform-timer-labels">
                    <span id="cur_${cleanId}">0:00</span>
                    <span id="dur_${cleanId}">--:--</span>
                </div>
            </div>
            <div class="item-actions-grid">
                <button class="action-card-btn play-btn play-card-btn" data-file="${item.filename}">
                    ${isCurrentPlaying ? ICONS.pause : ICONS.play}
                    <span>${isCurrentPlaying ? 'Pause' : 'Play'}</span>
                </button>
                <a href="${downloadUrl}" class="action-card-btn" download title="Download MP3">
                    ${ICONS.download}
                    <span>Download</span>
                </a>
                <button class="action-card-btn delete-btn delete-card-btn" data-file="${item.filename}" title="Delete Audio">
                    ${ICONS.trash}
                    <span>Delete</span>
                </button>
            </div>
        `;

        // Play/Pause button
        const playBtn = card.querySelector('.play-card-btn');
        playBtn.addEventListener('click', () => {
            togglePlayAudio(item, card, playBtn);
        });

        // Waveform click scrubber
        const track = card.querySelector('.waveform-bg-track');
        track.addEventListener('click', (e) => {
            const rect = track.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const fraction = Math.max(0, Math.min(1, clickX / rect.width));

            if (state.activePlayingFilename !== item.filename) {
                togglePlayAudio(item, card, playBtn);
            }
            if (!isNaN(state.activeAudioPlayer.duration)) {
                state.activeAudioPlayer.currentTime = fraction * state.activeAudioPlayer.duration;
            }
        });

        // Delete button
        card.querySelector('.delete-card-btn').addEventListener('click', async () => {
            if (confirm(`Delete ${item.filename}?`)) {
                await deleteAudioItem(item.filename);
            }
        });

        el.generatedAudioList.appendChild(card);
    });
}

// Play Audio Item
function togglePlayAudio(item, card, btn) {
    const audioUrl = `${API_BASE}${item.url}`;
    const cleanId = item.filename.replace(/[^a-zA-Z0-9]/g, '_');
    const fillEl = document.getElementById(`fill_${cleanId}`);
    const curEl = document.getElementById(`cur_${cleanId}`);
    const durEl = document.getElementById(`dur_${cleanId}`);

    if (state.activePlayingFilename === item.filename && !state.activeAudioPlayer.paused) {
        state.activeAudioPlayer.pause();
        btn.innerHTML = `${ICONS.play} <span>Play</span>`;
        return;
    }

    state.activeAudioPlayer.src = audioUrl;
    state.activePlayingFilename = item.filename;

    document.querySelectorAll('.play-card-btn').forEach(b => {
        b.innerHTML = `${ICONS.play} <span>Play</span>`;
    });

    btn.innerHTML = `${ICONS.pause} <span>Pause</span>`;

    state.activeAudioPlayer.play().catch(console.warn);

    state.activeAudioPlayer.ontimeupdate = () => {
        if (!isNaN(state.activeAudioPlayer.duration)) {
            const pct = (state.activeAudioPlayer.currentTime / state.activeAudioPlayer.duration) * 100;
            if (fillEl) fillEl.style.width = `${pct}%`;
            if (curEl) curEl.textContent = formatTime(state.activeAudioPlayer.currentTime);
            if (durEl) durEl.textContent = formatTime(state.activeAudioPlayer.duration);
        }
    };

    state.activeAudioPlayer.onended = () => {
        state.activePlayingFilename = null;
        btn.innerHTML = `${ICONS.play} <span>Play</span>`;
        if (fillEl) fillEl.style.width = '0%';
    };
}

// Delete Audio
async function deleteAudioItem(filename) {
    try {
        await fetch(`${API_BASE}/api/audio/${encodeURIComponent(filename)}`, { method: 'DELETE' });
        await fetchHistory();
    } catch (err) {
        alert("Failed to delete audio: " + err);
    }
}

// Generate Speech
async function generateSpeech() {
    if (!el.ttsText) return;
    const text = el.ttsText.value.trim();
    if (!text) {
        alert("Please enter text in the input box to generate audio.");
        el.ttsText.focus();
        return;
    }

    state.isGenerating = true;
    if (el.generateBtn) el.generateBtn.disabled = true;
    if (el.generateText) el.generateText.textContent = "Synthesizing...";
    if (el.progressBox) el.progressBox.classList.add('active');
    
    if (el.progressMessage) {
        if (text.length > 1800) {
            el.progressMessage.textContent = "Synthesizing chunks concurrently in fast parallel mode...";
        } else {
            el.progressMessage.textContent = "Solving captcha in 0.4ms & generating high-fidelity speech...";
        }
    }

    const payload = {
        text: text,
        voice: state.selectedVoice ? state.selectedVoice.id : 'voice-107',
        pitch: el.pitchSlider ? parseInt(el.pitchSlider.value, 10) : 0,
        rate: el.rateSlider ? parseInt(el.rateSlider.value, 10) : 0,
        filename: el.customFilename && el.customFilename.value.trim() ? el.customFilename.value.trim() : null
    };

    try {
        const res = await fetch(`${API_BASE}/api/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || "TTS generation failed");
        }

        if (el.progressMessage) {
            el.progressMessage.textContent = `Completed! ${data.size_formatted} audio synthesized successfully.`;
        }

        await fetchHistory();

        // Auto-play newly generated audio
        const firstItem = state.history[0];
        if (firstItem) {
            const firstCard = el.generatedAudioList.querySelector('.generated-audio-item');
            if (firstCard) {
                const playBtn = firstCard.querySelector('.play-card-btn');
                togglePlayAudio(firstItem, firstCard, playBtn);
            }
        }

        setTimeout(() => {
            if (el.progressBox) el.progressBox.classList.remove('active');
        }, 2800);

    } catch (err) {
        console.error("TTS error:", err);
        if (el.progressMessage) el.progressMessage.textContent = `Error: ${err.message}`;
        alert("Synthesis Error: " + err.message);
    } finally {
        state.isGenerating = false;
        if (el.generateBtn) el.generateBtn.disabled = false;
        if (el.generateText) el.generateText.textContent = "Generate Audio";
    }
}

// Event Listeners Setup
function setupEventListeners() {
    // Textarea input
    if (el.ttsText) {
        el.ttsText.addEventListener('input', updateTextMetrics);
        el.ttsText.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                generateSpeech();
            }
        });
    }

    // Top action toolbar buttons
    if (el.uploadBtn && el.fileInput) {
        el.uploadBtn.addEventListener('click', () => el.fileInput.click());
        el.fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (evt) => {
                    el.ttsText.value = evt.target.result;
                    updateTextMetrics();
                };
                reader.readAsText(file);
            }
        });
    }

    if (el.cleanBtn) {
        el.cleanBtn.addEventListener('click', cleanTextContent);
    }

    if (el.pasteBtn) {
        el.pasteBtn.addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                el.ttsText.value = text;
                updateTextMetrics();
            } catch (err) {
                alert("Clipboard permission required. Please press Ctrl+V to paste.");
            }
        });
    }

    if (el.clearBtn) {
        el.clearBtn.addEventListener('click', () => {
            el.ttsText.value = '';
            updateTextMetrics();
            el.ttsText.focus();
        });
    }

    // Toggle Voice Effects Drawer
    if (el.effectsToggleBtn && el.effectsDrawer) {
        el.effectsToggleBtn.addEventListener('click', () => {
            el.effectsDrawer.classList.toggle('active');
            el.effectsToggleBtn.classList.toggle('active');
        });
    }

    // Sliders
    if (el.pitchSlider && el.pitchVal) {
        el.pitchSlider.addEventListener('input', () => {
            const val = el.pitchSlider.value;
            el.pitchVal.textContent = (val > 0 ? '+' : '') + val;
        });
    }

    if (el.rateSlider && el.rateVal) {
        el.rateSlider.addEventListener('input', () => {
            const val = el.rateSlider.value;
            el.rateVal.textContent = (val > 0 ? '+' : '') + val;
        });
    }

    if (el.resetPitch && el.pitchSlider && el.pitchVal) {
        el.resetPitch.addEventListener('click', () => {
            el.pitchSlider.value = 0;
            el.pitchVal.textContent = '0';
        });
    }

    if (el.resetRate && el.rateSlider && el.rateVal) {
        el.resetRate.addEventListener('click', () => {
            el.rateSlider.value = 0;
            el.rateVal.textContent = '0';
        });
    }

    // Voice search bar
    if (el.voiceSearchInput) {
        el.voiceSearchInput.addEventListener('input', (e) => {
            state.searchQuery = e.target.value;
            filterAndRenderVoices();
        });
    }

    // Gender filter buttons
    if (el.genderBtns) {
        el.genderBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                el.genderBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                state.selectedGender = btn.dataset.gender;
                filterAndRenderVoices();
            });
        });
    }

    // Generate Audio action
    if (el.generateBtn) {
        el.generateBtn.addEventListener('click', generateSpeech);
    }

    // Theme Toggle
    if (el.themeToggleBtn) {
        el.themeToggleBtn.addEventListener('click', toggleTheme);
    }
}

// Safely execute init
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
