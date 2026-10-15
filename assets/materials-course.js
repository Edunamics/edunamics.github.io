/* Accessible figure enlargement; legacy PDF reader is used only by Statics. */
(function(){
  var dialog=document.getElementById('figure-dialog'),last;
  document.querySelectorAll('[data-zoom]').forEach(function(button){button.addEventListener('click',function(){
    last=button;var original=button.querySelector('img'),image=dialog.querySelector('img');
    image.src=original.src;image.alt=original.alt;dialog.querySelector('p').textContent=original.alt;
    dialog.showModal();dialog.scrollLeft=0;
  });});
  dialog.querySelector('.zoom-close').addEventListener('click',function(){dialog.close();});
  dialog.addEventListener('click',function(e){if(e.target===dialog){var r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
  dialog.addEventListener('close',function(){if(last)last.focus();});
  var source=document.getElementById('source'),reader=document.querySelector('[data-pdf]');
  function load(){if(source.hidden||reader.dataset.loaded)return;var frame=document.createElement('iframe');frame.title='本章完整原講義 PDF';frame.src=reader.dataset.pdf+'#view=FitH';reader.replaceChildren(frame);reader.dataset.loaded='true';}
  if(source&&reader){new MutationObserver(load).observe(source,{attributes:true,attributeFilter:['hidden']});load();}
})();
