"""Prepare a small review overlay for the existing AGMAD Studio plugin. Never edits it in place."""
import argparse,re,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--studio',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 if a.output.exists():raise ValueError('Choose a fresh output directory')
 a.output.mkdir(parents=True);(a.output/'pages').mkdir();shutil.copytree(ROOT/'website/assets',a.output/'assets/cutter')
 for lang in ['en','ar']:
  path=Path('pages')/f'projects--silent-cutter.{lang}.html';page=(a.studio/path).read_text()
  if len(re.findall(r'<main\b',page))!=1:raise ValueError('Unexpected template; review manually')
  section=(ROOT/'website'/f'section.{lang}.html').read_text().replace('src="assets/','src="__AGMAD_ASSETS__/cutter/')
  page=re.sub(r'(<main\b[^>]*>).*?(</main>)',lambda m:m[1]+section+m[2],page,count=1,flags=re.S)
  page=page.replace('</head>','<link rel="stylesheet" href="__AGMAD_ASSETS__/cutter/site.css"><script>window.AGMAD_SERVER_PAGE=true;</script></head>')
  (a.output/path).write_text(page)
 # Patch only the documented project record. No other project or journal status changes.
 source=(a.studio/'assets/content.js').read_text();prefix='window.AGMAD_CONTENT = '
 if not source.startswith(prefix):raise ValueError('Unexpected content schema; review manually')
 data=json.loads(source[len(prefix):].strip().removesuffix(';'));project=next(p for p in data['projects'] if p['id']=='silent-cutter')
 project['tag']={'en':'Release candidate','ar':'إصدار مرشح'}
 project['scope']={'en':'Mac and Windows 1.3 owner-tested. Styled 1.4.0 prepared for release review; public downloads pending.','ar':'أكد صاحب المشروع عمل نسختي 1.3. تنسيق 1.4.0 جاهز لمراجعة الإصدار؛ التنزيل العام لم يُفعّل بعد.'}
 project['updates']=[{'en':'Unified -5 to +5 scale, Custom mode and optional local Noise/Music cleanup.','ar':'مقياس −5 إلى +5، وضع مخصص، وتنظيف اختياري للضوضاء أو الموسيقى محليًا.'},{'en':'Unsigned Windows / ad-hoc signed Mac; read installation guidance and validation limits.','ar':'Windows دون توقيع ناشر وMac بتوقيع محلي؛ راجع دليل التثبيت وحدود التحقق.'}]
 (a.output/'assets/content.js').write_text(prefix+json.dumps(data,ensure_ascii=False)+';\n')
 (a.output/'README.md').write_text('Review overlay only. These files were prepared against '+str(a.studio.name)+'. Re-read production bytes before applying. Only Silent Cutter project templates, its content record and cutter assets change. Existing Studio remains responsible for canonical/hreflang and noindex. Download buttons remain disabled. No production change was made. See website/INTEGRATION.md in the source repository.\n')
 print(a.output)
if __name__=='__main__':main()
