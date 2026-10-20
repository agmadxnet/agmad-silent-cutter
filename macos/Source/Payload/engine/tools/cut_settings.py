"""Validated cutting settings shared by the app adapter and focused checks."""
import math
GENTLE = {
 '1': (1.0, 0.35, 1.0, 'VERY_GENTLE'),
 '2': (2.0, 0.30, 0.8, 'GENTLE'),
 '3': (4.0, 0.25, 0.6, 'BALANCED'),
}
SCALE = {
 -5:(0.5,0.50,1.5), -4:(0.75,0.40,1.2), -3:(1.0,0.35,1.0),
 -2:(1.5,0.325,0.9), -1:(2.0,0.30,0.8), 0:(4.0,0.25,0.6),
}
LIMITS = {'threshold': (0.5,40.0), 'padding': (0.02,0.60), 'pause': (0.10,2.0)}
def resolve(profile, standard, strength='3', gentle='2', threshold=None, padding=None, pause=None, level=0):
 if profile=='scale':
  if level not in range(-5,6): raise ValueError('Level must be -5 to +5.')
  if level>0: return standard[str(level)]
  threshold,padding,pause=SCALE[level]
  return f'{threshold:g}%',f'{padding:g}s',f'{pause:g}s,0.15s','LEVEL_'+str(level)
 if profile=='standard':
  t,m,s,tag=standard[strength]
  return t,m,s,tag
 if profile=='gentle':
  threshold,padding,pause,tag=GENTLE[gentle]
 elif profile=='custom': tag='CUSTOM'
 else: raise ValueError('Unknown cutting mode')
 values=dict(threshold=threshold,padding=padding,pause=pause)
 for name,value in values.items():
  low,high=LIMITS[name]
  if value is None or not math.isfinite(value) or not low<=value<=high:
   raise ValueError(f'{name} must be between {low} and {high}.')
 return f'{threshold:g}%',f'{padding:g}s',f'{pause:g}s,0.15s',tag
