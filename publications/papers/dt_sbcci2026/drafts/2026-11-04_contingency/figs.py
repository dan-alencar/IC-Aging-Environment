import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm
plt.rcParams.update({"font.family":"serif","font.serif":["TeX Gyre Termes","Nimbus Roman","Liberation Serif","DejaVu Serif"],
 "font.size":8,"axes.titlesize":8,"axes.labelsize":8,"legend.fontsize":7,"xtick.labelsize":7,"ytick.labelsize":7,
 "axes.spines.top":False,"axes.spines.right":False,"axes.linewidth":0.6,"grid.color":"#e3e3e0","grid.linewidth":0.5,
 "lines.linewidth":1.6,"savefig.dpi":600,"pdf.fonttype":42,"mathtext.fontset":"stix"})
PID="#1f5fbf"; BB="#d9661f"; INK="#333333"; MUT="#777777"
k=8.617333e-5
AF=lambda T,Ea=0.7,Tu=55: np.exp(Ea/k*(1/(Tu+273.15)-1/(T+273.15)))
def AFg(m,s,Ea=0.7,Tu=55):
    x=np.linspace(-6,6,2001); return np.trapezoid(AF(m+s*x,Ea,Tu)*norm.pdf(x),x)
bb=(107.73,2.64); pid=(117.04,1.25)

# ---------- Fig 2: delivered stress ----------
fig,ax=plt.subplots(1,2,figsize=(7.0,2.35),constrained_layout=True)
Ea=np.linspace(0.4,1.0,121)
mean_only=np.array([AF(pid[0],e)/AF(bb[0],e) for e in Ea])
full=np.array([AFg(*pid,e)/AFg(*bb,e) for e in Ea])
ripple=np.array([AFg(*bb,e)/AF(bb[0],e) for e in Ea])
a=ax[0]
a.plot(Ea,full,color=PID,label="Measured trajectories (mean + ripple)")
a.plot(Ea,mean_only,color=INK,ls="--",lw=1.1,label="Mean shortfall only")
a.plot(Ea,ripple,color=BB,ls=":",lw=1.6,label="Ripple only (bang-bang)")
a.axhline(1,color=MUT,lw=0.6)
a.axvspan(0.5,0.9,color="#f1f1ee",zorder=0)
a.scatter([0.7],[AFg(*pid)/AFg(*bb)],s=22,color=PID,zorder=5,edgecolor="white",linewidth=1)
a.annotate("1.65×",(0.7,1.65),xytext=(0.74,1.42),fontsize=7.5,color=INK,arrowprops=dict(arrowstyle="-",lw=0.5,color=MUT))
a.set_xlabel("Activation energy $E_a$ (eV)"); a.set_ylabel("AF ratio, PID / bang-bang")
a.set_ylim(0.9,2.2); a.grid(True,axis="y"); a.legend(frameon=False,loc="upper left")
a.set_title("(a) Where the AF bias comes from",loc="left")
b=ax[1]
eta=np.linspace(0.01,0.4,200); Ts=115+273.15
for E,ls in [(0.5,":"),(0.7,"-"),(0.9,"--")]:
    b.plot(eta*100,k*Ts**2/E*np.log(1+eta),color=PID if E==0.7 else INK,ls=ls,lw=1.6 if E==0.7 else 1.0,label=f"$E_a$ = {E} eV")
b.axhline(7.27,color=BB,lw=1.4); b.text(1.5,7.55,"Bang-bang die shortfall, 7.27 °C",color=INK,fontsize=7)
b.axhline(2.04,color=PID,lw=1.0,ls="-."); b.text(19,1.35,"PID die overshoot, 2.04 °C",color=INK,fontsize=7)
b.set_xlabel("Tolerated AF deviation $\\eta$ (%)"); b.set_ylabel("Allowed mean die error $\\delta$ (°C)")
b.set_ylim(0,9); b.set_xlim(0,40); b.grid(True,axis="y"); b.legend(frameon=False,loc="upper left",bbox_to_anchor=(0.0,0.78))
b.set_title("(b) Tracking budget, Eq. (2), at 115 °C",loc="left")
fig.savefig("fig_stress.pdf"); fig.savefig("fig_stress.png",dpi=200)

# ---------- Fig 3: detectability ----------
s0,tau0,b0=0.84,314/3600,0.0183; rs=0.904/0.726
Tmin=lambda s,t,b:(216*s**2*t/b**2)**(1/3)
fig,ax=plt.subplots(1,2,figsize=(7.0,2.35),constrained_layout=True)
a=ax[0]
tf=np.linspace(0.5,3,100)
a.plot(tf,Tmin(s0,tau0*tf,b0),color=PID,label="PID (measured, 212.6 h run)")
afr=AFg(*pid)/AFg(*bb)
a.plot(tf,Tmin(s0*rs,tau0*tf,b0/afr),color=BB,ls="--",label="Bang-bang (projected)")
lo=[Tmin(s0*rs,tau0*t,b0/(AF(pid[0],0.5)/AF(bb[0],0.5))) for t in tf]
hi=[Tmin(s0*rs,tau0*t,b0/(AF(pid[0],0.9)/AF(bb[0],0.9))) for t in tf]
a.fill_between(tf,lo,hi,color=BB,alpha=0.15,lw=0)
a.axhline(22.08,color=MUT,lw=0.8,ls=":"); a.text(1.55,16.5,"SBCCI run length (22.1 h post-soak)",fontsize=7,color=INK)
a.scatter([1],[Tmin(s0,tau0,b0)],s=22,color=PID,zorder=5,edgecolor="white",linewidth=1)
a.text(0.83,37.5,"34 h",fontsize=7.5,color=INK)
a.scatter([1],[Tmin(s0*rs,tau0,b0/afr)],s=22,color=BB,zorder=5,edgecolor="white",linewidth=1)
a.text(0.83,59,"55 h",fontsize=7.5,color=INK)
a.set_xlabel("Decorrelation time, relative to measured $\\tau_{int}$ = 5.2 min")
a.set_ylabel("$T_{min}$ for 3σ aging detection (h)")
a.set_ylim(0,100); a.grid(True,axis="y"); a.legend(frameon=False,loc="upper left")
a.set_title("(a) Minimum burn-in time to see aging",loc="left")
b=ax[1]
w=np.logspace(0,2.3,400)
def C(w,s,t,bt):
    p=np.clip(norm.sf(bt*w/(s*np.sqrt(2*t/w))/2),1e-15,0.5); return 1+(p*np.log2(p)+(1-p)*np.log2(1-p))
b.semilogx(w,C(w,s0,tau0,b0),color=PID,label="PID (measured)")
b.semilogx(w,C(w,s0*rs,tau0,b0/afr),color=BB,ls="--",label="Bang-bang (projected)")
b.axvline(24,color=MUT,lw=0.8,ls=":"); b.text(25,0.06,"24 h window",fontsize=7,color=INK)
b.set_xlabel("Alarm decision window (h)"); b.set_ylabel("$C_{BSC}$ (bits/decision)")
b.set_ylim(0,1.05); b.grid(True,axis="y"); b.legend(frameon=False,loc="upper left")
b.set_title("(b) Aging-alarm reliability",loc="left")
fig.savefig("fig_detect.pdf"); fig.savefig("fig_detect.png",dpi=200)
print("C24 pid",C(np.array([24.]),s0,tau0,b0),"bb",C(np.array([24.]),s0*rs,tau0,b0/afr))
