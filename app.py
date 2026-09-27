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
    categoria = registro.get("categoria", "Veículo")
    descricao = registro.get("descricao", "")
    caminho_modelo = criar_url_modelo(registro["arquivo"])
    return f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{nome} — AUTO3D</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{{--bg:#0a0b0f;--s:#0f1117;--line:rgba(255,255,255,.09);--txt:#f5f7fb;--muted:#9aa2b1;--gold:#c9a961;--gold2:#d4b476}}
*{{box-sizing:border-box}}html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--txt);font-family:Inter,Arial,sans-serif}}
body:before{{content:"";position:fixed;inset:0;pointer-events:none;opacity:.3;background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:44px 44px}}
#viewer{{position:fixed;inset:0}}canvas{{display:block;width:100%;height:100%}}
.brand,.status,.info,.help{{position:fixed;z-index:5;border:1px solid var(--line);background:rgba(15,17,23,.76);backdrop-filter:blur(20px);box-shadow:0 20px 60px rgba(0,0,0,.5)}}
.brand{{top:20px;left:20px;padding:10px 14px;border-radius:14px;display:flex;gap:10px;align-items:center}}.mark{{width:32px;height:32px;display:grid;place-items:center;border-radius:10px;background:linear-gradient(135deg,var(--gold),var(--gold2));color:#111}}.brand b{{font:700 14px "Space Grotesk";letter-spacing:.13em}}
.status{{top:78px;left:20px;padding:9px 12px;border-radius:999px;font-size:12px;color:#ccd3df}}.info{{left:24px;bottom:24px;width:min(470px,calc(100vw - 48px));padding:24px;border-radius:20px}}.badge{{display:inline-block;padding:6px 10px;border-radius:999px;background:rgba(201,169,97,.12);border:1px solid rgba(201,169,97,.25);color:var(--gold2);font-size:11px;font-weight:700;text-transform:uppercase}}h1{{font:700 clamp(27px,4vw,40px)/1.05 "Space Grotesk";margin:12px 0 8px}}p{{margin:0;color:var(--muted);line-height:1.65}}.help{{right:24px;bottom:24px;padding:11px 14px;border-radius:12px;color:#aeb6c5;font-size:12px}}
@media(max-width:700px){{.brand{{top:12px;left:12px}}.status{{top:68px;left:12px}}.info{{left:12px;right:12px;bottom:12px;width:auto;padding:18px}}.help{{display:none}}}}
</style></head><body>
<div id="viewer"></div><div class="brand"><span class="mark">◆</span><b>AUTO3D</b></div>
<div class="status" id="status">Carregando modelo 3D...</div>
<section class="info"><span class="badge">{categoria}</span><h1>{nome}</h1><p>{descricao}</p></section>
<div class="help">🖱️ Arraste • 🔍 Scroll • ✋ Botão direito</div>
<script type="importmap">{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"}}}}</script>
<script type="module">
import * as THREE from 'three';import {{OrbitControls}} from 'three/addons/controls/OrbitControls.js';import {{GLTFLoader}} from 'three/addons/loaders/GLTFLoader.js';
const viewer=document.getElementById('viewer'),status=document.getElementById('status');const scene=new THREE.Scene();scene.background=new THREE.Color(0x0a0b0f);scene.fog=new THREE.Fog(0x0a0b0f,18,45);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.01,1000);camera.position.set(5.4,3.4,7.4);const renderer=new THREE.WebGLRenderer({{antialias:true,powerPreference:'high-performance'}});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;viewer.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.enablePan=true;controls.enableZoom=true;controls.minDistance=1;controls.maxDistance=30;scene.add(new THREE.HemisphereLight(0xffffff,0x202532,2));const key=new THREE.DirectionalLight(0xffffff,3);key.position.set(6,9,7);scene.add(key);const fill=new THREE.DirectionalLight(0xc9a961,1.5);fill.position.set(-6,3,-4);scene.add(fill);
new GLTFLoader().load('{caminho_modelo}',g=>{{const o=g.scene,b=new THREE.Box3().setFromObject(o),s=b.getSize(new THREE.Vector3()),c=b.getCenter(new THREE.Vector3()),m=Math.max(s.x,s.y,s.z);if(m>0){{const k=5/m;o.scale.setScalar(k);o.position.set(-c.x*k,-c.y*k,-c.z*k)}}scene.add(o);controls.target.copy(new THREE.Box3().setFromObject(o).getCenter(new THREE.Vector3()));controls.update();status.textContent='Modelo 3D pronto.'}},undefined,e=>{{console.error(e);status.textContent='Não foi possível carregar o modelo 3D.'}});
addEventListener('resize',()=>{{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)}});(function loop(){{requestAnimationFrame(loop);controls.update();renderer.render(scene,camera)}})();
</script></body></html>'''

@app.route("/")
def catalogo():
    catalogo = carregar_catalogo()
    if not catalogo:
        return ("<h1>Catálogo vazio</h1><p>Verifique o arquivo veiculos.json.</p>", 500)
    categorias = {}
    for codigo, dados in catalogo.items():
        categoria = dados.get("categoria", "Outros")
        categorias.setdefault(categoria, []).append((codigo, dados))

    cards=[]
    for codigo,dados in catalogo.items():
        categoria=dados.get("categoria","Outros"); descricao=dados.get("descricao",""); modelo=criar_url_modelo(dados["arquivo"])
        args=", ".join([json.dumps(codigo,ensure_ascii=False),json.dumps(modelo,ensure_ascii=False),json.dumps(dados["nome"],ensure_ascii=False),json.dumps(categoria,ensure_ascii=False),json.dumps(descricao,ensure_ascii=False)])
        cards.append(f'''<article class="card" data-category="{categoria}" data-name="{dados["nome"].lower()}" data-code="{codigo}">
<button class="preview" type="button" onclick='abrirModal3D({args})'><canvas class="thumb"></canvas><span class="thumb-loading">3D</span><span class="preview-tag">3D</span></button>
<div class="content"><div class="meta"><span class="badge">{categoria}</span><span>#{codigo}</span></div><button class="name" type="button" onclick='abrirModal3D({args})'>{dados["nome"]}</button><p>{descricao}</p><div class="actions"><button class="primary" type="button" onclick='abrirModal3D({args})'>Ver em 3D</button><button class="secondary" type="button" onclick='abrirQRCode({json.dumps(codigo,ensure_ascii=False)},{json.dumps(dados["nome"],ensure_ascii=False)})'>QR Code</button></div></div></article>''')

    nav=[];mobile=[]
    for categoria,veiculos in categorias.items():
        db=[];mb=[]
        for codigo,dados in veiculos:
            modelo=criar_url_modelo(dados["arquivo"]);args=", ".join([json.dumps(codigo,ensure_ascii=False),json.dumps(modelo,ensure_ascii=False),json.dumps(dados["nome"],ensure_ascii=False),json.dumps(dados.get("categoria",categoria),ensure_ascii=False),json.dumps(dados.get("descricao",""),ensure_ascii=False)])
            db.append(f'''<button type="button" onclick='abrirModal3D({args})'>{dados["nome"]}<span>›</span></button>''')
            mb.append(f'''<button type="button" onclick='abrirModal3D({args})'>{dados["nome"]}</button>''')
        nav.append(f'''<div class="nav-item"><button class="nav-trigger" type="button">{categoria}</button><div class="dropdown">{"".join(db)}</div></div>''')
        mobile.append(f'''<div class="mobile-cat"><button type="button" onclick="this.parentElement.classList.toggle('open')"><span>{categoria}</span><span>＋</span></button><div>{"".join(mb)}</div></div>''')
    filters=['<button class="filter active" data-filter="Todos" onclick="filtrar(\'Todos\')">Todos</button>']+[f'<button class="filter" data-filter="{c}" onclick="filtrar({json.dumps(c,ensure_ascii=False)})">{c}</button>' for c in categorias]

    return '''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0a0b0f"><title>AUTO3D — Catálogo de Veículos 3D</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{{--bg:#0a0b0f;--s:#0f1117;--s2:#14161d;--line:rgba(255,255,255,.09);--txt:#f5f7fb;--muted:#98a1b2;--gold:#c9a961;--gold2:#d4b476;--shadow:0 20px 60px rgba(0,0,0,.5)}}
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;background:radial-gradient(circle at 75% 10%,rgba(201,169,97,.075),transparent 28%),var(--bg);color:var(--txt);font-family:Inter,Arial,sans-serif}}body:before{{content:"";position:fixed;inset:0;pointer-events:none;opacity:.25;background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:48px 48px}}body.modal-open{{overflow:hidden}}button,input{{font:inherit}}button{{cursor:pointer}}
.header{{position:sticky;top:0;z-index:100;border-bottom:1px solid rgba(255,255,255,.07);background:rgba(10,11,15,.78);backdrop-filter:blur(20px)}}.header-inner{{width:min(1400px,calc(100% - 40px));height:74px;margin:auto;display:flex;align-items:center;gap:26px}}.logo{{display:flex;align-items:center;gap:10px;color:white;text-decoration:none}}.mark{{width:36px;height:36px;display:grid;place-items:center;border-radius:11px;background:linear-gradient(135deg,var(--gold),var(--gold2));color:#111}}.logo b{{font:700 17px "Space Grotesk";letter-spacing:.14em}}.nav{{display:flex;gap:4px;flex:1}}.nav-item{{position:relative}}.nav-trigger{{border:0;background:transparent;color:#b7bfcc;padding:10px 12px;border-radius:9px}}.nav-trigger:hover{{color:white;background:rgba(255,255,255,.055)}}.dropdown{{position:absolute;top:calc(100% + 8px);left:0;width:270px;padding:8px;border:1px solid var(--line);border-radius:14px;background:rgba(15,17,23,.98);box-shadow:var(--shadow);opacity:0;visibility:hidden;transform:translateY(7px);transition:.2s}}.nav-item:hover .dropdown{{opacity:1;visibility:visible;transform:none}}.dropdown button{{width:100%;display:flex;justify-content:space-between;padding:11px 12px;border:0;border-radius:9px;background:transparent;color:#c7ceda;text-align:left}}.dropdown button:hover{{background:rgba(201,169,97,.09);color:white}}.search{{position:relative;width:220px}}.search input{{width:100%;border:1px solid var(--line);border-radius:11px;padding:10px 12px 10px 34px;background:rgba(255,255,255,.035);color:white;outline:0}}.search span{{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#778092}}.hamb{{display:none;margin-left:auto;width:42px;height:42px;border:1px solid var(--line);border-radius:11px;background:#ffffff08;color:white;font-size:20px}}.mobile{{display:none;padding:10px 20px 20px;border-top:1px solid var(--line)}}.mobile.open{{display:block}}.mobile-cat{{padding:13px 0;border-bottom:1px solid var(--line)}}.mobile-cat>button{{width:100%;display:flex;justify-content:space-between;border:0;background:none;color:white;padding:0}}.mobile-cat>div{{display:none;padding:8px 0 0 14px}}.mobile-cat.open>div{{display:block}}.mobile-cat div button{{display:block;width:100%;border:0;background:none;color:var(--muted);text-align:left;padding:9px 0}}
.hero{{min-height:470px;display:grid;align-items:center;border-bottom:1px solid #ffffff0e;position:relative;overflow:hidden}}.hero:before{{content:"";position:absolute;width:650px;height:650px;right:-160px;top:-280px;border-radius:50%;background:radial-gradient(circle,rgba(201,169,97,.13),transparent 68%)}}.hero-in{{position:relative;z-index:1;width:min(1400px,calc(100% - 40px));margin:auto;padding:82px 0 74px}}.kicker{{color:var(--gold2);font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase}}.kicker:before{{content:"";display:inline-block;width:30px;height:1px;background:var(--gold);vertical-align:middle;margin-right:9px}}.hero h1{{max-width:850px;margin:22px 0 0;font:700 clamp(46px,7vw,86px)/.95 "Space Grotesk";letter-spacing:-.055em}}.hero h1 span{{color:var(--gold2)}}.hero p{{max-width:660px;margin:26px 0 0;color:#aab2c0;font-size:17px;line-height:1.75}}.stats{{display:flex;gap:34px;margin-top:38px}}.stat b{{display:block;font:700 25px "Space Grotesk"}}.stat small{{display:block;margin-top:6px;color:#737c8d;font-size:11px;text-transform:uppercase;letter-spacing:.1em}}
.main{{width:min(1400px,calc(100% - 40px));margin:auto}}.filters{{position:sticky;top:74px;z-index:30;display:flex;gap:8px;padding:18px 0;overflow:auto;background:linear-gradient(var(--bg) 72%,transparent);scrollbar-width:none}}.filter{{flex:0 0 auto;padding:9px 15px;border:1px solid var(--line);border-radius:999px;background:#ffffff06;color:#9da6b5}}.filter.active{{background:var(--gold);border-color:var(--gold);color:#111;font-weight:700}}.title{{display:flex;align-items:center;gap:15px;margin:24px 0 18px}}.title h2{{margin:0;font:600 23px "Space Grotesk"}}.title:after{{content:"";height:1px;flex:1;background:linear-gradient(90deg,#c9a96155,transparent)}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}}.card{{overflow:hidden;border:1px solid var(--line);border-radius:16px;background:linear-gradient(145deg,#14161df5,#0d0f14f5);box-shadow:0 12px 35px #00000030;transition:.28s}}.card:hover{{transform:translateY(-6px);border-color:#c9a96159;box-shadow:0 25px 60px #0000006b}}.card.hidden{{display:none}}.preview{{position:relative;width:100%;height:225px;padding:0;overflow:hidden;border:0;border-bottom:1px solid var(--line);background:radial-gradient(circle,#c9a96118,transparent 45%),#11141b}}.thumb{{position:absolute;inset:0;width:100%;height:100%;transition:.45s}}.preview:hover .thumb{{transform:scale(1.045)}}.thumb-loading{{position:absolute;inset:0;display:grid;place-items:center;color:#777;font-size:12px}}.preview-tag{{position:absolute;right:12px;top:12px;padding:5px 8px;border-radius:7px;background:#0a0b0fa6;border:1px solid var(--line);color:var(--gold);font-size:10px;font-weight:700}}.content{{padding:18px}}.meta{{display:flex;justify-content:space-between;color:#5f6878;font-size:10px}}.badge{{padding:5px 8px;border:1px solid #c9a96138;border-radius:999px;background:#c9a96114;color:var(--gold2);font-size:10px;font-weight:700;text-transform:uppercase}}.name{{display:block;width:100%;padding:0;margin:12px 0 8px;border:0;background:none;color:white;text-align:left;font:600 23px "Space Grotesk"}}.name:hover{{color:var(--gold2)}}.content p{{min-height:48px;margin:0;color:var(--muted);font-size:13px;line-height:1.6;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}.actions{{display:grid;grid-template-columns:1.25fr .75fr;gap:8px;margin-top:18px}}.primary,.secondary{{min-height:42px;border-radius:10px;font-weight:600}}.primary{{border:1px solid var(--gold);background:var(--gold);color:#111}}.secondary{{border:1px solid var(--line);background:#ffffff09;color:#d5dae3}}.footer{{margin-top:75px;padding:34px 0 42px;border-top:1px solid var(--line);color:#697384;text-align:center;font-size:12px}}
.modal,.qr{{position:fixed;inset:0;z-index:1000;display:grid;place-items:center;padding:5vh 5vw;background:#040508c7;backdrop-filter:blur(9px);opacity:0;visibility:hidden;transition:.25s}}.modal.open,.qr.open{{opacity:1;visibility:visible}}.shell{{position:relative;width:100%;height:90vh;overflow:hidden;border:1px solid var(--line);border-radius:20px;background:#0a0b0f;box-shadow:0 30px 100px #000000b3;transform:scale(.95);transition:.25s}}.modal.open .shell{{transform:scale(1)}}.modal-view{{position:absolute;inset:0}}.modal-view canvas{{display:block;width:100%;height:100%}}.close{{position:absolute;right:18px;top:18px;z-index:10;width:42px;height:42px;border:1px solid #ffffff1f;border-radius:50%;background:#0a0b0fa6;color:white;font-size:22px}}.modal-info{{position:absolute;left:22px;bottom:22px;z-index:5;width:min(430px,calc(100% - 44px));padding:22px;border:1px solid #ffffff1a;border-radius:17px;background:#0f1117cc;backdrop-filter:blur(22px)}}.modal-info h2{{margin:10px 0 7px;font:700 30px "Space Grotesk"}}.modal-info p{{color:var(--muted);font-size:13px;line-height:1.65}}.modal-actions{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:17px}}.modal-action{{min-height:40px;border-radius:9px;border:1px solid var(--line);background:#ffffff09;color:white;font-weight:600}}.modal-action.gold{{background:var(--gold);border-color:var(--gold);color:#111}}.loading{{position:absolute;inset:0;z-index:4;display:grid;place-items:center;background:#0a0b0f66}}.loading.hide{{opacity:0;pointer-events:none}}.spinner{{width:38px;height:38px;border:3px solid #ffffff1f;border-top-color:var(--gold);border-radius:50%;animation:spin .8s linear infinite}}@keyframes spin{{to{{transform:rotate(360deg)}}}}
.qr-box{{width:min(390px,100%);padding:25px;border:1px solid var(--line);border-radius:20px;background:var(--s);text-align:center;box-shadow:var(--shadow)}}.qr-box h3{{margin:0 0 5px;font:600 25px "Space Grotesk"}}.qr-box p{{margin:0 0 18px;color:var(--muted);font-size:13px}}.qr-img{{width:245px;height:245px;margin:auto;background:white;border-radius:15px;overflow:hidden}}.qr-img img{{width:100%;height:100%}}.qr-actions{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:18px}}
@media(max-width:900px){{.nav,.search{{display:none}}.hamb{{display:block}}.header-inner{{height:64px}}.filters{{top:64px}}}}@media(max-width:600px){{.header-inner,.main,.hero-in{{width:calc(100% - 24px)}}.hero{{min-height:430px}}.hero-in{{padding:65px 0}}.hero h1{{font-size:47px}}.grid{{grid-template-columns:1fr}}.modal,.qr{{padding:0}}.shell{{height:100vh;border-radius:0;border:0}}.modal-info{{left:12px;right:12px;bottom:12px;width:auto;padding:17px}.modal-info h2{{font-size:24px}}}}
</style></head><body>
<header class="header"><div class="header-inner"><a class="logo" href="/"><span class="mark">◆</span><b>AUTO3D</b></a><nav class="nav">__NAV__<div class="nav-item"><button class="nav-trigger" onclick="filtrar('Todos')">Todos</button></div></nav><label class="search"><span>⌕</span><input id="search" type="search" placeholder="Buscar veículo..."></label><button class="hamb" onclick="document.getElementById('mobile').classList.toggle('open')">☰</button></div><div class="mobile" id="mobile">__MOBILE__</div></header>
<section class="hero"><div class="hero-in"><div class="kicker">Digital showroom • Experiência 3D</div><h1>Catálogo de<br><span>Veículos 3D</span></h1><p>Explore cada detalhe em tempo real. Rotacione, aproxime e descubra os modelos em uma experiência imersiva de visualização 3D.</p><div class="stats"><div class="stat"><b>__COUNT__</b><small>Veículos</small></div><div class="stat"><b>__CATEGORIES_COUNT__</b><small>Categorias</small></div><div class="stat"><b>3D</b><small>Interativo</small></div></div></div></section>
<main class="main"><div class="filters">__FILTERS__</div><div class="title"><h2>Todos os modelos</h2></div><section class="grid" id="grid">__CARDS__</section></main>
<footer class="footer">AUTO3D • __COUNT__ veículos cadastrados • 2026</footer>
<div class="modal" id="modal" onclick="fecharModal(event)"><div class="shell" onclick="event.stopPropagation()"><button class="close" onclick="fecharModal()">×</button><div class="modal-view" id="modalView"></div><div class="loading" id="loading"><div class="spinner"></div></div><aside class="modal-info"><span class="badge" id="mCat">Veículo</span><h2 id="mName">Veículo</h2><p id="mDesc"></p><div class="modal-actions"><button class="modal-action gold" id="mQr">Baixar QR Code</button><button class="modal-action" id="mCopy">Copiar link</button></div></aside></div></div>
<div class="qr" id="qr" onclick="fecharQr(event)"><div class="qr-box" onclick="event.stopPropagation()"><h3 id="qrTitle">QR Code</h3><p>Aponte a câmera do celular para abrir o veículo em 3D.</p><div class="qr-img"><img id="qrImg"></div><div class="qr-actions"><button class="modal-action gold" id="qrDownload">Baixar PNG</button><button class="modal-action" onclick="fecharQr()">Fechar</button></div></div></div>
<script type="importmap">{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"}}}}</script>
<script type="module">
import * as THREE from 'three';import {{GLTFLoader}} from 'three/addons/loaders/GLTFLoader.js';import {{OrbitControls}} from 'three/addons/controls/OrbitControls.js';
const DATA=__DATA__;let renderer=null,scene=null,camera=null,controls=null,obj=null,anim=null,currentCode=null;
function dispose(o){{if(!o)return;o.traverse(c=>{{if(c.geometry)c.geometry.dispose();if(c.material){{(Array.isArray(c.material)?c.material:[c.material]).forEach(m=>{{Object.values(m).forEach(v=>{{if(v&&v.isTexture)v.dispose()}});m.dispose()}})}}}})}}
function destroy(){{if(anim)cancelAnimationFrame(anim);if(controls)controls.dispose();if(obj)dispose(obj);if(renderer){{renderer.dispose();renderer.domElement.remove()}}renderer=scene=camera=controls=obj=anim=null}}
window.abrirModal3D=(codigo,modelo,nome,categoria,descricao)=>{{currentCode=codigo;document.getElementById('mName').textContent=nome;document.getElementById('mCat').textContent=categoria;document.getElementById('mDesc').textContent=descricao;document.getElementById('modal').classList.add('open');document.body.classList.add('modal-open');document.getElementById('loading').classList.remove('hide');destroy();const v=document.getElementById('modalView');v.innerHTML='';scene=new THREE.Scene();scene.background=new THREE.Color(0x0a0b0f);camera=new THREE.PerspectiveCamera(42,(v.clientWidth||innerWidth)/(v.clientHeight||innerHeight),.01,1000);camera.position.set(5.4,3.4,7.4);renderer=new THREE.WebGLRenderer({{antialias:true,powerPreference:'high-performance'}});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(v.clientWidth||innerWidth,v.clientHeight||innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;v.appendChild(renderer.domElement);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.enablePan=true;controls.enableZoom=true;scene.add(new THREE.HemisphereLight(0xffffff,0x202532,2));let l=new THREE.DirectionalLight(0xffffff,3);l.position.set(6,9,7);scene.add(l);l=new THREE.DirectionalLight(0xc9a961,1.5);l.position.set(-6,3,-4);scene.add(l);new GLTFLoader().load(modelo,g=>{{obj=g.scene;let b=new THREE.Box3().setFromObject(obj),s=b.getSize(new THREE.Vector3()),c=b.getCenter(new THREE.Vector3()),m=Math.max(s.x,s.y,s.z);if(m>0){{let k=5/m;obj.scale.setScalar(k);obj.position.set(-c.x*k,-c.y*k,-c.z*k)}}scene.add(obj);controls.target.copy(new THREE.Box3().setFromObject(obj).getCenter(new THREE.Vector3()));controls.update();document.getElementById('loading').classList.add('hide')}},undefined,e=>{{console.error(e);document.getElementById('loading').textContent='Não foi possível carregar o modelo 3D.'}});(function loop(){{if(!renderer)return;anim=requestAnimationFrame(loop);controls.update();renderer.render(scene,camera)}})()}};
window.fecharModal=e=>{{if(e&&e.target!==document.getElementById('modal'))return;document.getElementById('modal').classList.remove('open');document.body.classList.remove('modal-open');destroy();document.getElementById('modalView').innerHTML=''}};
addEventListener('resize',()=>{{if(renderer&&camera){{let v=document.getElementById('modalView');camera.aspect=v.clientWidth/v.clientHeight;camera.updateProjectionMatrix();renderer.setSize(v.clientWidth,v.clientHeight)}}}});
function downloadQr(c){{let a=document.createElement('a');a.href='/qrcode/'+encodeURIComponent(c);a.download='qrcode-'+c+'.png';document.body.appendChild(a);a.click();a.remove()}}window.abrirQRCode=(c,n)=>{{document.getElementById('qrTitle').textContent=n;document.getElementById('qrImg').src='/qrcode/'+encodeURIComponent(c);document.getElementById('qrDownload').onclick=()=>downloadQr(c);document.getElementById('qr').classList.add('open')}};window.fecharQr=e=>{{if(e&&e.target!==document.getElementById('qr'))return;document.getElementById('qr').classList.remove('open')}};document.getElementById('mQr').onclick=()=>currentCode&&downloadQr(currentCode);document.getElementById('mCopy').onclick=async()=>{{let u=location.origin+'/objeto/'+encodeURIComponent(currentCode);try{{await navigator.clipboard.writeText(u);document.getElementById('mCopy').textContent='Link copiado ✓';setTimeout(()=>document.getElementById('mCopy').textContent='Copiar link',1600)}}catch(e){{prompt('Copie o link:',u)}}}};
window.filtrar=c=>{{document.querySelectorAll('.filter').forEach(b=>b.classList.toggle('active',b.dataset.filter===c));document.querySelectorAll('.card').forEach(x=>x.classList.toggle('hidden',c!=='Todos'&&x.dataset.category!==c))}};document.getElementById('search').addEventListener('input',e=>{{let t=e.target.value.toLowerCase().trim();document.querySelectorAll('.card').forEach(x=>x.classList.toggle('hidden',!!t&&!x.dataset.name.includes(t)))}});document.addEventListener('keydown',e=>{{if(e.key==='Escape'){{if(document.getElementById('qr').classList.contains('open'))fecharQr();else fecharModal()}}}});
/* Miniaturas 3D leves, sem controles, para manter a vitrine visual. */
document.querySelectorAll('.card').forEach(card=>{{let code=card.dataset.code,data=DATA.find(x=>x.codigo===code),canvas=card.querySelector('.thumb'),load=card.querySelector('.thumb-loading');if(!data)return;let s=new THREE.Scene();s.background=new THREE.Color(0x12151c);let c=new THREE.PerspectiveCamera(35,600/430,.01,100);c.position.set(5.2,2.8,7);let r=new THREE.WebGLRenderer({{canvas,antialias:true,powerPreference:'low-power'}});r.setPixelRatio(1);r.setSize(600,430,false);r.outputColorSpace=THREE.SRGBColorSpace;s.add(new THREE.HemisphereLight(0xffffff,0x202532,2));let l=new THREE.DirectionalLight(0xffffff,2.8);l.position.set(5,8,7);s.add(l);new GLTFLoader().load(data.modelo,g=>{{let o=g.scene,b=new THREE.Box3().setFromObject(o),z=b.getSize(new THREE.Vector3()),q=b.getCenter(new THREE.Vector3()),m=Math.max(z.x,z.y,z.z);if(m>0){{let k=4/m;o.scale.setScalar(k);o.position.set(-q.x*k,-q.y*k,-q.z*k)}}s.add(o);c.lookAt(0,0,0);load.style.display='none';let n=0;function spin(){{if(n++<180){{requestAnimationFrame(spin);o.rotation.y+=.0025;r.render(s,c)}}}}spin();}},undefined,()=>load.textContent='◇')}});
</script></body></html>'''.replace('{{','{').replace('}}','}').replace('__NAV__',''.join(nav)).replace('__MOBILE__',''.join(mobile)).replace('__FILTERS__',''.join(filters)).replace('__CARDS__',''.join(cards)).replace('__COUNT__',str(len(catalogo))).replace('__CATEGORIES_COUNT__',str(len(categorias))).replace('__DATA__',json.dumps([{"codigo":c,"nome":d["nome"],"modelo":criar_url_modelo(d["arquivo"])} for c,d in catalogo.items()],ensure_ascii=False))


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
