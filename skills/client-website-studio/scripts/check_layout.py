#!/usr/bin/env python3
"""Measure horizontal overflow of every page in a built preview, at phone, tablet and desktop widths.

    check_layout.py preview

Uses Edge or Chrome in headless mode (no install needed on most computers). Prints, for each page and
width, whether the page scrolls sideways and which elements stick out. Exit code 1 if any page overflows,
2 if no browser was found (then say plainly that layout was not measured).
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

sys.dont_write_bytecode = True
WIDTHS = [320, 360, 390, 768, 1024, 1440]
BROWSERS = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
]
NAMES = ['msedge', 'microsoft-edge', 'google-chrome', 'chrome', 'chromium', 'chromium-browser']

PAGE = '''<!doctype html><meta charset="utf-8"><body><pre id="out">running</pre><script>
var pages=%PAGES%,widths=%WIDTHS%,results=[];
function run(p,w){return new Promise(function(done){
  var f=document.createElement('iframe');f.style.cssText='position:absolute;left:0;top:0;border:0;height:900px;width:'+w+'px';
  f.onload=function(){setTimeout(function(){try{
    var d=f.contentDocument,de=d.documentElement,cw=de.clientWidth,bad=[];
    d.querySelectorAll('body *').forEach(function(e){var r=e.getBoundingClientRect();
      if(r.width&&(r.right>cw+1||r.left<-1)){var cs=getComputedStyle(e);if(cs.position!=='fixed'&&bad.length<6)bad.push(e.tagName.toLowerCase()+(e.className&&e.className.baseVal===undefined?'.'+String(e.className).split(' ')[0]:''));}});
    results.push({page:p,width:w,overflow:de.scrollWidth>cw+1,scrollWidth:de.scrollWidth,clientWidth:cw,offenders:bad});
  }catch(x){results.push({page:p,width:w,error:String(x)})}f.remove();done();},300)};
  f.src=p;document.body.appendChild(f);});}
(async function(){for(var i=0;i<pages.length;i++)for(var j=0;j<widths.length;j++)await run(pages[i],widths[j]);
document.getElementById('out').textContent='RESULT:'+JSON.stringify(results)+':END';})();
</script>'''


def find_browser() -> str | None:
    for path in BROWSERS:
        if Path(path).is_file():
            return path
    for name in NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    folder = args.folder.resolve()
    pages = sorted(p.relative_to(folder).as_posix() for p in folder.rglob('index.html'))
    if not pages:
        parser.error('no index.html files found')
    browser = find_browser()
    if not browser:
        print('No Edge or Chrome found: layout was NOT measured.')
        raise SystemExit(2)

    html = PAGE.replace('%PAGES%', json.dumps(pages)).replace('%WIDTHS%', json.dumps(WIDTHS)).encode('utf-8')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith('/__check__.html'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html)
            else:
                super().do_GET()

        def log_message(self, *a):
            pass

    server = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(folder)))
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    profile = tempfile.mkdtemp(prefix='layout-check-')
    try:
        out = subprocess.run([browser, '--headless', '--disable-gpu', f'--user-data-dir={profile}',
                              '--virtual-time-budget=60000', '--dump-dom',
                              f'http://127.0.0.1:{port}/__check__.html'],
                             capture_output=True, text=True, timeout=180, encoding='utf-8', errors='replace').stdout
    finally:
        server.shutdown()
        shutil.rmtree(profile, ignore_errors=True)
    match = re.search(r'RESULT:(\[.*?\]):END', out, re.S)
    if not match:
        print('The browser did not return measurements: layout was NOT measured.')
        print(out[:300])
        raise SystemExit(2)
    results = json.loads(match.group(1).replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>'))
    bad = 0
    for r in results:
        if r.get('error'):
            print(f'? {r["page"]} @ {r["width"]}px: could not measure ({r["error"]})')
            bad += 1
        elif r['overflow']:
            bad += 1
            print(f'OVERFLOW {r["page"]} @ {r["width"]}px: page is {r["scrollWidth"]}px wide, window {r["clientWidth"]}px; sticking out: {", ".join(r["offenders"]) or "unknown"}')
    if bad:
        print(f'\n{bad} problem(s). Fix them, rebuild the preview and run this again.')
        raise SystemExit(1)
    print(f'No sideways overflow: {len(pages)} page(s) x {len(WIDTHS)} widths ({", ".join(map(str, WIDTHS))} px).')


if __name__ == '__main__':
    main()
