(function(){
  var tip=document.getElementById('tip');
  document.addEventListener('pointerover',function(e){
    var t=e.target.closest&&e.target.closest('[data-tip]');
    if(!t){tip.hidden=true;return;}
    tip.textContent=t.getAttribute('data-tip');tip.hidden=false;
  });
  document.addEventListener('pointermove',function(e){
    if(tip.hidden)return;
    var x=e.clientX+12,y=e.clientY-34;
    var w=tip.offsetWidth; if(x+w>window.innerWidth-8)x=e.clientX-w-12;
    tip.style.left=x+'px';tip.style.top=Math.max(8,y)+'px';
  });
})();
addEventListener('message',function(e){
  if(!e.data||typeof e.data.appHeight!=='number')return;
  document.querySelectorAll('iframe.app').forEach(function(f){
    if(f.contentWindow===e.source){var h=Math.ceil(e.data.appHeight)+4;if(Math.abs(f.offsetHeight-h)>2)f.style.height=h+'px';}
  });
});
