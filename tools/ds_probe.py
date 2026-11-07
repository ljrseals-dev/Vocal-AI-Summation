import ctypes, numpy as np
from scipy import signal
import os, subprocess, tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); SO=os.path.join(tempfile.gettempdir(),'ds_probe.so')
subprocess.check_call(['g++','-O2','-std=c++17','-shared','-fPIC','-I'+os.path.join(HERE,'..'),os.path.join(HERE,'ds_wrap.cpp'),'-o',SO])
L=ctypes.CDLL(SO); L.ds_process.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_double,ctypes.c_int,ctypes.c_float,ctypes.c_float]
FS=48000
def run(x,stretch=1,mix=1.0,trim=0.0):
    x=np.ascontiguousarray(x,dtype=np.float32); y=np.zeros_like(x); L.ds_process(x.ctypes.data,y.ctypes.data,len(x),FS,stretch,mix,trim); return y.astype(np.float64)
def tone(f,db,sec=3.0): t=np.arange(int(FS*sec))/FS; return 10**(db/20)*np.sin(2*np.pi*f*t)
def gain_db(f,db,**kw):
    x=tone(f,db); y=run(x,**kw); s=slice(FS*2,None); return 20*np.log10(np.std(y[s])/np.std(x[s]))
print("=== A. steady-state gain (dB) vs tone level, mix=1 trim=0 | stretch=True ===")
levels=(-70,-60,-50,-40,-34,-30,-20,-6)
print(f"{'tone':>8s}"+"".join(f"{l:>8d}" for l in levels)+"   (dBFS peak)")
for f in (40,500,5000,14000):
    print(f"{f:>6d}Hz"+"".join(f"{gain_db(f,l):8.1f}" for l in levels))
print("\n=== A2. same with stretch=False ===")
for f in (40,500,5000,14000):
    print(f"{f:>6d}Hz"+"".join(f"{gain_db(f,l,stretch=0):8.1f}" for l in levels))
print("\n=== B. defaults (mix .55, trim -1 dB): gain at -6 dBFS across frequency (should be ~0 if transparent when loud) ===")
for f in (100,500,2000,8000,12000): print(f"  {f:6d} Hz: {gain_db(f,-6,mix=0.55,trim=-1.0):6.2f} dB   | mix=1,trim=0: {gain_db(f,-6):6.2f} dB")
print("\n=== C. README test: 8 kHz at -34 dBFS, mix=1 trim=0 (spec asked +8 dB) ===")
print(f"  stretch=True: {gain_db(8000,-34):+.2f} dB   stretch=False: {gain_db(8000,-34,stretch=0):+.2f} dB   (8 kHz sits in band 2: cap 16 dB, ratio 3)")
print("\n=== D. THD of the gain stage (tone below threshold so gain is active), dBc ===")
def thd(f,db):
    y=run(tone(f,db,4.0))[FS*2:]; N=len(y); S=np.abs(np.fft.rfft(y*np.hanning(N)))**2; fr=np.fft.rfftfreq(N,1/FS)
    P=lambda k:S[np.argmin(abs(fr-k*f))-3:np.argmin(abs(fr-k*f))+4].sum(); return 10*np.log10(sum(P(k) for k in range(2,7))/P(1))
for f,db in ((60,-45),(60,-36),(100,-45),(1000,-45),(5000,-45)): print(f"  {f:5d} Hz @ {db} dBFS: THD(2-6) = {thd(f,db):6.1f} dBc")
print("\n=== E. frequency flatness when loud (-6 dBFS, mix=1, trim=0): max deviation 100 Hz-16 kHz ===")
fs_=np.geomspace(100,16000,30); g=[gain_db(f,-6) for f in fs_]; print(f"  min {min(g):+.2f} dB  max {max(g):+.2f} dB")
print("\n=== F. is it expansion or compression? level in -> level out at 500 Hz (mix=1, trim=0) ===")
for l in (-70,-60,-50,-40,-30): print(f"  in {l:4d} dBFS -> out {l+gain_db(500,l):7.1f} dBFS")
