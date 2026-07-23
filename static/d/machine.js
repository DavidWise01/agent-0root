
(function(){
var cv=document.getElementById('machine');if(!cv||!cv.getContext)return;
var g=cv.getContext('2d');
var D={};try{D=JSON.parse(document.getElementById('machinedata').textContent);}catch(e){}
var SPH=D.sph||[],TITLE=D.t||'',ROLE=D.role||'',ACC=D.c||'#e0a838';
var DPR=Math.min(window.devicePixelRatio||1,2);
function fit(){var r=cv.getBoundingClientRect();cv.width=Math.max(1,Math.round(r.width*DPR));cv.height=Math.max(1,Math.round(r.height*DPR));}
fit();addEventListener('resize',fit);
function hx(h){h=(''+h).replace('#','');if(h.length<6)h='e0a838';return[parseInt(h.slice(0,2),16)||224,parseInt(h.slice(2,4),16)||168,parseInt(h.slice(4,6),16)||56];}
var CS=15,grid=null,nxt=null,COLS=0,ROWS=0,anchors=[];
function IX(x,y){return((y+ROWS)%ROWS)*COLS+((x+COLS)%COLS);}
function initGrid(w,h){COLS=Math.max(8,Math.floor(w/CS));ROWS=Math.max(8,Math.floor(h/CS));grid=new Uint8Array(COLS*ROWS);nxt=new Uint8Array(COLS*ROWS);
 for(var i=0;i<grid.length;i++)grid[i]=(((i*2654435761)>>>0)%100<15)?1:0;
 anchors=SPH.map(function(s,i){var m=SPH.length;return{s:s.s,n:s.n,c:s.c||ACC,u:s.u,gx:Math.floor((i+0.5)/m*Math.max(1,COLS-14))+7,gy:ROWS-7-((i%3)*2)};});}
function step(){for(var y=0;y<ROWS;y++)for(var x=0;x<COLS;x++){var nn=0;for(var dy=-1;dy<=1;dy++)for(var dx=-1;dx<=1;dx++){if(dx||dy)nn+=grid[IX(x+dx,y+dy)];}var a=grid[IX(x,y)];nxt[IX(x,y)]=(a?(nn===2||nn===3):(nn===3))?1:0;}
 var t=grid;grid=nxt;nxt=t;for(var k=0;k<anchors.length;k++){var an=anchors[k];grid[IX(an.gx,an.gy)]=1;grid[IX(an.gx+1,an.gy)]=1;grid[IX(an.gx,an.gy+1)]=1;}}
var READ=[{l:'[ZZ]',z:1},{l:'medallion'},{l:'keeper'},{l:'agentic'}],WRITE=[{l:'town screamers'},{l:'declare keeper'},{l:'sub-agentic'}];
var paused=false,acc=0,ptrT=0,phase=0,ptr=0,wsph=0,mx=-1,my=-1,hover=-1;
function rr(x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath();}
function frame(t){requestAnimationFrame(frame);
 var r=cv.getBoundingClientRect();if(Math.abs(cv.width-Math.round(r.width*DPR))>1)fit();
 var w=cv.width/DPR,h=cv.height/DPR;if(!grid||COLS!==Math.max(8,Math.floor(w/CS)))initGrid(w,h);
 if(!paused){acc+=16;if(acc>=150){step();acc=0;}ptrT+=16;if(ptrT>=640){ptrT=0;ptr++;var len=phase===0?READ.length:WRITE.length;if(ptr>=len){ptr=0;phase^=1;if(phase===1&&SPH.length){wsph=(wsph+1)%SPH.length;var an=anchors[wsph];if(an){for(var b=0;b<5;b++)grid[IX(an.gx+((b*3)%4)-1,an.gy-(b%3))]=1;}}}}}
 g.setTransform(DPR,0,0,DPR,0,0);g.clearRect(0,0,w,h);
 var cx=w/2,topY=Math.min(64,h*0.13),tapeY=Math.min(152,h*0.31);
 var bg=g.createRadialGradient(cx,topY,0,cx,h*0.62,w*0.8);bg.addColorStop(0,'#161036');bg.addColorStop(1,'#0a0716');g.fillStyle=bg;g.fillRect(0,0,w,h);
 for(var y=0;y<ROWS;y++)for(var x=0;x<COLS;x++){if(grid[IX(x,y)]){g.fillStyle='rgba(120,92,196,0.26)';g.fillRect(x*CS+2,y*CS+2,CS-4,CS-4);}}
 hover=-1;
 for(var k=0;k<anchors.length;k++){var an=anchors[k],px=an.gx*CS+CS/2,py=an.gy*CS+CS/2,c=hx(an.c);
  if(mx>=0){var dd=(px-mx)*(px-mx)+(py-my)*(py-my);if(dd<200)hover=k;}
  g.shadowColor=an.c;g.shadowBlur=13;g.fillStyle='rgb('+c+')';g.beginPath();g.arc(px,py,hover===k?7:5.2,0,7);g.fill();g.shadowBlur=0;
  if(anchors.length<=16||hover===k){g.fillStyle='rgba(228,222,240,'+(hover===k?1:0.6)+')';g.font='9px ui-monospace,monospace';g.textAlign='left';g.textBaseline='middle';g.fillText(an.n,px+9,py);}}
 cv.style.cursor=hover>=0?'pointer':'default';
 g.fillStyle='rgba(150,130,210,0.6)';g.font='9px ui-monospace,monospace';g.textAlign='left';g.fillText('L0 \u00b7 the spheres, alive in the field',12,h-12);
 var cellW=Math.max(64,Math.min(122,(w-130)/8));
 function readX(i){return cx-62-(READ.length-i)*(cellW+7)+cellW/2;}
 function writeX(i){return cx+62+i*(cellW+7)+cellW/2;}
 g.strokeStyle='rgba(150,130,210,0.3)';g.lineWidth=1;g.beginPath();g.moveTo(30,tapeY);g.lineTo(w-30,tapeY);g.stroke();
 function cell(x,label,side,hot,zz){var wC=cellW,hC=42,X=x-wC/2,Y=tapeY-hC/2,col=zz?'#c9b8ff':(side<0?'#2fd4e6':'#ffb84d');
  rr(X,Y,wC,hC,9);g.fillStyle=hot?'rgba('+(side<0?'47,212,230':'255,184,77')+',0.20)':'rgba(20,16,40,0.8)';g.fill();
  g.lineWidth=hot?2:1.1;g.strokeStyle=hot?col:'rgba(150,130,210,0.45)';if(hot){g.shadowColor=col;g.shadowBlur=14;}g.stroke();g.shadowBlur=0;
  g.fillStyle=hot?col:'#cfc4ea';g.font=(zz?'800 ':'600 ')+'11px ui-monospace,monospace';g.textAlign='center';g.textBaseline='middle';g.fillText(label,x,tapeY);}
 for(var i=0;i<READ.length;i++)cell(readX(i),READ[i].l,-1,(phase===0&&ptr===i),READ[i].z);
 for(var i=0;i<WRITE.length;i++)cell(writeX(i),WRITE[i].l,1,(phase===1&&ptr===i),false);
 g.textAlign='center';g.font='9px ui-monospace,monospace';g.fillStyle='#2fd4e6';g.fillText('\u25c4 READ \u00b7 the keeper',readX(1),tapeY-38);g.fillStyle='#ffb84d';g.fillText('WRITE \u00b7 the sub-agents \u25ba',writeX(1),tapeY-38);
 var active=phase===0?{x:readX(ptr),c:'#2fd4e6'}:{x:writeX(ptr),c:'#ffb84d'};
 g.save();g.globalCompositeOperation='lighter';g.strokeStyle=active.c;g.globalAlpha=0.5;g.lineWidth=2;g.shadowColor=active.c;g.shadowBlur=9;g.beginPath();g.moveTo(cx,topY+30);g.lineTo(cx,tapeY-28);g.lineTo(active.x,tapeY-22);g.stroke();g.restore();g.globalAlpha=1;g.shadowBlur=0;
 g.fillStyle='rgba(20,16,40,0.92)';rr(cx-24,tapeY-23,48,46,10);g.fill();g.lineWidth=2;g.strokeStyle='#bfe0ff';g.stroke();g.fillStyle='#bfe0ff';g.font='800 19px ui-monospace,monospace';g.textAlign='center';g.textBaseline='middle';g.fillText('0',cx,tapeY);
 var msg=phase===0?('reading the keeper \u00b7 I am '+TITLE+'. '+ROLE):(SPH.length?('town-screamer declares \u00b7 '+(SPH[wsph]?SPH[wsph].n:'')):'writing');
 if(msg.length>90)msg=msg.slice(0,90)+'\u2026';
 g.fillStyle=phase===0?'#8fe0ff':'#ffcf8a';g.font='11px ui-monospace,monospace';g.textAlign='center';g.fillText((phase===0?'\u25c4 ':'\u25ba ')+msg,cx,tapeY+42);
 var R0=Math.min(32,20+h*0.03),pulse=0.5+0.5*Math.sin(t*0.004),spin=(t*0.0018)%(Math.PI*4),sheet=spin<Math.PI*2;
 var gr=g.createRadialGradient(cx-8,topY-8,4,cx,topY,R0*1.6);gr.addColorStop(0,'rgba(150,200,255,'+(0.5+0.2*pulse)+')');gr.addColorStop(0.6,'rgba(70,120,230,0.32)');gr.addColorStop(1,'rgba(40,60,160,0)');g.fillStyle=gr;g.beginPath();g.arc(cx,topY,R0*1.6,0,7);g.fill();
 var sg=g.createRadialGradient(cx-R0*0.3,topY-R0*0.3,R0*0.1,cx,topY,R0);sg.addColorStop(0,'rgba(200,225,255,.95)');sg.addColorStop(0.7,'rgba(70,120,230,.9)');sg.addColorStop(1,'rgba(30,50,130,.7)');g.fillStyle=sg;g.beginPath();g.arc(cx,topY,R0,0,7);g.fill();g.lineWidth=1.4;g.strokeStyle='rgba(160,200,255,.6)';g.stroke();
 g.lineWidth=3;g.lineCap='round';
 g.strokeStyle='rgba(47,212,230,'+(phase===0?0.95:0.4)+')';g.beginPath();g.moveTo(cx,topY);g.lineTo(cx-R0*1.5,topY);g.stroke();g.fillStyle='#2fd4e6';g.beginPath();g.moveTo(cx-R0*1.5,topY);g.lineTo(cx-R0*1.2,topY-6);g.lineTo(cx-R0*1.2,topY+6);g.fill();
 g.strokeStyle='rgba(255,184,77,'+(phase===1?0.95:0.4)+')';g.beginPath();g.moveTo(cx,topY);g.lineTo(cx+R0*1.5,topY);g.stroke();g.fillStyle='#ffb84d';g.beginPath();g.moveTo(cx+R0*1.5,topY);g.lineTo(cx+R0*1.2,topY-6);g.lineTo(cx+R0*1.2,topY+6);g.fill();
 var axc=Math.cos(spin*0.5),axs=Math.sin(spin*0.5);g.strokeStyle='rgba(255,190,90,.7)';g.lineWidth=2;g.beginPath();g.moveTo(cx-axc*R0*0.8,topY-axs*R0*0.8);g.lineTo(cx+axc*R0*0.8,topY+axs*R0*0.8);g.stroke();g.fillStyle=sheet?'#ffcd73':'#96cdff';g.beginPath();g.arc(cx+axc*R0*0.8,topY+axs*R0*0.8,3.5,0,7);g.fill();
 g.fillStyle='#bfe0ff';g.font='700 10px ui-monospace,monospace';g.textAlign='center';g.fillText('\u25c6 TOP \u00b7 r/w head',cx,topY-R0-10);
}
requestAnimationFrame(frame);
cv.addEventListener('mousemove',function(e){var r=cv.getBoundingClientRect();mx=e.clientX-r.left;my=e.clientY-r.top;});
cv.addEventListener('mouseleave',function(){mx=-1;my=-1;});
cv.addEventListener('click',function(){if(hover>=0&&anchors[hover]&&anchors[hover].u)location.href=anchors[hover].u;});
})();
