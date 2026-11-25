import numpy as np
from scipy.stats import norm
k=8.617333e-5
def AF(T,Ea=0.7,Tu=55): return np.exp(Ea/k*(1/(Tu+273.15)-1/(T+273.15)))
def AFg(m,s,Ea=0.7,Tu=55):
    x=np.linspace(-6,6,4001); w=norm.pdf(x); return np.trapezoid(AF(m+s*x,Ea,Tu)*w,x)
bb=(107.73,2.64); pid=(117.04,1.25)
for n,(m,s) in [('bb',bb),('pid',pid)]:
    print(n,'AF(mean)',AF(m),'gauss',AFg(m,s),'ripple gain %',100*(AFg(m,s)/AF(m)-1))
for Ea in [0.5,0.7,0.9]:
    print(Ea,'ratio mean-only',AF(pid[0],Ea)/AF(bb[0],Ea),'ratio gauss',AFg(*pid,Ea)/AFg(*bb,Ea))
# equivalent hours at 55C over 22.08h post-soak? check 711/1182
for h in [22.08,23.08]: print(h, AFg(*bb)*h, AFg(*pid)*h, AF(bb[0])*h,AF(pid[0])*h)
# delta budget
for eta in [0.05,0.1,0.2]:
    Ts=115+273.15; print(eta,k*Ts**2/0.7*np.log(1+eta))
# detectability
s,tau,beta=0.84,314/3600,0.0183
Tmin=lambda s,tau,b:(216*s**2*tau/b**2)**(1/3)
print('Tmin pid',Tmin(s,tau,beta),'crlb',np.sqrt(24*s**2*tau/212.6**3)*1e3)
r_s=0.904/0.726
for Ea,afr in [(0.5,None),(0.7,None),(0.9,None)]:
    afr=AF(pid[0],Ea)/AF(bb[0],Ea)
    for tf in [1,2]:
        print(Ea,tf,'BB Tmin',Tmin(s*r_s,tau*tf,beta/afr),'ratio',Tmin(s*r_s,tau*tf,beta/afr)/Tmin(s,tau,beta))
print('noise only',r_s**(2/3),'signal only',1.65**(2/3))
# BSC
def C(w,s,tau,b):
    snr=b*w/(s*np.sqrt(2*tau/w)); p=norm.sf(snr/2); p=np.clip(p,1e-15,0.5)
    H=-(p*np.log2(p)+(1-p)*np.log2(1-p)); return 1-H
for w in [1,6,12,24,48,72]: print(w,C(w,s,tau,beta),C(w,s*r_s,tau,beta/1.65))
# w at which C=0.9
ws=np.logspace(-1,3,20000)
for lab,args in [('pid',(s,tau,beta)),('bb',(s*r_s,tau,beta/1.65))]:
    c=C(ws,*args); print(lab,'C>=0.9 at',ws[np.argmax(c>=0.9)],'C>=0.99',ws[np.argmax(c>=0.99)])
print('drift total ps', 0.0183*212.6*19.85, 'cnt',0.0183*212.6)
