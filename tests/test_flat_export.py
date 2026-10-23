"""Flat export naming, no-overwrite publication and real no-cut renders."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import hashlib,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
TOOLS=Path(os.environ.get('AGMAD_EXPORT_TEST_TOOLS') or Path(__file__).resolve().parents[1]/'macos/Source/Payload/engine/tools')
sys.path.insert(0,str(TOOLS))
import export_process as export
class ExportNamingTests(unittest.TestCase):
 def test_styles_and_unicode(self):
  self.assertEqual(export.filename_base('شرح.mp4','name'),'شرح')
  self.assertEqual(export.filename_base('lecture.mp4','date-name','AG',date(2026,10,22)),'AG_2026-10-22_lecture')
  self.assertEqual(export.filename_base('x.mp4','date','',date(2026,10,22)),'2026-10-22')
  self.assertLessEqual(len(export.filename_base('ع'*200+'.mp4','name','م'*60).encode()),220)
 def test_bad_prefixes(self):
  for value in ['../escape','a/b','a\\b','a\nb','x'*61,'..']:
   with self.assertRaises(ValueError):export.validate_prefix(value)
 def test_exclusive_copy_serial_and_failure_cleanup(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder).resolve();dest=root/'exports';dest.mkdir();video=root/'render.mp4';video.write_bytes(b'complete-video')
   original=dest/'lecture.mp4';original.write_bytes(b'original-preserved')
   target=export.publish(video,dest,'lecture.mp4','name');self.assertEqual(target.name,'lecture_002.mp4');self.assertEqual(original.read_bytes(),b'original-preserved')
   with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(lambda _:export.publish(video,dest,'a.mp4','serial','AG'),range(4)))
   self.assertEqual(sorted(p.name for p in files),['AG_0001.mp4','AG_0002.mp4','AG_0003.mp4','AG_0004.mp4'])
   for error in [OSError('disk full'),KeyboardInterrupt()]:
    before=set(dest.iterdir())
    with patch.object(export.shutil,'copyfileobj',side_effect=error):
     with self.assertRaises(type(error)):export.publish(video,dest,'failed.mp4','name')
    self.assertEqual(set(dest.iterdir()),before)
@unittest.skipUnless(all(shutil.which(x) for x in ['ffmpeg','ffprobe','auto-editor']),'Media tools required')
class FlatExportMediaTests(unittest.TestCase):
 def test_off_cleanup_watermark_and_normal_cut(self):
  with tempfile.TemporaryDirectory(prefix='agmad-flat-') as folder:
   root=Path(folder).resolve();dest=root/'exports';dest.mkdir();reports=root/'reports';engine=root/'engine';engine.mkdir();source=dest/'lecture.mp4';logo=root/'logo.png'
   def ff(args):return subprocess.run(['ffmpeg','-nostdin','-v','error','-y']+[str(a) for a in args],check=True,capture_output=True)
   ff(['-f','lavfi','-i','color=black:s=320x180:r=30:d=6','-f','lavfi','-i',r'aevalsrc=if(lt(mod(t\,3)\,2)\,0.2*sin(2*PI*440*t)\,0):s=48000:d=6','-c:v','libx264','-preset','ultrafast','-c:a','aac',source])
   ff(['-f','lavfi','-i','color=white:s=64x32','-frames:v','1',logo])
   source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
   base=[sys.executable,str(TOOLS/'export_process.py'),'--input',str(source),'--destination',str(dest),'--engine',str(engine),'--reports-root',str(reports)]
   # Prepared cache exercises Noise without running/downloading a model.
   binary=engine/'tools/runtime/deep-filter';binary.parent.mkdir(parents=True);binary.write_bytes(b'not-executed');binary.chmod(0o755)
   (engine/'CACHE').mkdir();key=hashlib.sha256((source_hash+'noise'+hashlib.sha256(binary.read_bytes()).hexdigest()+'v4.1-first-audio-48k-mono-delay-compensated').encode()).hexdigest()
   ff(['-i',source,'-vn','-ac','1','-ar','48000','-c:a','pcm_s16le',engine/'CACHE'/(key+'.wav')])
   # Cutting Off must not depend on Auto-Editor being on PATH.
   binpath=root/'bin';binpath.mkdir()
   for tool in ['ffmpeg','ffprobe']:(binpath/tool).symlink_to(shutil.which(tool))
   env=dict(os.environ,PATH=str(binpath))
   cases=[(['--mode','off','--cut-off'],'name','',env),
          (['--mode','off','--cut-off','--watermark-file',str(logo),'--watermark-opacity','.25'],'serial','Brand',env),
          (['--mode','noise','--cut-off'],'date','',env),
          (['--mode','off','--level','0'],'date-name','Lesson',None)]
   for options,style,prefix,environment in cases:
    completed=subprocess.run(base+options+['--filename-style',style,'--filename-prefix',prefix],capture_output=True,text=True,env=environment,timeout=30)
    self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
    done=next(json.loads(line) for line in completed.stdout.splitlines() if line.startswith('{') and json.loads(line)['event']=='done')
    path=Path(done['output']);self.assertEqual(path.parent,dest);self.assertTrue(path.is_file());self.assertTrue(Path(done['log']).is_relative_to(reports))
    report=json.loads((Path(done['log']).parent/'comparison.json').read_text());self.assertEqual(report['output'],str(path))
    log=Path(done['log']).read_text()
    if '--cut-off' in options:
     self.assertEqual(done['profile'],'off');self.assertEqual(len(done['clips']),1);self.assertLess(abs(done['outputDuration']-done['inputDuration']),.15);self.assertNotIn("COMMAND: ['auto-editor'",log)
    else:self.assertLess(done['outputDuration'],done['inputDuration']-.5)
    if style=='serial':self.assertEqual(path.name,'Brand_0001.mp4');self.assertIn('watermark',report)
    if style=='name':self.assertEqual(path.name,'lecture_002.mp4')
    self.assertTrue(all(p.suffix=='.mp4' and p.is_file() for p in dest.iterdir()))
    self.assertFalse(list(reports.glob('*/**/*_CLEAN.mp4')))
   self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),source_hash)
