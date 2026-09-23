import os
from flask import Flask, Response, send_from_directory
import qrcode
import io

servidor_web = Flask(__name__)

def criar_pagina_3d(objeto):

    nomes = {
        "cubo": "Cubo",
        "esfera": "Esfera",
        "triangulo": "Triângulo",
        "cone": "Cone",
        "suv": "SUV"
    }

    nome = nomes.get(
        objeto,
        "Objeto 3D"
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

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

<div id="ajuda">
Arraste para rotacionar • Pinça para zoom • Dois dedos para mover
</div>


<script type="importmap">

{{
    "imports": {{
        "three":
        "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",

        "three/addons/":
        "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"
    }}
}}

</script>


<script type="module">

import * as THREE from 'three';

import {{
    OrbitControls
}}
from 'three/addons/controls/OrbitControls.js';

import {{
    GLTFLoader
}}
from 'three/addons/loaders/GLTFLoader.js';


const cena = new THREE.Scene();

cena.background = new THREE.Color(
    0x101010
);


const camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth /
    window.innerHeight,
    0.1,
    1000
);


camera.position.set(
    5,
    4,
    7
);


const renderer =
new THREE.WebGLRenderer({{
    antialias: true
}});


renderer.setPixelRatio(
    Math.min(
        window.devicePixelRatio,
        2
    )
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

controls.target.set(
    0,
    0,
    0
);


const luzAmbiente =
new THREE.AmbientLight(
    0xffffff,
    1.5
);

cena.add(
    luzAmbiente
);


const luzDirecional =
new THREE.DirectionalLight(
    0xffffff,
    2
);

luzDirecional.position.set(
    5,
    8,
    6
);

cena.add(
    luzDirecional
);


const material =
new THREE.MeshStandardMaterial({{
    color: 0x4f8cff,
    roughness: 0.35,
    metalness: 0.05
}});


let objeto;


if ("{objeto}" === "cubo") {{

    objeto = new THREE.Mesh(

        new THREE.BoxGeometry(
            2.5,
            2.5,
            2.5
        ),

        material

    );

}}


if ("{objeto}" === "esfera") {{

    objeto = new THREE.Mesh(

        new THREE.SphereGeometry(
            1.5,
            48,
            32
        ),

        material

    );

}}


if ("{objeto}" === "triangulo") {{

    const forma =
    new THREE.BufferGeometry();


    const vertices =
    new Float32Array([

        -1.0, -1.25, -0.75,
         1.0, -1.25, -0.75,
         0.0,  1.25, -0.75,

        -1.0, -1.25,  0.75,
         1.0, -1.25,  0.75,
         0.0,  1.25,  0.75

    ]);


    const indices = [

        0,1,2,
        3,5,4,

        0,3,4,
        0,4,1,

        0,2,5,
        0,5,3,

        1,4,5,
        1,5,2

    ];


    forma.setAttribute(
        "position",

        new THREE.BufferAttribute(
            vertices,
            3
        )
    );


    forma.setIndex(
        indices
    );


    forma.computeVertexNormals();


    objeto =
    new THREE.Mesh(
        forma,
        material
    );

}}


if ("{objeto}" === "cone") {{

    objeto = new THREE.Mesh(

        new THREE.ConeGeometry(
            1.5,
            3.0,
            48
        ),

        material

    );

}}


if ("{objeto}" === "suv") {{

    const loader = new GLTFLoader();

    loader.load(
        "/modelos/SUV.glb",

        function (gltf) {{

            objeto = gltf.scene;

            const caixa =
            new THREE.Box3().setFromObject(
                objeto
            );

            const centro =
            caixa.getCenter(
                new THREE.Vector3()
            );

            const tamanho =
            caixa.getSize(
                new THREE.Vector3()
            );

            const maiorDimensao = Math.max(
                tamanho.x,
                tamanho.y,
                tamanho.z
            );

            if (maiorDimensao > 0) {{

                objeto.scale.setScalar(
                    4.5 / maiorDimensao
                );

            }}

            objeto.position.sub(
                centro.multiplyScalar(
                    objeto.scale.x
                )
            );

            cena.add(
                objeto
            );

            const caixaFinal =
            new THREE.Box3().setFromObject(
                objeto
            );

            controls.target.copy(
                caixaFinal.getCenter(
                    new THREE.Vector3()
                )
            );

        }},

        undefined,

        function (erro) {{

            console.error(
                "Erro ao carregar SUV.glb:",
                erro
            );

        }}
    );

}}


if (objeto) {{

    cena.add(
        objeto
    );

    if ("{objeto}" !== "suv") {{

        const arestas =
        new THREE.LineSegments(

            new THREE.EdgesGeometry(
                objeto.geometry
            ),

            new THREE.LineBasicMaterial({{
                color: 0x111111
            }})

        );

        objeto.add(
            arestas
        );

    }}

}}


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

    requestAnimationFrame(
        animar
    );

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


NOMES_OBJETOS = {
    "cubo": "Cubo",
    "esfera": "Esfera",
    "triangulo": "Triângulo",
    "cone": "Cone"
}

@servidor_web.route("/")
def inicio():
    return """
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visualizador 3D</title>
    </head>
    <body style="font-family:Arial; text-align:center; padding:30px;">
        <h1>Visualizador 3D</h1>
        <p>Escolha uma forma geométrica:</p>
        <p>
            <a href="/objeto/cubo">Cubo</a> |
            <a href="/objeto/esfera">Esfera</a> |
            <a href="/objeto/triangulo">Triângulo</a> |
            <a href="/objeto/cone">Cone</a> |\n            <a href="/objeto/suv">SUV</a>
        </p>
    </body>
    </html>
    """

@servidor_web.route("/objeto/<nome>")
def visualizar_objeto(nome):
    if nome not in NOMES_OBJETOS:
        return "Objeto não encontrado.", 404
    return criar_pagina_3d(nome)

@servidor_web.route("/modelos/<path:nome_arquivo>")
def fornecer_modelo(nome_arquivo):

    pasta_modelos = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "modelos"
    )

    caminho_arquivo = os.path.join(
        pasta_modelos,
        nome_arquivo
    )

    if not os.path.isfile(caminho_arquivo):
        return "Modelo 3D não encontrado.", 404

    return send_from_directory(
        pasta_modelos,
        nome_arquivo
    )


@servidor_web.route("/qrcode/<nome>")

def fornecer_qrcode(nome):
    if nome not in NOMES_OBJETOS:
        return "Objeto não encontrado.", 404

    # No Render, RENDER_EXTERNAL_URL é fornecida automaticamente.
    # Também permite definir URL_PUBLICA manualmente.
    url_base = os.environ.get("URL_PUBLICA") or os.environ.get(
        "RENDER_EXTERNAL_URL",
        ""
    )

    if not url_base:
        return (
            "URL pública não configurada. Defina URL_PUBLICA.",
            500
        )

    url = f"{url_base.rstrip('/')}/objeto/{nome}"

    imagem = qrcode.make(url)
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)

    return Response(buffer.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    servidor_web.run(host="0.0.0.0", port=port, debug=False)
