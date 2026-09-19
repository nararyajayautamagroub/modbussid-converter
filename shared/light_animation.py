from dataclasses import dataclass, asdict
from typing import Literal
LightType=Literal['strobo','rotator','ledbar']
@dataclass(frozen=True)
class LightFrame:
    time:float; intensity:float; enabled:bool; phase:float=0.0
@dataclass(frozen=True)
class LightAnimation:
    name:str; light_type:LightType; fps:int; loop:bool; frames:list[LightFrame]
def build_animation(light_type:LightType,fps:int=30)->LightAnimation:
    if light_type not in {'strobo','rotator','ledbar'}: raise ValueError('Jenis lampu tidak dikenal.')
    if light_type=='strobo': frames=[LightFrame(0,1,True),LightFrame(.06,0,False),LightFrame(.12,1,True),LightFrame(.18,0,False)]
    elif light_type=='rotator': frames=[LightFrame(0,1,True,0),LightFrame(.25,1,True,90),LightFrame(.5,1,True,180),LightFrame(.75,1,True,270)]
    else: frames=[LightFrame(0,1,True),LightFrame(.2,.35,True),LightFrame(.4,1,True),LightFrame(.6,.35,True),LightFrame(.8,1,True)]
    return LightAnimation(f'{light_type}_animation',light_type,fps,True,frames)
def to_dict(animation:LightAnimation)->dict:
    data=asdict(animation); data['format']='game-mod-light-animation-v1'; return data
