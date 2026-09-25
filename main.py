from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Point3,
    Vec2,
    Vec3
)

import math


class Aplicacao3D(ShowBase):

    def __init__(self):

        super().__init__()

        # ==================================================
        # CONFIGURAÇÕES GERAIS
        # ==================================================

        # Desativa o controle padrão da câmera do Panda3D.
        self.disableMouse()


        # ==================================================
        # CUBO
        # ==================================================

        # Carrega o cubo padrão do Panda3D.
        self.cubo = self.loader.loadModel(
            "models/box"
        )

        # Coloca o cubo diretamente na cena.
        self.cubo.reparentTo(
            self.render
        )

        # O cubo permanece exatamente na origem.
        self.cubo.setPos(
            0,
            0,
            0
        )

        # Tamanho do cubo.
        self.cubo.setScale(
            2
        )


        # ==================================================
        # ILUMINAÇÃO AMBIENTE
        # ==================================================

        luz_ambiente = AmbientLight(
            "luz_ambiente"
        )

        luz_ambiente.setColor(
            (0.35, 0.35, 0.35, 1)
        )

        objeto_luz_ambiente = self.render.attachNewNode(
            luz_ambiente
        )

        self.render.setLight(
            objeto_luz_ambiente
        )


        # ==================================================
        # LUZ DIRECIONAL
        # ==================================================

        luz_direcional = DirectionalLight(
            "luz_direcional"
        )

        luz_direcional.setColor(
            (0.9, 0.9, 0.9, 1)
        )

        objeto_luz_direcional = self.render.attachNewNode(
            luz_direcional
        )

        # Direção da luz.
        objeto_luz_direcional.setHpr(
            -45,
            -45,
            0
        )

        self.render.setLight(
            objeto_luz_direcional
        )


        # ==================================================
        # CÂMERA - COORDENADAS ESFÉRICAS
        # ==================================================

        # --------------------------------------------------
        # ALVO DA CÂMERA
        # --------------------------------------------------
        #
        # O alvo começa no centro do cubo.
        #
        # IMPORTANTE:
        # O cubo continua na origem.
        # Quem se movimenta é o alvo da câmera.
        #
        self.alvo = Point3(
            0,
            0,
            0
        )


        # --------------------------------------------------
        # ÂNGULO HORIZONTAL
        # --------------------------------------------------

        self.yaw = 0.0


        # --------------------------------------------------
        # ÂNGULO VERTICAL
        # --------------------------------------------------

        self.pitch = 20.0


        # --------------------------------------------------
        # DISTÂNCIA DA CÂMERA
        # --------------------------------------------------

        self.distancia = 12.0


        # ==================================================
        # VALORES INICIAIS PARA RESET
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
        # LIMITES DA CÂMERA
        # ==================================================

        # Evita que a câmera fique de cabeça para baixo.

        self.pitch_minimo = -89.0

        self.pitch_maximo = 89.0


        # Distância mínima e máxima.

        self.distancia_minima = 3.0

        self.distancia_maxima = 50.0


        # ==================================================
        # SENSIBILIDADE DA ROTAÇÃO
        # ==================================================

        self.sensibilidade_rotacao = 180.0


        # ==================================================
        # SENSIBILIDADE DO PAN
        # ==================================================

        self.sensibilidade_pan = 1.0


        # ==================================================
        # SENSIBILIDADE DO ZOOM
        # ==================================================

        self.sensibilidade_zoom = 1.0


        # ==================================================
        # CONTROLE DO MOUSE
        # ==================================================

        self.mouse_rotacionando = False

        self.mouse_movendo = False

        self.mouse_anterior = None


        # ==================================================
        # EVENTOS DO MOUSE
        # ==================================================

        # --------------------------------------------------
        # BOTÃO ESQUERDO
        # ROTACIONAR / ORBITAR
        # --------------------------------------------------

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


        # --------------------------------------------------
        # BOTÃO DIREITO
        # PAN
        # --------------------------------------------------

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


        # --------------------------------------------------
        # BOTÃO DO MEIO
        # PAN
        # --------------------------------------------------

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
        # POSICIONA A CÂMERA PELA PRIMEIRA VEZ
        # ==================================================

        self._atualizar_camera()


        # ==================================================
        # TASK PRINCIPAL DO MOUSE
        # ==================================================

        self.taskMgr.add(
            self._task_mouse,
            "task_mouse"
        )


    # ======================================================
    # ATUALIZAR CÂMERA
    # ======================================================

    def _atualizar_camera(self):

        # --------------------------------------------------
        # CONVERTE GRAUS PARA RADIANOS
        # --------------------------------------------------

        yaw_rad = math.radians(
            self.yaw
        )

        pitch_rad = math.radians(
            self.pitch
        )


        # --------------------------------------------------
        # COORDENADAS ESFÉRICAS
        # --------------------------------------------------
        #
        # A câmera é calculada em relação ao alvo.
        #
        # Não existe ponto fixo na tela.
        #

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


        # --------------------------------------------------
        # POSICIONA A CÂMERA
        # --------------------------------------------------

        self.camera.setPos(
            x,
            y,
            z
        )


        # --------------------------------------------------
        # CÂMERA SEMPRE OLHA PARA O ALVO
        # --------------------------------------------------

        self.camera.lookAt(
            self.alvo
        )


    # ======================================================
    # MOUSE DOWN
    # ======================================================

    def _mouse_down(self, tipo):

        if not self.mouseWatcherNode.hasMouse():

            return


        # Guarda posição inicial do mouse.

        self.mouse_anterior = Vec2(
            self.mouseWatcherNode.getMouseX(),
            self.mouseWatcherNode.getMouseY()
        )


        # --------------------------------------------------
        # ROTAÇÃO
        # --------------------------------------------------

        if tipo == "rotacao":

            self.mouse_rotacionando = True

            self.mouse_movendo = False


        # --------------------------------------------------
        # PAN
        # --------------------------------------------------

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


        # Não há mais mouse pressionado.

        if (
            not self.mouse_rotacionando
            and
            not self.mouse_movendo
        ):

            self.mouse_anterior = None


    # ======================================================
    # TASK CONTÍNUA DO MOUSE
    # ======================================================

    def _task_mouse(self, tarefa):

        # --------------------------------------------------
        # Verifica se existe mouse
        # --------------------------------------------------

        if not self.mouseWatcherNode.hasMouse():

            return Task.cont


        # --------------------------------------------------
        # Se não estiver interagindo, não faz nada.
        # --------------------------------------------------

        if (
            not self.mouse_rotacionando
            and
            not self.mouse_movendo
        ):

            return Task.cont


        # --------------------------------------------------
        # Mouse atual
        # --------------------------------------------------

        mouse_atual = Vec2(
            self.mouseWatcherNode.getMouseX(),
            self.mouseWatcherNode.getMouseY()
        )


        # --------------------------------------------------
        # Primeira leitura
        # --------------------------------------------------

        if self.mouse_anterior is None:

            self.mouse_anterior = mouse_atual

            return Task.cont


        # --------------------------------------------------
        # Diferença do mouse
        # --------------------------------------------------

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

            # Movimento horizontal
            #
            # esquerda/direita = yaw

            self.yaw -= (
                diferenca_x
                *
                self.sensibilidade_rotacao
            )


            # Movimento vertical
            #
            # cima/baixo = pitch

            self.pitch += (
                diferenca_y
                *
                self.sensibilidade_rotacao
            )


            # --------------------------------------------------
            # LIMITA O PITCH
            # --------------------------------------------------
            #
            # Isso evita que a câmera vire de cabeça
            # para baixo e também evita o gimbal lock
            # causado pela passagem pelos 90 graus.
            #

            self.pitch = max(
                self.pitch_minimo,
                min(
                    self.pitch_maximo,
                    self.pitch
                )
            )


            # --------------------------------------------------
            # ATUALIZA A CÂMERA
            # --------------------------------------------------

            self._atualizar_camera()


        # --------------------------------------------------
        # PAN
        # --------------------------------------------------

        elif self.mouse_movendo:

            self._executar_pan(
                diferenca_x,
                diferenca_y
            )


        # --------------------------------------------------
        # GUARDA POSIÇÃO ATUAL
        # --------------------------------------------------

        self.mouse_anterior = mouse_atual


        return Task.cont


    # ======================================================
    # PAN DA CÂMERA
    # ======================================================

    def _executar_pan(
        self,
        diferenca_x,
        diferenca_y
    ):

        # --------------------------------------------------
        # PEGA A ORIENTAÇÃO ATUAL DA CÂMERA
        # --------------------------------------------------

        quat_camera = self.camera.getQuat(
            self.render
        )


        # --------------------------------------------------
        # EIXO DIREITO DA CÂMERA
        # --------------------------------------------------

        eixo_direito = quat_camera.xform(
            Vec3(
                1,
                0,
                0
            )
        )


        # --------------------------------------------------
        # EIXO VERTICAL DA CÂMERA
        # --------------------------------------------------

        eixo_cima = quat_camera.xform(
            Vec3(
                0,
                0,
                1
            )
        )


        # --------------------------------------------------
        # VELOCIDADE DO PAN
        # --------------------------------------------------
        #
        # O pan fica proporcional à distância.
        #
        # Quanto mais longe:
        # maior o deslocamento.
        #
        # Quanto mais perto:
        # menor o deslocamento.
        #

        velocidade = (
            self.distancia
            *
            0.8
            *
            self.sensibilidade_pan
        )


        # --------------------------------------------------
        # CALCULA DESLOCAMENTO
        # --------------------------------------------------

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


        # --------------------------------------------------
        # MOVE O ALVO
        # --------------------------------------------------

        self.alvo += deslocamento


        # --------------------------------------------------
        # ATUALIZA A CÂMERA
        # --------------------------------------------------

        self._atualizar_camera()


    # ======================================================
    # ZOOM
    # ======================================================

    def _zoom(self, direcao):

        # --------------------------------------------------
        # Zoom positivo:
        # aproxima
        #
        # Zoom negativo:
        # afasta
        # --------------------------------------------------

        self.distancia -= (
            direcao
            *
            self.sensibilidade_zoom
        )


        # --------------------------------------------------
        # LIMITES DO ZOOM
        # --------------------------------------------------

        self.distancia = max(
            self.distancia_minima,
            min(
                self.distancia_maxima,
                self.distancia
            )
        )


        # --------------------------------------------------
        # ATUALIZA CÂMERA
        # --------------------------------------------------

        self._atualizar_camera()


    # ======================================================
    # RESETAR CÂMERA
    # ======================================================

    def _resetar_camera(self):

        # --------------------------------------------------
        # Restaura alvo
        # --------------------------------------------------

        self.alvo = Point3(
            self.alvo_inicial
        )


        # --------------------------------------------------
        # Restaura yaw
        # --------------------------------------------------

        self.yaw = (
            self.yaw_inicial
        )


        # --------------------------------------------------
        # Restaura pitch
        # --------------------------------------------------

        self.pitch = (
            self.pitch_inicial
        )


        # --------------------------------------------------
        # Restaura distância
        # --------------------------------------------------

        self.distancia = (
            self.distancia_inicial
        )


        # --------------------------------------------------
        # Atualiza câmera
        # --------------------------------------------------

        self._atualizar_camera()


# ==========================================================
# INICIAR A APLICAÇÃO
# ==========================================================

app = Aplicacao3D()

app.run()