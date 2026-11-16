"use strict";
/* JP Structural Analysis portal v1: entirely client-side presentation.
   No solver execution or unsafe server-side user data. */
(()=>{
  const q=(s)=>document.querySelector(s),qa=(s)=>[...document.querySelectorAll(s)];
  const menu=q("#menu-toggle"),nav=q("#primary-nav");
  if(menu&&nav){
    menu.addEventListener("click",()=>{
      const expanded=menu.getAttribute("aria-expanded")==="true";
      nav.classList.toggle("open",!expanded);
      menu.setAttribute("aria-expanded",String(!expanded));
      menu.querySelector("span:last-child").textContent=expanded?"☰":"✕";
    });
    nav.addEventListener("click",e=>{
      if(e.target.closest("a")){
        nav.classList.remove("open");
        menu.setAttribute("aria-expanded","false");
        menu.querySelector("span:last-child").textContent="☰";
      }
    });
  }
  const tocLinks=qa(".top-toc a, .left-toc a");
  const tocMap=new Map();
  for(const a of tocLinks){
    const id=a.getAttribute("data-toc-for");
    if(!tocMap.has(id))tocMap.set(id,[]);
    tocMap.get(id).push(a);
  }
  const mark=id=>{
    for(const [key,links] of tocMap.entries())
      for(const a of links){
        const same=key===id;
        a.classList.toggle("is-active",same);
        if(same)a.setAttribute("aria-current","location");
        else a.removeAttribute("aria-current");
      }
  };
  const sections=qa(".content-section");
  if(sections.length)mark(sections[0].id);
  if("IntersectionObserver" in window){
    const heights=new Map();
    const obs=new IntersectionObserver(entries=>{
      for(const entry of entries)heights.set(entry.target.id,entry.isIntersecting?entry.intersectionRatio:0);
      let best=null;
      for(const section of sections){
        const b=heights.get(section.id)||0;
        if(b>0&&(best===null||b>best.value))best={id:section.id,value:b};
      }
      if(best)mark(best.id);
    },{rootMargin:"-130px 0px -55% 0px",threshold:[0,.1,.3,.6,1]});
    sections.forEach(section=>obs.observe(section));
  }
  tocLinks.forEach(a=>a.addEventListener("click",()=>mark(a.getAttribute("data-toc-for"))));
  const copy=q(".copy-prompt");
  if(copy)copy.addEventListener("click",async()=>{
    const selector=copy.getAttribute("data-copy");
    const content=selector&&q(selector);
    if(!content)return;
    const original=copy.textContent;
    try{
      await navigator.clipboard.writeText(content.textContent.trim());
      copy.textContent="Copied";
    }catch(err){
      copy.textContent="Select text to copy";
      const range=document.createRange();range.selectNodeContents(content);
      const sel=window.getSelection();sel.removeAllRanges();sel.addRange(range);
    }
    copy.setAttribute("aria-live","polite");
    window.setTimeout(()=>{copy.textContent=original;},1800);
  });
  // Context information is fully readable without JavaScript. On compact
  // screens it begins collapsed to save vertical space, but remains tappable.
  const ctx=q(".context-details");
  const syncContext=()=>{
    if(!ctx)return;
    if(window.matchMedia("(max-width: 780px)").matches){
      if(!ctx.hasAttribute("data-mobile-set")){
        ctx.open=false;ctx.setAttribute("data-mobile-set","yes");
      }
    }else{ctx.removeAttribute("data-mobile-set");ctx.open=true;}
  };
  if(ctx){syncContext();window.addEventListener("resize",syncContext);}
})();
