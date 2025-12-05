/**
 * BROKER SELECTOR PATCH V2
 * NÃO intercepta o formulário, apenas adiciona campos ao request existente
 */

(function() {
    'use strict';

    console.log('[BROKER PATCH V2] Inicializando...');

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        console.log('[BROKER PATCH V2] DOM carregado');

        let attempts = 0;
        const maxAttempts = 20;

        const interval = setInterval(() => {
            attempts++;

            const iqEmailInput = document.querySelector('input[placeholder*="Email IQ Option"], input[placeholder*="email@iqoption"]');

            if (iqEmailInput) {
                console.log('[BROKER PATCH V2] Formulário encontrado!');
                clearInterval(interval);
                injectBrokerSelector(iqEmailInput);
            } else if (attempts >= maxAttempts) {
                console.warn('[BROKER PATCH V2] Formulário não encontrado');
                clearInterval(interval);
            }
        }, 500);
    }

    function injectBrokerSelector(iqEmailInput) {
        if (document.getElementById('broker-selector-v2')) {
            return;
        }

        console.log('[BROKER PATCH V2] Injetando seletor...');

        const formContainer = iqEmailInput.closest('div[class*="space-y"], div[class*="flex"], form');

        if (!formContainer) {
            console.error('[BROKER PATCH V2] Container não encontrado');
            return;
        }

        // Criar seletor
        const selectorHTML = `
            <div id="broker-selector-v2" style="margin-bottom: 1rem;">
                <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #fff; margin-bottom: 0.5rem;">
                    🏦 Selecione a Corretora
                </label>
                <select id="broker-type-v2" style="
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

            <div id="pocketoption-fields-v2" style="display: none; margin-bottom: 1rem;">
                <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #fff; margin-bottom: 0.5rem;">
                    🔑 SSID da Pocket Option
                </label>
                <input
                    type="text"
                    id="pocketoption-ssid-v2"
                    placeholder="Cole o SSID aqui..."
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
                    id="ssid-help-v2"
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
                <select id="pocketoption-account-v2" style="
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

        iqEmailInput.closest('div').insertAdjacentHTML('beforebegin', selectorHTML);

        // Campos IQ Option
        const iqEmailContainer = iqEmailInput.closest('div[class*="space-y"], div');
        const iqPasswordInput = document.querySelector('input[type="password"][placeholder*="Senha"]');
        const iqPasswordContainer = iqPasswordInput ? iqPasswordInput.closest('div[class*="space-y"], div') : null;
        const iqAccountTypeSelect = document.querySelector('select option[value*="REAL"]')?.closest('select');
        const iqAccountTypeContainer = iqAccountTypeSelect ? iqAccountTypeSelect.closest('div[class*="space-y"], div') : null;

        // Event: troca de broker
        const brokerSelect = document.getElementById('broker-type-v2');
        const pocketFields = document.getElementById('pocketoption-fields-v2');

        brokerSelect.addEventListener('change', (e) => {
            const broker = e.target.value;
            console.log('[BROKER PATCH V2] Broker:', broker);

            // Armazenar escolha
            localStorage.setItem('selected_broker', broker);

            if (broker === 'pocketoption') {
                pocketFields.style.display = 'block';
                if (iqEmailContainer) iqEmailContainer.style.display = 'none';
                if (iqPasswordContainer) iqPasswordContainer.style.display = 'none';
                if (iqAccountTypeContainer) iqAccountTypeContainer.style.display = 'none';
            } else {
                pocketFields.style.display = 'none';
                if (iqEmailContainer) iqEmailContainer.style.display = 'block';
                if (iqPasswordContainer) iqPasswordContainer.style.display = 'block';
                if (iqAccountTypeContainer) iqAccountTypeContainer.style.display = 'block';
            }
        });

        // Event: modal SSID
        document.getElementById('ssid-help-v2').addEventListener('click', showModal);

        // IMPORTANTE: NÃO interceptar o submit
        // Em vez disso, usar MutationObserver para injetar dados no request
        enhanceFormData();

        console.log('[BROKER PATCH V2] ✅ Seletor injetado!');
    }

    function showModal() {
        const modal = `
            <div id="ssid-modal-v2" style="
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
            " onclick="if(event.target.id==='ssid-modal-v2') this.remove()">
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
                        🔑 Como obter SSID
                    </h3>
                    <ol style="margin-left: 1.5rem; line-height: 1.8;">
                        <li>Abra <a href="https://pocketoption.com" target="_blank" style="color: #60a5fa;">pocketoption.com</a></li>
                        <li>Faça login</li>
                        <li>Pressione <strong>F12</strong></li>
                        <li>Aba <strong>Application</strong> (Chrome) ou <strong>Storage</strong> (Firefox)</li>
                        <li>Expanda <strong>Cookies</strong></li>
                        <li>Clique em <strong>https://pocketoption.com</strong></li>
                        <li>Procure cookie <strong>ssid</strong></li>
                        <li>Copie o <strong>VALOR</strong></li>
                        <li>Cole acima</li>
                    </ol>
                    <button onclick="this.closest('#ssid-modal-v2').remove()" style="
                        margin-top: 1.5rem;
                        width: 100%;
                        padding: 0.75rem;
                        background: #3b82f6;
                        color: white;
                        border: none;
                        border-radius: 0.5rem;
                        font-weight: 600;
                        cursor: pointer;
                    ">Entendi</button>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);
    }

    function enhanceFormData() {
        // Interceptar fetch/xhr globalmente
        const originalFetch = window.fetch;

        window.fetch = async function(...args) {
            const [url, options = {}] = args;

            // Se for request de login
            if (url && url.includes('/login')) {
                console.log('[BROKER PATCH V2] Interceptando request de login');

                const broker = localStorage.getItem('selected_broker') || 'iqoption';

                // Parse body existente
                let body = {};
                if (options.body) {
                    try {
                        body = JSON.parse(options.body);
                    } catch(e) {
                        body = {};
                    }
                }

                // Adicionar broker_type
                body.broker_type = broker;

                // Adicionar credenciais Pocket Option
                if (broker === 'pocketoption') {
                    const ssid = document.getElementById('pocketoption-ssid-v2')?.value;
                    const account = document.getElementById('pocketoption-account-v2')?.value;

                    body.pocketoption_ssid = ssid;
                    body.pocketoption_account_type = account || 'PRACTICE';

                    // Remover campos IQ Option
                    delete body.iqoption_email;
                    delete body.iqoption_password;
                }

                console.log('[BROKER PATCH V2] Body modificado:', { ...body, iqoption_password: '***', pocketoption_ssid: body.pocketoption_ssid ? '***' : undefined });

                // Atualizar options
                options.body = JSON.stringify(body);
            }

            return originalFetch.apply(this, [url, options]);
        };

        console.log('[BROKER PATCH V2] Fetch interceptado');
    }
})();
