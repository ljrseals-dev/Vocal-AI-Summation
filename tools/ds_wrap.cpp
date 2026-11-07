#include "DolbyStretch.h"
extern "C" void ds_process(const float* in, float* out, int n, double sr, int stretch, float mix, float trim){
  vh::DolbyStretch d; d.prepare(sr); vh::DolbyStretch::Params p; p.stretch=stretch!=0; p.mix=mix; p.trimDb=trim; d.setParams(p);
  for(int i=0;i<n;++i) out[i]=d.process(in[i],0);
}
