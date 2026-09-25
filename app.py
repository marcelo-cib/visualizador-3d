import os
import io
from flask import Flask, Response, send_from_directory, abort
import qrcode

servidor_web = Flask(__name__)

URL_RENDER = os.environ.get(
    "URL_RENDER",
    "https://visualizador-3d-xvr4.onrender.com"
).rstrip("/")

VEICULOS = {
    "suv": {"nome": "SUV", "arquivo": "SUV.glb"},
    "car": {"nome": "Car", "arquivo": "Car.glb"},
    "car-unqqkULtRU": {"nome": "Car-unqqkULtRU", "arquivo": "Car-unqqkULtRU.glb"},
    "police-car": {"nome": "Police Car", "arquivo": "Police Car.glb"},
    "sports-car": {"nome": "Sports Car", "arquivo": "Sports Car.glb"},
    "sports-car-1mkmFkAz5v": {"nome": "Sports Car-1mkmFkAz5v", "arquivo": "Sports Car-1mkmFkAz5v.glb"},
    "taxi": {"nome": "Taxi", "arquivo": "Taxi.glb"},
}


def criar_pagina_3d(objeto):
    if objeto not in VEICULOS:
        abort(404)

    dados = VEICULOS[objeto]
    nome = dados["nome"]
    arquivo = dados["arquivo"]

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{nome} - Visualizador 3D</title>
<style>
html, body {{ margin:0; width:100%; height:100%; overflow:hidden; background:#101010; font-family:Arial,sans-serif; }}
#titulo {{ position:fixed; top:12px; left:12px; z-index:10; color:white; background:rgba(0,0,0,.65); padding:10px 14px; border-radius:8px; font-size:18px; }}
#ajuda {{ position:fixed; bottom:12px; left:50%; transform:translateX(-50%); z-index:10; color:white; background:rgba(0,0,0,.65); padding:9px 13px; border-radius:8px; text-align:center; font-size:13px; }}
#erro {{ position:fixed; top:60px; left:12px; z-index:10; color:#ff8080; background:rgba(0,0,0,.75); padding:10px; border-radius:8px; display:none; }}
canvas {{ display:block; }}
</style>
</head>
<body>
<div id="titulo">{nome}</div>
<div id="erro"></div>
<div id="ajuda">Arraste para rotacionar • Pinça para zoom • Dois dedos para mover</div>
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
cena.background = new THREE.Color(0x101010);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.01, 1000);
camera.position.set(5, 3.5, 7);

const renderer = new THREE.WebGLRenderer({{ antialias:true }});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.enablePan = true;
controls.enableZoom = true;
controls.target.set(0, 0, 0);

cena.add(new THREE.AmbientLight(0xffffff, 1.5));
const luzDirecional = new THREE.DirectionalLight(0xffffff, 2);
luzDirecional.position.set(5, 8, 6);
cena.add(luzDirecional);

const loader = new GLTFLoader();
const caminhoModelo = "/modelos/" + encodeURIComponent({arquivo!r});

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
            objeto.position.set(-centro.x * escala, -centro.y * escala, -centro.z * escala);
        }}

        cena.add(objeto);

        const caixaFinal = new THREE.Box3().setFromObject(objeto);
        controls.target.copy(caixaFinal.getCenter(new THREE.Vector3()));
        camera.position.set(5, 3.5, 7);
        controls.update();
    }},
    undefined,
    function(erro) {{
        console.error("Erro ao carregar modelo GLB:", erro);
        const elemento = document.getElementById("erro");
        elemento.textContent = "Não foi possível carregar o modelo 3D.";
        elemento.style.display = "block";
    }}
);

window.addEventListener("resize", () => {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}});

function animar() {{
    requestAnimationFrame(animar);
    controls.update();
    renderer.render(cena, camera);
}}
animar();
</script>
</body>
</html>'''


@servidor_web.route("/")
def inicio():
    links = "".join(
        f'<li><a href="/objeto/{slug}">{dados["nome"]}</a> - <a href="/qrcode/{slug}">QR</a></li>'
        for slug, dados in VEICULOS.items()
    )
    return f"""<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>Veículos 3D</title></head><body style='font-family:Arial;padding:25px'><h1>Veículos 3D</h1><ul>{links}</ul></body></html>"""


@servidor_web.route("/objeto/<nome>")
def visualizar_objeto(nome):
    if nome not in VEICULOS:
        return "Veículo não encontrado.", 404
    return criar_pagina_3d(nome)


@servidor_web.route("/qrcode/<nome>")
def fornecer_qrcode(nome):
    if nome not in VEICULOS:
        return "Veículo não encontrado.", 404

    url = f"{URL_RENDER}/objeto/{nome}"
    imagem = qrcode.make(url)
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)
    return Response(buffer.getvalue(), mimetype="image/png")


@servidor_web.route("/modelos/<path:nome_arquivo>")
def fornecer_modelo(nome_arquivo):
    caminho_modelos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelos")
    caminho_completo = os.path.join(caminho_modelos, nome_arquivo)
    if not os.path.isfile(caminho_completo):
        return "Modelo 3D não encontrado.", 404
    return send_from_directory(caminho_modelos, nome_arquivo, as_attachment=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    servidor_web.run(host="0.0.0.0", port=port, debug=False)
