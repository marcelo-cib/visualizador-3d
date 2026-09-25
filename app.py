import io
import json
import os
from html import escape
from flask import Flask, Response, abort, send_from_directory
import qrcode

app = Flask(__name__)

URL_RENDER = os.environ.get(
    "URL_RENDER",
    "https://visualizador-3d-xvr4.onrender.com"
).rstrip("/")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELOS_DIR = os.path.join(BASE_DIR, "modelos")
CATALOGO_FILE = os.path.join(BASE_DIR, "veiculos.json")


def carregar_catalogo():
    try:
        with open(CATALOGO_FILE, "r", encoding="utf-8") as arquivo:
            registros = json.load(arquivo)
        return {registro["codigo"]: registro for registro in registros}
    except Exception as erro:
        print(f"ERRO ao carregar veiculos.json: {erro}")
        return {}


def criar_pagina_3d(codigo):
    catalogo = carregar_catalogo()
    registro = catalogo.get(codigo)

    if registro is None:
        abort(404)

    nome = escape(registro.get("nome", codigo))
    categoria = escape(registro.get("categoria", "Veículo"))
    descricao = escape(registro.get("descricao", ""))
    arquivo = registro["arquivo"]
    codigo_seguro = escape(codigo)
    url_objeto = f"{URL_RENDER}/objeto/{codigo}"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{nome} • Visualizador 3D</title>
<style>
* {{ box-sizing: border-box; }}

:root {{
    --bg: #080b10;
    --panel: rgba(16, 21, 29, .92);
    --panel-soft: rgba(23, 30, 41, .88);
    --border: rgba(255,255,255,.10);
    --text: #f5f7fa;
    --muted: #a9b1bd;
    --accent: #3b82f6;
    --accent-hover: #60a5fa;
}}

html, body {{
    margin: 0;
    width: 100%;
    min-height: 100%;
    background: var(--bg);
    color: var(--text);
    font-family: Inter, Arial, sans-serif;
}}

body {{
    min-height: 100vh;
    overflow-x: hidden;
}}

.topbar {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 20;
    height: 68px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 22px;
    background: rgba(8, 11, 16, .78);
    border-bottom: 1px solid var(--border);
    backdrop-filter: blur(14px);
}}

.brand {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 1.4px;
}}

.top-actions {{
    display: flex;
    gap: 8px;
}}

.btn {{
    border: 1px solid var(--border);
    border-radius: 9px;
    padding: 10px 14px;
    color: white;
    background: rgba(255,255,255,.06);
    text-decoration: none;
    cursor: pointer;
    font-weight: 700;
    font-size: 13px;
}}

.btn:hover {{
    background: rgba(255,255,255,.12);
}}

.btn-primary {{
    background: var(--accent);
    border-color: var(--accent);
}}

.btn-primary:hover {{
    background: var(--accent-hover);
}}

.viewer {{
    position: relative;
    min-height: 100vh;
    padding-top: 68px;
}}

#canvas-container {{
    position: absolute;
    inset: 68px 0 0 0;
}}

canvas {{
    display: block;
    width: 100%;
    height: 100%;
}}

.info-panel {{
    position: fixed;
    z-index: 10;
    left: 22px;
    bottom: 22px;
    width: min(390px, calc(100vw - 44px));
    padding: 20px;
    border: 1px solid var(--border);
    border-radius: 16px;
    background: var(--panel);
    backdrop-filter: blur(16px);
    box-shadow: 0 18px 50px rgba(0,0,0,.35);
}}

.tag {{
    display: inline-block;
    margin-bottom: 9px;
    padding: 5px 9px;
    border-radius: 999px;
    background: rgba(59,130,246,.15);
    color: #8fc1ff;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .8px;
}}

.info-panel h1 {{
    margin: 0 0 8px;
    font-size: 28px;
}}

.info-panel p {{
    margin: 0 0 16px;
    color: var(--muted);
    line-height: 1.55;
    font-size: 14px;
}}

.controls-help {{
    color: #8993a1;
    font-size: 12px;
    line-height: 1.6;
}}

.loading {{
    position: fixed;
    z-index: 15;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    padding: 13px 18px;
    border-radius: 10px;
    background: rgba(0,0,0,.72);
    color: white;
    font-size: 14px;
}}

.error {{
    display: none;
    position: fixed;
    z-index: 16;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: min(420px, calc(100vw - 40px));
    padding: 22px;
    border-radius: 14px;
    background: #171b22;
    border: 1px solid #56333a;
    text-align: center;
}}

.modal {{
    display: none;
    position: fixed;
    z-index: 100;
    inset: 0;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: rgba(0,0,0,.78);
}}

.modal-card {{
    position: relative;
    width: min(390px, 100%);
    padding: 26px;
    border-radius: 18px;
    background: #121820;
    border: 1px solid var(--border);
    text-align: center;
    box-shadow: 0 25px 80px rgba(0,0,0,.55);
}}

.modal-card h2 {{
    margin: 0 0 8px;
}}

.modal-card p {{
    margin: 0 0 18px;
    color: var(--muted);
    font-size: 14px;
}}

.qr-image {{
    width: 250px;
    max-width: 80%;
    height: auto;
    background: white;
    padding: 10px;
    border-radius: 10px;
}}

.close {{
    position: absolute;
    top: 10px;
    right: 12px;
    width: 34px;
    height: 34px;
    border: 0;
    border-radius: 50%;
    color: white;
    background: rgba(255,255,255,.08);
    cursor: pointer;
    font-size: 20px;
}}

.url-text {{
    margin-top: 14px;
    color: #7f8a98;
    font-size: 11px;
    word-break: break-all;
}}

@media (max-width: 700px) {{
    .topbar {{
        padding: 0 12px;
        height: 60px;
    }}

    .brand {{
        font-size: 11px;
    }}

    .top-actions .btn {{
        padding: 8px 9px;
        font-size: 11px;
    }}

    .viewer {{
        padding-top: 60px;
    }}

    #canvas-container {{
        inset: 60px 0 0 0;
    }}

    .info-panel {{
        left: 12px;
        right: 12px;
        bottom: 12px;
        width: auto;
        padding: 15px;
    }}

    .info-panel h1 {{
        font-size: 22px;
    }}

    .info-panel p {{
        font-size: 13px;
        margin-bottom: 10px;
    }}

    .controls-help {{
        display: none;
    }}
}}
</style>
</head>
<body>

<header class="topbar">
    <a class="btn" href="/" aria-label="Voltar ao catálogo">← Catálogo</a>
    <div class="brand">VISUALIZADOR 3D</div>
    <div class="top-actions">
        <button class="btn" onclick="abrirQRCode()">📱 QR</button>
        <button class="btn btn-primary" onclick="compartilhar()">Compartilhar</button>
    </div>
</header>

<main class="viewer">
    <div id="canvas-container"></div>

    <section class="info-panel">
        <div class="tag">{categoria}</div>
        <h1>{nome}</h1>
        <p>{descricao}</p>
        <div class="controls-help">
            🖱️ Arraste para girar • Roda para zoom • Botão direito para mover<br>
            📱 No celular: arraste para girar • pinça para zoom • dois dedos para mover
        </div>
    </section>
</main>

<div id="loading" class="loading">Carregando modelo 3D...</div>

<div id="error" class="error">
    <h2>Não foi possível carregar o modelo</h2>
    <p>Verifique o arquivo GLB e tente novamente.</p>
</div>

<div id="qrModal" class="modal" onclick="fecharQRCode(event)">
    <div class="modal-card" onclick="event.stopPropagation()">
        <button class="close" onclick="fecharQRCode()">×</button>
        <h2>Ver no celular</h2>
        <p>Aponte a câmera do celular para o QR Code.</p>
        <img class="qr-image" src="/qrcode/{codigo_seguro}" alt="QR Code de {nome}">
        <div class="url-text">{escape(url_objeto)}</div>
    </div>
</div>

<script type="importmap">
{{
    "imports": {{
        "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"
    }}
}}
</script>

<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';

const cena = new THREE.Scene();
cena.background = new THREE.Color(0x080b10);

const container = document.getElementById("canvas-container");

const camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);
camera.position.set(5, 3.5, 7);

const renderer = new THREE.WebGLRenderer({{
    antialias: true,
    alpha: false
}});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight - 68);
renderer.outputColorSpace = THREE.SRGBColorSpace;
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.07;
controls.enablePan = true;
controls.enableZoom = true;
controls.rotateSpeed = 0.65;
controls.zoomSpeed = 0.9;
controls.panSpeed = 0.8;
controls.minDistance = 2;
controls.maxDistance = 30;
controls.target.set(0, 0, 0);

const ambiente = new THREE.AmbientLight(0xffffff, 1.7);
cena.add(ambiente);

const luzPrincipal = new THREE.DirectionalLight(0xffffff, 2.5);
luzPrincipal.position.set(5, 8, 6);
cena.add(luzPrincipal);

const luzPreenchimento = new THREE.DirectionalLight(0xffffff, 1.0);
luzPreenchimento.position.set(-5, 3, -4);
cena.add(luzPreenchimento);

const grid = new THREE.GridHelper(18, 18, 0x273142, 0x18202b);
grid.position.y = -2.3;
cena.add(grid);

const loader = new GLTFLoader();
const caminhoModelo = "/modelos/" + encodeURIComponent("{arquivo}");

loader.load(
    caminhoModelo,
    function(gltf) {{
        const objeto = gltf.scene;

        const caixa = new THREE.Box3().setFromObject(objeto);
        const tamanho = caixa.getSize(new THREE.Vector3());
        const centro = caixa.getCenter(new THREE.Vector3());
        const maior = Math.max(tamanho.x, tamanho.y, tamanho.z);

        if (maior > 0) {{
            const escala = 4.5 / maior;
            objeto.scale.setScalar(escala);
            objeto.position.set(
                -centro.x * escala,
                -centro.y * escala,
                -centro.z * escala
            );
        }}

        cena.add(objeto);

        const caixaFinal = new THREE.Box3().setFromObject(objeto);
        const centroFinal = caixaFinal.getCenter(new THREE.Vector3());
        controls.target.copy(centroFinal);

        const tamanhoFinal = caixaFinal.getSize(new THREE.Vector3());
        const maiorFinal = Math.max(
            tamanhoFinal.x,
            tamanhoFinal.y,
            tamanhoFinal.z
        );

        const distancia = Math.max(maiorFinal * 1.65, 6);
        camera.position.set(distancia, distancia * 0.65, distancia);
        controls.update();

        document.getElementById("loading").style.display = "none";
    }},
    undefined,
    function(erro) {{
        console.error("Erro ao carregar modelo GLB:", erro);
        document.getElementById("loading").style.display = "none";
        document.getElementById("error").style.display = "block";
    }}
);

function redimensionar() {{
    const altura = window.innerWidth <= 700
        ? window.innerHeight - 60
        : window.innerHeight - 68;

    camera.aspect = window.innerWidth / Math.max(altura, 1);
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, altura);
}}

window.addEventListener("resize", redimensionar);
redimensionar();

function animar() {{
    requestAnimationFrame(animar);
    controls.update();
    renderer.render(cena, camera);
}}

animar();

window.abrirQRCode = function() {{
    document.getElementById("qrModal").style.display = "flex";
}};

window.fecharQRCode = function(event) {{
    if (!event || event.target.id === "qrModal") {{
        document.getElementById("qrModal").style.display = "none";
    }}
}};

window.compartilhar = async function() {{
    const dados = {{
        title: "{escape(nome)} • Visualizador 3D",
        text: "Confira este veículo em 3D.",
        url: window.location.href
    }};

    try {{
        if (navigator.share) {{
            await navigator.share(dados);
        }} else {{
            await navigator.clipboard.writeText(window.location.href);
            alert("Link copiado para a área de transferência.");
        }}
    }} catch (erro) {{
        console.log("Compartilhamento cancelado ou indisponível.");
    }}
}};
</script>
</body>
</html>"""


@app.route("/")
def catalogo():
    catalogo = carregar_catalogo()

    cards = []
    for codigo, dados in catalogo.items():
        nome = escape(dados.get("nome", codigo))
        categoria = escape(dados.get("categoria", "Veículo"))
        descricao = escape(dados.get("descricao", ""))
        codigo_seguro = escape(codigo)

        cards.append(f"""
        <article class="card">
            <div class="card-preview">
                <div class="preview-icon">3D</div>
            </div>

            <div class="card-content">
                <span class="categoria">{categoria}</span>
                <h2>{nome}</h2>
                <p>{descricao}</p>

                <div class="botoes">
                    <a class="botao botao-principal"
                       href="/objeto/{codigo_seguro}">
                        Visualizar 3D
                    </a>

                    <button class="botao botao-qr"
                            onclick="abrirQRCode('{codigo_seguro}', '{nome}')">
                        📱 QR
                    </button>
                </div>
            </div>
        </article>
        """)

    if not cards:
        conteudo = """
        <div class="vazio">
            <h2>Nenhum veículo cadastrado</h2>
            <p>O catálogo ainda não possui veículos disponíveis.</p>
        </div>
        """
    else:
        conteudo = "".join(cards)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3D Garage • Catálogo de Veículos</title>

<style>
* {{ box-sizing: border-box; }}

:root {{
    --bg: #070a0f;
    --panel: #10151d;
    --panel-hover: #151c26;
    --border: rgba(255,255,255,.09);
    --text: #f5f7fa;
    --muted: #9ca6b3;
    --accent: #3b82f6;
    --accent-hover: #60a5fa;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    margin: 0;
    min-height: 100vh;
    background:
        radial-gradient(circle at 50% -10%, rgba(59,130,246,.15), transparent 35%),
        var(--bg);
    color: var(--text);
    font-family: Inter, Arial, sans-serif;
}}

.header {{
    padding: 54px 20px 35px;
    text-align: center;
}}

.logo {{
    display: inline-block;
    margin-bottom: 14px;
    color: #8fc1ff;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 2px;
}}

.header h1 {{
    margin: 0;
    font-size: clamp(32px, 6vw, 58px);
    line-height: 1.05;
}}

.header p {{
    max-width: 650px;
    margin: 18px auto 0;
    color: var(--muted);
    line-height: 1.6;
    font-size: 16px;
}}

.catalogo {{
    width: min(1180px, calc(100% - 32px));
    margin: 10px auto 60px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(265px, 1fr));
    gap: 20px;
}}

.card {{
    overflow: hidden;
    background: linear-gradient(180deg, #111720, #0d1219);
    border: 1px solid var(--border);
    border-radius: 18px;
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}}

.card:hover {{
    transform: translateY(-4px);
    border-color: rgba(59,130,246,.45);
    box-shadow: 0 18px 45px rgba(0,0,0,.28);
}}

.card-preview {{
    height: 190px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        radial-gradient(circle, rgba(59,130,246,.18), transparent 55%),
        #0a0e14;
    border-bottom: 1px solid var(--border);
}}

.preview-icon {{
    width: 88px;
    height: 88px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(96,165,250,.35);
    border-radius: 22px;
    color: #8fc1ff;
    background: rgba(59,130,246,.08);
    font-weight: 900;
    font-size: 25px;
    letter-spacing: 1px;
}}

.card-content {{
    padding: 20px;
}}

.categoria {{
    color: #8fc1ff;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .9px;
    text-transform: uppercase;
}}

.card h2 {{
    margin: 7px 0 8px;
    font-size: 23px;
}}

.card p {{
    min-height: 48px;
    margin: 0;
    color: var(--muted);
    line-height: 1.5;
    font-size: 14px;
}}

.botoes {{
    display: flex;
    gap: 9px;
    margin-top: 18px;
}}

.botao {{
    border: 0;
    border-radius: 9px;
    padding: 11px 13px;
    font-size: 13px;
    font-weight: 800;
    cursor: pointer;
    text-decoration: none;
    text-align: center;
}}

.botao-principal {{
    flex: 1;
    color: white;
    background: var(--accent);
}}

.botao-principal:hover {{
    background: var(--accent-hover);
}}

.botao-qr {{
    min-width: 72px;
    color: white;
    background: rgba(255,255,255,.08);
    border: 1px solid var(--border);
}}

.botao-qr:hover {{
    background: rgba(255,255,255,.14);
}}

.rodape {{
    padding: 0 20px 35px;
    text-align: center;
    color: #687383;
    font-size: 12px;
}}

.vazio {{
    grid-column: 1 / -1;
    padding: 60px 20px;
    border: 1px solid var(--border);
    border-radius: 18px;
    text-align: center;
    background: var(--panel);
}}

.vazio p {{
    color: var(--muted);
}}

.modal {{
    display: none;
    position: fixed;
    z-index: 100;
    inset: 0;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: rgba(0,0,0,.8);
}}

.modal-card {{
    position: relative;
    width: min(390px, 100%);
    padding: 26px;
    border: 1px solid var(--border);
    border-radius: 18px;
    background: #121820;
    text-align: center;
    box-shadow: 0 25px 80px rgba(0,0,0,.55);
}}

.modal-card h2 {{
    margin: 0 0 7px;
}}

.modal-card p {{
    margin: 0 0 18px;
    color: var(--muted);
    font-size: 14px;
}}

.qr-image {{
    width: 245px;
    max-width: 82%;
    padding: 10px;
    border-radius: 10px;
    background: white;
}}

.close {{
    position: absolute;
    top: 10px;
    right: 12px;
    width: 34px;
    height: 34px;
    border: 0;
    border-radius: 50%;
    color: white;
    background: rgba(255,255,255,.08);
    cursor: pointer;
    font-size: 20px;
}}

.url-text {{
    margin-top: 13px;
    color: #717c8a;
    font-size: 10px;
    word-break: break-all;
}}

@media (max-width: 600px) {{
    .header {{
        padding: 40px 18px 25px;
    }}

    .header p {{
        font-size: 14px;
    }}

    .catalogo {{
        width: min(100% - 24px, 520px);
        grid-template-columns: 1fr;
        gap: 14px;
    }}

    .card-preview {{
        height: 160px;
    }}
}}
</style>
</head>

<body>

<header class="header">
    <div class="logo">3D GARAGE</div>
    <h1>Catálogo de Veículos 3D</h1>
    <p>
        Explore os veículos, visualize cada modelo em 3D e,
        quando quiser, escaneie o QR Code para continuar no seu celular.
    </p>
</header>

<main class="catalogo">
    {conteudo}
</main>

<footer class="rodape">
    Visualizador 3D • {len(catalogo)} veículos cadastrados
</footer>

<div id="qrModal" class="modal" onclick="fecharQRCode(event)">
    <div class="modal-card" onclick="event.stopPropagation()">
        <button class="close" onclick="fecharQRCode()">×</button>
        <h2 id="qrTitulo">Ver no celular</h2>
        <p>Aponte a câmera do celular para o QR Code.</p>
        <img id="qrImagem" class="qr-image" src="" alt="QR Code">
        <div id="qrUrl" class="url-text"></div>
    </div>
</div>

<script>
function abrirQRCode(codigo, nome) {{
    const url = window.location.origin + "/objeto/" + encodeURIComponent(codigo);

    document.getElementById("qrTitulo").textContent = "Ver " + nome + " no celular";
    document.getElementById("qrImagem").src =
        "/qrcode/" + encodeURIComponent(codigo);
    document.getElementById("qrImagem").alt = "QR Code de " + nome;
    document.getElementById("qrUrl").textContent = url;

    document.getElementById("qrModal").style.display = "flex";
}}

function fecharQRCode(event) {{
    if (!event || event.target.id === "qrModal") {{
        document.getElementById("qrModal").style.display = "none";
    }}
}}

document.addEventListener("keydown", function(event) {{
    if (event.key === "Escape") {{
        fecharQRCode();
    }}
}});
</script>

</body>
</html>"""


@app.route("/objeto/<codigo>")
def objeto(codigo):
    return criar_pagina_3d(codigo)


@app.route("/qrcode/<codigo>")
def qrcode_veiculo(codigo):
    if codigo not in carregar_catalogo():
        abort(404)

    url = f"{URL_RENDER}/objeto/{codigo}"
    imagem = qrcode.make(url)
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)
    return Response(buffer.getvalue(), mimetype="image/png")


@app.route("/modelos/<path:nome_arquivo>")
def modelo(nome_arquivo):
    return send_from_directory(MODELOS_DIR, nome_arquivo)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
