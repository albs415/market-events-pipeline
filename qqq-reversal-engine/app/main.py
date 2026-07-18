from __future__ import annotations
import asyncio, math, random
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title='QQQ Reversal Engine')
state = {'price': 700.0, 'vwap': 704.0, 'p15': .34, 'p5': .23, 'fast_v': .29, 'expected': .35, 'grade': 'D', 'phase': 'WATCHING', 'updated': None}

HTML = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>QQQ Reversal Engine</title><style>
:root{color-scheme:dark;font-family:Inter,system-ui,sans-serif;background:#0b0d10;color:#f5f7fa}*{box-sizing:border-box}body{margin:0;background:#0b0d10}main{max-width:1180px;margin:auto;padding:22px}.top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #262b33;padding-bottom:16px}.tag{font:12px ui-monospace;color:#78e3a4}.grid{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:16px;margin-top:16px}.card{background:#12161c;border:1px solid #252b34;border-radius:14px;padding:18px}.label{font:12px ui-monospace;color:#8f98a6}.big{font:700 58px ui-monospace;margin:8px 0}.mid{font:700 28px ui-monospace}.bar{height:7px;background:#242a33;border-radius:9px;overflow:hidden}.bar i{display:block;height:100%;background:#78e3a4}.row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #20252d}.grade{font:800 42px ui-monospace;color:#78e3a4}.warn{color:#ff8a76}.states{display:flex;gap:8px;flex-wrap:wrap;margin-top:15px}.states span{padding:7px 10px;border:1px solid #2d3440;border-radius:999px;font:11px ui-monospace;color:#6f7887}.states .on{background:#78e3a4;color:#07120b;border-color:#78e3a4}.foot{margin-top:16px;color:#788291;font-size:12px}.mono{font-family:ui-monospace,monospace}@media(max-width:850px){.grid{grid-template-columns:1fr}.big{font-size:48px}.top{align-items:flex-start;gap:12px;flex-direction:column}}</style></head><body><main><div class="top"><div><div class="label">REAL-TIME DECISION SUPPORT</div><h1>QQQ Reversal Engine</h1></div><div class="tag" id="status">● SIMULATION LIVE</div></div><div class="states" id="states"></div><div class="grid"><section class="card"><div class="label">P(REVERSAL ≤ 15 MIN)</div><div class="big" id="p15">—</div><div class="bar"><i id="p15b"></i></div><div class="row"><span>P(REVERSAL ≤ 5 MIN)</span><b class="mono" id="p5">—</b></div><div class="row"><span>FAST V PROBABILITY</span><b class="mono" id="fv">—</b></div></section><section class="card"><div class="label">MAGNITUDE</div><div class="mid" id="exp">—</div><div class="row"><span>QQQ</span><b class="mono" id="px">—</b></div><div class="row"><span>VWAP</span><b class="mono" id="vw">—</b></div><div class="row"><span>TO VWAP</span><b class="mono" id="gap">—</b></div></section><section class="card"><div class="label">SIGNAL GRADE</div><div class="grade" id="grade">—</div><div class="row"><span>STATE</span><b class="mono" id="phase">—</b></div><div class="row"><span>MODE</span><b class="mono">SIMULATION</b></div><div class="row"><span>EXECUTION</span><b class="warn">MANUAL ONLY</b></div></section></div><div class="foot">The deployed public build runs in simulation mode. Add licensed market-data credentials and switch DATA_MODE to live before using real-time feeds.</div></main><script>
const order=['WATCHING','DEVELOPING','ARMED','TRIGGERED','CONFIRMED'];function pct(x){return Math.round(x*100)+'%'}async function tick(){let r=await fetch('/api/signal');let s=await r.json();p15.textContent=pct(s.p15);p15b.style.width=pct(s.p15);p5.textContent=pct(s.p5);fv.textContent=pct(s.fast_v);exp.textContent=s.expected.toFixed(2)+'% expected max';px.textContent=s.price.toFixed(2);vw.textContent=s.vwap.toFixed(2);gap.textContent=((s.vwap-s.price)/s.vwap*100).toFixed(2)+'%';grade.textContent=s.grade;phase.textContent=s.phase;states.innerHTML=order.map(x=>'<span class="'+(x===s.phase?'on':'')+'">'+x+'</span>').join('')}setInterval(tick,1000);tick();</script></body></html>'''

def logistic(x): return 1/(1+math.exp(-x))

def grade(p, v, e):
    score=.45*p+.35*v+.20*min(e/1.25,1)
    return 'A+' if score>=.82 else 'A' if score>=.70 else 'B' if score>=.58 else 'C' if score>=.46 else 'D'

async def simulator():
    t=0
    while True:
        t=(t+1)%240
        if t<80: drift=-.055; pressure=-.6
        elif t<125: drift=-.02; pressure=-.15
        elif t<165: drift=.07; pressure=.55
        else: drift=.025; pressure=.25
        state['price']=max(650,state['price']+drift+random.gauss(0,.055))
        stretch=max(0,(state['vwap']-state['price'])/state['vwap']*100)
        exhaustion=max(0,min(1,(t-70)/70)) if 70<t<165 else 0
        p15=logistic(-1.25+stretch*.9+exhaustion*1.6+pressure*.7)
        p5=logistic(math.log(p15/(1-p15))-.35)
        fast=logistic(-1.1+stretch*.7+exhaustion*1.4+pressure)
        exp=max(.08,min(2.25,.18+fast*1.45+stretch*.12))
        phase='WATCHING'
        if p15>=.55: phase='DEVELOPING'
        if p15>=.72 and fast>=.60: phase='ARMED'
        if p5>=.68 and pressure>.2: phase='TRIGGERED'
        if state['price']>=state['vwap']: phase='CONFIRMED'
        state.update(p15=p15,p5=p5,fast_v=fast,expected=exp,grade=grade(p15,fast,exp),phase=phase,updated=datetime.now(timezone.utc).isoformat())
        await asyncio.sleep(1)

@app.on_event('startup')
async def startup(): asyncio.create_task(simulator())

@app.get('/', response_class=HTMLResponse)
def home(): return HTML

@app.get('/api/signal')
def signal(): return state

@app.get('/healthz')
def healthz(): return {'status':'ok','updated':state['updated']}
