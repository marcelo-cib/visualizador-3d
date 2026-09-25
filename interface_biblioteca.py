from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    DirectLabel
)


class InterfaceBiblioteca:

    def __init__(self, aplicacao):

        self.aplicacao = aplicacao

        # =====================================================
        # PAINEL PRINCIPAL
        # =====================================================

        self.painel = DirectFrame(
            parent=self.aplicacao.aspect2d,

            frameColor=(0.08, 0.08, 0.10, 0.95),

            frameSize=(
                -0.95,
                0.95,
                -0.90,
                0.90
            )
        )

        # =====================================================
        # TÍTULO
        # =====================================================

        self.titulo = DirectLabel(

            parent=self.painel,

            text="BIBLIOTECA DE OBJETOS 3D",

            text_scale=0.065,

            text_fg=(1, 1, 1, 1),

            relief=None,

            pos=(
                0,
                0,
                0.80
            )
        )

        # =====================================================
        # DESCRIÇÃO
        # =====================================================

        self.subtitulo = DirectLabel(

            parent=self.painel,

            text="Selecione um objeto",

            text_scale=0.045,

            text_fg=(0.75, 0.75, 0.75, 1),

            relief=None,

            pos=(
                0,
                0,
                0.69
            )
        )

        # =====================================================
        # BOTÕES DOS OBJETOS
        # =====================================================

        self.botoes = {}

        self._criar_botao(
            "cubo",
            "CUBO",
            0.42
        )

        self._criar_botao(
            "esfera",
            "ESFERA",
            0.18
        )

        self._criar_botao(
            "triangulo",
            "TRIÂNGULO",
            -0.06
        )

        self._criar_botao(
            "cone",
            "CONE",
            -0.30
        )

        # =====================================================
        # OBJETO ATUAL
        # =====================================================

        self.objeto_atual = DirectLabel(

            parent=self.painel,

            text="Objeto atual: Cubo",

            text_scale=0.045,

            text_fg=(0.8, 0.8, 0.8, 1),

            relief=None,

            pos=(
                0,
                0,
                -0.70
            )
        )

    # =========================================================
    # CRIAR BOTÃO
    # =========================================================

    def _criar_botao(
        self,
        identificador,
        texto,
        posicao_z
    ):

        botao = DirectButton(

            parent=self.painel,

            text=texto,

            text_scale=0.045,

            text_fg=(1, 1, 1, 1),

            frameColor=(
                0.16,
                0.16,
                0.20,
                1
            ),

            frameColor1=(
                0.25,
                0.25,
                0.30,
                1
            ),

            frameColor2=(
                0.35,
                0.35,
                0.40,
                1
            ),

            frameColor3=(
                0.10,
                0.10,
                0.12,
                1
            ),

            scale=0.8,

            pos=(
                0,
                0,
                posicao_z
            ),

            command=self._selecionar_objeto,

            extraArgs=[
                identificador
            ]
        )

        self.botoes[identificador] = botao

    # =========================================================
    # SELECIONAR OBJETO
    # =========================================================

    def _selecionar_objeto(
        self,
        identificador
    ):

        # Solicita que a aplicação carregue o objeto
        self.aplicacao.carregar_objeto(
            identificador
        )

        # Atualiza o texto
        nome = (
            self.aplicacao.biblioteca_objetos[
                identificador
            ]
        )

        self.objeto_atual["text"] = (
            "Objeto atual: " + nome
        )