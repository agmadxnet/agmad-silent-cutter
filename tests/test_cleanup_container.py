"""Real cached-cleanup mux regression; no models downloaded or executed."""
import importlib.util,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cleanup_engine',ROOT/'macos/Source/Payload/engine/tools/process.py')
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
def run(args):
 result=subprocess.run([str(x) for x in args],capture_output=True)
 if result.returncode:
  error=subprocess.CalledProcessError(result.returncode,args,output=result.stdout,stderr=result.stderr)
  error.add_note(result.stderr.decode(errors="replace")[-2000:]);raise error
 return result
@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
class CleanupContainerTests(unittest.TestCase):
 def exercise(self,codec,mode):
  if codec=='libsvtav1' and b'libsvtav1' not in run(['ffmpeg','-hide_banner','-encoders']).stdout:self.skipTest('AV1 encoder unavailable')
  with tempfile.TemporaryDirectory(prefix='agmad-codec-') as folder:
   temp=Path(folder);source=temp/'source.mp4'
   cmd=['ffmpeg','-nostdin','-v','error','-y','-f','lavfi','-i','testsrc2=size=160x90:rate=15:duration=8','-f','lavfi','-i',r'aevalsrc=if(lt(mod(t\,4)\,2)\,0.2*sin(2*PI*440*t)\,0):s=48000:d=8','-c:v',codec,'-preset','12' if codec=='libsvtav1' else 'ultrafast','-crf','40','-c:a','aac',source]
   run(cmd);original=engine.fingerprint(source);saved=engine.ROOT;engine.ROOT=temp/'engine'
   (engine.ROOT/'CACHE').mkdir(parents=True)
   binary=engine.ROOT/('tools/runtime/deep-filter' if mode=='noise' else 'tools/models/'+engine.MODEL)
   binary.parent.mkdir(parents=True);binary.write_bytes(b'cache-key-fixture-not-executed')
   key=engine.hashlib.sha256((original+mode+engine.fingerprint(binary)+'v4.1-first-audio-48k-mono-delay-compensated').encode()).hexdigest()
   cache=engine.ROOT/'CACHE'/(key+'.wav')
   run(['ffmpeg','-nostdin','-v','error','-y','-i',source,'-vn','-ac','1','-ar','48000','-c:a','pcm_s16le',cache])
   try:
    if codec=='libsvtav1':
     with self.assertRaises(subprocess.CalledProcessError) as error:run(['ffmpeg','-nostdin','-v','error','-y','-i',source,'-i',cache,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','pcm_s16le',temp/'old.mov'])
     self.assertIn(b'av1 only supported',error.exception.stderr.lower())
    with (temp/'PROCESS.log').open('w') as log:ready=engine.cleaned_source(source,mode,temp,log,lambda m:None)
    self.assertEqual(ready.suffix,'.mkv');info=engine.probe(ready)
    self.assertEqual(next(s['codec_name'] for s in info['streams'] if s['codec_type']=='video'),'av1' if codec=='libsvtav1' else 'h264')
    self.assertEqual(next(s['codec_name'] for s in info['streams'] if s['codec_type']=='audio'),'flac')
    self.assertLess(abs(float(info['format']['duration'])-8),.15)
    run(['ffmpeg','-v','error','-i',ready,'-f','null','-'])
    def packet_hash(p):return run(['ffmpeg','-v','error','-i',p,'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()
    self.assertEqual(packet_hash(source),packet_hash(ready));self.assertEqual(engine.fingerprint(source),original)
    if shutil.which('auto-editor'):
     common=['auto-editor',ready,'--edit','audio:threshold=4%','--margin','.25s','--smooth','.6s,.15s','--no-open']
     timeline=temp/'timeline.v3';run(common+['--export','v3','-o',timeline]);self.assertTrue(json.loads(timeline.read_text())['v'][0])
     output=temp/'result.mp4';run(common+['--video-codec','libx264','--audio-codec','aac','--pix-fmt','yuv420p','-o',output])
     rendered=engine.probe(output);self.assertEqual({s['codec_type'] for s in rendered['streams']},{'audio','video'})
     timeline_data=json.loads(timeline.read_text());from fractions import Fraction
     planned=max(c['start']+c['dur'] for c in timeline_data['v'][0])/float(Fraction(timeline_data['timebase']))
     self.assertLess(abs(float(rendered['format']['duration'])-planned),.15)
     self.assertGreater(float(rendered['format']['duration']),0);self.assertLess(float(rendered['format']['duration']),8)
   finally:engine.ROOT=saved
 def test_av1_noise_full_source(self):self.exercise('libsvtav1','noise')
 def test_av1_music_full_source(self):self.exercise('libsvtav1','music')
 def test_h264_noise_full_source(self):self.exercise('libx264','noise')
