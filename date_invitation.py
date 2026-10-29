import json
import os
from datetime import datetime

try:
    from flask import Flask, jsonify, request
except ImportError:
    raise SystemExit("Требуется Flask. Выполните:  pip install flask")

# ===================== НАСТРОЙКИ =====================
TELEGRAM_USERNAME = os.environ.get("TELEGRAM_USERNAME", "your_username")
PORT = int(os.environ.get("PORT", 5000))
# ========================================================


TELEGRAM_USERNAME = TELEGRAM_USERNAME.strip().lstrip("@") or "your_username"
ANSWERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "date_answers.jsonl")

app = Flask(__name__)

PAGE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#B2F2D8">
<title>Пойдешь со мной на свидание? 💌</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💌</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shrikhand&family=Nunito:ital,wght@0,400;0,700;0,800;1,400&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --mint:#B2F2D8; --mint-2:#DFFAEF; --navy:#121A3A;
  --navy-70:rgba(18,26,58,.7); --coral:#FF8FAB; --bsod:#0078D7;
}
html{scroll-behavior:smooth}
body{
  font-family:'Nunito',system-ui,sans-serif; color:var(--navy);
  background:var(--mint); min-height:100vh; overflow-x:hidden;
}
body.locked{overflow:hidden}

/* ---------- анимированный фон ---------- */
#sky{
  position:fixed; inset:0; z-index:0; pointer-events:none; overflow:hidden;
  background:
    radial-gradient(900px 480px at 82% -10%, rgba(255,255,255,.65), transparent 65%),
    radial-gradient(760px 460px at -8% 108%, rgba(18,26,58,.14), transparent 60%);
}
#sky::before{
  content:""; position:absolute; inset:0;
  background-image:radial-gradient(rgba(18,26,58,.10) 1.6px, transparent 1.7px);
  background-size:30px 30px;
}
.float-heart{position:absolute; top:100%; animation:rise linear infinite; will-change:transform,opacity}
@keyframes rise{
  0%{transform:translate(0,10vh) rotate(0);opacity:0}
  12%{opacity:var(--o)} 88%{opacity:var(--o)}
  100%{transform:translate(var(--drift),-120vh) rotate(26deg);opacity:0}
}

/* ---------- экраны ---------- */
.screen{min-height:100vh;display:none;align-items:center;justify-content:center;
  padding:40px 20px;position:relative;z-index:1}
.screen.active{display:flex;animation:screen-in .55s cubic-bezier(.2,.9,.25,1.15) both}
@keyframes screen-in{from{opacity:0;transform:translateY(28px) scale(.985)}to{opacity:1;transform:none}}

/* ---------- приглашение ---------- */
.invite{text-align:center;max-width:840px}
.kitty-wrap{position:relative;display:inline-block;animation:bob 3.4s ease-in-out infinite}
.kitty-wrap svg{width:clamp(168px,32vw,248px);height:auto;display:block;
  filter:drop-shadow(0 16px 22px rgba(18,26,58,.20))}
.kitty-shadow{width:140px;height:18px;border-radius:50%;background:rgba(18,26,58,.18);
  margin:8px auto 0;filter:blur(4px);animation:shadow-pulse 3.4s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-11px)}}
@keyframes shadow-pulse{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.85)}}
.tw{transform-box:fill-box;transform-origin:center;animation:twinkle 2.6s ease-in-out infinite}
.t2{animation-delay:.9s}.t3{animation-delay:1.7s}
@keyframes twinkle{0%,100%{opacity:.25;transform:scale(.7)}50%{opacity:1;transform:scale(1.1)}}

h1{font-family:'Shrikhand',cursive;font-weight:400;font-size:clamp(2.1rem,5.8vw,4.3rem);
  line-height:1.1;margin:26px 0 8px;text-wrap:balance}
h1 span{text-decoration:underline wavy var(--coral);
  text-decoration-thickness:5px;text-underline-offset:9px}
.sub{font-style:italic;color:var(--navy-70);font-size:1.06rem}
.invite-foot{position:absolute;bottom:16px;left:0;right:0;text-align:center;
  font-weight:800;font-size:.8rem;letter-spacing:1.5px;text-transform:uppercase;opacity:.45}

.choices{display:flex;gap:18px;justify-content:center;margin-top:36px;flex-wrap:wrap}
.btn{font-family:'Nunito',sans-serif;font-weight:800;font-size:1.22rem;border:none;
  cursor:pointer;padding:16px 44px;border-radius:999px;letter-spacing:.3px;
  transition:transform .18s ease, box-shadow .18s ease, background .18s ease, opacity .18s}
.btn:active{transform:scale(var(--grow,1)) translateY(2px)!important}
.btn-yes{background:var(--navy);color:var(--mint);transform:scale(var(--grow,1));
  box-shadow:0 9px 0 rgba(18,26,58,.30), 0 20px 34px rgba(18,26,58,.25)}
.btn-yes:hover{transform:scale(var(--grow,1)) translateY(-4px) rotate(-1.2deg);
  box-shadow:0 13px 0 rgba(18,26,58,.30), 0 26px 40px rgba(18,26,58,.28)}
.btn-no{background:transparent;color:var(--navy);border:3px solid var(--navy);
  transform:scale(var(--shrink,1))}
.btn-no:hover{animation:wobble .45s ease-in-out}
@keyframes wobble{0%,100%{transform:scale(var(--shrink,1)) rotate(0)}
  25%{transform:scale(var(--shrink,1)) rotate(-5deg)}
  75%{transform:scale(var(--shrink,1)) rotate(5deg)}}

/* вылетающие сердечки */
.pop-heart{position:fixed;z-index:60;pointer-events:none;font-size:22px;
  transform:translate(-50%,-50%);animation:popfly .9s cubic-bezier(.2,.7,.3,1) forwards}
@keyframes popfly{to{transform:translate(calc(var(--dx) - 50%),calc(var(--dy) - 50%)) scale(.4) rotate(30deg);opacity:0}}

/* ---------- окно планирования (оверлей) ---------- */
#screen-plan{display:none;position:fixed;inset:0;z-index:20;overflow:auto;padding:28px 16px;
  background:rgba(18,26,58,.45);backdrop-filter:blur(4px)}
#screen-plan.open{display:flex}
.window{margin:auto;width:min(680px,100%);background:var(--mint-2);
  border:3px solid var(--navy);border-radius:18px;overflow:hidden;
  box-shadow:14px 14px 0 rgba(18,26,58,.18);animation:screen-in .5s cubic-bezier(.2,.9,.25,1.15) both}
.window-bar{display:flex;align-items:center;gap:12px;background:var(--navy);
  color:var(--mint);padding:10px 14px}
.dots{display:flex;gap:6px}
.dots i{width:11px;height:11px;border-radius:50%;background:var(--mint);opacity:.35}
.dots i:nth-child(1){background:var(--coral);opacity:.95}
.dots i:nth-child(2){background:var(--mint);opacity:.8}
.window-title{flex:1;text-align:center;font-weight:800;letter-spacing:1.5px;font-size:.82rem;opacity:.95}
.window-close{background:none;border:none;color:var(--mint);font-size:1rem;cursor:pointer;
  width:30px;height:30px;border-radius:8px;line-height:1;transition:.15s}
.window-close:hover{background:rgba(255,255,255,.18);transform:rotate(90deg)}
.window-body{padding:26px clamp(18px,4vw,38px) 34px}
.window-body h2{font-family:'Shrikhand',cursive;font-weight:400;
  font-size:clamp(1.5rem,3.4vw,2.15rem);line-height:1.2;margin-bottom:4px}
.window-sub{color:var(--navy-70);font-style:italic;margin-bottom:6px}

.field-label{display:block;font-weight:800;margin:20px 0 8px;font-size:1.03rem}
input[type=text]{width:100%;padding:14px 16px;font:inherit;font-size:1.05rem;font-weight:700;
  border:3px solid var(--navy);border-radius:12px;background:#fff;color:var(--navy);transition:.15s}
input[type=text]::placeholder{color:rgba(18,26,58,.4);font-weight:400;font-style:italic}
input[type=text]:focus{outline:none;box-shadow:0 0 0 4px rgba(18,26,58,.18)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.chips button{font:inherit;font-weight:700;font-size:.88rem;background:transparent;
  border:2px solid rgba(18,26,58,.45);border-radius:999px;padding:6px 14px;cursor:pointer;
  color:var(--navy);transition:.15s}
.chips button:hover{background:var(--navy);color:var(--mint);transform:translateY(-2px)}

.picker{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:6px}
.cal,.times{background:rgba(255,255,255,.68);border:2px solid var(--navy);
  border-radius:14px;padding:14px}
.cal-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.cal-head strong{font-size:.98rem;letter-spacing:.4px}
.cal-head button{width:32px;height:32px;border-radius:10px;border:2px solid var(--navy);
  background:transparent;color:var(--navy);font-size:1.15rem;font-weight:800;cursor:pointer;transition:.15s}
.cal-head button:hover:not(:disabled){background:var(--navy);color:var(--mint)}
.cal-head button:disabled{opacity:.25;cursor:default}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}
.cal-grid .wd{font-size:.7rem;font-weight:800;text-align:center;opacity:.55;padding:4px 0;letter-spacing:.6px}
.day{aspect-ratio:1;border:none;background:transparent;border-radius:10px;font:inherit;
  font-weight:700;color:var(--navy);cursor:pointer;transition:.12s;position:relative}
.day:hover:not(:disabled){background:rgba(18,26,58,.14);transform:scale(1.1)}
.day:disabled{opacity:.25;cursor:default}
.day.today::after{content:"";position:absolute;left:50%;bottom:3px;width:4px;height:4px;
  margin-left:-2px;border-radius:50%;background:var(--coral)}
.day.sel{background:var(--navy);color:var(--mint);box-shadow:0 4px 12px rgba(18,26,58,.35)}
.times-hint{font-style:italic;opacity:.65;margin-bottom:10px;font-size:.92rem}
.time-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(70px,1fr));gap:8px;
  max-height:252px;overflow-y:auto;padding-right:4px}
.time-grid::-webkit-scrollbar{width:8px}
.time-grid::-webkit-scrollbar-thumb{background:rgba(18,26,58,.35);border-radius:8px}
.slot{padding:8px 2px;border:2px solid rgba(18,26,58,.5);border-radius:10px;background:transparent;
  font:inherit;font-weight:800;font-size:.88rem;color:var(--navy);cursor:pointer;transition:.12s}
.slot:hover:not(:disabled){border-color:var(--navy);transform:translateY(-2px)}
.slot:disabled{opacity:.3;cursor:default}
.slot.sel{background:var(--navy);color:var(--mint);border-color:var(--navy)}

.summary{margin:22px 0 6px;font-weight:700;background:rgba(255,255,255,.6);
  border:2px dashed rgba(18,26,58,.4);border-radius:12px;padding:12px 14px;line-height:1.5}
.summary em{font-style:normal;opacity:.5;font-weight:400}
.summary .sep{opacity:.5;margin:0 4px}
.btn-confirm{width:100%;margin-top:14px;background:var(--navy);color:var(--mint);
  box-shadow:0 8px 0 rgba(18,26,58,.28)}
.btn-confirm:hover:not(:disabled){transform:translateY(-3px)}
.btn-confirm:disabled{opacity:.4;cursor:not-allowed;box-shadow:none}

/* ---------- экран успеха ---------- */
.done-card{text-align:center;background:var(--mint-2);border:3px solid var(--navy);
  border-radius:22px;padding:52px clamp(26px,5vw,64px);box-shadow:14px 14px 0 rgba(18,26,58,.18)}
.big-heart{font-size:4.2rem;animation:heartbeat 1.3s ease-in-out infinite;display:inline-block}
@keyframes heartbeat{0%,100%{transform:scale(1)}12%{transform:scale(1.2)}24%{transform:scale(1)}36%{transform:scale(1.12)}}
.done-card h2{font-family:'Shrikhand',cursive;font-weight:400;font-size:clamp(2rem,5vw,3rem);margin:10px 0 12px}
.done-card .details{font-weight:800;font-size:1.12rem;background:rgba(255,255,255,.7);
  border-radius:12px;padding:12px 18px;display:inline-block;margin-bottom:6px}
.done-card .btn{margin-top:26px}

/* ---------- СИНИЙ ЭКРАН СМЕРТИ ---------- */
#bsod{position:fixed;inset:0;z-index:100;background:var(--bsod);color:#fff;display:none;
  align-items:center;font-family:"Segoe UI",system-ui,sans-serif}
#bsod.show{display:flex;animation:bsod-flicker .4s steps(1,end)}
@keyframes bsod-flicker{0%{opacity:0}25%{opacity:1}40%{opacity:.15}55%{opacity:1}70%{opacity:.35}100%{opacity:1}}
.bsod-inner{width:min(780px,90vw);margin:0 auto;padding:44px 22px;
  font-size:clamp(15px,1.9vw,21px);line-height:1.6}
.bsod .sad{font-size:clamp(90px,16vw,158px);font-weight:200;line-height:1;margin-bottom:26px}
.bsod .pct{margin:30px 0 34px}
.bsod .fix p{margin:12px 0}
.bsod kbd{display:inline-block;padding:2px 10px;border:2px solid rgba(255,255,255,.9);
  border-radius:6px;font-family:inherit;font-weight:700;box-shadow:0 2px 0 rgba(255,255,255,.55)}
.bsod a{color:#fff;font-weight:700;text-underline-offset:3px}
.bsod a:hover{background:rgba(255,255,255,.22)}
.stoprow{display:flex;align-items:center;gap:22px;margin-top:46px}
.stoprow svg{flex:none;opacity:.95}
.stop{font-size:.85em;opacity:.92;line-height:1.5}
body.bsod-mode{overflow:hidden}

@media (max-width:680px){
  .picker{grid-template-columns:1fr}
  .btn{padding:15px 34px}
}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation:none!important;transition:none!important}
}
</style>
</head>
<body>
<div id="sky" aria-hidden="true"></div>

<!-- ================= ЭКРАН 1 : ВОПРОС ================= -->
<main id="screen-invite" class="screen active">
  <div class="invite">
    <div class="kitty-wrap">
      <svg viewBox="0 0 260 240" role="img" aria-label="Милый котик, держащий сердечко">
        <g class="tw t1"><path d="M30 60 l4 10 10 4 -10 4 -4 10 -4 -10 -10 -4 10 -4 z" fill="#121A3A" opacity=".5"/></g>
        <g class="tw t2"><path d="M226 96 l3 8 8 3 -8 3 -3 8 -3 -8 -8 -3 8 -3 z" fill="#FF8FAB"/></g>
        <g class="tw t3"><path d="M212 28 l3.5 9 9 3.5 -9 3.5 -3.5 9 -3.5 -9 -9 -3.5 9 -3.5 z" fill="#121A3A" opacity=".4"/></g>
        <path d="M198 192 q36 -4 32 -42 q-2 -16 -16 -19" fill="none" stroke="#121A3A" stroke-width="16" stroke-linecap="round"/>
        <path d="M84 62 L66 12 L118 44 Z" fill="#121A3A"/>
        <path d="M176 62 L194 12 L142 44 Z" fill="#121A3A"/>
        <path d="M87 52 L77 25 L106 43 Z" fill="#FF8FAB" opacity=".85"/>
        <path d="M173 52 L183 25 L154 43 Z" fill="#FF8FAB" opacity=".85"/>
        <ellipse cx="130" cy="104" rx="74" ry="64" fill="#121A3A"/>
        <ellipse cx="130" cy="188" rx="58" ry="44" fill="#121A3A"/>
        <ellipse cx="102" cy="223" rx="17" ry="9" fill="#121A3A"/>
        <ellipse cx="158" cy="223" rx="17" ry="9" fill="#121A3A"/>
        <path d="M130 208 C 102 190 90 172 96 158 C 100 148 114 146 130 160 C 146 146 160 148 164 158 C 170 172 158 190 130 208 Z" fill="#FF8FAB"/>
        <ellipse cx="111" cy="161" rx="7" ry="3.5" fill="#fff" opacity=".75" transform="rotate(-28 111 161)"/>
        <ellipse cx="99" cy="169" rx="11" ry="15" fill="#121A3A" transform="rotate(24 99 169)"/>
        <ellipse cx="161" cy="169" rx="11" ry="15" fill="#121A3A" transform="rotate(-24 161 169)"/>
        <path d="M100 96 q11 -14 22 0" stroke="#B2F2D8" stroke-width="6" fill="none" stroke-linecap="round"/>
        <path d="M138 96 q11 -14 22 0" stroke="#B2F2D8" stroke-width="6" fill="none" stroke-linecap="round"/>
        <circle cx="88" cy="116" r="9" fill="#FF8FAB" opacity=".9"/>
        <circle cx="172" cy="116" r="9" fill="#FF8FAB" opacity=".9"/>
        <path d="M124 110 h12 l-6 8 z" fill="#B2F2D8"/>
        <path d="M130 120 q-5 7 -13 5 M130 120 q5 7 13 5" stroke="#B2F2D8" stroke-width="3.5" fill="none" stroke-linecap="round"/>
        <g stroke="#B2F2D8" stroke-width="3" stroke-linecap="round" opacity=".85">
          <path d="M58 100 H32"/><path d="M60 112 L36 120"/>
          <path d="M202 100 H228"/><path d="M200 112 L224 120"/>
        </g>
      </svg>
      <div class="kitty-shadow"></div>
    </div>

    <h1>Пойдешь со мной на <span>свидание?</span></h1>
    <p class="sub">( ну пожалуйста, скажи да 🥺 )</p>

    <div class="choices">
      <button class="btn btn-yes" id="btn-yes" type="button">Да! 💖</button>
      <button class="btn btn-no" id="btn-no" type="button">Нет</button>
    </div>
  </div>
  <p class="invite-foot">100% без риска · 0% шансов пожалеть</p>
</main>

<!-- ================= ЭКРАН 2 : ОКНО ПЛАНИРОВАНИЯ ================= -->
<section id="screen-plan" aria-label="Планирование свидания">
  <div class="window">
    <header class="window-bar">
      <span class="dots"><i></i><i></i><i></i></span>
      <span class="window-title">plan_our_date.exe</span>
      <button class="window-close" id="plan-close" type="button" title="вернуться к вопросу">✕</button>
    </header>
    <div class="window-body">
      <h2>Урааа!! 🎉</h2>
      <p class="window-sub">а теперь важные детали… (неправильных ответов не бывает)</p>

      <label class="field-label" for="place">1 · Куда мы пойдем?</label>
      <input id="place" type="text" maxlength="120" autocomplete="off"
             placeholder="кафе, парк, кино… на твой выбор ✨">
      <div class="chips" id="chips">
        <button type="button">☕ Кофе</button>
        <button type="button">🎬 Кино</button>
        <button type="button">🌸 Прогулка в парке</button>
        <button type="button">🍦 Мороженое</button>
        <button type="button">🕹️ Игровые автоматы</button>
      </div>

      <span class="field-label">2 · Когда мы пойдем?</span>
      <div class="picker">
        <div class="cal">
          <div class="cal-head">
            <button id="cal-prev" type="button" aria-label="предыдущий месяц">‹</button>
            <strong id="cal-month"></strong>
            <button id="cal-next" type="button" aria-label="следующий месяц">›</button>
          </div>
          <div class="cal-grid" id="cal-days"></div>
        </div>
        <div class="times">
          <p class="times-hint" id="times-hint">сначала выбери день ✨</p>
          <div class="time-grid" id="time-grid"></div>
        </div>
      </div>

      <p class="summary" id="summary"></p>
      <button class="btn btn-confirm" id="btn-confirm" type="button" disabled>Подтвердить наше свидание 💘</button>
    </div>
  </div>
</section>

<!-- ================= ЭКРАН 3 : ДОГОВОРИЛИСЬ ================= -->
<section id="screen-done" class="screen">
  <div class="done-card">
    <span class="big-heart">💖</span>
    <h2>Договорились!</h2>
    <p class="details" id="done-summary"></p>
    <p class="sub">жду не дождусь ✨</p>
    <button class="btn btn-yes" id="btn-again" type="button">В начало</button>
  </div>
</section>

<!-- ================= СИНИЙ ЭКРАН СМЕРТИ ================= -->
<div id="bsod" role="alertdialog" aria-label="Ошибка">
  <div class="bsod-inner">
    <div class="sad">:(</div>
    <p>На вашем ПК возникла проблема, и его необходимо перезагрузить. Мы собираем данные об ошибке, а затем выполним перезагрузку.</p>
    <p class="pct"><span id="bsod-pct">0</span>% выполнено</p>
    <div class="fix">
      <p>Просто нажми <kbd>F5</kbd> или <kbd>Ctrl</kbd> + <kbd>R</kbd>, и всё будет хорошо.</p>
      <p>Напиши мне в Telegram — <a href="https://t.me/__TELEGRAM_USERNAME__" target="_blank" rel="noopener">@__TELEGRAM_USERNAME__</a></p>
    </div>
    <div class="stoprow">
      <svg width="66" height="58" viewBox="0 0 56 48" fill="#fff" aria-hidden="true">
        <rect x="8" y="0" width="8" height="8"/><rect x="16" y="0" width="8" height="8"/>
        <rect x="32" y="0" width="8" height="8"/><rect x="40" y="0" width="8" height="8"/>
        <rect x="0" y="8" width="56" height="16"/>
        <rect x="8" y="24" width="40" height="8"/>
        <rect x="16" y="32" width="24" height="8"/>
        <rect x="24" y="40" width="8" height="8"/>
      </svg>
      <p class="stop">Код остановки: DATE_DECLINED_EXCEPTION<br>Что сломалось: HEART.SYS</p>
    </div>
  </div>
</div>

<noscript><p style="position:fixed;inset:0;display:grid;place-items:center;background:#B2F2D8;font-weight:800">Пожалуйста, включите JavaScript, чтобы открыть это приглашение 💌</p></noscript>

<script>
(function(){
"use strict";
function $(id){return document.getElementById(id);}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
var MONTHS=["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"];
var today=new Date(); today.setHours(0,0,0,0);

/* ----- парящие сердечки и искорки ----- */
(function(){
  var sky=$("sky"), glyphs=["♥","♥","♡","✦"],
      colors=["rgba(18,26,58,.45)","rgba(255,143,171,.85)","rgba(255,255,255,.9)","rgba(18,26,58,.3)"];
  for(var i=0;i<18;i++){
    var s=document.createElement("span");
    s.className="float-heart";
    s.textContent=glyphs[i%glyphs.length];
    s.style.left=(Math.random()*100)+"vw";
    s.style.fontSize=(11+Math.random()*24)+"px";
    s.style.color=colors[i%colors.length];
    s.style.setProperty("--drift",(Math.random()*140-70)+"px");
    s.style.setProperty("--o",(0.25+Math.random()*0.5).toFixed(2));
    var dur=9+Math.random()*11;
    s.style.animationDuration=dur+"s";
    s.style.animationDelay=(-Math.random()*dur)+"s";
    sky.appendChild(s);
  }
})();

/* ----- экраны ----- */
var screens={invite:$("screen-invite"),done:$("screen-done")};
function show(name){
  var plan=$("screen-plan");
  if(name==="plan"){plan.classList.add("open");document.body.classList.add("locked");return;}
  plan.classList.remove("open");document.body.classList.remove("locked");
  screens.invite.classList.toggle("active",name==="invite");
  screens.done.classList.toggle("active",name==="done");
  window.scrollTo({top:0});
}
function burst(x,y,n){
  n=n||14; var g=["💖","💘","💕","✨","💗"];
  for(var i=0;i<n;i++){
    var p=document.createElement("span");
    p.className="pop-heart"; p.textContent=g[i%g.length];
    p.style.left=x+"px"; p.style.top=y+"px";
    var a=Math.random()*Math.PI*2, d=60+Math.random()*120;
    p.style.setProperty("--dx",(Math.cos(a)*d)+"px");
    p.style.setProperty("--dy",(Math.sin(a)*d-50)+"px");
    document.body.appendChild(p);
    (function(el){setTimeout(function(){el.remove();},950);})(p);
  }
}

/* ----- Да / Нет ----- */
var yes=$("btn-yes"), no=$("btn-no");
var noLabels=["нет?","ты уверена?","серьезно??","подумай еще раз 🥺","последний шанс!"];
var dodge=0;
no.addEventListener("mouseenter",function(){
  if(dodge<noLabels.length-1) dodge++;
  no.textContent=noLabels[dodge];
  no.style.setProperty("--shrink",Math.max(0.72,1-dodge*0.055).toFixed(3));
  yes.style.setProperty("--grow",Math.min(1.18,1+dodge*0.035).toFixed(3));
});
no.addEventListener("click",bsod);
yes.addEventListener("click",function(){
  var r=yes.getBoundingClientRect();
  burst(r.left+r.width/2,r.top+r.height/2,16);
  setTimeout(function(){show("plan");},180);
});
$("plan-close").addEventListener("click",function(){show("invite");});
$("btn-again").addEventListener("click",function(){show("invite");});
document.addEventListener("keydown",function(e){
  if(e.key==="Escape" && !bsodStarted) show("invite");
});

/* ----- состояние ----- */
var state={place:"",date:null,time:null};
var placeInput=$("place");
placeInput.addEventListener("input",function(){state.place=placeInput.value;validate();});
Array.prototype.forEach.call(document.querySelectorAll("#chips button"),function(ch){
  ch.addEventListener("click",function(){
    placeInput.value=ch.textContent; state.place=ch.textContent; validate();
    var r=ch.getBoundingClientRect();
    burst(r.left+r.width/2,r.top+r.height/2,6);
  });
});

/* ----- календарь ----- */
var view=new Date(today.getFullYear(),today.getMonth(),1);
var minMonth=new Date(today.getFullYear(),today.getMonth(),1);
var maxMonth=new Date(today.getFullYear(),today.getMonth()+11,1);
function sameDay(a,b){return a&&b&&a.getFullYear()===b.getFullYear()&&a.getMonth()===b.getMonth()&&a.getDate()===b.getDate();}
function renderCal(){
  $("cal-month").textContent=MONTHS[view.getMonth()]+" "+view.getFullYear();
  $("cal-prev").disabled=view<=minMonth;
  $("cal-next").disabled=view>=maxMonth;
  var grid=$("cal-days"); grid.innerHTML="";
  ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"].forEach(function(d){
    var w=document.createElement("span"); w.className="wd"; w.textContent=d; grid.appendChild(w);
  });
  var first=new Date(view.getFullYear(),view.getMonth(),1);
  var offset=(first.getDay()+6)%7;
  var total=new Date(view.getFullYear(),view.getMonth()+1,0).getDate();
  for(var i=0;i<offset;i++) grid.appendChild(document.createElement("span"));
  for(var d=1;d<=total;d++){
    (function(){
      var dt=new Date(view.getFullYear(),view.getMonth(),d);
      var b=document.createElement("button");
      b.type="button"; b.className="day"; b.textContent=d;
      if(sameDay(dt,today)) b.classList.add("today");
      if(dt<today){b.disabled=true;}
      else{b.addEventListener("click",function(){selectDate(dt);});}
      if(sameDay(dt,state.date)) b.classList.add("sel");
      grid.appendChild(b);
    })();
  }
}
$("cal-prev").addEventListener("click",function(){view.setMonth(view.getMonth()-1);renderCal();});
$("cal-next").addEventListener("click",function(){view.setMonth(view.getMonth()+1);renderCal();});

/* ----- слоты времени: 09:00 → 22:00, каждые 30 минут ----- */
function buildTimes(){
  var g=$("time-grid"); g.innerHTML="";
  var isToday=sameDay(state.date,today);
  var now=new Date(), nowMin=now.getHours()*60+now.getMinutes();
  for(var m=540;m<=1320;m+=30){
    (function(){
      var mm=m;
      var label=("0"+Math.floor(mm/60)).slice(-2)+":"+("0"+(mm%60)).slice(-2);
      var b=document.createElement("button");
      b.type="button"; b.className="slot"; b.textContent=label;
      b.disabled=!state.date||(isToday&&mm<=nowMin);
      if(state.time===label&&state.date) b.classList.add("sel");
      b.addEventListener("click",function(){state.time=label;buildTimes();validate();});
      g.appendChild(b);
    })();
  }
}
function selectDate(dt){
  state.date=dt; state.time=null;
  $("times-hint").textContent="теперь выбери время ⏰";
  renderCal(); buildTimes(); validate();
}

/* ----- сводка / валидация ----- */
function fmtDate(d){return d.toLocaleDateString("ru-RU",{weekday:"long",month:"long",day:"numeric"});}
function isoDate(d){return d.getFullYear()+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+("0"+d.getDate()).slice(-2);}
function validate(){
  $("btn-confirm").disabled=!(state.place.trim()&&state.date&&state.time);
  var p=state.place.trim()?esc(state.place.trim()):"<em>выбери место</em>";
  var t=(state.date&&state.time)?fmtDate(state.date)+" · "+state.time:"<em>выбери время</em>";
  $("summary").innerHTML="📍 "+p+' <span class="sep">·</span> 🗓 '+t;
}

/* ----- подтверждение ----- */
$("btn-confirm").addEventListener("click",function(){
  var btn=$("btn-confirm");
  btn.disabled=true; btn.textContent="договариваемся… 💌";
  function finish(){
    $("done-summary").textContent=state.place.trim()+"  ·  "+fmtDate(state.date)+" в "+state.time;
    show("done");
    burst(window.innerWidth/2,window.innerHeight/2,22);
    btn.textContent="Подтвердить наше свидание 💘"; validate();
  }
  fetch("/save-plan",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({place:state.place.trim(),date:isoDate(state.date),time:state.time})})
    .then(finish,finish);
});

/* ----- СИНИЙ ЭКРАН ----- */
var bsodStarted=false;
function bsod(){
  if(bsodStarted) return; bsodStarted=true;
  document.body.classList.add("bsod-mode");
  $("bsod").classList.add("show");
  document.title=":(";
  var p=0;
  var t=setInterval(function(){
    if(Math.random()>0.18) p=Math.min(100,p+1+Math.floor(Math.random()*6));
    $("bsod-pct").textContent=p;
    if(p>=100) clearInterval(t);
  },550);
}

/* инициализация */
renderCal(); buildTimes(); validate();
})();
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return PAGE.replace("__TELEGRAM_USERNAME__", TELEGRAM_USERNAME)


@app.route("/save-plan", methods=["POST"])
def save_plan():
    data = request.get_json(silent=True) or {}
    record = {
        "place": str(data.get("place", ""))[:300],
        "date": str(data.get("date", "")),
        "time": str(data.get("time", "")),
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        with open(ANSWERS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        return jsonify(ok=False, error=str(e)), 500
    return jsonify(ok=True, message="Сохранено! Удачи 💘")


if __name__ == "__main__":
    print("💌  Откройте  http://127.0.0.1:%d  в браузере" % PORT)
    print("📬  Ответы будут сохраняться в  %s" % ANSWERS_FILE)
    app.run(host="0.0.0.0", port=PORT, debug=False)