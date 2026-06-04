import re
with open('utils/camera_utils.py', 'r') as f:
    text = f.read()

new_cam = '''
    return Camera(colmap_id=cam_info.uid, R=cam_info.R, T=cam_info.T, 
                  FoVx=cam_info.FovX, FoVy=cam_info.FovY, 
                  image=gt_image, gt_alpha_mask=loaded_mask,
                  image_name=cam_info.image_name, uid=id, data_device=args.data_device,
                  thermal=gt_thermal, R_thermal=getattr(cam_info, 'R_thermal', None), T_thermal=getattr(cam_info, 'T_thermal', None))
'''

text = re.sub(
    r'return Camera\(colmap_id=cam_info.uid, R=cam_info.R, T=cam_info.T,.*?thermal=gt_thermal\)',
    new_cam.strip(),
    text, flags=re.DOTALL
)

with open('utils/camera_utils.py', 'w') as f:
    f.write(text)
