import io
import json
import os
from flask import Flask, Response, abort, send_from_directory
import qrcode

app = Flask(__name__)

# URL pública utilizada pelos QR Codes.
URL_RENDER = os.environ.get(
    "URL_RENDER",
    "https://visualizador-3d-xvr4.onrender.com"
).rstrip("/")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELOS_DIR = os.path.join(BASE_DIR, "modelos")
CATALOGO_FILE = os.path.join(BASE_DIR, "veiculos.json")


# ---------------------------------------------------------------------------
# Backend auxiliar (intacto)
# ---------------------------------------------------------------------------

def carregar_catalogo():
    """Carrega o catálogo centralizado no veiculos.json."""
    try:
        with open(CATALOGO_FILE, "r", encoding="utf-8") as arquivo:
            registros = json.load(arquivo)

        return {
            registro["codigo"]: registro
            for registro in registros
        }

    except Exception as erro:
        print(f"ERRO ao carregar veiculos.json: {erro}")
        return {}


def criar_url_modelo(arquivo):
    """
    Monta uma URL para um GLB dentro de uma subpasta de modelos.

    Exemplo:
        classico/carro.glb
    vira:
        /modelos/classico/carro.glb
    """
    partes = arquivo.replace("\\", "/").strip("/").split("/")

    partes_seguras = [
        parte.replace(" ", "%20")
        for parte in partes
    ]

    return "/modelos/" + "/".join(partes_seguras)


# ---------------------------------------------------------------------------
# CSS compartilhado (usado tanto pelo catálogo quanto pela página standalone)
# ---------------------------------------------------------------------------

CSS_BASE = """
* { box-sizing: border-box; }

:root {
    --bg-deep: #08090d;
    --bg-dark: #0e1016;
    --bg-card: #14161d;
    --bg-elev: #1a1d26;
    --border: #262a36;
    --border-soft: #1e222c;
    --text: #f1f3f7;
    --text-muted: #8f96a8;
    --text-dim: #5d6478;
    --gold: #d4b476;
    --gold-bright: #e8cb8d;
    --gold-dim: #9a8253;
    --danger: #ef4444;
    --radius: 14px;
    --radius-sm: 10px;
    --shadow-lg: 0 24px 60px rgba(0, 0, 0, 0.55);
    --shadow-md: 0 10px 30px rgba(0, 0, 0, 0.35);
}

html, body {
    margin: 0;
    padding: 0;
    background: var(--bg-deep);
    color: var(--text);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
    line-height: 1.5;
}

a { color: inherit; }

button { font-family: inherit; }
"""

CSS_CATALOGO = """
body {
    background:
        radial-gradient(circle at 20% -10%, rgba(212, 180, 118, 0.06), transparent 45%),
        radial-gradient(circle at 90% 10%, rgba(59, 130, 246, 0.05), transparent 40%),
        var(--bg-deep);
    min-height: 100vh;
}

/* ============ HEADER ============ */
.header {
    position: sticky;
    top: 0;
    z-index: 50;
    background: rgba(8, 9, 13, 0.75);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-bottom: 1px solid var(--border-soft);
}

.header-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 24px;
    height: 68px;
    display: flex;
    align-items: center;
    gap: 32px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    letter-spacing: -0.01em;
    font-size: 17px;
    color: var(--text);
    text-decoration: none;
    flex-shrink: 0;
}

.brand-mark {
    width: 32px;
    height: 32px;
    border-radius: 9px;
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dim) 100%);
    display: grid;
    place-items: center;
    font-size: 16px;
    box-shadow: 0 4px 14px rgba(212, 180, 118, 0.28);
}

.brand-name {
    background: linear-gradient(180deg, #fff 0%, #c9cdd8 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ============ MENU ============ */
.menu {
    display: flex;
    align-items: center;
    gap: 4px;
    flex: 1;
    flex-wrap: nowrap;
    overflow-x: auto;
    scrollbar-width: none;
}
.menu::-webkit-scrollbar { display: none; }

.menu-item {
    position: relative;
    flex-shrink: 0;
}

.menu-trigger {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border-radius: 9px;
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all .2s ease;
    white-space: nowrap;
}

.menu-trigger:hover,
.menu-item.aberto .menu-trigger {
    background: var(--bg-elev);
    color: var(--text);
}

.menu-trigger .chev {
    font-size: 9px;
    transition: transform .2s ease;
    opacity: .6;
}

.menu-item.aberto .menu-trigger .chev {
    transform: rotate(180deg);
}

.submenu {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    min-width: 240px;
    max-height: 340px;
    overflow-y: auto;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    box-shadow: var(--shadow-lg);
    padding: 6px;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-6px);
    transition: all .18s ease;
    z-index: 60;
}

.menu-item.aberto .submenu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.submenu a {
    display: block;
    padding: 9px 12px;
    border-radius: 8px;
    color: var(--text-muted);
    text-decoration: none;
    font-size: 13.5px;
    transition: all .15s ease;
}

.submenu a:hover {
    background: var(--bg-elev);
    color: var(--gold-bright);
}

/* ============ HERO ============ */
.hero {
    max-width: 1280px;
    margin: 0 auto;
    padding: 72px 24px 40px;
    text-align: center;
}

.hero h1 {
    margin: 0 0 16px;
    font-size: clamp(30px, 5vw, 52px);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.08;
}

.hero h1 .accent {
    background: linear-gradient(135deg, var(--gold-bright), var(--gold-dim));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    margin: 0 auto;
    max-width: 620px;
    color: var(--text-muted);
    font-size: 16px;
}

/* ============ FILTROS ============ */
.filtros {
    max-width: 1280px;
    margin: 0 auto;
    padding: 8px 24px 24px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
}

.filtro {
    padding: 8px 18px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-muted);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all .2s ease;
}

.filtro:hover {
    border-color: var(--gold-dim);
    color: var(--gold-bright);
}

.filtro.ativo {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dim) 100%);
    border-color: transparent;
    color: #0b0c10;
    font-weight: 600;
    box-shadow: 0 6px 20px rgba(212, 180, 118, 0.25);
}

/* ============ SEÇÕES ============ */
.categoria-secao {
    max-width: 1280px;
    margin: 40px auto 0;
    padding: 0 24px;
    scroll-margin-top: 90px;
}

.categoria-secao[hidden] { display: none; }

.categoria-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
}

.categoria-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: var(--text);
    text-transform: uppercase;
}

.categoria-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border), transparent);
}

.categoria-count {
    font-size: 12px;
    color: var(--text-dim);
    font-weight: 500;
}

/* ============ GRID ============ */
.catalogo {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}

/* ============ CARD ============ */
.card {
    background: linear-gradient(180deg, var(--bg-card) 0%, #101219 100%);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
    cursor: pointer;
    position: relative;
}

.card:hover {
    transform: translateY(-4px);
    border-color: rgba(212, 180, 118, 0.4);
    box-shadow: var(--shadow-md), 0 0 0 1px rgba(212, 180, 118, 0.08);
}

.card-thumb {
    position: relative;
    width: 100%;
    aspect-ratio: 4 / 3;
    background:
        radial-gradient(circle at 50% 40%, #1c2030 0%, #0c0e14 75%);
    border-bottom: 1px solid var(--border-soft);
    overflow: hidden;
}

.card-thumb canvas {
    width: 100% !important;
    height: 100% !important;
    display: block;
}

.card-thumb .thumb-loader {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    color: var(--text-dim);
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    pointer-events: none;
    transition: opacity .3s ease;
}

.card-thumb.pronto .thumb-loader { opacity: 0; }

.thumb-badge {
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(8, 9, 13, 0.7);
    backdrop-filter: blur(8px);
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--gold-bright);
    border: 1px solid rgba(212, 180, 118, 0.25);
}

.card-body {
    padding: 18px 20px 20px;
    display: flex;
    flex-direction: column;
    flex: 1;
}

.card-body h3 {
    margin: 0 0 6px;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--text);
}

.card-body .desc {
    margin: 0;
    font-size: 13.5px;
    color: var(--text-muted);
    line-height: 1.55;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    min-height: 42px;
}

.card-actions {
    display: flex;
    gap: 8px;
    margin-top: 16px;
}

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 10px 14px;
    border-radius: 9px;
    border: none;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    transition: all .2s ease;
    white-space: nowrap;
}

.btn-gold {
    flex: 1;
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dim) 100%);
    color: #0b0c10;
    box-shadow: 0 4px 14px rgba(212, 180, 118, 0.2);
}

.btn-gold:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(212, 180, 118, 0.35);
}

.btn-ghost {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-muted);
}

.btn-ghost:hover {
    border-color: var(--gold-dim);
    color: var(--gold-bright);
}

/* ============ FOOTER ============ */
.rodape {
    max-width: 1280px;
    margin: 64px auto 0;
    padding: 32px 24px 40px;
    border-top: 1px solid var(--border-soft);
    text-align: center;
    color: var(--text-dim);
    font-size: 13px;
}

.rodape strong { color: var(--text-muted); font-weight: 500; }

/* ============ MODAL 3D ============ */
.modal-3d {
    position: fixed;
    inset: 0;
    z-index: 200;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background: rgba(4, 5, 8, 0.78);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    opacity: 0;
    transition: opacity .25s ease;
}

.modal-3d.aberto {
    display: flex;
    opacity: 1;
}

.modal-inner {
    position: relative;
    width: min(1280px, 100%);
    height: min(820px, 92vh);
    background: var(--bg-dark);
    border: 1px solid var(--border);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: var(--shadow-lg);
    display: flex;
    flex-direction: column;
    transform: scale(0.96);
    transition: transform .25s ease;
}

.modal-3d.aberto .modal-inner { transform: scale(1); }

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 14px 20px;
    border-bottom: 1px solid var(--border-soft);
    background: rgba(8, 9, 13, 0.6);
    backdrop-filter: blur(10px);
    flex-shrink: 0;
}

.modal-titulo {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}

.modal-titulo h2 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.modal-tag {
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gold-bright);
    background: rgba(212, 180, 118, 0.1);
    border: 1px solid rgba(212, 180, 118, 0.25);
    padding: 3px 9px;
    border-radius: 999px;
    flex-shrink: 0;
}

.modal-close {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 16px;
    display: grid;
    place-items: center;
    transition: all .2s ease;
    flex-shrink: 0;
}

.modal-close:hover {
    background: rgba(239, 68, 68, 0.12);
    border-color: rgba(239, 68, 68, 0.4);
    color: #ff8080;
}

.modal-content {
    flex: 1;
    display: flex;
    min-height: 0;
    position: relative;
}

.modal-canvas-wrap {
    flex: 1;
    position: relative;
    background:
        radial-gradient(circle at 50% 45%, #171a24 0%, #08090d 78%);
    min-width: 0;
}

.modal-canvas-wrap canvas {
    display: block;
    width: 100% !important;
    height: 100% !important;
}

.modal-loader {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    pointer-events: none;
    transition: opacity .35s ease;
}

.modal-loader.escondido { opacity: 0; }

.spinner {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    border: 2px solid rgba(212, 180, 118, 0.18);
    border-top-color: var(--gold);
    animation: spin 0.9s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.modal-hint {
    position: absolute;
    bottom: 14px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(8, 9, 13, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    padding: 7px 14px;
    border-radius: 999px;
    font-size: 11.5px;
    color: var(--text-muted);
    letter-spacing: 0.02em;
    white-space: nowrap;
    pointer-events: none;
}

.modal-side {
    width: 320px;
    padding: 24px;
    border-left: 1px solid var(--border-soft);
    background: var(--bg-card);
    overflow-y: auto;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.modal-side .label {
    font-size: 10.5px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-dim);
    font-weight: 600;
    margin-bottom: 6px;
}

.modal-side .desc-completa {
    font-size: 14px;
    color: var(--text-muted);
    line-height: 1.65;
    margin: 0;
}

.modal-side .acoes {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: auto;
    padding-top: 8px;
}

.modal-side .btn { width: 100%; }

.toast {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%) translateY(20px);
    background: var(--bg-elev);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 11px 20px;
    border-radius: 10px;
    font-size: 13px;
    box-shadow: var(--shadow-lg);
    opacity: 0;
    pointer-events: none;
    transition: all .25s ease;
    z-index: 300;
}

.toast.visivel {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}

/* ============ RESPONSIVO ============ */
@media (max-width: 900px) {
    .modal-side { width: 260px; padding: 18px; }
}

@media (max-width: 768px) {
    .header-inner { height: auto; padding: 12px 16px; flex-wrap: wrap; gap: 10px; }
    .menu { order: 3; width: 100%; flex-wrap: wrap; overflow: visible; }
    .menu-trigger { padding: 7px 12px; font-size: 13px; }
    .submenu { position: static; box-shadow: none; border-radius: 8px; margin-top: 4px; }
    .menu-item.aberto .submenu { max-height: 400px; }
    .hero { padding: 48px 16px 24px; }
    .filtros { padding: 8px 16px 20px; }
    .categoria-secao { padding: 0 16px; }
    .catalogo { grid-template-columns: 1fr; gap: 16px; }
    .modal-3d { padding: 0; }
    .modal-inner { width: 100%; height: 100%; border-radius: 0; border: none; }
    .modal-content { flex-direction: column; }
    .modal-side {
        width: 100%;
        max-height: 42vh;
        border-left: none;
        border-top: 1px solid var(--border-soft);
        padding: 18px;
    }
    .modal-hint { font-size: 10.5px; padding: 6px 11px; bottom: 10px; }
}
"""


# ---------------------------------------------------------------------------
# JS compartilhado: loader Three.js reutilizável
# ---------------------------------------------------------------------------

JS_THREE_LOADER = """
async function carregarModelo({
    container,
    caminho,
    interativo = true,
    aoCarregar = null,
    aoErro = null
}) {
    const { loadThreeDeps, ajustarObjetoNaCena } = window.__AUTO3D__;
    const THREE = await loadThreeDeps();

    const largura = container.clientWidth || 300;
    const altura = container.clientHeight || 200;

    const cena = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(38, largura / altura, 0.1, 1000);
    camera.position.set(5, 3.4, 7);

    const renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        preserveDrawingBuffer: true
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(largura, altura, false);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';
    renderer.domElement.style.display = 'block';

    container.appendChild(renderer.domElement);

    cena.add(new THREE.AmbientLight(0xffffff, 1.1));

    const hemi = new THREE.HemisphereLight(0xffffff, 0x1a1d26, 0.9);
    cena.add(hemi);

    const dir = new THREE.DirectionalLight(0xffffff, 2.2);
    dir.position.set(6, 9, 7);
    cena.add(dir);

    const dir2 = new THREE.DirectionalLight(0xd4b476, 0.9);
    dir2.position.set(-6, 4, -5);
    cena.add(dir2);

    let controls = null;

    if (interativo) {
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.enablePan = true;
        controls.minDistance = 2;
        controls.maxDistance = 30;
    }

    const estado = {
        animId: null,
        renderer,
        cena,
        camera,
        controls,
        modelo: null,
        dispose() {
            if (this.animId) cancelAnimationFrame(this.animId);
            if (this.controls && this.controls.dispose) this.controls.dispose();
            if (this.modelo) {
                this.modelo.traverse((o) => {
                    if (o.geometry) o.geometry.dispose();
                    if (o.material) {
                        const mats = Array.isArray(o.material) ? o.material : [o.material];
                        mats.forEach((m) => {
                            for (const k in m) {
                                const v = m[k];
                                if (v && v.isTexture) v.dispose();
                            }
                            m.dispose && m.dispose();
                        });
                    }
                });
            }
            this.renderer.dispose();
            if (this.renderer.domElement.parentNode) {
                this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
            }
        }
    };

    const loader = new THREE.GLTFLoader();

    loader.load(
        caminho,
        (gltf) => {
            const objeto = gltf.scene;
            ajustarObjetoNaCena(THREE, objeto, cena, camera, controls);
            estado.modelo = objeto;

            const loop = () => {
                estado.animId = requestAnimationFrame(loop);
                if (controls) controls.update();
                renderer.render(cena, camera);
            };
            loop();

            if (aoCarregar) aoCarregar(estado);
        },
        undefined,
        (erro) => {
            console.error('Erro ao carregar GLB:', erro);
            if (aoErro) aoErro(erro);
        }
    );

    return estado;
}
"""

JS_THREE_CORE = """
window.__AUTO3D__ = (() => {
    let threePromise = null;

    function loadThreeDeps() {
        if (!threePromise) {
            threePromise = (async () => {
                const [THREE, { OrbitControls }, { GLTFLoader }] = await Promise.all([
                    import('three'),
                    import('three/addons/controls/OrbitControls.js'),
                    import('three/addons/loaders/GLTFLoader.js')
                ]);
                THREE.OrbitControls = OrbitControls;
                THREE.GLTFLoader = GLTFLoader;
                return THREE;
            })();
        }
        return threePromise;
    }

    function ajustarObjetoNaCena(THREE, objeto, cena, camera, controls) {
        const caixa = new THREE.Box3().setFromObject(objeto);
        const tamanho = caixa.getSize(new THREE.Vector3());
        const centro = caixa.getCenter(new THREE.Vector3());
        const maior = Math.max(tamanho.x, tamanho.y, tamanho.z);

        if (maior > 0) {
            const escala = 4.5 / maior;
            objeto.scale.setScalar(escala);
            objeto.position.set(
                -centro.x * escala,
                -centro.y * escala,
                -centro.z * escala
            );
        }

        cena.add(objeto);

        const caixaFinal = new THREE.Box3().setFromObject(objeto);
        const centroFinal = caixaFinal.getCenter(new THREE.Vector3());

        if (controls) {
            controls.target.copy(centroFinal);
            controls.update();
        }

        camera.lookAt(centroFinal);
    }

    return { loadThreeDeps, ajustarObjetoNaCena };
})();
"""


# ---------------------------------------------------------------------------
# Página principal (catálogo) — HTML completo
# ---------------------------------------------------------------------------

def _montar_catalogo_html(catalogo):
    # Agrupa por categoria preservando ordem de inserção
    categorias = {}
    for codigo, dados in catalogo.items():
        categoria = dados.get("categoria", "Outros")
        categorias.setdefault(categoria, []).append((codigo, dados))

    nomes_categorias = list(categorias.keys())

    # ----- Menu principal + submenus -----
    itens_menu = []
    for categoria in nomes_categorias:
        veiculos = categorias[categoria]
        sublinks = "".join(
            f'<a href="#{codigo}" data-codigo="{codigo}">{dados["nome"]}</a>'
            for codigo, dados in veiculos
        )
        itens_menu.append(f"""
            <div class="menu-item" data-categoria-menu="{categoria}">
                <button class="menu-trigger" type="button">
                    <span>{categoria}</span>
                    <span class="chev">▼</span>
                </button>
                <div class="submenu">{sublinks}</div>
            </div>
        """)

    menu_html = "".join(itens_menu)

    # ----- Filtros pill -----
    botoes_filtro = ['<button class="filtro ativo" data-filtro="__todos__">Todos</button>']
    for categoria in nomes_categorias:
        botoes_filtro.append(
            f'<button class="filtro" data-filtro="{categoria}">{categoria}</button>'
        )
    filtros_html = "".join(botoes_filtro)

    # ----- Seções + cards -----
    secoes = []
    for categoria, veiculos in categorias.items():
        cards = []
        for codigo, dados in veiculos:
            nome = dados["nome"]
            descricao = dados.get("descricao", "")
            arquivo = dados["arquivo"]
            caminho_modelo = criar_url_modelo(arquivo)

            cards.append(f"""
            <article
                class="card"
                id="{codigo}"
                data-codigo="{codigo}"
                data-categoria="{categoria}"
                data-nome="{nome}"
                data-descricao="{descricao}"
                data-modelo="{caminho_modelo}"
                tabindex="0"
            >
                <div class="card-thumb" data-thumb>
                    <div class="thumb-loader">Carregando</div>
                    <span class="thumb-badge">{categoria}</span>
                </div>
                <div class="card-body">
                    <h3>{nome}</h3>
                    <p class="desc">{descricao}</p>
                    <div class="card-actions">
                        <button
                            class="btn btn-gold"
                            type="button"
                            data-abrir-modal
                        >
                            Ver em 3D
                        </button>
                        <a
                            class="btn btn-ghost"
                            href="/qrcode/{codigo}"
                            target="_blank"
                            rel="noopener"
                        >
                            QR Code
                        </a>
                    </div>
                </div>
            </article>
            """)

        secoes.append(f"""
        <section
            class="categoria-secao"
            data-categoria-secao="{categoria}"
        >
            <div class="categoria-header">
                <h2>{categoria}</h2>
                <span class="categoria-count">{len(veiculos)} modelo{'s' if len(veiculos) > 1 else ''}</span>
            </div>
            <div class="catalogo">
                {''.join(cards)}
            </div>
        </section>
        """)

    secoes_html = "".join(secoes)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Catálogo de Veículos 3D</title>
<meta name="description" content="Explore veículos em 3D — rotacione, aproxime e descubra cada detalhe.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS_BASE}{CSS_CATALOGO}</style>
<script type="importmap">
{{
  "imports": {{
    "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"
  }}
}}
</script>
</head>
<body>

<header class="header">
    <div class="header-inner">
        <a class="brand" href="/">
            <span class="brand-mark">◆</span>
            <span class="brand-name">AUTO<span style="color:var(--gold-bright)">3D</span></span>
        </a>
        <nav class="menu" id="menu-principal">
            {menu_html}
        </nav>
    </div>
</header>

<section class="hero">
    <h1>Catálogo de <span class="accent">Veículos 3D</span></h1>
    <p>Explore cada modelo em tempo real. Rotacione, aproxime e descubra cada detalhe antes de decidir.</p>
</section>

<div class="filtros" id="filtros">