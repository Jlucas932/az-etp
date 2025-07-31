// Estado da aplicação
let currentMode = 'welcome'; // welcome, etp, chat
let etpSession = null;
let chatHistory = [];
let isProcessing = false;

// Elementos DOM
const elements = {
    sidebar: document.getElementById('sidebar'),
    sidebarToggle: document.getElementById('sidebarToggle'),
    newChatBtn: document.getElementById('newChatBtn'),
    chatMessages: document.getElementById('chatMessages'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    charCount: document.getElementById('charCount'),
    attachmentBtn: document.getElementById('attachmentBtn'),
    fileInput: document.getElementById('fileInput'),
    attachedFiles: document.getElementById('attachedFiles'),
    welcomeMessage: document.getElementById('welcomeMessage'),
    etpStartBtn: document.getElementById('etpStartBtn'),
    chatModeBtn: document.getElementById('chatModeBtn'),
    etpModalOverlay: document.getElementById('etpModalOverlay'),
    etpModal: document.getElementById('etpModal'),
    etpModalTitle: document.getElementById('etpModalTitle'),
    etpModalContent: document.getElementById('etpModalContent'),
    etpModalClose: document.getElementById('etpModalClose'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    toastContainer: document.getElementById('toastContainer'),
    chatList: document.getElementById('chatList')
};

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadChatHistory();
});

function initializeApp() {
    // Configurar tema
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Configurar input
    updateCharCount();
    updateSendButton();
}

function setupEventListeners() {
    // Sidebar
    elements.sidebarToggle?.addEventListener('click', toggleSidebar);
    elements.newChatBtn?.addEventListener('click', startNewChat);
    
    // Input
    elements.messageInput?.addEventListener('input', handleInputChange);
    elements.messageInput?.addEventListener('keydown', handleKeyDown);
    elements.sendBtn?.addEventListener('click', sendMessage);
    
    // Anexos
    elements.attachmentBtn?.addEventListener('click', () => elements.fileInput?.click());
    elements.fileInput?.addEventListener('change', handleFileAttachment);
    
    // Botões principais
    elements.etpStartBtn?.addEventListener('click', startETPFlow);
    elements.chatModeBtn?.addEventListener('click', startChatMode);
    
    // Modal ETP
    elements.etpModalClose?.addEventListener('click', closeETPModal);
    elements.etpModalOverlay?.addEventListener('click', (e) => {
        if (e.target === elements.etpModalOverlay) closeETPModal();
    });
    
    // Configurações
    const settingsBtn = document.querySelector('.header-btn[title="Configurações"]');
    settingsBtn?.addEventListener('click', openSettings);
    
    // Responsividade
    window.addEventListener('resize', handleResize);
}

// Gerenciamento de chat
function startNewChat() {
    // Salvar conversa atual se existir
    if (chatHistory.length > 0) {
        saveCurrentConversation();
    }
    
    currentMode = 'welcome';
    chatHistory = [];
    etpSession = null;
    
    elements.chatMessages.innerHTML = `
        <div class="welcome-message" id="welcomeMessage">
            <div class="welcome-icon">
                <i class="fas fa-file-contract" style="font-size: 60px; color: #4a90e2;"></i>
            </div>
            <h2>Bem-vindo ao AZ ETP Fácil!</h2>
            <p>Sistema inteligente para geração de documentos de Estudo Técnico Preliminar (ETP) conforme a Lei 14.133/21.</p>
            
            <div class="etp-options">
                <button class="etp-option-btn" id="etpStartBtn">
                    <i class="fas fa-file-alt"></i>
                    <div class="option-content">
                        <span class="option-title">Iniciar Novo ETP</span>
                        <span class="option-desc">Criar um novo Estudo Técnico Preliminar</span>
                    </div>
                </button>
                
                <button class="etp-option-btn" id="chatModeBtn">
                    <i class="fas fa-comments"></i>
                    <div class="option-content">
                        <span class="option-title">Chat sobre Compras Públicas</span>
                        <span class="option-desc">Tire dúvidas sobre licitações e Lei 14.133/21</span>
                    </div>
                </button>
            </div>
        </div>
    `;
    
    // Reconfigurar event listeners
    document.getElementById('etpStartBtn')?.addEventListener('click', startETPFlow);
    document.getElementById('chatModeBtn')?.addEventListener('click', startChatMode);
    
    updateChatHistory();
}

function startETPFlow() {
    currentMode = 'etp';
    elements.welcomeMessage.style.display = 'none';
    
    // Iniciar ETP diretamente sem modal
    fetch('/api/etp/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            etpSession = data.session_id;
            addChatMessage('assistant', 'Vamos criar seu Estudo Técnico Preliminar! Você pode:');
            
            // Adicionar opções de início
            setTimeout(() => {
                addETPStartOptions();
            }, 1000);
        } else {
            showToast('Erro ao iniciar ETP: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showToast('Erro de conexão: ' + error.message, 'error');
    });
}

function addETPStartOptions() {
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'etp-start-options';
    buttonContainer.innerHTML = `
        <button class="option-btn" onclick="startManualQuestions()">
            <i class="fas fa-edit"></i> Responder Perguntas Manualmente
        </button>
        <button class="option-btn" onclick="showUploadOption()">
            <i class="fas fa-upload"></i> Enviar Documento para Análise
        </button>
    `;
    
    elements.chatMessages.appendChild(buttonContainer);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function startManualQuestions() {
    // Remover botões de opção
    const buttons = document.querySelector('.etp-start-options');
    if (buttons) buttons.remove();
    
    addChatMessage('assistant', 'Perfeito! Vou fazer algumas perguntas obrigatórias conforme a Lei 14.133/21.');
    
    // Começar com a primeira pergunta
    setTimeout(() => {
        askETPQuestion(1);
    }, 1000);
}

function showUploadOption() {
    // Remover botões de opção
    const buttons = document.querySelector('.etp-start-options');
    if (buttons) buttons.remove();
    
    addChatMessage('assistant', 'Ótimo! Envie um documento (PDF, DOC, DOCX ou TXT) e eu tentarei extrair as informações automaticamente.');
    
    // Adicionar área de upload
    setTimeout(() => {
        addUploadArea();
    }, 500);
}

function addUploadArea() {
    const uploadContainer = document.createElement('div');
    uploadContainer.className = 'upload-container';
    uploadContainer.innerHTML = `
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <i class="fas fa-cloud-upload-alt"></i>
            <p>Clique aqui para selecionar um arquivo</p>
            <small>Formatos aceitos: PDF, DOC, DOCX, TXT</small>
        </div>
        <input type="file" id="fileInput" accept=".pdf,.doc,.docx,.txt" style="display: none;" onchange="handleFileUpload(this)">
        <button class="option-btn" onclick="startManualQuestions()" style="margin-top: 10px;">
            <i class="fas fa-edit"></i> Ou responder manualmente
        </button>
    `;
    
    elements.chatMessages.appendChild(uploadContainer);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    addChatMessage('user', `Arquivo selecionado: ${file.name}`);
    addChatMessage('assistant', 'Analisando documento... Isso pode levar alguns segundos.');
    
    showLoading('Analisando documento...');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', etpSession);
    
    fetch('/api/etp/upload-document', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        // Remover área de upload
        const uploadContainer = document.querySelector('.upload-container');
        if (uploadContainer) uploadContainer.remove();
        
        if (data.success) {
            if (data.auto_filled) {
                addChatMessage('assistant', 'Excelente! Consegui extrair as informações do documento automaticamente. Agora vou gerar seu ETP...');
                
                // Pular para geração do preview
                setTimeout(() => {
                    generateETPPreview();
                }, 2000);
            } else {
                addChatMessage('assistant', 'Documento analisado, mas não consegui extrair todas as informações automaticamente. Vamos às perguntas manuais:');
                
                // Começar perguntas manuais
                setTimeout(() => {
                    askETPQuestion(1);
                }, 1000);
            }
        } else {
            addChatMessage('assistant', `Erro na análise: ${data.error}. Vamos às perguntas manuais:`);
            
            // Começar perguntas manuais como fallback
            setTimeout(() => {
                askETPQuestion(1);
            }, 1000);
        }
    })
    .catch(error => {
        hideLoading();
        
        // Remover área de upload
        const uploadContainer = document.querySelector('.upload-container');
        if (uploadContainer) uploadContainer.remove();
        
        addChatMessage('assistant', `Erro no upload: ${error.message}. Vamos às perguntas manuais:`);
        
        // Começar perguntas manuais como fallback
        setTimeout(() => {
            askETPQuestion(1);
        }, 1000);
    });
}

let currentETPQuestion = 0;
let etpAnswers = {};

const ETP_QUESTIONS = [
    {
        id: 1,
        question: "1. Qual a descrição da necessidade da contratação?",
        type: "text",
        placeholder: "Descreva detalhadamente o que precisa ser contratado..."
    },
    {
        id: 2,
        question: "2. Possui demonstrativo de previsão no PCA (Plano de Contratações Anual)?",
        type: "boolean",
        options: ["Sim", "Não"]
    },
    {
        id: 3,
        question: "3. Quais normas legais pretende utilizar?",
        type: "text",
        placeholder: "Ex: Lei 14.133/21, Decreto 10.024/19, etc..."
    },
    {
        id: 4,
        question: "4. Qual o quantitativo e valor estimado?",
        type: "text",
        placeholder: "Ex: 100 unidades, valor estimado R$ 50.000,00..."
    },
    {
        id: 5,
        question: "5. Haverá parcelamento da contratação?",
        type: "boolean",
        options: ["Sim", "Não"]
    }
];

function askETPQuestion(questionNumber) {
    if (questionNumber > ETP_QUESTIONS.length) {
        // Todas as perguntas foram respondidas
        finishETPQuestions();
        return;
    }
    
    currentETPQuestion = questionNumber;
    const question = ETP_QUESTIONS[questionNumber - 1];
    
    addChatMessage('assistant', question.question);
    
    if (question.type === 'boolean') {
        // Adicionar botões de opção
        setTimeout(() => {
            addQuestionButtons(question.options, questionNumber);
        }, 500);
    } else {
        // Aguardar resposta de texto
        elements.messageInput.placeholder = question.placeholder;
        elements.messageInput.focus();
    }
}

function addQuestionButtons(options, questionNumber) {
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'question-buttons';
    buttonContainer.innerHTML = options.map(option => 
        `<button class="option-btn" onclick="selectETPOption('${option}', ${questionNumber})">${option}</button>`
    ).join('');
    
    elements.chatMessages.appendChild(buttonContainer);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function selectETPOption(option, questionNumber) {
    // Remover botões
    const buttons = document.querySelector('.question-buttons');
    if (buttons) buttons.remove();
    
    // Adicionar resposta do usuário
    addChatMessage('user', option);
    
    // Salvar resposta
    etpAnswers[questionNumber] = option;
    
    // Próxima pergunta
    setTimeout(() => {
        askETPQuestion(questionNumber + 1);
    }, 1000);
}

function finishETPQuestions() {
    addChatMessage('assistant', 'Perfeito! Todas as perguntas foram respondidas. Agora vou gerar seu Estudo Técnico Preliminar...');
    
    showLoading('Gerando ETP...');
    
    // Garantir que temos um session_id válido
    if (!etpSession) {
        // Criar nova sessão se não existir
        fetch('/api/etp/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                etpSession = data.session_id;
                // Agora validar com session_id válido
                validateAnswersWithSession();
            } else {
                hideLoading();
                showToast('Erro ao criar sessão ETP: ' + data.error, 'error');
            }
        })
        .catch(error => {
            hideLoading();
            showToast('Erro de conexão: ' + error.message, 'error');
        });
    } else {
        validateAnswersWithSession();
    }
}

function validateAnswersWithSession() {
    // Salvar respostas e gerar documento
    fetch('/api/etp/validate-answers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: etpSession,
            answers: etpAnswers
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            addChatMessage('assistant', 'Respostas validadas! Gerando preview do documento...');
            generateETPPreviewWithProgress();
        } else {
            addChatMessage('assistant', 'Erro na validação: ' + data.error);
        }
    })
    .catch(error => {
        hideLoading();
        addChatMessage('assistant', 'Erro ao validar respostas: ' + error.message);
    });
}

function generateETPPreview() {
    showLoading('Gerando preview do ETP...');
    
    fetch('/api/etp/generate-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: etpSession
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            addChatMessage('assistant', 'Preview gerado com sucesso! Você pode visualizar e aprovar o documento.');
            
            // Mostrar preview do conteúdo
            if (data.preview) {
                const previewDiv = document.createElement('div');
                previewDiv.className = 'etp-preview';
                previewDiv.innerHTML = `
                    <div class="preview-header">
                        <h3>📋 Preview do Estudo Técnico Preliminar</h3>
                    </div>
                    <div class="preview-content">
                        ${data.preview.replace(/\n/g, '<br>')}
                    </div>
                `;
                elements.chatMessages.appendChild(previewDiv);
            }
            
            // Adicionar botões de ação
            setTimeout(() => {
                addETPActionButtons();
            }, 500);
        } else {
            addChatMessage('assistant', 'Erro ao gerar preview: ' + (data.error || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        hideLoading();
        addChatMessage('assistant', 'Erro na geração: ' + error.message);
        console.error('Erro detalhado:', error);
    });
}

function addETPActionButtons() {
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'etp-action-buttons';
    buttonContainer.innerHTML = `
        <button class="action-btn preview-btn" onclick="showETPPreview()">
            <i class="fas fa-eye"></i> Ver Preview
        </button>
        <button class="action-btn generate-btn" onclick="generateFinalETP()">
            <i class="fas fa-file-word"></i> Gerar Documento Final
        </button>
    `;
    
    elements.chatMessages.appendChild(buttonContainer);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function showETPPreview() {
    // Buscar preview salvo da sessão
    fetch('/api/etp/get-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: etpSession
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.preview) {
            // Mostrar preview em modal ou área expandida
            const previewModal = document.createElement('div');
            previewModal.className = 'preview-modal';
            previewModal.innerHTML = `
                <div class="preview-modal-content">
                    <div class="preview-modal-header">
                        <h3>📋 Preview do Estudo Técnico Preliminar</h3>
                        <button class="close-modal" onclick="closePreviewModal()">&times;</button>
                    </div>
                    <div class="preview-modal-body">
                        <pre class="preview-text">${data.preview}</pre>
                    </div>
                    <div class="preview-modal-footer">
                        <button class="action-btn" onclick="closePreviewModal()">Fechar</button>
                        <button class="action-btn primary" onclick="approveAndGenerateWord()">Aprovar e Gerar Word</button>
                    </div>
                </div>
            `;
            document.body.appendChild(previewModal);
        } else {
            addChatMessage('assistant', 'Preview não encontrado. Gere o preview primeiro.');
        }
    })
    .catch(error => {
        addChatMessage('assistant', 'Erro ao buscar preview: ' + error.message);
    });
}

function generateFinalETP() {
    addChatMessage('assistant', 'Gerando documento Word final...');
    showLoading('Criando documento...');
    
    fetch('/api/etp/generate-final-document', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: etpSession
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            addChatMessage('assistant', 'Documento gerado com sucesso! Você pode fazer o download.');
            
            // Adicionar botão de download
            setTimeout(() => {
                addDownloadButton(data.document_path);
            }, 500);
        } else {
            addChatMessage('assistant', 'Erro ao gerar documento: ' + data.error);
        }
    })
    .catch(error => {
        hideLoading();
        addChatMessage('assistant', 'Erro na geração: ' + error.message);
    });
}

function addDownloadButton(documentPath) {
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'download-container';
    buttonContainer.innerHTML = `
        <button class="download-btn" onclick="downloadETP('${documentPath}')">
            <i class="fas fa-download"></i> Download ETP
        </button>
    `;
    
    elements.chatMessages.appendChild(buttonContainer);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function downloadETP(documentPath) {
    window.open(`/api/etp/download-document/${documentPath}`, '_blank');
}

function startChatMode() {
    currentMode = 'chat';
    elements.welcomeMessage.style.display = 'none';
    addChatMessage('assistant', 'Olá! Sou seu assistente especializado em compras públicas e Lei 14.133/21. Como posso ajudá-lo hoje?');
    elements.messageInput.placeholder = 'Digite sua pergunta sobre compras públicas...';
    elements.messageInput.focus();
}

function sendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message || isProcessing) return;
    
    addChatMessage('user', message);
    elements.messageInput.value = '';
    updateCharCount();
    updateSendButton();
    
    if (currentMode === 'etp' && currentETPQuestion > 0) {
        // Processar resposta do ETP
        etpAnswers[currentETPQuestion] = message;
        
        // Próxima pergunta
        setTimeout(() => {
            askETPQuestion(currentETPQuestion + 1);
        }, 1000);
        
        // Resetar placeholder
        elements.messageInput.placeholder = 'Digite sua mensagem aqui...';
    } else if (currentMode === 'chat') {
        sendChatMessage(message);
    }
}

function sendChatMessage(message) {
    isProcessing = true;
    showLoading('Processando sua pergunta...');
    
    fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            message: message,
            session_id: etpSession 
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        isProcessing = false;
        
        if (data.success) {
            addFormattedChatMessage('assistant', data.response);
        } else {
            addChatMessage('assistant', 'Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente.');
        }
    })
    .catch(error => {
        hideLoading();
        isProcessing = false;
        addChatMessage('assistant', 'Erro de conexão. Verifique sua internet e tente novamente.');
    });
}

function addFormattedChatMessage(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${sender}`;
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content formatted';
    
    // Formatar o conteúdo para melhor legibilidade
    const formattedContent = formatChatResponse(content);
    messageContent.innerHTML = formattedContent;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    elements.chatMessages.appendChild(messageDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    
    // Salvar no histórico
    chatHistory.push({ sender, content, timestamp: Date.now() });
    updateChatHistory();
}

function formatChatResponse(content) {
    // Converter texto em HTML formatado
    let formatted = content
        // Converter **texto** em negrito
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Converter *texto* em itálico
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Converter quebras de linha duplas em parágrafos
        .replace(/\n\n/g, '</p><p>')
        // Converter quebras de linha simples em <br>
        .replace(/\n/g, '<br>')
        // Converter listas com • ou -
        .replace(/^[•\-]\s(.+)$/gm, '<li>$1</li>')
        // Converter números seguidos de ponto em listas numeradas
        .replace(/^(\d+)\.\s(.+)$/gm, '<li>$2</li>');
    
    // Envolver em parágrafo se não começar com tag
    if (!formatted.startsWith('<')) {
        formatted = '<p>' + formatted + '</p>';
    }
    
    // Converter sequências de <li> em listas
    formatted = formatted.replace(/(<li>.*?<\/li>)/gs, (match) => {
        return '<ul>' + match + '</ul>';
    });
    
    return formatted;
}

function addChatMessage(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${sender}`;
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    elements.chatMessages.appendChild(messageDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    
    // Salvar no histórico
    chatHistory.push({ sender, content, timestamp: Date.now() });
    updateChatHistory();
}

// Modal ETP
function showETPModal() {
    elements.etpModalOverlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeETPModal() {
    elements.etpModalOverlay.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function loadETPStep(step) {
    showLoading('Carregando etapa do ETP...');
    
    fetch(`/api/etp/step/${step}?session_id=${etpSession}`)
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            elements.etpModalTitle.textContent = data.title;
            elements.etpModalContent.innerHTML = data.content;
            setupETPStepEvents(step);
        } else {
            showToast('Erro ao carregar etapa: ' + data.error, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showToast('Erro de conexão: ' + error.message, 'error');
    });
}

function setupETPStepEvents(step) {
    // Configurar eventos específicos de cada etapa
    const nextBtn = elements.etpModalContent.querySelector('.next-btn');
    const prevBtn = elements.etpModalContent.querySelector('.prev-btn');
    const uploadBtn = elements.etpModalContent.querySelector('.upload-btn');
    const skipBtn = elements.etpModalContent.querySelector('.skip-btn');
    
    nextBtn?.addEventListener('click', () => {
        if (validateETPStep(step)) {
            saveETPStep(step);
            loadETPStep(step + 1);
        }
    });
    
    prevBtn?.addEventListener('click', () => {
        loadETPStep(step - 1);
    });
    
    uploadBtn?.addEventListener('click', () => {
        const fileInput = elements.etpModalContent.querySelector('input[type="file"]');
        fileInput?.click();
    });
    
    skipBtn?.addEventListener('click', () => {
        loadETPStep(step + 1);
    });
    
    // Upload de arquivo
    const fileInput = elements.etpModalContent.querySelector('input[type="file"]');
    fileInput?.addEventListener('change', handleETPFileUpload);
}

function validateETPStep(step) {
    // Validação específica por etapa
    const requiredFields = elements.etpModalContent.querySelectorAll('[required]');
    for (let field of requiredFields) {
        if (!field.value.trim()) {
            showToast('Por favor, preencha todos os campos obrigatórios.', 'warning');
            field.focus();
            return false;
        }
    }
    return true;
}

function saveETPStep(step) {
    const formData = new FormData();
    formData.append('session_id', etpSession);
    formData.append('step', step);
    
    // Coletar dados do formulário
    const inputs = elements.etpModalContent.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        if (input.type === 'file') {
            if (input.files.length > 0) {
                formData.append(input.name, input.files[0]);
            }
        } else if (input.type === 'radio' || input.type === 'checkbox') {
            if (input.checked) {
                formData.append(input.name, input.value);
            }
        } else {
            formData.append(input.name, input.value);
        }
    });
    
    fetch('/api/etp/save-step', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            showToast('Erro ao salvar dados: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showToast('Erro ao salvar: ' + error.message, 'error');
    });
}

function handleETPFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    showLoading('Analisando documento...');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', etpSession);
    
    fetch('/api/etp/analyze-document', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Documento analisado com sucesso!', 'success');
            // Atualizar interface com dados extraídos
            if (data.extracted_data) {
                populateFormWithExtractedData(data.extracted_data);
            }
        } else {
            showToast('Erro na análise: ' + data.error, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showToast('Erro no upload: ' + error.message, 'error');
    });
}

function populateFormWithExtractedData(data) {
    // Preencher formulário com dados extraídos
    Object.keys(data).forEach(key => {
        const field = elements.etpModalContent.querySelector(`[name="${key}"]`);
        if (field) {
            field.value = data[key];
        }
    });
}

// Utilitários
function handleInputChange() {
    updateCharCount();
    updateSendButton();
    autoResizeTextarea();
}

function updateCharCount() {
    const count = elements.messageInput.value.length;
    elements.charCount.textContent = `${count}/4000`;
    
    if (count > 3800) {
        elements.charCount.style.color = 'var(--warning-color)';
    } else if (count > 3900) {
        elements.charCount.style.color = 'var(--danger-color)';
    } else {
        elements.charCount.style.color = 'var(--text-secondary)';
    }
}

function updateSendButton() {
    const hasText = elements.messageInput.value.trim().length > 0;
    elements.sendBtn.disabled = !hasText || isProcessing;
}

function autoResizeTextarea() {
    elements.messageInput.style.height = 'auto';
    elements.messageInput.style.height = Math.min(elements.messageInput.scrollHeight, 200) + 'px';
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function handleFileAttachment(event) {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;
    
    files.forEach(file => {
        addAttachedFile(file);
    });
    
    elements.attachedFiles.style.display = files.length > 0 ? 'flex' : 'none';
}

function addAttachedFile(file) {
    const fileDiv = document.createElement('div');
    fileDiv.className = 'attached-file';
    
    const icon = getFileIcon(file.type);
    fileDiv.innerHTML = `
        <i class="${icon}"></i>
        <span>${file.name}</span>
        <button class="remove-file" onclick="removeAttachedFile(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    elements.attachedFiles.appendChild(fileDiv);
}

function removeAttachedFile(button) {
    button.parentElement.remove();
    if (elements.attachedFiles.children.length === 0) {
        elements.attachedFiles.style.display = 'none';
    }
}

function getFileIcon(mimeType) {
    if (mimeType.includes('pdf')) return 'fas fa-file-pdf';
    if (mimeType.includes('word')) return 'fas fa-file-word';
    if (mimeType.includes('image')) return 'fas fa-file-image';
    return 'fas fa-file';
}

// Loading e Toast
function showLoading(text = 'Carregando...') {
    elements.loadingText.textContent = text;
    elements.loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    toast.innerHTML = `
        <div class="toast-content">
            <span>${message}</span>
            <button class="toast-close" onclick="removeToast(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Auto remove após 5 segundos
    setTimeout(() => {
        if (toast.parentElement) {
            removeToast(toast.querySelector('.toast-close'));
        }
    }, 5000);
}

function removeToast(button) {
    button.closest('.toast').remove();
}

// Histórico de chat
function loadChatHistory() {
    const saved = localStorage.getItem('chatHistory');
    if (saved) {
        try {
            const history = JSON.parse(saved);
            updateChatHistoryDisplay(history);
        } catch (e) {
            console.error('Erro ao carregar histórico:', e);
        }
    }
}

function updateChatHistory() {
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    
    // Atualizar display do histórico
    const sessions = groupChatSessions();
    updateChatHistoryDisplay(sessions);
}

function groupChatSessions() {
    // Agrupar mensagens em sessões
    const sessions = [];
    let currentSession = null;
    
    chatHistory.forEach(msg => {
        if (!currentSession || (Date.now() - msg.timestamp) > 3600000) { // 1 hora
            currentSession = {
                id: Date.now(),
                title: msg.content.substring(0, 30) + '...',
                timestamp: msg.timestamp,
                messages: []
            };
            sessions.push(currentSession);
        }
        currentSession.messages.push(msg);
    });
    
    return sessions.slice(-10); // Últimas 10 sessões
}

function updateChatHistoryDisplay(sessions) {
    elements.chatList.innerHTML = '';
    
    sessions.forEach(session => {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        chatItem.innerHTML = `
            <i class="fas fa-message"></i>
            <span>${session.title}</span>
            <div class="chat-actions">
                <button class="chat-options" title="Opções">
                    <i class="fas fa-ellipsis-h"></i>
                </button>
                <button class="chat-delete" title="Excluir conversa" onclick="deleteChat(${session.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        chatItem.addEventListener('click', () => loadChatSession(session));
        elements.chatList.appendChild(chatItem);
    });
}

function loadChatSession(session) {
    elements.chatMessages.innerHTML = '';
    session.messages.forEach(msg => {
        addChatMessage(msg.sender, msg.content);
    });
}

function deleteChat(sessionId) {
    if (confirm('Deseja excluir esta conversa?')) {
        // Implementar exclusão
        showToast('Conversa excluída', 'success');
    }
}

// Sidebar e responsividade
function toggleSidebar() {
    elements.sidebar.classList.toggle('open');
}

function handleResize() {
    if (window.innerWidth > 768) {
        elements.sidebar.classList.remove('open');
    }
}

// Configurações
function openSettings() {
    const modalOverlay = document.getElementById('modalOverlay');
    if (modalOverlay) {
        modalOverlay.style.display = 'flex';
    }
}

// Fechar modais ao clicar fora
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});

// Configurar fechamento de modais
document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const modal = e.target.closest('.modal-overlay');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
});

// Exportar funções globais necessárias
window.removeAttachedFile = removeAttachedFile;
window.removeToast = removeToast;
window.deleteChat = deleteChat;


function closePreviewModal() {
    const modal = document.querySelector('.preview-modal');
    if (modal) {
        modal.remove();
    }
}

function approveAndGenerateWord() {
    closePreviewModal();
    generateFinalETPWithProgress();
}

function generateFinalETPWithProgress() {
    addChatMessage('assistant', 'Iniciando geração do documento Word...');
    
    // Criar barra de progresso
    const progressContainer = document.createElement('div');
    progressContainer.className = 'progress-container';
    progressContainer.innerHTML = `
        <div class="progress-header">
            <span>📄 Gerando Documento Word</span>
            <span class="progress-percentage">0%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 0%"></div>
        </div>
        <div class="progress-status">Preparando...</div>
    `;
    elements.chatMessages.appendChild(progressContainer);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    
    // Simular progresso enquanto gera
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        
        updateProgress(progress);
    }, 500);
    
    // Aprovar preview primeiro
    fetch('/api/etp/approve-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: etpSession
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateProgressStatus('Aprovação concluída. Gerando documento...');
            
            // Gerar documento final
            return fetch('/api/etp/generate-final', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: etpSession
                })
            });
        } else {
            throw new Error(data.error || 'Erro na aprovação');
        }
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        updateProgress(100);
        updateProgressStatus('Documento gerado com sucesso!');
        
        setTimeout(() => {
            progressContainer.remove();
            
            if (data.success) {
                addChatMessage('assistant', 'Documento Word gerado com sucesso! Você pode baixá-lo agora.');
                
                // Adicionar botão de download
                const downloadContainer = document.createElement('div');
                downloadContainer.className = 'download-container';
                downloadContainer.innerHTML = `
                    <a href="/api/etp/download/${etpSession}" class="action-btn download-btn" target="_blank">
                        📥 Baixar Documento Word
                    </a>
                `;
                elements.chatMessages.appendChild(downloadContainer);
            } else {
                addChatMessage('assistant', 'Erro ao gerar documento: ' + (data.error || 'Erro desconhecido'));
            }
        }, 1000);
    })
    .catch(error => {
        clearInterval(progressInterval);
        progressContainer.remove();
        addChatMessage('assistant', 'Erro na geração: ' + error.message);
    });
}

function updateProgress(percentage) {
    const progressFill = document.querySelector('.progress-fill');
    const progressPercentage = document.querySelector('.progress-percentage');
    
    if (progressFill && progressPercentage) {
        progressFill.style.width = percentage + '%';
        progressPercentage.textContent = Math.round(percentage) + '%';
    }
}

function updateProgressStatus(status) {
    const progressStatus = document.querySelector('.progress-status');
    if (progressStatus) {
        progressStatus.textContent = status;
    }
}

// Melhorar função generateETPPreview com progresso
function generateETPPreviewWithProgress() {
    addChatMessage('assistant', 'Iniciando geração do preview...');
    
    // Criar barra de progresso simples
    const progressContainer = document.createElement('div');
    progressContainer.className = 'progress-container simple';
    progressContainer.innerHTML = `
        <div class="progress-header">
            <span>📋 Gerando Preview</span>
            <span class="progress-percentage">0%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 0%"></div>
        </div>
        <div class="progress-status">Analisando respostas...</div>
    `;
    elements.chatMessages.appendChild(progressContainer);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    
    // Simular progresso
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress > 85) progress = 85;
        updateProgress(progress);
    }, 300);
    
    fetch('/api/etp/generate-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: etpSession
        })
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        updateProgress(100);
        updateProgressStatus('Preview gerado!');
        
        setTimeout(() => {
            progressContainer.remove();
            
            if (data.success) {
                addChatMessage('assistant', 'Preview gerado com sucesso! Você pode visualizar e aprovar o documento.');
                
                // Mostrar preview inline se disponível
                if (data.preview) {
                    const previewDiv = document.createElement('div');
                    previewDiv.className = 'etp-preview-inline';
                    previewDiv.innerHTML = `
                        <div class="preview-header">
                            <h4>📋 Preview Rápido</h4>
                        </div>
                        <div class="preview-content-short">
                            ${data.preview.substring(0, 500).replace(/\n/g, '<br>')}...
                        </div>
                    `;
                    elements.chatMessages.appendChild(previewDiv);
                }
                
                // Adicionar botões de ação
                setTimeout(() => {
                    addETPActionButtons();
                }, 500);
            } else {
                addChatMessage('assistant', 'Erro ao gerar preview: ' + (data.error || 'Erro desconhecido'));
            }
        }, 800);
    })
    .catch(error => {
        clearInterval(progressInterval);
        progressContainer.remove();
        addChatMessage('assistant', 'Erro na geração: ' + error.message);
    });
}



// Funções de salvamento de conversas
function saveCurrentConversation() {
    if (chatHistory.length === 0) return;
    
    const now = new Date();
    const dateTime = formatDateTime(now);
    let conversationName;
    
    if (currentMode === 'etp' || etpSession) {
        conversationName = `ETP-${dateTime}`;
    } else {
        conversationName = `Chat-${dateTime}`;
    }
    
    const conversation = {
        id: generateId(),
        name: conversationName,
        type: currentMode === 'etp' || etpSession ? 'etp' : 'chat',
        messages: [...chatHistory],
        etpSession: etpSession ? {...etpSession} : null,
        timestamp: now.toISOString(),
        dateTime: dateTime
    };
    
    // Salvar no localStorage
    const savedConversations = JSON.parse(localStorage.getItem('conversations') || '[]');
    savedConversations.unshift(conversation); // Adicionar no início
    
    // Manter apenas as últimas 50 conversas
    if (savedConversations.length > 50) {
        savedConversations.splice(50);
    }
    
    localStorage.setItem('conversations', JSON.stringify(savedConversations));
    
    // Atualizar lista na sidebar
    updateConversationsList();
    
    showToast(`Conversa salva como "${conversationName}"`, 'success');
}

function formatDateTime(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function updateConversationsList() {
    const savedConversations = JSON.parse(localStorage.getItem('conversations') || '[]');
    const chatList = elements.chatList;
    
    if (!chatList) return;
    
    chatList.innerHTML = '';
    
    if (savedConversations.length === 0) {
        chatList.innerHTML = '<div class="no-conversations">Nenhuma conversa salva</div>';
        return;
    }
    
    savedConversations.forEach(conversation => {
        const conversationElement = document.createElement('div');
        conversationElement.className = 'conversation-item';
        conversationElement.innerHTML = `
            <div class="conversation-info">
                <div class="conversation-name">
                    <i class="fas ${conversation.type === 'etp' ? 'fa-file-alt' : 'fa-comments'}"></i>
                    ${conversation.name}
                </div>
                <div class="conversation-date">${conversation.dateTime}</div>
            </div>
            <button class="delete-conversation" onclick="deleteConversation('${conversation.id}')" title="Excluir">
                <i class="fas fa-trash"></i>
            </button>
        `;
        
        conversationElement.addEventListener('click', (e) => {
            if (!e.target.closest('.delete-conversation')) {
                loadConversation(conversation.id);
            }
        });
        
        chatList.appendChild(conversationElement);
    });
}

function loadConversation(conversationId) {
    const savedConversations = JSON.parse(localStorage.getItem('conversations') || '[]');
    const conversation = savedConversations.find(c => c.id === conversationId);
    
    if (!conversation) {
        showToast('Conversa não encontrada', 'error');
        return;
    }
    
    // Salvar conversa atual antes de carregar nova
    if (chatHistory.length > 0) {
        saveCurrentConversation();
    }
    
    // Carregar conversa
    chatHistory = [...conversation.messages];
    etpSession = conversation.etpSession ? {...conversation.etpSession} : null;
    currentMode = conversation.type;
    
    // Limpar e recriar mensagens
    elements.chatMessages.innerHTML = '';
    chatHistory.forEach(message => {
        addChatMessage(message.role, message.content, false);
    });
    
    // Fechar sidebar em mobile
    if (window.innerWidth <= 768) {
        elements.sidebar.classList.remove('active');
    }
    
    showToast(`Conversa "${conversation.name}" carregada`, 'success');
}

function deleteConversation(conversationId) {
    if (!confirm('Tem certeza que deseja excluir esta conversa?')) return;
    
    const savedConversations = JSON.parse(localStorage.getItem('conversations') || '[]');
    const updatedConversations = savedConversations.filter(c => c.id !== conversationId);
    
    localStorage.setItem('conversations', JSON.stringify(updatedConversations));
    updateConversationsList();
    
    showToast('Conversa excluída', 'success');
}

// Modificar funções existentes para salvar automaticamente
function startETPFlow() {
    // Salvar conversa atual se existir
    if (chatHistory.length > 0) {
        saveCurrentConversation();
    }
    
    currentMode = 'etp';
    chatHistory = [];
    etpSession = null;
    
    addChatMessage('assistant', 'Olá! Vou ajudá-lo a criar um Estudo Técnico Preliminar (ETP) conforme a Lei 14.133/21. Como você gostaria de começar?');
    
    setTimeout(() => {
        addETPStartOptions();
    }, 1000);
}

function startChatMode() {
    // Salvar conversa atual se existir
    if (chatHistory.length > 0) {
        saveCurrentConversation();
    }
    
    currentMode = 'chat';
    chatHistory = [];
    etpSession = null;
    
    addChatMessage('assistant', 'Olá! Sou seu assistente especializado em licitações e contratos públicos. Como posso ajudá-lo hoje?');
}

// Carregar conversas ao inicializar
function loadChatHistory() {
    updateConversationsList();
}

