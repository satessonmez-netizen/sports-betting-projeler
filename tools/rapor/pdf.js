const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2]);
await p.pdf({path:process.argv[3],format:'A4',margin:{top:'14mm',bottom:'14mm',left:'12mm',right:'12mm'},printBackground:true});
await b.close();})();
