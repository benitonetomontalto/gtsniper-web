// Script para adicionar cache busting aos assets do Vite
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const indexPath = join(__dirname, 'dist', 'index.html');
let html = readFileSync(indexPath, 'utf-8');

const timestamp = Date.now();

// Adiciona ?v=TIMESTAMP a todos os imports de JS e CSS
html = html.replace(/(src|href)="([^"]+\.(js|css))"/g, `$1="$2?v=${timestamp}"`);

writeFileSync(indexPath, html);
console.log(`✅ Cache busting adicionado: ?v=${timestamp}`);
