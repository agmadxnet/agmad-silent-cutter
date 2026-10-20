"""Render original AGMAD-coloured waveform artwork. Build-only dependency: Pillow."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
BRAND=ROOT/'branding';BRAND.mkdir(exist_ok=True)
# Paired waveforms separated by an intentional pause; no third-party logo/artwork.
bars=[(240,120),(310,240),(380,360),(450,190),(574,190),(644,360),(714,240),(784,120)]
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><defs><linearGradient id="tile" x2="100%" y2="100%"><stop stop-color="#252d3c"/><stop offset="1" stop-color="#060708"/></linearGradient><linearGradient id="wave" gradientUnits="userSpaceOnUse" x1="200" y1="200" x2="800" y2="800"><stop stop-color="#f2f3f6"/><stop offset="1" stop-color="#c6d4ff"/></linearGradient></defs><rect x="64" y="64" width="896" height="896" rx="200" fill="url(#tile)" stroke="#7d8596" stroke-width="3"/><g stroke="url(#wave)" stroke-width="38" stroke-linecap="round">'
for x,h in bars:svg+=f'<path d="M{x} {512-h/2}v{h}"/>'
svg+='</g><path d="M512 310v404" stroke="#7d8596" stroke-width="3" stroke-dasharray="8 18"/></svg>'
(BRAND/'silent-cutter.svg').write_text(svg)
scale=2;image=Image.new('RGBA',(2048,2048));draw=ImageDraw.Draw(image)
draw.rounded_rectangle((128,128,1920,1920),radius=400,fill='#10151e',outline='#7d8596',width=4)
for x,h in bars:
 box=(int((x-19)*scale),int((512-h/2-19)*scale),int((x+19)*scale),int((512+h/2+19)*scale));draw.rounded_rectangle(box,radius=38,fill='#c6d4ff')
for y in range(310,714,26):draw.line((1024,y*2,1024,(y+8)*2),fill='#7d8596',width=6)
image=image.resize((1024,1024),Image.Resampling.LANCZOS);image.save(BRAND/'silent-cutter.png')
image.save(ROOT/'windows/assets/icon.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
image.save(ROOT/'windows/assets/icon.png');image.save(ROOT/'macos/Source/AppIcon.png')
if sys.platform=='darwin':
 iconset=BRAND/'AppIcon.iconset';iconset.mkdir(exist_ok=True)
 for n in [16,32,128,256,512]:
  for factor in [1,2]:image.resize((n*factor,n*factor),Image.Resampling.LANCZOS).save(iconset/f'icon_{n}x{n}{"@2x" if factor==2 else ""}.png')
 subprocess.run(['iconutil','-c','icns',str(iconset),'-o',str(ROOT/'macos/Source/AppIcon.icns')],check=True)
print('Icons generated')
