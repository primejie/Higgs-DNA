import numpy as np
def get2BodyMass(data,ddata,pt1,phi1,eta1,m1,pt2,phi2,eta2,m2,H=125,Y=700):
    
        px1 = ddata[pt1]*np.cos(ddata[phi1])
        py1 = ddata[pt1]*np.sin(ddata[phi1])
        pz1 = ddata[pt1]*np.sinh(ddata[eta1])
        px2 = data[pt2]*np.cos(data[phi2])
        py2 = data[pt2]*np.sin(data[phi2])
        pz2 = data[pt2]*np.sinh(data[eta2])
        E1=np.sqrt(px1*px1+py1*py1+pz1*pz1+ddata[m1]*ddata[m1])
        E2=np.sqrt(px2*px2+py2*py2+pz2*pz2+data[m2]*data[m2])
        mass=np.sqrt((E1+E2)*(E1+E2)-(px1+px2)*(px1+px2)-(py1+py2)*(py1+py2)-(pz1+pz2)*(pz1+pz2))
        #mStar = mass-ddata[m1]-data[m2]+H+Y
        #px = px1+px2
        #py = py1+py2
        #pz = pz1+pz2
        # if type:
        #     return mStar
        #else:

        return mass