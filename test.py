from scene.dataset_readers import *

colmap_path = "/cluster/scratch/languo/RGBT-Scenes/Building/colmap"

cam_infos = readColmapSceneInfo(colmap_path, "images")

nerfstudio_path = "/cluster/scratch/languo/RGBT-Scenes/Building/"

cam_infos_nerfstudio = readNerfstudioThermalInfo(nerfstudio_path)
# print("COLMAP R", cam_infos.train_cameras[1].R)
# print("Nerfstudio R", cam_infos_nerfstudio.train_cameras[1].R)
# print("COLMAP T", cam_infos.train_cameras[1].T)
# print("Nerfstudio T", cam_infos_nerfstudio.train_cameras[1].T)

print("colmap", cam_infos.train_cameras[0])
print("nerfstudio", cam_infos_nerfstudio.train_cameras[0])

print("colmap length", len(cam_infos.train_cameras))
print("nerfstudio length", len(cam_infos_nerfstudio.train_cameras))
print("test colmap length", len(cam_infos.test_cameras))
print("test nerfstudio length", len(cam_infos_nerfstudio.test_cameras))

for colmap_cam, nerfstudio_cam in zip(cam_infos.train_cameras, cam_infos_nerfstudio.train_cameras):
    for key, colmap_cam_item, nerfstudio_cam_item in zip(colmap_cam._fields, colmap_cam, nerfstudio_cam):
        if isinstance(colmap_cam_item, np.ndarray) and isinstance(nerfstudio_cam_item, np.ndarray):
            if not np.allclose(colmap_cam_item, nerfstudio_cam_item, atol=1e-5):
                print(f"Difference found in key '{key}': COLMAP Value: {colmap_cam_item}, Nerfstudio Value: {nerfstudio_cam_item}")
        elif key != "image_path" and key != "thermal_path":
            if colmap_cam_item != nerfstudio_cam_item:
                print(f"Difference found in key '{key}': COLMAP Value: {colmap_cam_item}, Nerfstudio Value: {nerfstudio_cam_item}")
