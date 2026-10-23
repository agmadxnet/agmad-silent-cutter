"""Build Windows package with a verified existing runtime or locked official downloads."""
import argparse,hashlib,html,json,re,shutil,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def unpack(source,destination):
 with zipfile.ZipFile(source) as archive:
  for item in archive.infolist():
   target=(destination/item.filename).resolve()
   if not target.is_relative_to(destination.resolve()):raise ValueError('Unsafe archive path')
  archive.extractall(destination)
def download(url,sha,target):
 if not target.exists() or digest(target)!=sha:
  with urllib.request.urlopen(url,timeout=120) as response,target.open('wb') as output:shutil.copyfileobj(response,output)
 if digest(target)!=sha:target.unlink();raise ValueError('Checksum mismatch: '+url)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--runtime',type=Path);ap.add_argument('--version');ap.add_argument('--readme',type=Path);ap.add_argument('--validation',type=Path);args=ap.parse_args()
 version=args.version or (ROOT/'VERSION').read_text().strip();
 if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:_Test)?',version):raise ValueError('Invalid package version')
 dest=args.output/f'Agmad_Silent_Cutter_Windows_{version}'
 if dest.exists():raise ValueError('Output exists; choose a fresh build folder')
 shutil.copytree(ROOT/'windows',dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc','runtime','.DS_Store'))
 info_path=dest/'assets/build-info.json';info=json.loads(info_path.read_text());info['app_version']=version;info_path.write_text(json.dumps(info,indent=2)+'\n')
 runtime=dest/'runtime';expected=json.loads((ROOT/'windows/assets/runtime-sha256.json').read_text())
 if args.runtime:shutil.copytree(args.runtime,runtime,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 else:
  cache=args.output/'downloads';cache.mkdir(parents=True,exist_ok=True);runtime.mkdir()
  info=json.loads((ROOT/'windows/assets/build-info.json').read_text())
  target=cache/'python.zip';download(info['python_url'],info['python_sha256'],target);unpack(target,runtime)
  site=runtime/'Lib/site-packages';site.mkdir(parents=True)
  for filename,sha in info['wheels'].items():
   name,version=filename.split('-')[:2]
   with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/{version}/json',timeout=60) as response:meta=json.load(response)
   url=next(item['url'] for item in meta['urls'] if item['filename']==filename)
   target=cache/filename;download(url,sha,target);unpack(target,site)
  (runtime/'python313._pth').write_bytes(b'python313.zip\n.\nLib\\site-packages\n..\\app\n..\\app\\tools\nimport site\n')
  for item in list(runtime.rglob('*')):
   if item.is_file() and item.relative_to(runtime).as_posix() not in expected:item.unlink()
 # The interpreter path file is generated; newline differences are harmless, all binary files must match.
 for name,sha in expected.items():
  item=runtime/name
  if name=='python313._pth':continue
  if not item.is_file() or digest(item)!=sha:raise ValueError('Runtime file mismatch: '+name)
 readme=(args.readme or ROOT/'docs/WINDOWS.ar.md').read_text(encoding='utf-8');(dest/'README_AR.md').write_text(readme,encoding='utf-8')
 (dest/'README_AR.html').write_text('<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><title>AGMAD Silent Cutter</title><style>body{background:#060708;color:#f2f3f6;font:17px/1.9 Tahoma,Arial,sans-serif;max-width:960px;margin:40px auto;padding:24px}pre{font:inherit;white-space:pre-wrap}</style><h1>AGMAD Silent Cutter</h1><pre>'+html.escape(readme)+'</pre></html>',encoding='utf-8')
 (dest/'START_HERE.txt').write_text('AGMAD Silent Cutter '+version+'\nأغلق النسخة القديمة، وفك ضغط الحزمة بالكامل، ثم افتح Install.cmd.\nافتح README_AR.html للتعليمات العربية.\nالأدوات والنماذج والنتائج السابقة تبقى محفوظة.\n',encoding='utf-8-sig')
 shutil.copy2(ROOT/'LICENSE',dest/'LICENSE');shutil.copy2(args.validation or ROOT/'docs/VALIDATION.md',dest/'VALIDATION.md')
 archive=dest.with_name(dest.name+'.zip')
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for item in sorted(dest.rglob('*')):
   if item.is_file() and '__pycache__' not in item.parts and item.suffix!='.pyc':z.write(item,item.relative_to(dest.parent))
 with zipfile.ZipFile(archive) as z:
  if z.testzip():raise ValueError('ZIP integrity failure')
 archive.with_name(archive.name+'.sha256').write_text(digest(archive)+'  '+archive.name+'\n')
 print(archive)
if __name__=='__main__':main()
