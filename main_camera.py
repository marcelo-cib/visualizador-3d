from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    AmbientLight, DirectionalLight, Point3, Vec2, Vec3,
    Geom, GeomNode, GeomVertexData, GeomVertexFormat,
    GeomVertexWriter, GeomTriangles, LineSegs, Texture,
    PNMImage, Filename
)
import math
import socket
import threading
import io
import os
import tempfile
import qrcode
from flask import Flask, Response, send_from_directory
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DirectEntry
from direct.gui.OnscreenImage import OnscreenImage

servidor_web = Flask(__name__)

URL_RENDER = os.environ.get(
    "URL_RENDER",
    "https://visualizador-3d-xvr4.onrender.com"
).rstrip("/")


def obter_ip_rede():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return "127.0.0.1"


def carregar_catalogo_web():
    """Carrega o catálogo compartilhado pelo servidor Flask."""
    caminho = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "veiculos.json"
    )
    try:
        import json
        with open(caminho, "r", encoding="utf-8") as arquivo:
            registros = json.load(arquivo)
        return {
            registro["codigo"]: registro
            for registro in registros
        }
    except Exception as erro:
        print(f"ERRO ao carregar veiculos.json no servidor: {erro}")
        return {}


def criar_pagina_3d(objeto):
    catalogo = carregar_catalogo_web()
    registro = catalogo.get(objeto)

    if registro is None:
        return None

    nome = registro["nome"]
    nome_arquivo = registro["arquivo"]

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
canvas {{ display: block; }}
</style>
</head>
<body>
<div id="titulo">{nome}</div>
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

const camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);
camera.position.set(5, 4, 7);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
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
const caminhoModelo = "/modelos/" + encodeURIComponent("{nome_arquivo}");

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
        controls.target.copy(caixaFinal.getCenter(new THREE.Vector3()));
        camera.position.set(5, 3.5, 7);
        controls.update();
    }},
    undefined,
    function(erro) {{
        console.error("Erro ao carregar modelo GLB:", erro);
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
</html>"""


@servidor_web.route("/")
def catalogo_web():
    """Página inicial pública com todos os veículos cadastrados."""
    catalogo = carregar_catalogo_web()

    cards = []
    for codigo, dados in catalogo.items():
        cards.append(f"""
        <div class="card">
            <div class="icone">🚗</div>
            <h2>{dados["nome"]}</h2>
            <div class="categoria">{dados.get("categoria", "")}</div>
            <p>{dados.get("descricao", "")}</p>
            <div class="botoes">
                <a class="botao" href="/objeto/{codigo}">Visualizar 3D</a>
                <a class="botao secundario" href="/qrcode/{codigo}">QR Code</a>
            </div>
        </div>
        """)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Catálogo de Veículos 3D</title>
<style>
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #101010;
    color: white;
}}
.cabecalho {{
    text-align: center;
    padding: 32px 16px 20px;
    background: linear-gradient(180deg, #1d1d1d, #101010);
}}
.cabecalho h1 {{ margin: 0 0 8px; font-size: 30px; }}
.cabecalho p {{ margin: 0; color: #bdbdbd; }}
.catalogo {{
    width: min(1100px, 94%);
    margin: 25px auto 45px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 18px;
}}
.card {{
    background: #1c1c1c;
    border: 1px solid #333;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 8px 22px rgba(0,0,0,.25);
}}
.icone {{ font-size: 44px; }}
.card h2 {{ margin: 10px 0 5px; }}
.categoria {{ color: #8ec5ff; font-size: 14px; margin-bottom: 10px; }}
.card p {{ color: #c7c7c7; min-height: 42px; }}
.botoes {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 18px; }}
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
.botao.secundario {{ background: #444; }}
.rodape {{
    text-align: center;
    color: #888;
    padding: 0 15px 30px;
    font-size: 13px;
}}
</style>
</head>
<body>
<header class="cabecalho">
    <h1>CATÁLOGO DE VEÍCULOS 3D</h1>
    <p>Selecione um veículo para visualizar o modelo em 3D.</p>
</header>
<main class="catalogo">
    {''.join(cards)}
</main>
<div class="rodape">
    Visualizador 3D • {len(catalogo)} veículos cadastrados
</div>
</body>
</html>"""
    return html


@servidor_web.route("/objeto/<nome>")
def visualizar_objeto(nome):
    if nome not in carregar_catalogo_web():
        return "Objeto não encontrado.", 404

    pagina = criar_pagina_3d(nome)
    if pagina is None:
        return "Objeto não encontrado.", 404
    return pagina


@servidor_web.route("/qrcode/<nome>")
def fornecer_qrcode(nome):
    if nome not in carregar_catalogo_web():
        return "Objeto não encontrado.", 404

    url = f"{URL_RENDER}/objeto/{nome}"
    imagem = qrcode.make(url)
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)
    return Response(buffer.getvalue(), mimetype="image/png")


@servidor_web.route("/modelos/<path:nome_arquivo>")
def fornecer_modelo(nome_arquivo):
    pasta_modelos = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "modelos"
    )

    # Permite também executar localmente quando os GLBs estão
    # na mesma pasta do programa.
    caminho_modelos = os.path.join(pasta_modelos, nome_arquivo)
    if os.path.isfile(caminho_modelos):
        return send_from_directory(pasta_modelos, nome_arquivo)

    pasta_programa = os.path.dirname(os.path.abspath(__file__))
    caminho_local = os.path.join(pasta_programa, nome_arquivo)

    if os.path.isfile(caminho_local):
        return send_from_directory(pasta_programa, nome_arquivo)

    return "Modelo 3D não encontrado.", 404


def iniciar_servidor_web():
    servidor_web.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )


class Aplicacao3D(ShowBase):

    def __init__(self):
        super().__init__()

        self.ip_rede = obter_ip_rede()
        self.thread_servidor = threading.Thread(
            target=iniciar_servidor_web,
            daemon=True
        )
        self.thread_servidor.start()

        print("=" * 60)
        print("SERVIDOR 3D PARA CELULAR")
        print(f"IP da máquina: {self.ip_rede}")
        print(f"URL pública dos QR Codes: {URL_RENDER}")
        print("Porta local: 5000")
        print("=" * 60)

        self.disableMouse()

        caminho_catalogo = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "veiculos.json"
        )

        self.catalogo_veiculos = {}

        try:
            import json
            with open(caminho_catalogo, "r", encoding="utf-8") as arquivo_catalogo:
                registros = json.load(arquivo_catalogo)

            for registro in registros:
                codigo = registro["codigo"]
                self.catalogo_veiculos[codigo] = registro

            print(
                f"Catálogo carregado: "
                f"{len(self.catalogo_veiculos)} veículos."
            )
        except Exception as erro:
            print(f"ERRO ao carregar veiculos.json: {erro}")

        self.biblioteca_objetos = {
            codigo: dados["nome"]
            for codigo, dados in self.catalogo_veiculos.items()
        }

        self.arquivos_veiculos = {
            codigo: dados["arquivo"]
            for codigo, dados in self.catalogo_veiculos.items()
        }

        self.alvo = Point3(0, 0, 0)
        self.yaw = 0.0
        self.pitch = 20.0
        self.distancia = 12.0

        self.yaw_inicial = 0.0
        self.pitch_inicial = 20.0
        self.distancia_inicial = 12.0
        self.alvo_inicial = Point3(0, 0, 0)

        self.pitch_minimo = -89.0
        self.pitch_maximo = 89.0
        self.distancia_minima = 3.0
        self.distancia_maxima = 50.0

        self.sensibilidade_rotacao = 180.0
        self.sensibilidade_pan = 1.0
        self.sensibilidade_zoom = 1.0

        self.mouse_rotacionando = False
        self.mouse_movendo = False
        self.mouse_anterior = None

        self.qr_texture = None
        self.qr_imagem = None
        self.qr_arquivo_temp = None

        # CORREÇÃO PRINCIPAL:
        # inicializa os atributos antes de carregar o primeiro veículo.
        self.modelo_atual = None
        self.objeto_atual = None

        self.configurar_luzes()

        self.carregar_objeto("car")

        if self.modelo_atual is None:
            self.carregar_objeto("suv")

        self.criar_interface_biblioteca()

        self.accept("mouse1", self._mouse_down, ["rotacao"])
        self.accept("mouse1-up", self._mouse_up, ["rotacao"])
        self.accept("mouse3", self._mouse_down, ["pan"])
        self.accept("mouse3-up", self._mouse_up, ["pan"])
        self.accept("mouse2", self._mouse_down, ["pan"])
        self.accept("mouse2-up", self._mouse_up, ["pan"])

        self.accept("wheel_up", self._zoom, [1])
        self.accept("wheel_down", self._zoom, [-1])

        self.accept("c", self._carregar_car)
        self.accept("C", self._carregar_car)
        self.accept("p", self._carregar_police_car)
        self.accept("P", self._carregar_police_car)
        self.accept("s", self._carregar_sports_car)
        self.accept("S", self._carregar_sports_car)
        self.accept("t", self._carregar_taxi)
        self.accept("T", self._carregar_taxi)
        self.accept("u", self._carregar_suv)
        self.accept("U", self._carregar_suv)
        self.accept("n", lambda: self.carregar_objeto("car_un"))
        self.accept("N", lambda: self.carregar_objeto("car_un"))
        self.accept("d", lambda: self.carregar_objeto("sports_car_1"))
        self.accept("D", lambda: self.carregar_objeto("sports_car_1"))

        self.accept("r", self._resetar_camera)
        self.accept("R", self._resetar_camera)

        self._atualizar_camera()

        self.taskMgr.add(self._task_mouse, "task_mouse")

    def criar_interface_biblioteca(self):
        self.painel_biblioteca = DirectFrame(
            parent=self.aspect2d,
            frameColor=(0.06, 0.06, 0.06, 0.92),
            frameSize=(-0.58, 0.58, -0.92, 0.48),
            pos=(-0.76, 0, 0.48)
        )

        self.titulo_biblioteca = DirectLabel(
            parent=self.painel_biblioteca,
            text="CATÁLOGO DE VEÍCULOS 3D",
            scale=0.045,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(-0.22, 0, 0.38)
        )

        self.label_qr_coluna = DirectLabel(
            parent=self.painel_biblioteca,
            text="QR",
            scale=0.035,
            text_fg=(0.7, 0.9, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0.39, 0, 0.38)
        )

        linha_inicial = 0.25
        espacamento = 0.15

        for indice, (codigo, dados) in enumerate(
            self.catalogo_veiculos.items()
        ):
            pos_z = linha_inicial - (indice * espacamento)

            DirectButton(
                parent=self.painel_biblioteca,
                text=dados["nome"],
                scale=0.040,
                frameSize=(-2.5, 2.5, -0.42, 0.42),
                pos=(-0.20, 0, pos_z),
                command=self.carregar_objeto,
                extraArgs=[codigo]
            )

            DirectButton(
                parent=self.painel_biblioteca,
                text="QR",
                scale=0.035,
                frameSize=(-0.85, 0.85, -0.48, 0.48),
                pos=(0.40, 0, pos_z),
                command=self.mostrar_qrcode,
                extraArgs=[codigo]
            )

        self.objeto_selecionado_label = DirectLabel(
            parent=self.painel_biblioteca,
            text=(
                "Veículo atual: "
                + (
                    self.catalogo_veiculos[self.objeto_atual]["nome"]
                    if self.objeto_atual in self.catalogo_veiculos
                    else "Nenhum veículo carregado"
                )
            ),
            scale=0.029,
            text_fg=(0.75, 0.75, 0.75, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, -0.84)
        )

        self.criar_painel_qrcode()

    def criar_painel_qrcode(self):
        self.painel_qrcode = DirectFrame(
            parent=self.aspect2d,
            frameColor=(0.04, 0.04, 0.04, 0.97),
            frameSize=(-0.42, 0.42, -0.48, 0.48),
            pos=(-0.05, 0, 0.02)
        )

        self.titulo_qrcode = DirectLabel(
            parent=self.painel_qrcode,
            text="QR CODE",
            scale=0.045,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.40)
        )

        self.qr_nome = DirectLabel(
            parent=self.painel_qrcode,
            text="",
            scale=0.038,
            text_fg=(0.75, 0.9, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.31)
        )

        self.qr_instrucao = DirectLabel(
            parent=self.painel_qrcode,
            text="Selecione um QR Code",
            scale=0.028,
            text_fg=(0.65, 0.65, 0.65, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.20)
        )

        self.botao_fechar_qr = DirectButton(
            parent=self.painel_qrcode,
            text="X",
            scale=0.035,
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            pos=(0.34, 0, 0.40),
            command=self.fechar_qrcode
        )

        self.painel_qrcode.hide()

    def mostrar_qrcode(self, nome):
        if nome not in self.biblioteca_objetos:
            return

        url = f"{URL_RENDER}/objeto/{nome}"

        print()
        print("=" * 60)
        print(f"QR CODE: {self.biblioteca_objetos[nome]}")
        print(f"URL: {url}")
        print("=" * 60)

        self.painel_qrcode.show()
        self.qr_nome["text"] = self.biblioteca_objetos[nome]
        self.qr_instrucao["text"] = "Aponte a câmera do celular para o QR Code"

        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4
            )

            qr.add_data(url)
            qr.make(fit=True)

            imagem_pil = qr.make_image(
                fill_color="black",
                back_color="white"
            ).convert("RGB")

            largura, altura = imagem_pil.size

            imagem_pnm = PNMImage(largura, altura, 3)
            pixels = imagem_pil.load()

            for y in range(altura):
                for x in range(largura):
                    r, g, b = pixels[x, y]
                    imagem_pnm.setXel(
                        x, altura - y - 1,
                        r / 255.0, g / 255.0, b / 255.0
                    )

            self.qr_texture = Texture("qr_code")
            self.qr_texture.load(imagem_pnm)

            if self.qr_imagem is not None:
                self.qr_imagem.destroy()
                self.qr_imagem = None

            self.qr_imagem = OnscreenImage(
                parent=self.painel_qrcode,
                image=self.qr_texture,
                pos=(0, 0, -0.02),
                scale=(0.29, 1, 0.29)
            )

            self.qr_imagem.setBin("gui-popup", 0)
            print("QR Code carregado na interface.")

        except Exception as erro:
            print()
            print("ERRO AO GERAR QR CODE:")
            print(type(erro).__name__, "-", erro)
            print()

    def fechar_qrcode(self):
        if self.qr_imagem is not None:
            self.qr_imagem.destroy()
            self.qr_imagem = None
        self.painel_qrcode.hide()

    def configurar_luzes(self):
        luz_ambiente = AmbientLight("luz_ambiente")
        luz_ambiente.setColor((0.35, 0.35, 0.35, 1))

        objeto_luz_ambiente = self.render.attachNewNode(luz_ambiente)
        self.render.setLight(objeto_luz_ambiente)

        luz_direcional = DirectionalLight("luz_direcional")
        luz_direcional.setColor((0.9, 0.9, 0.9, 1))

        objeto_luz_direcional = self.render.attachNewNode(luz_direcional)
        objeto_luz_direcional.setHpr(-45, -45, 0)
        self.render.setLight(objeto_luz_direcional)

    def carregar_objeto(self, nome):
        if nome not in self.biblioteca_objetos:
            print("Veículo não encontrado:", nome)
            return

        self.remover_objeto_atual()

        self.modelo_atual = self.criar_veiculo(nome)

        if self.modelo_atual is not None:
            self.modelo_atual.reparentTo(self.render)
            self.modelo_atual.setPos(0, 0, 0)
            self.objeto_atual = nome

            if hasattr(self, "objeto_selecionado_label"):
                dados = self.catalogo_veiculos[nome]
                self.objeto_selecionado_label["text"] = (
                    "Veículo atual: "
                    + dados["nome"]
                    + " | Categoria: "
                    + dados["categoria"]
                )

            print(
                "Veículo carregado:",
                self.biblioteca_objetos[nome]
            )

    def remover_objeto_atual(self):
        if self.modelo_atual is not None:
            self.modelo_atual.removeNode()
            self.modelo_atual = None

        self.objeto_atual = None

    def criar_veiculo(self, nome):
        try:
            nome_arquivo = self.arquivos_veiculos[nome]
            pasta_programa = os.path.dirname(os.path.abspath(__file__))

            candidatos = [
                os.path.join(pasta_programa, nome_arquivo),
                os.path.join(pasta_programa, "modelos", nome_arquivo)
            ]

            caminho_modelo = next(
                (
                    caminho for caminho in candidatos
                    if os.path.isfile(caminho)
                ),
                None
            )

            if caminho_modelo is None:
                print(f"Arquivo {nome_arquivo} não encontrado.")
                print(
                    "Coloque o arquivo na mesma pasta do .py "
                    "ou em modelos\\."
                )
                return None

            arquivo_modelo = Filename.fromOsSpecific(caminho_modelo)
            modelo = self.loader.loadModel(arquivo_modelo)

            if modelo.isEmpty():
                print(
                    f"Erro ao carregar {nome_arquivo}: "
                    "o modelo foi encontrado, mas o Panda3D "
                    "não conseguiu carregá-lo."
                )
                return None

            limites = modelo.getTightBounds()

            if (
                limites
                and limites[0] is not None
                and limites[1] is not None
            ):
                minimo, maximo = limites
                tamanho = maximo - minimo
                maior = max(
                    abs(tamanho.x),
                    abs(tamanho.y),
                    abs(tamanho.z)
                )

                if maior > 0:
                    escala = 4.5 / maior
                    modelo.setScale(escala)

                    centro = (minimo + maximo) * 0.5

                    modelo.setPos(
                        -centro.x * escala,
                        -centro.y * escala,
                        -centro.z * escala
                    )
            else:
                modelo.setScale(2.5)

            return modelo

        except Exception as erro:
            print(
                f"Erro ao carregar "
                f"{self.arquivos_veiculos.get(nome, nome)}:",
                erro
            )
            return None

    def _carregar_car(self):
        self.carregar_objeto("car")

    def _carregar_police_car(self):
        self.carregar_objeto("police_car")

    def _carregar_sports_car(self):
        self.carregar_objeto("sports_car")

    def _carregar_taxi(self):
        self.carregar_objeto("taxi")

    def _carregar_suv(self):
        self.carregar_objeto("suv")

    def _carregar_car_un(self):
        self.carregar_objeto("car_un")

    def _carregar_sports_car_1(self):
        self.carregar_objeto("sports_car_1")

    def _atualizar_camera(self):
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        x = (
            self.alvo.x
            + self.distancia
            * math.cos(pitch_rad)
            * math.sin(yaw_rad)
        )

        y = (
            self.alvo.y
            + self.distancia
            * math.cos(pitch_rad)
            * math.cos(yaw_rad)
        )

        z = (
            self.alvo.z
            + self.distancia
            * math.sin(pitch_rad)
        )

        self.camera.setPos(x, y, z)
        self.camera.lookAt(self.alvo)

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

    def _mouse_up(self, tipo):
        if tipo == "rotacao":
            self.mouse_rotacionando = False
        elif tipo == "pan":
            self.mouse_movendo = False

        if not self.mouse_rotacionando and not self.mouse_movendo:
            self.mouse_anterior = None

    def _task_mouse(self, tarefa):
        if not self.mouseWatcherNode.hasMouse():
            return Task.cont

        if not self.mouse_rotacionando and not self.mouse_movendo:
            return Task.cont

        mouse_atual = Vec2(
            self.mouseWatcherNode.getMouseX(),
            self.mouseWatcherNode.getMouseY()
        )

        if self.mouse_anterior is None:
            self.mouse_anterior = mouse_atual
            return Task.cont

        diferenca_x = mouse_atual.x - self.mouse_anterior.x
        diferenca_y = mouse_atual.y - self.mouse_anterior.y

        if self.mouse_rotacionando:
            self.yaw -= diferenca_x * self.sensibilidade_rotacao
            self.pitch += diferenca_y * self.sensibilidade_rotacao

            self.pitch = max(
                self.pitch_minimo,
                min(self.pitch_maximo, self.pitch)
            )

            self._atualizar_camera()

        elif self.mouse_movendo:
            self._executar_pan(diferenca_x, diferenca_y)

        self.mouse_anterior = mouse_atual
        return Task.cont

    def _executar_pan(self, diferenca_x, diferenca_y):
        quat_camera = self.camera.getQuat(self.render)

        eixo_direito = quat_camera.xform(Vec3(1, 0, 0))
        eixo_cima = quat_camera.xform(Vec3(0, 0, 1))

        velocidade = (
            self.distancia
            * 0.8
            * self.sensibilidade_pan
        )

        deslocamento = eixo_direito * (
            -diferenca_x * velocidade
        )

        deslocamento += eixo_cima * (
            -diferenca_y * velocidade
        )

        self.alvo += deslocamento
        self._atualizar_camera()

    def _zoom(self, direcao):
        self.distancia -= direcao * self.sensibilidade_zoom

        self.distancia = max(
            self.distancia_minima,
            min(self.distancia_maxima, self.distancia)
        )

        self._atualizar_camera()

    def _resetar_camera(self):
        self.alvo = Point3(self.alvo_inicial)
        self.yaw = self.yaw_inicial
        self.pitch = self.pitch_inicial
        self.distancia = self.distancia_inicial
        self._atualizar_camera()


app = Aplicacao3D()
app.run()
