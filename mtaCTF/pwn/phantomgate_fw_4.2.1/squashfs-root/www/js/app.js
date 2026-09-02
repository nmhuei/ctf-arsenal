/* PhantomGate PG-400 Management Interface */
(function(){
  /* Clock */
  function updateClock(){
    var el=document.getElementById('clock');
    if(!el)return;
    var d=new Date();
    el.textContent=d.toISOString().replace('T',' ').substring(0,19)+' UTC';
  }
  updateClock();
  setInterval(updateClock,1000);

  /* Login form */
  var form=document.getElementById('loginForm');
  if(form){
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var user=document.getElementById('username').value;
      var pass=document.getElementById('password').value;
      var errEl=document.getElementById('loginError');
      var btn=form.querySelector('button[type="submit"]');
      btn.disabled=true;
      btn.textContent='Signing in...';
      errEl.style.display='none';

      var xhr=new XMLHttpRequest();
      xhr.open('POST','/api/auth/login',true);
      xhr.setRequestHeader('Content-Type','application/json');
      xhr.onload=function(){
        if(xhr.status===200){
          try{
            var resp=JSON.parse(xhr.responseText);
            if(resp.token){
              document.cookie='session='+resp.token+';path=/';
            }
          }catch(ex){}
          window.location.href='/www/dashboard.html';
        }else{
          errEl.textContent='Invalid credentials';
          errEl.style.display='block';
          btn.disabled=false;
          btn.textContent='Sign In';
        }
      };
      xhr.onerror=function(){
        errEl.textContent='Connection error';
        errEl.style.display='block';
        btn.disabled=false;
        btn.textContent='Sign In';
      };
      xhr.send(JSON.stringify({username:user,password:pass}));
    });
  }

  /* Sidebar active state */
  var links=document.querySelectorAll('.nav-list a');
  var path=window.location.pathname;
  for(var i=0;i<links.length;i++){
    links[i].classList.remove('active');
    if(links[i].getAttribute('href')===path){
      links[i].classList.add('active');
    }
  }
})();
