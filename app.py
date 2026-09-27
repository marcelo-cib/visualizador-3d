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

    # Codifica cada parte separadamente para preservar as barras.
    partes_seguras = [
        parte.replace(" ", "%20")
        for parte in partes
    ]

    return "/modelos/" + "/".join(partes_seguras)


def criar_pagina_3d(codigo):
    catalogo = carregar_catalogo()
    registro = catalogo.get(codigo)

    if registro is None:
        abort(404)

    nome = registro["nome"]
    arquivo = registro["arquivo"]
    caminho_modelo = criar_url_modelo(arquivo)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{nome} - Visualizador 3D</title>

<style>
html, body {{
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #101010;
    font-family: Arial, sans-serif;
}}

#titulo {{
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 10;
    color: white;
    background: rgba(0,0,0,.65);
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 18px;
}}

#status {{
    position: fixed;
    top: 60px;
    left: 12px;
    z-index: 10;
    color: #ddd;
    background: rgba(0,0,0,.55);
    padding: 7px 10px;
    border-radius: 7px;
    font-size: 12px;
}}

#ajuda {{
    position: fixed;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    color: white;
    background: rgba(0,0,0,.65);
    padding: 9px 13px;
    border-radius: 8px;
    text-align: center;
    font-size: 13px;
}}

canvas {{
    display: block;
}}
</style>
</head>

<body>

<div id="titulo">{nome}</div>
<div id="status">Carregando modelo 3D...</div>

<div id="ajuda">
Arraste para rotacionar • Pinça para zoom • Dois dedos para mover
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

import {{ OrbitControls }}
from 'three/addons/controls/OrbitControls.js';

import {{ GLTFLoader }}
from 'three/addons/loaders/GLTFLoader.js';


const cena = new THREE.Scene();

cena.background =
    new THREE.Color(0x101010);


const camera =
    new THREE.PerspectiveCamera(
        45,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );

camera.position.set(5, 4, 7);


const renderer =
    new THREE.WebGLRenderer({{
        antialias: true
    }});

renderer.setPixelRatio(
    Math.min(window.devicePixelRatio, 2)
);

renderer.setSize(
    window.innerWidth,
    window.innerHeight
);

document.body.appendChild(
    renderer.domElement
);


const controls =
    new OrbitControls(
        camera,
        renderer.domElement
    );

controls.enableDamping = true;
controls.enablePan = true;
controls.enableZoom = true;

controls.target.set(0, 0, 0);


const luzAmbiente =
    new THREE.AmbientLight(
        0xffffff,
        1.5
    );

cena.add(luzAmbiente);


const luzDirecional =
    new THREE.DirectionalLight(
        0xffffff,
        2
    );

luzDirecional.position.set(5, 8, 6);

cena.add(luzDirecional);


const loader =
    new GLTFLoader();

const caminhoModelo =
    "{caminho_modelo}";


loader.load(
    caminhoModelo,

    function(gltf) {{

        const objeto = gltf.scene;

        const caixa =
            new THREE.Box3()
                .setFromObject(objeto);

        const tamanho =
            caixa.getSize(
                new THREE.Vector3()
            );

        const centro =
            caixa.getCenter(
                new THREE.Vector3()
            );

        const maior =
            Math.max(
                tamanho.x,
                tamanho.y,
                tamanho.z
            );


        if (maior > 0) {{

            const escala =
                4.5 / maior;

            objeto.scale.setScalar(escala);

            objeto.position.set(
                -centro.x * escala,
                -centro.y * escala,
                -centro.z * escala
            );
        }}


        cena.add(objeto);


        const caixaFinal =
            new THREE.Box3()
                .setFromObject(objeto);

        controls.target.copy(
            caixaFinal.getCenter(
                new THREE.Vector3()
            )
        );

        camera.position.set(
            5,
            3.5,
            7
        );

        controls.update();


        document.getElementById(
            "status"
        ).textContent =
            "Modelo 3D carregado.";

    }},

    undefined,

    function(erro) {{

        console.error(
            "Erro ao carregar modelo GLB:",
            erro
        );

        document.getElementById(
            "status"
        ).textContent =
            "Não foi possível carregar o modelo 3D.";
    }}
);


window.addEventListener(
    "resize",
    () => {{

        camera.aspect =
            window.innerWidth /
            window.innerHeight;

        camera.updateProjectionMatrix();

        renderer.setSize(
            window.innerWidth,
            window.innerHeight
        );
    }}
);


function animar() {{

    requestAnimationFrame(animar);

    controls.update();

    renderer.render(
        cena,
        camera
    );
}}

animar();

</script>

</body>
</html>"""


@app.route("/")
def catalogo():

    catalogo = carregar_catalogo()

    if not catalogo:
        return (
            "<h1>Catálogo vazio</h1>"
            "<p>Verifique o arquivo veiculos.json.</p>",
            500
        )

    categorias = {}

    for codigo, dados in catalogo.items():

        categoria = dados.get(
            "categoria",
            "Outros"
        )

        categorias.setdefault(
            categoria,
            []
        ).append(
            (codigo, dados)
        )


    secoes = []

    for categoria, veiculos in categorias.items():

        cards = []

        for codigo, dados in veiculos:

            cards.append(f"""
            <div class="card">

                <div class="icone">🚗</div>

                <h2>{dados["nome"]}</h2>

                <div class="categoria">
                    {dados.get("categoria", "")}
                </div>

                <p>
                    {dados.get("descricao", "")}
                </p>

                <div class="botoes">

                    <a
                        class="botao"
                        href="/objeto/{codigo}"
                    >
                        Visualizar 3D
                    </a>

                    <a
                        class="botao secundario"
                        href="/qrcode/{codigo}"
                    >
                        QR Code
                    </a>

                </div>

            </div>
            """)

        secoes.append(f"""
        <section class="categoria-secao">

            <h2 class="titulo-categoria">
                {categoria}
            </h2>

            <div class="catalogo">
                {''.join(cards)}
            </div>

        </section>
        """)


    return f"""<!DOCTYPE html>
<html lang="pt-BR">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Catálogo de Veículos 3D</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #101010;
    color: white;
}}

.cabecalho {{
    text-align: center;
    padding: 32px 16px 20px;
    background:
        linear-gradient(
            180deg,
            #1d1d1d,
            #101010
        );
}}

.cabecalho h1 {{
    margin: 0 0 8px;
    font-size: 30px;
}}

.cabecalho p {{
    margin: 0;
    color: #bdbdbd;
}}

.categoria-secao {{
    width: min(1100px, 94%);
    margin: 28px auto 0;
}}

.titulo-categoria {{
    margin: 0 0 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #333;
    color: #8ec5ff;
}}

.catalogo {{
    display: grid;
    grid-template-columns:
        repeat(
            auto-fit,
            minmax(240px, 1fr)
        );
    gap: 18px;
}}

.card {{
    background: #1c1c1c;
    border: 1px solid #333;
    border-radius: 14px;
    padding: 22px;
    box-shadow:
        0 8px 22px
        rgba(0,0,0,.25);
}}

.icone {{
    font-size: 44px;
}}

.card h2 {{
    margin: 10px 0 5px;
}}

.categoria {{
    color: #8ec5ff;
    font-size: 14px;
    margin-bottom: 10px;
}}

.card p {{
    color: #c7c7c7;
    min-height: 42px;
}}

.botoes {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 18px;
}}

.botao {{
    flex: 1;
    min-width: 105px;
    text-align: center;
    text-decoration: none;
    color: white;
    background: #2563eb;
    padding: 11px 12px;
    border-radius: 8px;
    font-weight: bold;
}}

.botao.secundario {{
    background: #444;
}}

.rodape {{
    text-align: center;
    color: #888;
    padding: 30px 15px;
    font-size: 13px;
}}

</style>

</head>

<body>

<header class="cabecalho">

<h1>
CATÁLOGO DE VEÍCULOS 3D
</h1>

<p>
Selecione uma categoria e um veículo para visualizar o modelo em 3D.
</p>

</header>

<main>

{''.join(secoes)}

</main>

<div class="rodape">
Visualizador 3D • {len(catalogo)} veículos cadastrados
</div>

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

    imagem.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype="image/png"
    )


@app.route("/modelos/<path:nome_arquivo>")
def modelo(nome_arquivo):

    return send_from_directory(
        MODELOS_DIR,
        nome_arquivo
    )


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "5000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
