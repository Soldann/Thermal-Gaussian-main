import re
with open('scene/cameras.py', 'r') as f:
    text = f.read()

new_init = '''
    def __init__(self, colmap_id, R, T, FoVx, FoVy, image, thermal, gt_alpha_mask,
                 image_name, uid,
                 trans=np.array([0.0, 0.0, 0.0]), scale=1.0, data_device = "cuda",
                 R_thermal=None, T_thermal=None
                 ):
'''
text = re.sub(
    r'def __init__\(self, colmap_id, R, T, FoVx, FoVy, image, thermal, gt_alpha_mask,\n\s+image_name, uid,\n\s+trans=np.array\(\[0.0, 0.0, 0.0\]\), scale=1.0, data_device = "cuda"\n\s+\):',
    new_init.strip(),
    text, flags=re.DOTALL
)

new_proj = '''
        self.world_view_transform = torch.tensor(getWorld2View2(R, T, trans, scale)).transpose(0, 1).cuda()
        self.projection_matrix = getProjectionMatrix(znear=self.znear, zfar=self.zfar, fovX=self.FoVx, fovY=self.FoVy).transpose(0,1).cuda()
        self.full_proj_transform = (self.world_view_transform.unsqueeze(0).bmm(self.projection_matrix.unsqueeze(0))).squeeze(0)
        self.camera_center = self.world_view_transform.inverse()[3, :3]

        if R_thermal is not None and T_thermal is not None:
             self.world_view_transform_thermal = torch.tensor(getWorld2View2(R_thermal, T_thermal, trans, scale)).transpose(0, 1).cuda()
             self.full_proj_transform_thermal = (self.world_view_transform_thermal.unsqueeze(0).bmm(self.projection_matrix.unsqueeze(0))).squeeze(0)
             self.camera_center_thermal = self.world_view_transform_thermal.inverse()[3, :3]
        else:
             self.world_view_transform_thermal = self.world_view_transform
             self.full_proj_transform_thermal = self.full_proj_transform
             self.camera_center_thermal = self.camera_center
'''

text = re.sub(
    r'self\.world_view_transform = torch\.tensor\(getWorld2View2\(R, T, trans, scale\)\)\.transpose\(0, 1\)\.cuda\(\)\n\s+self\.projection_matrix = getProjectionMatrix\(znear=self\.znear, zfar=self\.zfar, fovX=self\.FoVx, fovY=self\.FoVy\)\.transpose\(0,1\)\.cuda\(\)\n\s+self\.full_proj_transform = \(self\.world_view_transform\.unsqueeze\(0\)\.bmm\(self\.projection_matrix\.unsqueeze\(0\)\)\)\.squeeze\(0\)\n\s+self\.camera_center = self\.world_view_transform\.inverse\(\)\[3, :3\]',
    new_proj.strip(),
    text, flags=re.DOTALL
)

with open('scene/cameras.py', 'w') as f:
    f.write(text)
