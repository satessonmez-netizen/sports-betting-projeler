const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:912,height:800},deviceScaleFactor:2});
await p.goto('file://'+process.argv[2]);
await (await p.$('#w')).screenshot({path:process.argv[3],type:'jpeg',quality:92});await b.close();})();
