
(function(){
var cv=document.getElementById('pocket');if(!cv||!cv.getContext)return;
var g=cv.getContext('2d');
var data=[];try{data=JSON.parse(document.getElementById('pocketdata').textContent);}catch(e){}
var N=data.length;if(!N)return;
var accent=cv.getAttribute('data-accent')||'#e0a838';
var DPR=Math.min(window.devicePixelRatio||1,2);
function fit(){var r=cv.getBoundingClientRect();cv.width=Math.max(1,Math.round(r.width*DPR));cv.height=Math.max(1,Math.round(r.height*DPR));}
fit();addEventListener('resize',fit);
function hx(h){h=(''+h).replace('#','');if(h.length<6)h='e0a838';return [parseInt(h.slice(0,2),16)||224,parseInt(h.slice(2,4),16)||168,parseInt(h.slice(4,6),16)||56];}
var AC=hx(accent),GA=2.399963;
var stars=[];for(var i=0;i<80;i++)stars.push({x:((i*137.0)%1000)/1000,y:((i*271.0)%1000)/1000,r:((i*7)%10)/10+0.2,a:((i*53)%40)/100+0.1});
var rgb=[];for(var i=0;i<N;i++)rgb.push(hx(data[i].c||accent));
var mx=-1,my=-1,hover=-1,lay=null;
var tip=document.getElementById('pockettip');
function frame(t){requestAnimationFrame(frame);if(document.hidden)return;
  var rect=cv.getBoundingClientRect();if(cv.width!==Math.round(rect.width*DPR))fit();
  var w=cv.width/DPR,h=cv.height/DPR;
  g.setTransform(DPR,0,0,DPR,0,0);g.clearRect(0,0,w,h);
  var bg=g.createRadialGradient(w/2,h/2,0,w/2,h/2,Math.max(w,h)*0.62);bg.addColorStop(0,'#0c1622');bg.addColorStop(1,'#050810');g.fillStyle=bg;g.fillRect(0,0,w,h);
  for(var s=0;s<stars.length;s++){var st=stars[s];g.fillStyle='rgba(170,198,230,'+st.a.toFixed(2)+')';g.beginPath();g.arc(st.x*w,st.y*h,st.r,0,7);g.fill();}
  var cx=w/2,cy=h/2,Rmax=Math.min(w,h)*0.42,pts=[];
  for(var i=0;i<N;i++){var rr=Math.sqrt((i+0.6)/N),rad=rr*Rmax,ang=i*GA+t*0.00012*(0.35+(1-rr)*1.1);pts.push({x:cx+Math.cos(ang)*rad,y:cy+Math.sin(ang)*rad*0.5,dep:(Math.sin(ang)*0.5+1)/2,i:i});}
  lay={pts:pts};pts.sort(function(a,b){return a.dep-b.dep;});
  hover=-1;var hd=210;
  g.globalCompositeOperation='lighter';
  for(var q=0;q<pts.length;q++){var pp=pts[q],c=rgb[pp.i],sz=1.4+pp.dep*2.3;
    if(mx>=0){var dd=(pp.x-mx)*(pp.x-mx)+(pp.y-my)*(pp.y-my);if(dd<hd){hd=dd;hover=pp.i;}}
    g.globalAlpha=0.16+pp.dep*0.22;g.fillStyle='rgb('+c[0]+','+c[1]+','+c[2]+')';g.beginPath();g.arc(pp.x,pp.y,sz*2.4,0,7);g.fill();
    g.globalAlpha=0.6+pp.dep*0.4;g.beginPath();g.arc(pp.x,pp.y,sz,0,7);g.fill();}
  g.globalAlpha=1;g.globalCompositeOperation='source-over';
  var R0=Math.min(w,h)*0.055,pulse=0.5+0.5*Math.sin(t*0.003);
  var sg=g.createRadialGradient(cx,cy,0,cx,cy,R0*2.0);sg.addColorStop(0,'rgba('+AC[0]+','+AC[1]+','+AC[2]+','+(0.5+0.2*pulse).toFixed(2)+')');sg.addColorStop(0.5,'rgba('+AC[0]+','+AC[1]+','+AC[2]+',.2)');sg.addColorStop(1,'rgba('+AC[0]+','+AC[1]+','+AC[2]+',0)');g.fillStyle=sg;g.beginPath();g.arc(cx,cy,R0*2.0,0,7);g.fill();
  g.fillStyle='rgb('+Math.min(255,AC[0]+60)+','+Math.min(255,AC[1]+55)+','+Math.min(255,AC[2]+45)+')';g.beginPath();g.arc(cx,cy,R0*0.5+pulse*2,0,7);g.fill();
  if(hover>=0){var hp=null;for(var q2=0;q2<lay.pts.length;q2++)if(lay.pts[q2].i===hover){hp=lay.pts[q2];break;}if(hp){g.strokeStyle='#fff';g.lineWidth=1.5;g.beginPath();g.arc(hp.x,hp.y,7,0,7);g.stroke();}cv.style.cursor='pointer';}else cv.style.cursor='default';
  if(tip){if(hover>=0){tip.textContent=data[hover].n;tip.style.left=Math.min(mx+14,w-tip.offsetWidth-8)+'px';tip.style.top=(my+12)+'px';tip.style.opacity=1;}else tip.style.opacity=0;}
}
requestAnimationFrame(frame);
cv.addEventListener('mousemove',function(e){var r=cv.getBoundingClientRect();mx=e.clientX-r.left;my=e.clientY-r.top;});
cv.addEventListener('mouseleave',function(){mx=-1;my=-1;});
cv.addEventListener('click',function(){if(hover>=0&&data[hover]&&data[hover].u)location.href=data[hover].u;});
})();
