"""Watermark export tests: actual output pixels, audio/timeline and invalid input."""
import importlib.util,json,math,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TOOLS=Path(os.environ.get('AGMAD_EXPORT_TEST_TOOLS') or ROOT/'macos/Source/Payload/engine/tools')
sys.path.insert(0,str(TOOLS))
import watermark_process as wm
class WatermarkValidationTests(unittest.TestCase):
 def test_geometry_and_edges(self):
  self.assertEqual(wm.geometry(320,180,64,32,.2,1,0),(64,32,256,0))
  w,h,x,y=wm.geometry(320,180,32,1000,.4,1,1)
  self.assertLessEqual(h,145);self.assertGreaterEqual(x,0);self.assertGreaterEqual(y,0)
 def test_invalid_values_rejected_before_reading(self):
  for index in range(4):
   for value in [float('nan'),float('inf'),-1]:
    args=[.15,.95,.95,.7];args[index]=value
    with self.assertRaises(ValueError):wm.validate('missing.png',*args)
@unittest.skipUnless(all(shutil.which(x) for x in ['ffmpeg','ffprobe','auto-editor']),'Media tools required')
class WatermarkExportTests(unittest.TestCase):
 def test_opacity_position_and_comparison(self):
  with tempfile.TemporaryDirectory(prefix='agmad-watermark-') as folder:
   root=Path(folder);source=root/'source.mp4';logo=root/'logo.png';engine=root/'engine';engine.mkdir()
   def ff(args):return subprocess.run(['ffmpeg','-nostdin','-v','error','-y']+[str(a) for a in args],check=True,capture_output=True)
   ff(['-f','lavfi','-i','color=black:s=320x180:r=30:d=6','-f','lavfi','-i',r'aevalsrc=if(lt(mod(t\,3)\,2)\,0.2*sin(2*PI*440*t)\,0):s=48000:d=6','-c:v','libx264','-preset','ultrafast','-c:a','aac',source])
   ff(['-f','lavfi','-i','color=white:s=64x32','-frames:v','1',logo])
   base=[sys.executable,str(TOOLS/'watermark_process.py'),'--input',str(source),'--destination',str(root),'--engine',str(engine),'--mode','off','--profile','scale','--level','0','--watermark-file',str(logo),'--watermark-width','.2','--watermark-x','1','--watermark-y','0']
   for opacity,alpha in [(.25,1),(0,1),(1,1),(.5,.5)]:
    if alpha < 1:ff(['-f','lavfi','-i','color=white@0.5:s=64x32,format=rgba','-frames:v','1',logo])
    result=subprocess.run(base+['--watermark-opacity',str(opacity)],capture_output=True,text=True,timeout=30)
    self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    events=[json.loads(s) for s in result.stdout.splitlines() if s.startswith('{')];done=next(e for e in events if e['event']=='done')
    output=Path(done['output']);self.assertTrue(output.exists());self.assertLess(abs(done['outputDuration']-max(c['start']+c['duration'] for c in done['clips'])),.15)
    pixels=ff(['-i',output,'-frames:v','1','-vf','format=rgb24','-f','rawvideo','-']).stdout
    sample=pixels[(10*320+280)*3:(10*320+280)*3+3];self.assertTrue(all(abs(v-255*opacity*alpha)<8 for v in sample),list(sample))
    self.assertLess(max(pixels[(100*320+100)*3:(100*320+100)*3+3]),5)
    report=json.loads((output.parent/'comparison.json').read_text());self.assertEqual(report['watermark']['opacity'],opacity)
    self.assertFalse(list(output.parent.glob('branding_*')))
    log=(output.parent/'PROCESS.log').read_text();self.assertEqual('Applying watermark' in result.stdout,opacity>0)
    self.assertEqual(log.count('unbranded.mp4')>0,opacity>0)
   bad=subprocess.run(base+['--watermark-opacity','nan'],capture_output=True,text=True)
   self.assertNotEqual(bad.returncode,0);self.assertIn('outside its allowed range',bad.stdout)
