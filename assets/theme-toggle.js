(function(){
  const root=document.documentElement;
  const key='edunamics-theme';
  const saved=localStorage.getItem(key);
  if(saved==='light'||saved==='dark') root.dataset.theme=saved;
  function label(){return root.dataset.theme==='dark'?'亮色主題':'暗色主題'}
  function sync(btn){const dark=root.dataset.theme==='dark';btn.setAttribute('aria-pressed',String(dark));btn.querySelector('.theme-icon').textContent=dark?'☀':'☾';btn.querySelector('.theme-label').textContent=label()}
  function init(){const btn=document.createElement('button');btn.type='button';btn.className='theme-toggle';btn.setAttribute('aria-label','切換主題');btn.innerHTML='<span class="theme-icon" aria-hidden="true"></span><span class="theme-label"></span>';btn.addEventListener('click',function(){const next=root.dataset.theme==='dark'?'light':'dark';root.dataset.theme=next;localStorage.setItem(key,next);sync(btn)});document.body.appendChild(btn);sync(btn)}
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
