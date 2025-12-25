document.addEventListener('DOMContentLoaded', function(){
  var btn = document.getElementById('nav-toggle');
  var menu = document.getElementById('nav-menu');
  if(!btn || !menu) return;
  btn.addEventListener('click', function(){
    var open = menu.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  // close menu when clicking outside on small screens
  document.addEventListener('click', function(e){
    if(window.innerWidth > 800) return;
    if(!menu.classList.contains('open')) return;
    if(!menu.contains(e.target) && e.target !== btn){
      menu.classList.remove('open');
      btn.setAttribute('aria-expanded','false');
    }
  });
});
