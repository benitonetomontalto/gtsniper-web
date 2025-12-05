/**
 * BROKER SELECTOR PATCH
 * Adiciona seleção de broker (IQ Option / Pocket Option) no login
 *
 * INSTALAÇÃO:
 * 1. Adicionar <script src="/assets/broker-selector-patch.js"></script> no index.html
 * 2. Este script modifica o DOM após carregar para adicionar seleção de broker
 */

(function() {
    'use strict';

    console.log('[BROKER PATCH] Inicializando patch de seleção de broker...');

    // Aguardar DOM carregar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBrokerSelector);
    } else {
        initBrokerSelector();
    }

    function initBrokerSelector() {
        console.log('[BROKER PATCH] DOM carregado, procurando formulário de login...');

        // Tentar encontrar formulário de login (retry até 10 segundos)
        let attempts = 0;
        const maxAttempts = 20;

        const interval = setInterval(() => {
            attempts++;

            // Procurar pelo input de email IQ Option
            const iqEmailInput = document.querySelector('input[placeholder*="Email IQ Option"], input[placeholder*="email@iqoption"]');

            if (iqEmailInput) {
                console.log('[BROKER PATCH] Formulário de login encontrado!');
                clearInterval(interval);
                injectBrokerSelector(iqEmailInput);
            } else if (attempts >= maxAttempts) {
                console.warn('[BROKER PATCH] Formulário de login não encontrado após 10 segundos');
                clearInterval(interval);
            }
        }, 500);
    }

    function injectBrokerSelector(iqEmailInput) {
        // Verificar se já foi injetado
        if (document.getElementById('broker-selector-container')) {
            console.log('[BROKER PATCH] Seletor já injetado, abortando');
            return;
        }

        console.log('[BROKER PATCH] Injetando seletor de broker...');

        // Encontrar o container pai do formulário
        const formContainer = iqEmailInput.closest('div[class*="space-y"], div[class*="flex"], form');

        if (!formContainer) {
            console.error('[BROKER PATCH] Container do formulário não encontrado');
            return;
        }

        // Criar seletor de broker
        const brokerSelectorHTML = `
            <div id="broker-selector-container" style="margin-bottom: 1rem;">
                <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #fff; margin-bottom: 0.5rem;">
                    🏦 Selecione a Corretora
                </label>
                <select id="broker-type-select" style="
                    width: 100%;
                    padding: 0.625rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 0.5rem;
                    background: rgba(255, 255, 255, 0.05);
                    color: white;
                    font-size: 0.875rem;
                    outline: none;
                    cursor: pointer;
                ">
                    <option value="iqoption">IQ Option (Email + Senha)</option>
                    <option value="pocketoption">Pocket Option (SSID)</option>
                </select>
            </div>

            <!-- Container para campos Pocket Option (inicialmente oculto) -->
            <div id="pocketoption-fields" style="display: none; margin-bottom: 1rem;">
                <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #fff; margin-bottom: 0.5rem;">
                    🔑 SSID da Pocket Option
                </label>
                <input
                    type="text"
                    id="pocketoption-ssid-input"
                    placeholder="Cole aqui o SSID do cookie..."
                    style="
                        width: 100%;
                        padding: 0.625rem;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 0.5rem;
                        background: rgba(255, 255, 255, 0.05);
                        color: white;
                        font-size: 0.875rem;
                        outline: none;
                    "
                />
                <button
                    type="button"
                    id="show-ssid-instructions"
                    style="
                        margin-top: 0.5rem;
                        padding: 0.5rem 1rem;
                        background: rgba(59, 130, 246, 0.2);
                        color: #60a5fa;
                        border: 1px solid rgba(59, 130, 246, 0.3);
                        border-radius: 0.375rem;
                        font-size: 0.75rem;
                        cursor: pointer;
                        width: 100%;
                    "
                >
                    ❓ Como obter SSID?
                </button>

                <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #fff; margin-top: 1rem; margin-bottom: 0.5rem;">
                    Tipo de Conta
                </label>
                <select id="pocketoption-account-type" style="
                    width: 100%;
                    padding: 0.625rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 0.5rem;
                    background: rgba(255, 255, 255, 0.05);
                    color: white;
                    font-size: 0.875rem;
                    outline: none;
                ">
                    <option value="PRACTICE">💵 PRACTICE (Demo)</option>
                    <option value="REAL">💰 REAL (Dinheiro Real)</option>
                </select>
            </div>
        `;

        // Inserir seletor ANTES dos campos de email
        iqEmailInput.closest('div').insertAdjacentHTML('beforebegin', brokerSelectorHTML);

        // Encontrar containers dos campos IQ Option
        const iqEmailContainer = iqEmailInput.closest('div[class*="space-y"], div');
        const iqPasswordInput = document.querySelector('input[type="password"][placeholder*="Senha"]');
        const iqPasswordContainer = iqPasswordInput ? iqPasswordInput.closest('div[class*="space-y"], div') : null;
        const iqAccountTypeSelect = document.querySelector('select option[value*="REAL"]')?.closest('select');
        const iqAccountTypeContainer = iqAccountTypeSelect ? iqAccountTypeSelect.closest('div[class*="space-y"], div') : null;

        console.log('[BROKER PATCH] Campos IQ Option encontrados:', {
            email: !!iqEmailContainer,
            password: !!iqPasswordContainer,
            accountType: !!iqAccountTypeContainer
        });

        // Event listener para trocar broker
        const brokerSelect = document.getElementById('broker-type-select');
        const pocketFields = document.getElementById('pocketoption-fields');

        brokerSelect.addEventListener('change', (e) => {
            const selectedBroker = e.target.value;
            console.log('[BROKER PATCH] Broker selecionado:', selectedBroker);

            if (selectedBroker === 'pocketoption') {
                // Mostrar campos Pocket Option
                pocketFields.style.display = 'block';

                // Esconder campos IQ Option
                if (iqEmailContainer) iqEmailContainer.style.display = 'none';
                if (iqPasswordContainer) iqPasswordContainer.style.display = 'none';
                if (iqAccountTypeContainer) iqAccountTypeContainer.style.display = 'none';
            } else {
                // Mostrar campos IQ Option
                pocketFields.style.display = 'none';

                if (iqEmailContainer) iqEmailContainer.style.display = 'block';
                if (iqPasswordContainer) iqPasswordContainer.style.display = 'block';
                if (iqAccountTypeContainer) iqAccountTypeContainer.style.display = 'block';
            }
        });

        // Botão de instruções SSID
        document.getElementById('show-ssid-instructions').addEventListener('click', showSSIDModal);

        // Interceptar submissão do formulário
        interceptFormSubmit();

        console.log('[BROKER PATCH] Seletor de broker injetado com sucesso! ✅');
    }

    function showSSIDModal() {
        // Criar modal
        const modalHTML = `
            <div id="ssid-modal" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            ">
                <div style="
                    background: #1a1a2e;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 1rem;
                    padding: 2rem;
                    max-width: 600px;
                    max-height: 80vh;
                    overflow-y: auto;
                    color: white;
                ">
                    <h3 style="font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
                        🔑 Como obter SSID da Pocket Option
                    </h3>

                    <ol style="margin-left: 1.5rem; line-height: 1.8;">
                        <li>Abra <a href="https://pocketoption.com" target="_blank" style="color: #60a5fa;">https://pocketoption.com</a> no navegador</li>
                        <li>Faça login normalmente</li>
                        <li>Pressione <strong>F12</strong> para abrir DevTools</li>
                        <li>Vá na aba <strong>"Application"</strong> (Chrome) ou <strong>"Storage"</strong> (Firefox)</li>
                        <li>No menu lateral, expanda <strong>"Cookies"</strong></li>
                        <li>Clique em <strong>"https://pocketoption.com"</strong></li>
                        <li>Procure o cookie chamado <strong>"ssid"</strong></li>
                        <li>Copie o <strong>VALOR</strong> do cookie (string longa)</li>
                        <li>Cole aqui no campo SSID</li>
                    </ol>

                    <div style="
                        margin-top: 1.5rem;
                        padding: 1rem;
                        background: rgba(239, 68, 68, 0.1);
                        border: 1px solid rgba(239, 68, 68, 0.3);
                        border-radius: 0.5rem;
                    ">
                        <strong style="color: #f87171;">⚠️ IMPORTANTE:</strong>
                        <ul style="margin-left: 1.5rem; margin-top: 0.5rem; line-height: 1.6;">
                            <li>O SSID expira após algumas horas</li>
                            <li>Você precisará renovar quando expirar</li>
                            <li>Não compartilhe seu SSID (é como uma senha)</li>
                        </ul>
                    </div>

                    <button onclick="document.getElementById('ssid-modal').remove()" style="
                        margin-top: 1.5rem;
                        width: 100%;
                        padding: 0.75rem;
                        background: #3b82f6;
                        color: white;
                        border: none;
                        border-radius: 0.5rem;
                        font-weight: 600;
                        cursor: pointer;
                    ">
                        Entendi
                    </button>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    function interceptFormSubmit() {
        console.log('[BROKER PATCH] Interceptando submissão do formulário...');

        // Encontrar botão de submit
        const submitButton = Array.from(document.querySelectorAll('button')).find(btn =>
            btn.textContent.includes('Conectar') || btn.textContent.includes('Entrar')
        );

        if (!submitButton) {
            console.warn('[BROKER PATCH] Botão de submit não encontrado');
            return;
        }

        // Armazenar handler original
        const originalClickHandler = submitButton.onclick;

        // Substituir handler
        submitButton.onclick = async function(e) {
            e.preventDefault();
            console.log('[BROKER PATCH] Formulário submetido, processando...');

            const brokerType = document.getElementById('broker-type-select').value;

            // Construir objeto de login baseado no broker selecionado
            const loginData = {
                username: document.querySelector('input[type="text"]')?.value || 'user',
                access_token: localStorage.getItem('activation_token') || '',
                broker_type: brokerType
            };

            if (brokerType === 'iqoption') {
                const emailInput = document.querySelector('input[placeholder*="Email IQ Option"]');
                const passwordInput = document.querySelector('input[type="password"]');
                const accountTypeSelect = document.querySelector('select option[value*="REAL"]')?.closest('select');

                loginData.iqoption_email = emailInput?.value;
                loginData.iqoption_password = passwordInput?.value;
                loginData.iqoption_account_type = accountTypeSelect?.value || 'PRACTICE';
            } else if (brokerType === 'pocketoption') {
                const ssidInput = document.getElementById('pocketoption-ssid-input');
                const accountTypeSelect = document.getElementById('pocketoption-account-type');

                loginData.pocketoption_ssid = ssidInput?.value;
                loginData.pocketoption_account_type = accountTypeSelect?.value || 'PRACTICE';
            }

            console.log('[BROKER PATCH] Dados de login:', { ...loginData, iqoption_password: '***', pocketoption_ssid: loginData.pocketoption_ssid ? '***' : undefined });

            // Fazer request customizado
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(loginData)
                });

                const data = await response.json();
                console.log('[BROKER PATCH] Resposta do login:', data);

                if (data.broker_connected) {
                    console.log(`[BROKER PATCH] ✅ Conectado ao ${data.broker_type}`);

                    // Armazenar dados
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('broker_type', data.broker_type);
                    localStorage.setItem('broker_balance', data.broker_balance);

                    // Chamar handler original se existir
                    if (originalClickHandler) {
                        originalClickHandler.call(submitButton, e);
                    } else {
                        // Redirecionar manualmente
                        window.location.reload();
                    }
                } else {
                    alert(`❌ Erro ao conectar: ${data.broker_message || 'Erro desconhecido'}`);
                }
            } catch (error) {
                console.error('[BROKER PATCH] Erro no login:', error);
                alert(`❌ Erro ao conectar: ${error.message}`);
            }
        };

        console.log('[BROKER PATCH] Interceptação de formulário configurada ✅');
    }
})();
