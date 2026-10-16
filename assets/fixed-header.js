/* Move the original breadcrumb out of the hero so its sticky range spans the page. */
(function(){
  var crumb=document.querySelector('header.hero .crumb');
  var header=document.querySelector('header.top');
  if(crumb){
    header=document.createElement('nav');
    header.className='fixed-chapter-header';
    header.setAttribute('aria-label','科目與章節');
    header.appendChild(crumb);
    document.body.insertBefore(header,document.body.firstChild);
  }
  if(!header)return;
  function measure(){document.documentElement.style.setProperty('--fixed-header-height',header.getBoundingClientRect().height+'px');}
  measure();
  if(window.ResizeObserver)new ResizeObserver(measure).observe(header);
  else window.addEventListener('resize',measure);
  if(document.fonts)document.fonts.ready.then(measure);
})();
