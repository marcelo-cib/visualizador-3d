from direct.showbase.ShowBase import ShowBase

from direct.task import Task

from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Point3,
    Vec2,
    Vec3,
    Geom,
    GeomNode,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomTriangles,
    LineSegs,
    Texture,
    PNMImage,
    Filename
)

import math
import socket
import threading
import io
import os
import tempfile
import qrcode

from flask import Flask, Response

from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectLabel,
    DirectEntry
)

from direct.gui.OnscreenImage import OnscreenImage


# ==========================================================
# SERVIDOR WEB PARA O VISUALIZADOR 3D DO CELULAR
# ==========================================================

servidor_web = Flask(__name__)

# ==========================================================
# URL PÚBLICA DO RENDER
# ==========================================================
# Substitua pelo endereço HTTPS fornecido pelo Render.
URL_RENDER = os.environ.get(
    "URL_RENDER",
    "https://visualizador-3d-xvr4.onrender.com"
).rstrip("/")


# ==========================================================
# OBTÉM IP DA REDE LOCAL
# ==========================================================

def obter_ip_rede():
    """Obtém o IP da máquina na rede local."""

    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.connect(
            ("8.8.8.8", 80)
        )

        ip = sock.getsockname()[0]

        sock.close()

        return ip

    except Exception:
        return "127.0.0.1"


# ==========================================================
# PÁGINA 3D PARA O CELULAR
# ==========================================================

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


# ==========================================================
# ROTA DO OBJETO 3D
# ==========================================================

@servidor_web.route("/objeto/<nome>")
def visualizar_objeto(nome):

    if nome not in (
        "cubo",
        "esfera",
        "triangulo",
        "cone",
        "suv"
    ):

        return (
            "Objeto não encontrado.",
            404
        )

    return criar_pagina_3d(
        nome
    )


# ==========================================================
# ROTA PARA QR CODE
# ==========================================================

@servidor_web.route("/qrcode/<nome>")
def fornecer_qrcode(nome):

    if nome not in (
        "cubo",
        "esfera",
        "triangulo",
        "cone",
        "suv"
    ):

        return (
            "Objeto não encontrado.",
            404
        )


    url = f"{URL_RENDER}/objeto/{nome}"


    imagem = qrcode.make(
        url
    )


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


# ==========================================================
# INICIAR SERVIDOR WEB
# ==========================================================

def iniciar_servidor_web():

    servidor_web.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )


# ==========================================================
# APLICAÇÃO 3D
# ==========================================================

class Aplicacao3D(ShowBase):


    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    def __init__(self):

        super().__init__()


        # ==================================================
        # SERVIDOR WEB
        # ==================================================

        self.ip_rede = obter_ip_rede()


        self.thread_servidor = threading.Thread(
            target=iniciar_servidor_web,
            daemon=True
        )


        self.thread_servidor.start()


        print("=" * 60)

        print(
            "SERVIDOR 3D PARA CELULAR"
        )

        print(
            f"IP da máquina: {self.ip_rede}"
        )

        print(
            f"URL pública dos QR Codes: {URL_RENDER}"
        )

        print(
            "Porta local: 5000"
        )

        print("=" * 60)


        # ==================================================
        # CONFIGURAÇÕES GERAIS
        # ==================================================

        self.disableMouse()


        # ==================================================
        # BIBLIOTECA DE OBJETOS
        # ==================================================

        self.biblioteca_objetos = {

            "cubo": "Cubo",

            "esfera": "Esfera",

            "triangulo": "Triângulo",

            "cone": "Cone",

            "suv": "SUV"

        }


        self.modelo_atual = None

        self.objeto_atual = None


        # ==================================================
        # CÂMERA
        # ==================================================

        self.alvo = Point3(
            0,
            0,
            0
        )


        self.yaw = 0.0

        self.pitch = 20.0

        self.distancia = 12.0


        # ==================================================
        # VALORES INICIAIS
        # ==================================================

        self.yaw_inicial = 0.0

        self.pitch_inicial = 20.0

        self.distancia_inicial = 12.0


        self.alvo_inicial = Point3(
            0,
            0,
            0
        )


        # ==================================================
        # LIMITES
        # ==================================================

        self.pitch_minimo = -89.0

        self.pitch_maximo = 89.0


        self.distancia_minima = 3.0

        self.distancia_maxima = 50.0


        # ==================================================
        # SENSIBILIDADES
        # ==================================================

        self.sensibilidade_rotacao = 180.0

        self.sensibilidade_pan = 1.0

        self.sensibilidade_zoom = 1.0


        # ==================================================
        # CONTROLE DO MOUSE
        # ==================================================

        self.mouse_rotacionando = False

        self.mouse_movendo = False

        self.mouse_anterior = None


        # ==================================================
        # QR CODE
        # ==================================================

        self.qr_texture = None

        self.qr_imagem = None

        self.qr_arquivo_temp = None


        # ==================================================
        # LUZES
        # ==================================================

        self.configurar_luzes()


        # ==================================================
        # OBJETO INICIAL
        # ==================================================

        self.carregar_objeto(
            "cubo"
        )


        # ==================================================
        # INTERFACE PRINCIPAL
        # ==================================================

        self.criar_interface_biblioteca()


        # ==================================================
        # EVENTOS DO MOUSE
        # ==================================================

        self.accept(
            "mouse1",
            self._mouse_down,
            ["rotacao"]
        )


        self.accept(
            "mouse1-up",
            self._mouse_up,
            ["rotacao"]
        )


        self.accept(
            "mouse3",
            self._mouse_down,
            ["pan"]
        )


        self.accept(
            "mouse3-up",
            self._mouse_up,
            ["pan"]
        )


        self.accept(
            "mouse2",
            self._mouse_down,
            ["pan"]
        )


        self.accept(
            "mouse2-up",
            self._mouse_up,
            ["pan"]
        )


        # ==================================================
        # ZOOM
        # ==================================================

        self.accept(
            "wheel_up",
            self._zoom,
            [1]
        )


        self.accept(
            "wheel_down",
            self._zoom,
            [-1]
        )


        # ==================================================
        # ATALHOS
        # ==================================================

        self.accept(
            "c",
            self._carregar_cubo
        )

        self.accept(
            "C",
            self._carregar_cubo
        )


        self.accept(
            "e",
            self._carregar_esfera
        )

        self.accept(
            "E",
            self._carregar_esfera
        )


        self.accept(
            "t",
            self._carregar_triangulo
        )

        self.accept(
            "T",
            self._carregar_triangulo
        )


        self.accept(
            "o",
            self._carregar_cone
        )

        self.accept(
            "O",
            self._carregar_cone
        )


        # ==================================================
        # RESET
        # ==================================================

        self.accept(
            "r",
            self._resetar_camera
        )

        self.accept(
            "R",
            self._resetar_camera
        )


        # ==================================================
        # CÂMERA INICIAL
        # ==================================================

        self._atualizar_camera()


        # ==================================================
        # TASK DO MOUSE
        # ==================================================

        self.taskMgr.add(
            self._task_mouse,
            "task_mouse"
        )


    # ======================================================
    # INTERFACE DA BIBLIOTECA + QR CODE
    # ======================================================

    def criar_interface_biblioteca(self):


        # --------------------------------------------------
        # PAINEL PRINCIPAL
        # --------------------------------------------------

        self.painel_biblioteca = DirectFrame(

            parent=self.aspect2d,

            frameColor=(
                0.06,
                0.06,
                0.06,
                0.92
            ),

            frameSize=(
                -0.58,
                0.58,
                -0.48,
                0.48
            ),

            pos=(
                -0.76,
                0,
                0.48
            )
        )


        # --------------------------------------------------
        # TÍTULO
        # --------------------------------------------------

        self.titulo_biblioteca = DirectLabel(

            parent=self.painel_biblioteca,

            text="BIBLIOTECA 3D",

            scale=0.045,

            text_fg=(
                1,
                1,
                1,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            pos=(
                -0.22,
                0,
                0.38
            )
        )


        # --------------------------------------------------
        # CABEÇALHO QR
        # --------------------------------------------------

        self.label_qr_coluna = DirectLabel(

            parent=self.painel_biblioteca,

            text="QR",

            scale=0.035,

            text_fg=(
                0.7,
                0.9,
                1,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            pos=(
                0.39,
                0,
                0.38
            )
        )


        # ==================================================
        # CUBO
        # ==================================================

        self.botao_cubo = DirectButton(

            parent=self.painel_biblioteca,

            text="Cubo",

            scale=0.043,

            frameSize=(
                -2.5,
                2.5,
                -0.42,
                0.42
            ),

            pos=(
                -0.20,
                0,
                0.22
            ),

            command=self.carregar_objeto,

            extraArgs=[
                "cubo"
            ]
        )


        self.botao_qr_cubo = DirectButton(

            parent=self.painel_biblioteca,

            text="QR",

            scale=0.035,

            frameSize=(
                -0.85,
                0.85,
                -0.48,
                0.48
            ),

            pos=(
                0.40,
                0,
                0.22
            ),

            command=self.mostrar_qrcode,

            extraArgs=[
                "cubo"
            ]
        )


        # ==================================================
        # ESFERA
        # ==================================================

        self.botao_esfera = DirectButton(

            parent=self.painel_biblioteca,

            text="Esfera",

            scale=0.043,

            frameSize=(
                -2.5,
                2.5,
                -0.42,
                0.42
            ),

            pos=(
                -0.20,
                0,
                0.07
            ),

            command=self.carregar_objeto,

            extraArgs=[
                "esfera"
            ]
        )


        self.botao_qr_esfera = DirectButton(

            parent=self.painel_biblioteca,

            text="QR",

            scale=0.035,

            frameSize=(
                -0.85,
                0.85,
                -0.48,
                0.48
            ),

            pos=(
                0.40,
                0,
                0.07
            ),

            command=self.mostrar_qrcode,

            extraArgs=[
                "esfera"
            ]
        )


        # ==================================================
        # TRIÂNGULO
        # ==================================================

        self.botao_triangulo = DirectButton(

            parent=self.painel_biblioteca,

            text="Triângulo",

            scale=0.043,

            frameSize=(
                -2.5,
                2.5,
                -0.42,
                0.42
            ),

            pos=(
                -0.20,
                0,
                -0.08
            ),

            command=self.carregar_objeto,

            extraArgs=[
                "triangulo"
            ]
        )


        self.botao_qr_triangulo = DirectButton(

            parent=self.painel_biblioteca,

            text="QR",

            scale=0.035,

            frameSize=(
                -0.85,
                0.85,
                -0.48,
                0.48
            ),

            pos=(
                0.40,
                0,
                -0.08
            ),

            command=self.mostrar_qrcode,

            extraArgs=[
                "triangulo"
            ]
        )


        # ==================================================
        # CONE
        # ==================================================

        self.botao_cone = DirectButton(

            parent=self.painel_biblioteca,

            text="Cone",

            scale=0.043,

            frameSize=(
                -2.5,
                2.5,
                -0.42,
                0.42
            ),

            pos=(
                -0.20,
                0,
                -0.23
            ),

            command=self.carregar_objeto,

            extraArgs=[
                "cone"
            ]
        )


        self.botao_qr_cone = DirectButton(

            parent=self.painel_biblioteca,

            text="QR",

            scale=0.035,

            frameSize=(
                -0.85,
                0.85,
                -0.48,
                0.48
            ),

            pos=(
                0.40,
                0,
                -0.23
            ),

            command=self.mostrar_qrcode,

            extraArgs=[
                "cone"
            ]
        )


        # ==================================================
        # SUV
        # ==================================================

        self.botao_suv = DirectButton(

            parent=self.painel_biblioteca,

            text="SUV",

            scale=0.043,

            frameSize=(
                -2.5,
                2.5,
                -0.42,
                0.42
            ),

            pos=(
                -0.20,
                0,
                -0.38
            ),

            command=self.carregar_objeto,

            extraArgs=[
                "suv"
            ]
        )


        self.botao_qr_suv = DirectButton(

            parent=self.painel_biblioteca,

            text="QR",

            scale=0.035,

            frameSize=(
                -0.85,
                0.85,
                -0.48,
                0.48
            ),

            pos=(
                0.40,
                0,
                -0.38
            ),

            command=self.mostrar_qrcode,

            extraArgs=[
                "suv"
            ]
        )


        # --------------------------------------------------
        # OBJETO ATUAL
        # --------------------------------------------------

        self.objeto_selecionado_label = DirectLabel(

            parent=self.painel_biblioteca,

            text=(
                "Objeto atual: "
                +
                self.biblioteca_objetos[
                    self.objeto_atual
                ]
            ),

            scale=0.029,

            text_fg=(
                0.75,
                0.75,
                0.75,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            pos=(
                0,
                0,
                -0.50
            )
        )


        # ==================================================
        # PAINEL DO QR CODE
        # ==================================================

        self.criar_painel_qrcode()


    # ======================================================
    # CRIA PAINEL DO QR CODE
    # ======================================================

    def criar_painel_qrcode(self):


        # --------------------------------------------------
        # PAINEL
        # --------------------------------------------------

        self.painel_qrcode = DirectFrame(

            parent=self.aspect2d,

            frameColor=(
                0.04,
                0.04,
                0.04,
                0.97
            ),

            frameSize=(
                -0.42,
                0.42,
                -0.48,
                0.48
            ),

            pos=(
                -0.05,
                0,
                0.02
            )
        )


        # --------------------------------------------------
        # TÍTULO
        # --------------------------------------------------

        self.titulo_qrcode = DirectLabel(

            parent=self.painel_qrcode,

            text="QR CODE",

            scale=0.045,

            text_fg=(
                1,
                1,
                1,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            pos=(
                0,
                0,
                0.40
            )
        )


        # --------------------------------------------------
        # NOME DO OBJETO
        # --------------------------------------------------

        self.qr_nome = DirectLabel(

            parent=self.painel_qrcode,

            text="",

            scale=0.038,

            text_fg=(
                0.75,
                0.9,
                1,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            pos=(
                0,
                0,
                0.31
            )
        )


        # --------------------------------------------------
        # TEXTO INICIAL
        # --------------------------------------------------

        self.qr_instrucao = DirectLabel(

            parent=self.painel_qrcode,

            text="Selecione um QR Code",

            scale=0.028,

            text_fg=(
                0.65,
                0.65,
                0.65,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            pos=(
                0,
                0,
                0.20
            )
        )


        # --------------------------------------------------
        # BOTÃO FECHAR
        # --------------------------------------------------

        self.botao_fechar_qr = DirectButton(

            parent=self.painel_qrcode,

            text="X",

            scale=0.035,

            frameSize=(
                -0.7,
                0.7,
                -0.7,
                0.7
            ),

            pos=(
                0.34,
                0,
                0.40
            ),

            command=self.fechar_qrcode
        )


        # --------------------------------------------------
        # ESCONDE O PAINEL INICIALMENTE
        # --------------------------------------------------

        self.painel_qrcode.hide()


    # ======================================================
    # MOSTRAR QR CODE
    # ======================================================

    def mostrar_qrcode(self, nome):

        if nome not in self.biblioteca_objetos:
            return


        # --------------------------------------------------
        # URL
        # --------------------------------------------------

        # O QR Code aponta para o visualizador público hospedado no Render.
        url = f"{URL_RENDER}/objeto/{nome}"


        print()

        print("=" * 60)

        print(
            f"QR CODE: "
            f"{self.biblioteca_objetos[nome]}"
        )

        print(
            f"URL: {url}"
        )

        print("=" * 60)


        # --------------------------------------------------
        # MOSTRA PAINEL
        # --------------------------------------------------

        self.painel_qrcode.show()


        # --------------------------------------------------
        # ATUALIZA NOME
        # --------------------------------------------------

        self.qr_nome["text"] = (

            self.biblioteca_objetos[nome]

        )


        self.qr_instrucao["text"] = (

            "Aponte a câmera do celular para o QR Code"

        )


        # --------------------------------------------------
        # GERA QR CODE
        # --------------------------------------------------

        try:

            qr = qrcode.QRCode(

                version=None,

                error_correction=
                qrcode.constants.ERROR_CORRECT_M,

                box_size=10,

                border=4

            )


            qr.add_data(
                url
            )


            qr.make(
                fit=True
            )


            imagem_pil = qr.make_image(

                fill_color="black",

                back_color="white"

            ).convert("RGB")


            # --------------------------------------------------
            # DIMENSÕES DA IMAGEM
            # --------------------------------------------------

            largura, altura = imagem_pil.size


            # --------------------------------------------------
            # CRIA PNMIMAGE
            # --------------------------------------------------

            imagem_pnm = PNMImage(

                largura,

                altura,

                3

            )


            # --------------------------------------------------
            # PIXELS DA IMAGEM PIL
            # --------------------------------------------------

            pixels = imagem_pil.load()


            # --------------------------------------------------
            # CONVERTE PIL PARA PNMIMAGE
            # --------------------------------------------------

            for y in range(altura):

                for x in range(largura):

                    r, g, b = pixels[x, y]


                    imagem_pnm.setXel(

                        x,

                        altura - y - 1,

                        r / 255.0,

                        g / 255.0,

                        b / 255.0

                    )


            # --------------------------------------------------
            # CRIA TEXTURA PANDA3D
            # --------------------------------------------------

            self.qr_texture = Texture(
                "qr_code"
            )


            self.qr_texture.load(
                imagem_pnm
            )


            # --------------------------------------------------
            # REMOVE IMAGEM ANTIGA
            # --------------------------------------------------

            if self.qr_imagem is not None:

                self.qr_imagem.destroy()

                self.qr_imagem = None


            # --------------------------------------------------
            # MOSTRA QR CODE NA INTERFACE
            # --------------------------------------------------

            self.qr_imagem = OnscreenImage(

                parent=self.painel_qrcode,

                image=self.qr_texture,

                pos=(

                    0,

                    0,

                    -0.02

                ),

                scale=(

                    0.29,

                    1,

                    0.29

                )

            )


            # --------------------------------------------------
            # GARANTE QUE A IMAGEM FIQUE ACIMA DO PAINEL
            # --------------------------------------------------

            self.qr_imagem.setBin(

                "gui-popup",

                0

            )


            print(
                "QR Code carregado na interface."
            )


        except Exception as erro:

            print()

            print(
                "ERRO AO GERAR QR CODE:"
            )

            print(
                type(erro).__name__,
                "-",
                erro
            )

            print()


    # ======================================================
    # FECHAR QR CODE
    # ======================================================

    def fechar_qrcode(self):

        if self.qr_imagem is not None:

            self.qr_imagem.destroy()

            self.qr_imagem = None


        self.painel_qrcode.hide()


    # ======================================================
    # CONFIGURAR LUZES
    # ======================================================

    def configurar_luzes(self):


        # --------------------------------------------------
        # LUZ AMBIENTE
        # --------------------------------------------------

        luz_ambiente = AmbientLight(
            "luz_ambiente"
        )


        luz_ambiente.setColor(
            (
                0.35,
                0.35,
                0.35,
                1
            )
        )


        objeto_luz_ambiente = (

            self.render.attachNewNode(
                luz_ambiente
            )

        )


        self.render.setLight(
            objeto_luz_ambiente
        )


        # --------------------------------------------------
        # LUZ DIRECIONAL
        # --------------------------------------------------

        luz_direcional = DirectionalLight(
            "luz_direcional"
        )


        luz_direcional.setColor(
            (
                0.9,
                0.9,
                0.9,
                1
            )
        )


        objeto_luz_direcional = (

            self.render.attachNewNode(
                luz_direcional
            )

        )


        objeto_luz_direcional.setHpr(
            -45,
            -45,
            0
        )


        self.render.setLight(
            objeto_luz_direcional
        )


    # ======================================================
    # CARREGAR OBJETO
    # ======================================================

    def carregar_objeto(self, nome):

        if nome not in self.biblioteca_objetos:

            print(
                "Objeto não encontrado:",
                nome
            )

            return


        # --------------------------------------------------
        # REMOVE OBJETO ANTERIOR
        # --------------------------------------------------

        self.remover_objeto_atual()


        # --------------------------------------------------
        # CRIA OBJETO
        # --------------------------------------------------

        if nome == "cubo":

            self.modelo_atual = (
                self.criar_cubo()
            )


        elif nome == "esfera":

            self.modelo_atual = (
                self.criar_esfera()
            )


        elif nome == "triangulo":

            self.modelo_atual = (
                self.criar_triangulo()
            )


        elif nome == "cone":

            self.modelo_atual = (
                self.criar_cone()
            )


        elif nome == "suv":

            self.modelo_atual = (
                self.criar_suv()
            )


        # --------------------------------------------------
        # COLOCA NA CENA
        # --------------------------------------------------

        if self.modelo_atual is not None:

            self.modelo_atual.reparentTo(
                self.render
            )


            self.modelo_atual.setPos(
                0,
                0,
                0
            )


            self.modelo_atual.setScale(
                2
            )


            self.objeto_atual = nome


            # --------------------------------------------------
            # ATUALIZA INTERFACE
            # --------------------------------------------------

            if hasattr(
                self,
                "objeto_selecionado_label"
            ):

                self.objeto_selecionado_label[
                    "text"
                ] = (

                    "Objeto atual: "

                    +

                    self.biblioteca_objetos[
                        nome
                    ]

                )


            print(
                "Objeto carregado:",
                self.biblioteca_objetos[
                    nome
                ]
            )


    # ======================================================
    # REMOVER OBJETO
    # ======================================================

    def remover_objeto_atual(self):

        if self.modelo_atual is not None:

            self.modelo_atual.removeNode()

            self.modelo_atual = None

            self.objeto_atual = None


    # ======================================================
    # CRIAR SUV
    # ======================================================

    def criar_suv(self):

        try:

            caminho_suv = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "SUV.glb"
            )

            if not os.path.isfile(caminho_suv):
                print(
                    "Arquivo SUV.glb não encontrado em:",
                    caminho_suv
                )
                return None

            # Converte o caminho do Windows para o formato aceito
            # corretamente pelo Panda3D/Assimp.
            arquivo_suv = Filename.fromOsSpecific(
                caminho_suv
            )

            suv = self.loader.loadModel(
                arquivo_suv
            )

            if suv.isEmpty():
                print(
                    "Erro ao carregar SUV.glb: o modelo foi encontrado, "
                    "mas o Panda3D não conseguiu carregá-lo."
                )
                return None

            # Ajusta o SUV para ficar com tamanho semelhante
            # às formas geométricas da biblioteca.
            suv.setScale(2.5)
            suv.setPos(0, 0, 0)

            return suv

        except Exception as erro:

            print(
                "Erro ao carregar SUV.glb:",
                erro
            )

            return None


    # ======================================================
    # CRIAR CUBO
    # ======================================================

    def criar_cubo(self):

        cubo = self.loader.loadModel(
            "models/box"
        )

        return cubo


    # ======================================================
    # CRIAR ESFERA
    # ======================================================

    def criar_esfera(self):

        raio = 1.0

        segmentos = 32

        aneis = 16


        formato = (
            GeomVertexFormat.getV3n3()
        )


        dados = GeomVertexData(

            "esfera",

            formato,

            Geom.UHStatic

        )


        dados.setNumRows(

            (aneis + 1)
            *
            segmentos

        )


        vertices = GeomVertexWriter(

            dados,

            "vertex"

        )


        normais = GeomVertexWriter(

            dados,

            "normal"

        )


        # --------------------------------------------------
        # VÉRTICES
        # --------------------------------------------------

        for i in range(
            aneis + 1
        ):

            phi = (

                math.pi
                *
                i
                /
                aneis

            )


            z = (

                raio
                *
                math.cos(phi)

            )


            raio_horizontal = (

                raio
                *
                math.sin(phi)

            )


            for j in range(
                segmentos
            ):

                theta = (

                    2
                    *
                    math.pi
                    *
                    j
                    /
                    segmentos

                )


                x = (

                    raio_horizontal
                    *
                    math.cos(theta)

                )


                y = (

                    raio_horizontal
                    *
                    math.sin(theta)

                )


                vertices.addData3f(

                    x,
                    y,
                    z

                )


                comprimento = math.sqrt(

                    x * x
                    +
                    y * y
                    +
                    z * z

                )


                if comprimento != 0:

                    nx = (

                        x /
                        comprimento

                    )

                    ny = (

                        y /
                        comprimento

                    )

                    nz = (

                        z /
                        comprimento

                    )

                else:

                    nx = 0

                    ny = 0

                    nz = 1


                normais.addData3f(

                    nx,
                    ny,
                    nz

                )


        # --------------------------------------------------
        # TRIÂNGULOS
        # --------------------------------------------------

        primitivas = GeomTriangles(

            Geom.UHStatic

        )


        for i in range(
            aneis
        ):

            for j in range(
                segmentos
            ):

                atual = (

                    i
                    *
                    segmentos
                    +
                    j

                )


                proximo = (

                    i
                    *
                    segmentos
                    +
                    (
                        (j + 1)
                        %
                        segmentos
                    )

                )


                abaixo = (

                    (i + 1)
                    *
                    segmentos
                    +
                    j

                )


                abaixo_proximo = (

                    (i + 1)
                    *
                    segmentos
                    +
                    (
                        (j + 1)
                        %
                        segmentos
                    )

                )


                primitivas.addVertices(

                    atual,
                    abaixo,
                    proximo

                )


                primitivas.addVertices(

                    proximo,
                    abaixo,
                    abaixo_proximo

                )


        # --------------------------------------------------
        # GEOMETRIA
        # --------------------------------------------------

        geom = Geom(
            dados
        )


        geom.addPrimitive(
            primitivas
        )


        node = GeomNode(
            "esfera"
        )


        node.addGeom(
            geom
        )


        esfera = (

            self.render.attachNewNode(
                node
            )

        )


        return esfera


    # ======================================================
    # CRIAR TRIÂNGULO
    # ======================================================

    def criar_triangulo(self):

        largura = 2.0

        altura = 2.5

        profundidade = 1.5


        # --------------------------------------------------
        # VÉRTICES
        # --------------------------------------------------

        A = (
            -largura / 2,
            -profundidade / 2,
            -altura / 2
        )


        B = (
            largura / 2,
            -profundidade / 2,
            -altura / 2
        )


        C = (
            0,
            -profundidade / 2,
            altura / 2
        )


        D = (
            -largura / 2,
            profundidade / 2,
            -altura / 2
        )


        E = (
            largura / 2,
            profundidade / 2,
            -altura / 2
        )


        F = (
            0,
            profundidade / 2,
            altura / 2
        )


        # --------------------------------------------------
        # FACES
        # --------------------------------------------------

        faces = [

            (A, B, C),

            (D, F, E),

            (A, D, E, B),

            (A, C, F, D),

            (B, E, F, C)

        ]


        # --------------------------------------------------
        # VDATA
        # --------------------------------------------------

        vdata = GeomVertexData(

            "Triangulo3D",

            GeomVertexFormat.getV3n3(),

            Geom.UHStatic

        )


        vertex = GeomVertexWriter(

            vdata,

            "vertex"

        )


        normal = GeomVertexWriter(

            vdata,

            "normal"

        )


        triangles = GeomTriangles(

            Geom.UHStatic

        )


        indice = 0


        # --------------------------------------------------
        # FACES
        # --------------------------------------------------

        for face in faces:

            v1 = Vec3(
                *face[0]
            )


            v2 = Vec3(
                *face[1]
            )


            v3 = Vec3(
                *face[2]
            )


            normal_face = (

                v2 - v1
            ).cross(
                v3 - v1
            )


            normal_face.normalize()


            for ponto in face:

                vertex.addData3f(
                    *ponto
                )


                normal.addData3f(

                    normal_face.x,

                    normal_face.y,

                    normal_face.z

                )


            if len(face) == 3:

                triangles.addVertices(

                    indice,

                    indice + 1,

                    indice + 2

                )


            elif len(face) == 4:

                triangles.addVertices(

                    indice,

                    indice + 1,

                    indice + 2

                )


                triangles.addVertices(

                    indice,

                    indice + 2,

                    indice + 3

                )


            indice += len(face)


        # --------------------------------------------------
        # GEOMETRIA
        # --------------------------------------------------

        geom = Geom(
            vdata
        )


        geom.addPrimitive(
            triangles
        )


        node = GeomNode(
            "Triangulo3D"
        )


        node.addGeom(
            geom
        )


        triangulo = (

            self.render.attachNewNode(
                node
            )

        )


        # --------------------------------------------------
        # ARESTAS
        # --------------------------------------------------

        linhas = LineSegs()


        linhas.setThickness(
            2.5
        )


        # Frente

        linhas.moveTo(
            *A
        )

        linhas.drawTo(
            *B
        )


        linhas.moveTo(
            *B
        )

        linhas.drawTo(
            *C
        )


        linhas.moveTo(
            *C
        )

        linhas.drawTo(
            *A
        )


        # Trás

        linhas.moveTo(
            *D
        )

        linhas.drawTo(
            *E
        )


        linhas.moveTo(
            *E
        )

        linhas.drawTo(
            *F
        )


        linhas.moveTo(
            *F
        )

        linhas.drawTo(
            *D
        )


        # Ligações

        linhas.moveTo(
            *A
        )

        linhas.drawTo(
            *D
        )


        linhas.moveTo(
            *B
        )

        linhas.drawTo(
            *E
        )


        linhas.moveTo(
            *C
        )

        linhas.drawTo(
            *F
        )


        arestas = (

            triangulo.attachNewNode(
                linhas.create()
            )

        )


        return triangulo


    # ======================================================
    # CRIAR CONE
    # ======================================================

    def criar_cone(self):

        raio = 1.0

        altura = 2.5

        segmentos = 32


        formato = (
            GeomVertexFormat.getV3n3()
        )


        dados = GeomVertexData(

            "cone",

            formato,

            Geom.UHStatic

        )


        dados.setNumRows(

            segmentos + 2

        )


        vertices = GeomVertexWriter(

            dados,

            "vertex"

        )


        normais = GeomVertexWriter(

            dados,

            "normal"

        )


        # --------------------------------------------------
        # BASE
        # --------------------------------------------------

        for i in range(
            segmentos
        ):

            theta = (

                2
                *
                math.pi
                *
                i
                /
                segmentos

            )


            x = (

                raio
                *
                math.cos(theta)

            )


            y = (

                raio
                *
                math.sin(theta)

            )


            z = (
                -altura / 2
            )


            vertices.addData3f(

                x,
                y,
                z

            )


            normal = Vec3(

                x,
                y,
                0

            )


            normal.normalize()


            normais.addData3f(

                normal.x,
                normal.y,
                normal.z

            )


        # --------------------------------------------------
        # TOPO
        # --------------------------------------------------

        indice_topo = segmentos


        vertices.addData3f(

            0,
            0,
            altura / 2

        )


        normais.addData3f(

            0,
            0,
            1

        )


        # --------------------------------------------------
        # CENTRO DA BASE
        # --------------------------------------------------

        indice_centro = (

            segmentos + 1

        )


        vertices.addData3f(

            0,
            0,
            -altura / 2

        )


        normais.addData3f(

            0,
            0,
            -1

        )


        # --------------------------------------------------
        # TRIÂNGULOS
        # --------------------------------------------------

        primitivas = GeomTriangles(

            Geom.UHStatic

        )


        for i in range(
            segmentos
        ):

            atual = i


            proximo = (

                (i + 1)
                %
                segmentos

            )


            # Lateral

            primitivas.addVertices(

                atual,
                proximo,
                indice_topo

            )


            # Base

            primitivas.addVertices(

                indice_centro,
                proximo,
                atual

            )


        # --------------------------------------------------
        # GEOMETRIA
        # --------------------------------------------------

        geom = Geom(
            dados
        )


        geom.addPrimitive(
            primitivas
        )


        node = GeomNode(
            "cone"
        )


        node.addGeom(
            geom
        )


        cone = (

            self.render.attachNewNode(
                node
            )

        )


        return cone


    # ======================================================
    # ATALHOS
    # ======================================================

    def _carregar_cubo(self):

        self.carregar_objeto(
            "cubo"
        )


    def _carregar_esfera(self):

        self.carregar_objeto(
            "esfera"
        )


    def _carregar_triangulo(self):

        self.carregar_objeto(
            "triangulo"
        )


    def _carregar_cone(self):

        self.carregar_objeto(
            "cone"
        )


    # ======================================================
    # ATUALIZAR CÂMERA
    # ======================================================

    def _atualizar_camera(self):

        yaw_rad = math.radians(
            self.yaw
        )


        pitch_rad = math.radians(
            self.pitch
        )


        x = (

            self.alvo.x

            +

            self.distancia
            *
            math.cos(pitch_rad)
            *
            math.sin(yaw_rad)

        )


        y = (

            self.alvo.y

            +

            self.distancia
            *
            math.cos(pitch_rad)
            *
            math.cos(yaw_rad)

        )


        z = (

            self.alvo.z

            +

            self.distancia
            *
            math.sin(pitch_rad)

        )


        self.camera.setPos(

            x,
            y,
            z

        )


        self.camera.lookAt(
            self.alvo
        )


    # ======================================================
    # MOUSE DOWN
    # ======================================================

    def _mouse_down(self, tipo):

        if not self.mouseWatcherNode.hasMouse():

            return


        self.mouse_anterior = Vec2(

            self.mouseWatcherNode.getMouseX(),

            self.mouseWatcherNode.getMouseY()

        )


        if tipo == "rotacao":

            self.mouse_rotacionando = True

            self.mouse_movendo = False


        elif tipo == "pan":

            self.mouse_movendo = True

            self.mouse_rotacionando = False


    # ======================================================
    # MOUSE UP
    # ======================================================

    def _mouse_up(self, tipo):

        if tipo == "rotacao":

            self.mouse_rotacionando = False


        elif tipo == "pan":

            self.mouse_movendo = False


        if (

            not self.mouse_rotacionando

            and

            not self.mouse_movendo

        ):

            self.mouse_anterior = None


    # ======================================================
    # TASK DO MOUSE
    # ======================================================

    def _task_mouse(self, tarefa):

        if not self.mouseWatcherNode.hasMouse():

            return Task.cont


        if (

            not self.mouse_rotacionando

            and

            not self.mouse_movendo

        ):

            return Task.cont


        mouse_atual = Vec2(

            self.mouseWatcherNode.getMouseX(),

            self.mouseWatcherNode.getMouseY()

        )


        if self.mouse_anterior is None:

            self.mouse_anterior = mouse_atual

            return Task.cont


        diferenca_x = (

            mouse_atual.x

            -

            self.mouse_anterior.x

        )


        diferenca_y = (

            mouse_atual.y

            -

            self.mouse_anterior.y

        )


        # --------------------------------------------------
        # ROTAÇÃO
        # --------------------------------------------------

        if self.mouse_rotacionando:

            self.yaw -= (

                diferenca_x

                *

                self.sensibilidade_rotacao

            )


            self.pitch += (

                diferenca_y

                *

                self.sensibilidade_rotacao

            )


            self.pitch = max(

                self.pitch_minimo,

                min(

                    self.pitch_maximo,

                    self.pitch

                )

            )


            self._atualizar_camera()


        # --------------------------------------------------
        # PAN
        # --------------------------------------------------

        elif self.mouse_movendo:

            self._executar_pan(

                diferenca_x,

                diferenca_y

            )


        self.mouse_anterior = mouse_atual


        return Task.cont


    # ======================================================
    # PAN
    # ======================================================

    def _executar_pan(

        self,

        diferenca_x,

        diferenca_y

    ):

        quat_camera = (

            self.camera.getQuat(
                self.render
            )

        )


        eixo_direito = (

            quat_camera.xform(

                Vec3(
                    1,
                    0,
                    0
                )

            )

        )


        eixo_cima = (

            quat_camera.xform(

                Vec3(
                    0,
                    0,
                    1
                )

            )

        )


        velocidade = (

            self.distancia

            *

            0.8

            *

            self.sensibilidade_pan

        )


        deslocamento = (

            eixo_direito

            *

            (

                -diferenca_x

                *

                velocidade

            )

        )


        deslocamento += (

            eixo_cima

            *

            (

                -diferenca_y

                *

                velocidade

            )

        )


        self.alvo += (
            deslocamento
        )


        self._atualizar_camera()


    # ======================================================
    # ZOOM
    # ======================================================

    def _zoom(self, direcao):

        self.distancia -= (

            direcao

            *

            self.sensibilidade_zoom

        )


        self.distancia = max(

            self.distancia_minima,

            min(

                self.distancia_maxima,

                self.distancia

            )

        )


        self._atualizar_camera()


    # ======================================================
    # RESET
    # ======================================================

    def _resetar_camera(self):

        self.alvo = Point3(
            self.alvo_inicial
        )


        self.yaw = (
            self.yaw_inicial
        )


        self.pitch = (
            self.pitch_inicial
        )


        self.distancia = (
            self.distancia_inicial
        )


        self._atualizar_camera()


# ==========================================================
# INICIAR A APLICAÇÃO
# ==========================================================

app = Aplicacao3D()

app.run()