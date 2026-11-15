"""Render the maintained Markdown summary for optional browser print/export.

Uses the existing Markdown dependency. Does not launch a browser or claim a PDF.
"""
from pathlib import Path
import markdown

HERE=Path(__file__).resolve().parent


def build():
    source=(HERE/'ONE_PAGER.md').read_text(encoding='utf-8')
    body=markdown.markdown(source,extensions=['tables','fenced_code'])
    page='''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'">
<title>LymeScope — one-page submission draft</title>
<style>
@page{size:letter;margin:.5in}
*{box-sizing:border-box}body{background:#eaf1f1;color:#18343e;font:14px/1.38 system-ui,Arial,sans-serif;margin:0}
main{width:min(100%,8.5in);margin:24px auto;background:white;padding:.5in;border-top:7px solid #087f80}
h1{font-size:31px;letter-spacing:.16em;margin:0 0 2px;color:#075b66}p{margin:9px 0}a{color:#086b78;overflow-wrap:anywhere}strong{color:#0a4650}code{font-size:.87em;overflow-wrap:anywhere}
.print-note{max-width:8.5in;margin:12px auto;padding:0 12px;font-size:13px}
@media print{body{background:white;font-size:9pt;line-height:1.29}main{width:auto;margin:0;padding:0;border-top:5px solid #087f80}h1{font-size:25pt}p{margin:6pt 0}.print-note{display:none}a{color:inherit;text-decoration:none}}
@media(max-width:600px){main{margin:0;padding:24px}h1{font-size:28px}}
</style><p class="print-note">Print-oriented copy of ONE_PAGER.md. Browser pagination and PDF export are not verified. Scientific source links remain live.</p><main>'''+body+'</main></html>\n'
    (HERE/'ONE_PAGER.html').write_text(page,encoding='utf-8',newline='\n')
    print('ONE_PAGER.html generated; PDF/layout not verified')


if __name__=='__main__':build()
