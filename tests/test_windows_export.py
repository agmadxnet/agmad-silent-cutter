"""Windows filename/copy rules run in isolation from the Mac adapter imports."""
import os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WindowsExportTests(unittest.TestCase):
 def test_windows_naming_collisions_and_cancelled_copy(self):
  code=r'''
from concurrent.futures import ThreadPoolExecutor
import os,tempfile
from pathlib import Path
import export_process as e
for bad in ['a:b','a?b','a*b','a"b','a|b','a<b','a>b','name.']:
 try:e.validate_prefix(bad)
 except ValueError:pass
 else:raise AssertionError(bad)
assert e.filename_base('CON.mp4','name')=='video_CON'
assert e.filename_base('nul.any.mp4','name')=='video_nul.any'
assert e.filename_base('شرح.mp4','name')=='شرح'
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder);dest=root/'out';dest.mkdir();video=root/'render.mp4';video.write_bytes(b'render')
 original=dest/'lecture.mp4';original.write_bytes(b'original')
 assert e.publish(video,dest,'lecture.mp4','name').name=='lecture_002.mp4'
 assert original.read_bytes()==b'original'
 with ThreadPoolExecutor(max_workers=4) as pool:outputs=list(pool.map(lambda _:e.publish(video,dest,'x.mp4','serial','AG'),range(4)))
 assert sorted(p.name for p in outputs)==['AG_0001.mp4','AG_0002.mp4','AG_0003.mp4','AG_0004.mp4']
 before=set(dest.iterdir())
 try:e.publish(root/'missing.mp4',dest,'failed.mp4','name')
 except FileNotFoundError:pass
 else:raise AssertionError('missing source accepted')
 assert set(dest.iterdir())==before
 cancel=root/'cancel';cancel.touch();os.environ['AGMAD_CANCEL_FILE']=str(cancel)
 try:e.publish(video,dest,'cancelled.mp4','name')
 except KeyboardInterrupt:pass
 else:raise AssertionError('cancel ignored')
 assert set(dest.iterdir())==before
print('Windows filename, Unicode, concurrent serial, no-overwrite, failure and cancellation checks passed')
'''
  env=dict(os.environ,PYTHONPATH=str(ROOT/'windows/app/tools'))
  result=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True,env=env,timeout=20)
  self.assertEqual(result.returncode,0,result.stdout+result.stderr)
