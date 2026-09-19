from shared.light_animation import build_animation
def test_light_types():
    for kind in ('strobo','rotator','ledbar'):
        a=build_animation(kind);assert a.light_type==kind and a.loop and a.frames
