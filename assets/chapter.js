/* 機械製造學各章共用：節次分頁、上下節切換、寬圖自動收合 */
(function(){
  var tabs=[].slice.call(document.querySelectorAll('.tabs .tab'));
  var secs=tabs.map(function(t){return document.getElementById(t.getAttribute('aria-controls'));});
  var wrap=document.querySelector('.wrap');

  /* 分類樹放不下時改為縮排清單（只量測目前顯示的分頁） */
  function fit(){
    document.querySelectorAll('.tree').forEach(function(t){
      if(!t.offsetParent)return;
      t.classList.remove('as-list');
      var pe=t.parentElement,cs=getComputedStyle(pe);
      var avail=pe.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
      if(t.scrollWidth>avail+1)t.classList.add('as-list');
    });
  }

  if(tabs.length){
    document.documentElement.classList.add('tabbed');
    tabs.forEach(function(t,i){
      var s=secs[i]; if(!s)return;
      s.setAttribute('role','tabpanel'); s.setAttribute('aria-labelledby',t.id);
      var pg=document.createElement('nav'); pg.className='pager'; pg.setAttribute('aria-label','上下節');
      if(i>0)pg.appendChild(link(tabs[i-1],'prev','← 上一節'));
      if(i<tabs.length-1)pg.appendChild(link(tabs[i+1],'next','下一節 →'));
      s.appendChild(pg);
    });
  }
  function link(t,cls,lab){
    var a=document.createElement('a'); a.className=cls; a.href=t.getAttribute('href');
    a.innerHTML='<small>'+lab+'</small><b>'+t.querySelector('.no').textContent+'　'+t.querySelector('.nm').textContent+'</b>';
    return a;
  }
  function show(id,scroll){
    var idx=secs.findIndex(function(s){return s&&s.id===id;});
    if(idx<0)idx=0;
    tabs.forEach(function(t,i){
      var on=i===idx;
      t.setAttribute('aria-selected',on?'true':'false');
      t.tabIndex=on?0:-1;
      if(secs[i])secs[i].hidden=!on;
    });
    fit();
    if(scroll&&wrap){var top=wrap.getBoundingClientRect().top;if(top<0)window.scrollTo({top:window.scrollY+top-12});}
  }
  function fromHash(scroll){
    var h=decodeURIComponent(location.hash.slice(1));
    if(!h){show(secs[0]&&secs[0].id,false);return;}
    var el=document.getElementById(h);
    if(!el)return;
    var sec=el.closest('main>section');
    if(sec){show(sec.id,false);if(el!==sec)el.scrollIntoView();else if(scroll&&wrap){var top=wrap.getBoundingClientRect().top;if(top<0)window.scrollTo({top:window.scrollY+top-12});}}
  }
  if(tabs.length){
    document.addEventListener('click',function(e){
      var a=e.target.closest('a[href^="#"]'); if(!a)return;
      var id=a.getAttribute('href').slice(1); var el=document.getElementById(id);
      if(!el||!el.closest('main>section'))return;
      e.preventDefault();
      if(location.hash!=='#'+id)history.pushState(null,'','#'+id);
      fromHash(true);
      if(a.classList.contains('tab'))a.focus({preventScroll:true});
    });
    window.addEventListener('popstate',function(){fromHash(true);});
    document.querySelector('.tabs').addEventListener('keydown',function(e){
      var i=tabs.indexOf(document.activeElement); if(i<0)return;
      var n=null;
      if(e.key==='ArrowDown'||e.key==='ArrowRight')n=(i+1)%tabs.length;
      else if(e.key==='ArrowUp'||e.key==='ArrowLeft')n=(i-1+tabs.length)%tabs.length;
      else if(e.key==='Home')n=0; else if(e.key==='End')n=tabs.length-1;
      if(n===null)return; e.preventDefault(); tabs[n].click();
    });
    fromHash(false);
  }
  window.addEventListener('resize',fit);
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fit);
  fit();
})();
