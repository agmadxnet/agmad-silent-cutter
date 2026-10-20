import hashlib,importlib.util,json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
MAC=ROOT/'macos/Source/Payload/engine/tools';WIN=ROOT/'windows/app/tools'
settings=module(MAC/'cut_settings.py','settings');engine=module(MAC/'process.py','engine')
class SettingsTests(unittest.TestCase):
 def test_platform_parity(self):self.assertEqual((MAC/'cut_settings.py').read_bytes(),(WIN/'cut_settings.py').read_bytes())
 def test_positive_presets_remain_original(self):
  expected=[('8%','0.20s','0.45s,0.15s'),('12%','0.12s','0.25s,0.12s'),('20%','0.06s','0.15s,0.08s'),('30%','0.04s','0.10s,0.06s'),('40%','0.02s','0.08s,0.05s')]
  for level,triple in enumerate(expected,1):self.assertEqual(settings.resolve('scale',engine.PRESETS,level=level)[:3],triple)
 def test_zero_is_balanced(self):self.assertEqual(settings.resolve('scale',engine.PRESETS,level=0)[:3],('4%','0.25s','0.6s,0.15s'))
 def test_gentlest_preserves_long_pauses(self):self.assertEqual(settings.resolve('scale',engine.PRESETS,level=-5)[:3],('0.5%','0.5s','1.5s,0.15s'))
 def test_custom_rejects_invalid_values(self):
  for key,(low,high) in settings.LIMITS.items():
   for bad in (low-.001,high+.001,float('nan'),float('inf'),None):
    values=dict(threshold=2,padding=.3,pause=.8);values[key]=bad
    with self.subTest(key=key,value=bad),self.assertRaises(ValueError):settings.resolve('custom',engine.PRESETS,**values)
 def test_custom_inclusive_bounds(self):
  for index in [0,1]:settings.resolve('custom',engine.PRESETS,**{key:limits[index] for key,limits in settings.LIMITS.items()})
 def test_no_processing_drift_from_working_13(self):
  baseline=json.loads((ROOT/'tests/engine-baseline-1.3.json').read_text())
  for path,sha in baseline.items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),sha,path)
if __name__=='__main__':unittest.main()
