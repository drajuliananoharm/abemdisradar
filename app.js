let opportunities = [];
let discardedOpps = JSON.parse(localStorage.getItem('abemdis_discarded') || '[]');
let currentFilter = 'all';

// Checa ser o usuário é administrador (via URL: ?admin=true ou localStorage)
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('admin') === 'true') {
    localStorage.setItem('abemdis_admin', 'true');
} else if (urlParams.get('admin') === 'false') {
    localStorage.removeItem('abemdis_admin');
}
const isAdmin = localStorage.getItem('abemdis_admin') === 'true';

// DOM Elements
const container = document.getElementById('opportunities-container');
const filterBtns = document.querySelectorAll('.main-nav li');
const searchInput = document.getElementById('search-input');
const themeToggle = document.querySelector('.theme-toggle');
const savedCount = document.getElementById('saved-count');
const totalEl = document.getElementById('total-opportunities');

// Modal Elements
const modalOverlay = document.getElementById('details-modal');
const modalContent = document.getElementById('modal-content-area');
const closeModalBtn = document.querySelector('.close-modal');

// Init
async function init() {
    setupEventListeners();

    // Tenta carregar o JSON gerado dinamicamente pelo Scraper
    try {
        const response = await fetch('editais_raspados.json');
        if (!response.ok) throw new Error("Erro na rede");
        opportunities = await response.json();
    } catch (e) {
        // Fallback no caso do arquivo local ser aberto diretamente no Chrome (Erro de CORS file://)
        console.warn('Falha ao usar fetch() devido a permissões de rede ou arquivo não encontrado. Tentando acessar fallback...');
        container.innerHTML = `<div style="grid-column: 1/-1; padding: 40px; text-align: center;">
            ⚠️ <b>Aviso:</b> Para o painel carregar os dados reais, abra-o através de um servidor local ou utilize a versão hospedada.<br><br>
            Se estiver em um Mac, abra o terminal na pasta do projeto e digite: <code>python3 -m http.server</code>.<br>
            Depois acesse <a href="http://localhost:8000" style="color:var(--primary);">http://localhost:8000</a> no navegador.
        </div>`;
        return;
    }

    renderCards();
    updateSavedCount();
}

function renderCards() {
    container.innerHTML = '';

    let filtered = opportunities.filter(opp => {
        // Se alguém for admin e descartar, ou se o JSON tiver uma flag 'discarded' que possamos adicionar depois
        if (discardedOpps.includes(opp.id)) return false;

        // Text Search
        const search = searchInput.value.toLowerCase();
        const matchesSearch = opp.title.toLowerCase().includes(search) ||
            opp.org.toLowerCase().includes(search);

        // Category
        let matchesCategory = true;
        if (currentFilter === 'saved') {
            matchesCategory = opp.saved;
        } else if (currentFilter !== 'all') {
            matchesCategory = opp.category === currentFilter;
        }

        return matchesSearch && matchesCategory;
    });

    totalEl.textContent = filtered.length;

    if (filtered.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
                Sem resultados encontrados.
            </div>`;
        return;
    }

    filtered.forEach(opp => {
        const catMap = {
            'saude': 'Saúde',
            'direitos': 'Dir. Humanos',
            'pesquisa': 'Pesquisa'
        };

        const card = document.createElement('article');
        card.className = 'opp-card';
        card.innerHTML = `
            <div class="card-header">
                <span class="tag">${catMap[opp.category] || opp.category}</span>
                <div style="display:flex; gap: 12px;">
                    ${isAdmin ? `
                    <button class="discard-btn" title="Descartar edital (Apenas Admin)" onclick="discardOpp(event, ${opp.id})">
                        <i class="fa-regular fa-trash-can"></i>
                    </button>
                    ` : ''}
                    <button class="save-btn ${opp.saved ? 'saved' : ''}" title="Salvar edital" onclick="toggleSave(event, ${opp.id})">
                        <i class="${opp.saved ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
                    </button>
                </div>
            </div>
            <h3 class="card-title">${opp.title}</h3>
            <div class="card-org"><i class="fa-regular fa-building"></i> ${opp.org}</div>
            
            <div class="card-meta">
                <div><i class="fa-regular fa-calendar"></i> ${opp.deadline}</div>
                <div><i class="fa-solid fa-money-bill-wave"></i> ${opp.amount}</div>
            </div>
        `;

        card.addEventListener('click', () => openModal(opp));
        container.appendChild(card);
    });
}

function toggleSave(event, id) {
    event.stopPropagation();
    const opp = opportunities.find(o => o.id === id);
    if (opp) {
        opp.saved = !opp.saved;
        renderCards();
        updateSavedCount();
    }
}

function discardOpp(event, id) {
    event.stopPropagation();
    if (confirm("Ocultar definitivamente este edital? Ele não aparecerá mais para a ABEMDIS.")) {
        discardedOpps.push(id);
        localStorage.setItem('abemdis_discarded', JSON.stringify(discardedOpps));

        // Remove dos salvos caso estivesse favoritado
        const opp = opportunities.find(o => o.id === id);
        if (opp) opp.saved = false;

        renderCards();
        updateSavedCount();
    }
}

function updateSavedCount() {
    const count = opportunities.filter(o => o.saved).length;
    savedCount.textContent = count;
}

function setupEventListeners() {
    // Filters
    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            filterBtns.forEach(b => b.classList.remove('active'));
            const target = e.currentTarget;
            target.classList.add('active');
            currentFilter = target.dataset.filter;
            renderCards();
        });
    });

    // Search
    searchInput.addEventListener('input', renderCards);

    // Theme Toggle
    themeToggle.addEventListener('click', () => {
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        if (isDark) {
            document.body.removeAttribute('data-theme');
            themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
        } else {
            document.body.setAttribute('data-theme', 'dark');
            themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
        }
    });

    // Modal
    closeModalBtn.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });
}

function openModal(opp) {
    modalContent.innerHTML = `
        <div class="modal-header">
            <span class="tag">${opp.category.toUpperCase()}</span>
            <h2 class="modal-title">${opp.title}</h2>
            <div class="card-org"><i class="fa-regular fa-building"></i> ${opp.org}</div>
        </div>
        <div class="modal-body">
            <p>${opp.desc}</p>
            
            <div class="detail-grid">
                <div class="detail-item">
                    <div class="detail-label">Prazo Final</div>
                    <div class="detail-value"><i class="fa-regular fa-calendar"></i> ${opp.deadline}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Valor Máximo</div>
                    <div class="detail-value"><i class="fa-solid fa-money-bill-wave"></i> ${opp.amount}</div>
                </div>
            </div>

            <a href="${opp.link}" target="_blank" class="action-btn">Acessar Edital Oficial</a>
        </div>
    `;
    modalOverlay.classList.add('active');
}

function closeModal() {
    modalOverlay.classList.remove('active');
}

// Boot
init();
