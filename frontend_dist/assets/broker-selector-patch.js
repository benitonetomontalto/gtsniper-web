/**
 * BROKER SELECTOR PATCH V3 - IQ Option + Binomo
 * Ambos usam EMAIL + SENHA (sem SSID!)
 */

(function() {
    'use strict';

    console.log('[BROKER PATCH V3] Inicializando (IQ Option + Binomo)...');

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        console.log('[BROKER PATCH V3] DOM carregado');

        let attempts = 0;
        const maxAttempts = 20;

        const interval = setInterval(() => {
            attempts++;

            const iqEmailInput = document.querySelector('input[placeholder*="Email IQ Option"], input[placeholder*="email@iqoption"]');

            if (iqEmailInput) {
                console.log('[BROKER PATCH V3] Formulário encontrado!');
                clearInterval(interval);
                injectBrokerSelector(iqEmailInput);
            } else if (attempts >= maxAttempts) {
                console.warn('[BROKER PATCH V3] Formulário não encontrado');
                clearInterval(interval);
            }
        }, 500);
    }

    function injectBrokerSelector(iqEmailInput) {
        if (document.getElementById('broker-selector-v3')) {
            return;
        }

        console.log('[BROKER PATCH V3] Injetando seletor...');

        const formContainer = iqEmailInput.closest('div[class*="space-y"], div[class*="flex"], form');

        if (!formContainer) {
            console.error('[BROKER PATCH V3] Container não encontrado');
            return;
        }

        // Criar seletor de broker
        const selectorHTML = `
            <div id="broker-selector-v3" style="margin-bottom: 1rem;">
                <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #fff; margin-bottom: 0.5rem;">
                    🏦 Selecione a Corretora
                </label>
                <select id="broker-type-v3" style="
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
                    <option value="iqoption">IQ Option</option>
                    <option value="binomo">Binomo</option>
                </select>
            </div>
        `;

        iqEmailInput.closest('div').insertAdjacentHTML('beforebegin', selectorHTML);

        // Atualizar placeholders baseado no broker
        updatePlaceholders('iqoption'); // Default

        // Event: troca de broker
        const brokerSelect = document.getElementById('broker-type-v3');

        brokerSelect.addEventListener('change', (e) => {
            const broker = e.target.value;
            console.log('[BROKER PATCH V3] Broker selecionado:', broker);

            // Salvar escolha
            localStorage.setItem('selected_broker', broker);

            // Atualizar placeholders
            updatePlaceholders(broker);
        });

        // Interceptar fetch para adicionar broker_type
        enhanceFetchWithBrokerType();

        console.log('[BROKER PATCH V3] ✅ Seletor injetado!');
    }

    function updatePlaceholders(broker) {
        // Atualizar placeholders dos campos
        const emailInput = document.querySelector('input[placeholder*="Email"], input[placeholder*="email"]');
        const passwordInput = document.querySelector('input[type="password"]');

        if (broker === 'binomo') {
            if (emailInput) emailInput.placeholder = 'Email Binomo';
            if (passwordInput) passwordInput.placeholder = 'Senha Binomo';
        } else {
            // IQ Option (default)
            if (emailInput) emailInput.placeholder = 'Email IQ Option';
            if (passwordInput) passwordInput.placeholder = 'Senha IQ Option';
        }
    }

    function enhanceFetchWithBrokerType() {
        // Interceptar fetch globalmente
        const originalFetch = window.fetch;

        window.fetch = async function(...args) {
            const [url, options = {}] = args;

            // Se for request de login
            if (url && url.includes('/login')) {
                console.log('[BROKER PATCH V3] Interceptando request de login');

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

                // Renomear campos baseado no broker
                if (broker === 'binomo') {
                    // Binomo usa binomo_email e binomo_password
                    if (body.iqoption_email) {
                        body.binomo_email = body.iqoption_email;
                        delete body.iqoption_email;
                    }
                    if (body.iqoption_password) {
                        body.binomo_password = body.iqoption_password;
                        delete body.iqoption_password;
                    }
                    if (body.iqoption_account_type) {
                        body.binomo_account_type = body.iqoption_account_type;
                        delete body.iqoption_account_type;
                    }
                }
                // Se for IQ Option, manter como está (iqoption_email, iqoption_password)

                console.log('[BROKER PATCH V3] Body modificado:', {
                    ...body,
                    iqoption_password: body.iqoption_password ? '***' : undefined,
                    binomo_password: body.binomo_password ? '***' : undefined
                });

                // Atualizar options
                options.body = JSON.stringify(body);
            }

            return originalFetch.apply(this, [url, options]);
        };

        console.log('[BROKER PATCH V3] Fetch interceptado');
    }
})();
