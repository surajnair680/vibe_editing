import sys, cv2, numpy as np
sys.path.insert(0, '.')
from fig import *
tiles=[]
for yaw in (45, 55):
    row=[]
    for name,kw in (("current",dict(swing=-4,abd=-4,shrug=2.5)),("correct",dict(swing=6,abd=9))):
        for flex in (10,140):
            surf,cv=new_surface(400,820,(246,243,236))
            Figure(Cam(yaw,4.3,200,800)).draw(cv,Pose(flex=flex,**kw))
            im=to_rgb(surf); cv2.putText(im,f"{yaw} {name} {flex}",(10,30),0,0.8,(0,0,0),2); row.append(im)
    tiles.append(np.hstack(row))
cv2.imwrite(sys.argv[1], cv2.cvtColor(np.vstack(tiles),cv2.COLOR_RGB2BGR))
