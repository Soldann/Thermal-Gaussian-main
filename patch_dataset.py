import re, os
with open('scene/dataset_readers.py', 'r') as f:
    text = f.read()

# Make thermal optional so original readColmapCameras etc still works
text = re.sub(
    r'class CameraInfo\(NamedTuple\):.*?(?=class SceneInfo)',
    '''class CameraInfo(NamedTuple):
    uid: int
    R: np.array
    T: np.array
    FovY: np.array
    FovX: np.array
    image: np.array
    image_path: str
    image_name: str
    width: int
    height: int
    thermal: np.array = None
    thermal_path: str = None
    R_thermal: np.array = None
    T_thermal: np.array = None

''', text, flags=re.DOTALL
)

# Append new loader
new_loader = '''
def readTemperCamerasFromTransforms(path, transformsfile, white_background, extension=".png"):
    cam_infos = []

    with open(os.path.join(path, transformsfile)) as json_file:
        contents = json.load(json_file)
        fovx = contents["camera_angle_x"]

        frames = contents["frames"]
        for idx, frame in enumerate(frames):
            cam_name = os.path.join(path, frame["file_path"] + extension)
            c2w = np.array(frame["transform_matrix"])
            c2w[:3, 1:3] *= -1
            w2c = np.linalg.inv(c2w)
            R = np.transpose(w2c[:3,:3])
            T = w2c[:3, 3]

            image_path = os.path.join(path, cam_name)
            image_name = Path(cam_name).stem
            image = Image.open(image_path)
            im_data = np.array(image.convert("RGBA"))
            bg = np.array([1,1,1]) if white_background else np.array([0, 0, 0])
            norm_data = im_data / 255.0
            arr = norm_data[:,:,:3] * norm_data[:, :, 3:4] + bg * (1 - norm_data[:, :, 3:4])
            image = Image.fromarray(np.array(arr*255.0, dtype=np.byte), "RGB")

            R_thermal, T_thermal, thermal, thermal_path = None, None, None, None
            if "thermal_transform_matrix" in frame and "thermal_file_path" in frame:
                c2w_thermal = np.array(frame["thermal_transform_matrix"])
                c2w_thermal[:3, 1:3] *= -1
                w2c_thermal = np.linalg.inv(c2w_thermal)
                R_thermal = np.transpose(w2c_thermal[:3,:3])
                T_thermal = w2c_thermal[:3, 3]
                
                thermal_n = os.path.join(path, frame["thermal_file_path"])
                thermal_path = thermal_n
                # Check for .jpg or other without extension, or use exact
                if not os.path.exists(thermal_n) and os.path.exists(thermal_n + extension):
                    thermal_path = thermal_n + extension
                try:
                    t_img = Image.open(thermal_path)
                    t_data = np.array(t_img.convert("RGBA"))
                    t_norm_data = t_data / 255.0
                    t_arr = t_norm_data[:,:,:3] * t_norm_data[:, :, 3:4] + bg * (1 - t_norm_data[:, :, 3:4])
                    thermal = Image.fromarray(np.array(t_arr*255.0, dtype=np.byte), "RGB")
                except Exception as e:
                    print(f"Failed to load thermal image {thermal_path}: {e}")

            fovy = focal2fov(fov2focal(fovx, image.size[0]), image.size[1])

            cam_infos.append(CameraInfo(uid=idx, R=R, T=T, FovY=fovy, FovX=fovx, image=image,
                            image_path=image_path, image_name=image_name, width=image.size[0], height=image.size[1],
                            thermal=thermal, thermal_path=thermal_path, R_thermal=R_thermal, T_thermal=T_thermal))
            
    return cam_infos

def readTemperNerfSyntheticInfo(path, white_background, extension=".png"):
    print("Reading Temper Training Transforms")
    train_cam_infos = readTemperCamerasFromTransforms(path, "transforms_train.json", white_background, extension)
    print("Reading Temper Test Transforms")
    test_cam_infos = readTemperCamerasFromTransforms(path, "transforms_test.json", white_background, extension)
    
    nerf_normalization = getNerfppNorm(train_cam_infos)

    ply_path = os.path.join(path, "points3d.ply")
    if not os.path.exists(ply_path):
        num_pts = 100_000
        xyz = np.random.random((num_pts, 3)) * 2.6 - 1.3
        shs = np.random.random((num_pts, 3)) / 255.0
        pcd = BasicPointCloud(points=xyz, colors=SH2RGB(shs), normals=np.zeros((num_pts, 3)))
        storePly(ply_path, xyz, SH2RGB(shs) * 255)
    try:
        pcd = fetchPly(ply_path)
    except:
        pcd = None

    scene_info = SceneInfo(point_cloud=pcd,
                           train_cameras=train_cam_infos,
                           test_cameras=test_cam_infos,
                           nerf_normalization=nerf_normalization,
                           ply_path=ply_path)
    return scene_info
'''

text = text.replace('sceneLoadTypeCallbacks = {\n    "Colmap": readColmapSceneInfo,\n    "Blender" : readNerfSyntheticInfo\n}',
'''sceneLoadTypeCallbacks = {
    "Colmap": readColmapSceneInfo,
    "Temper": readTemperSceneInfo if 'readTemperSceneInfo' in globals() else readColmapSceneInfo,
    "Blender": readNerfSyntheticInfo,
    "TemperBlender": readTemperNerfSyntheticInfo
}''')
text = text + "\n" + new_loader

with open('scene/dataset_readers.py', 'w') as f:
    f.write(text)
