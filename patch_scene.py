import os, re
with open('scene/__init__.py', 'r') as f:
    text = f.read()

# patch scene selection
new_code = '''
        if os.path.exists(os.path.join(args.source_path, "sparse")):
            scene_info = sceneLoadTypeCallbacks["Temper"](args.source_path, args.images) if "Temper" in sceneLoadTypeCallbacks else sceneLoadTypeCallbacks["Colmap"](args.source_path, args.images)
        elif os.path.exists(os.path.join(args.source_path, "transforms_train.json")):
            with open(os.path.join(args.source_path, "transforms_train.json")) as jf:
                content = jf.read()
                if "thermal_file_path" in content:
                    print("Found transforms_train.json with thermal_file_path, using TemperBlender!")
                    scene_info = sceneLoadTypeCallbacks["TemperBlender"](args.source_path, args.white_background)
                else:
                    print("Found transforms_train.json file, assuming Blender data set!")
                    scene_info = sceneLoadTypeCallbacks["Blender"](args.source_path, args.white_background)
'''
text = re.sub(
    r'if os\.path\.exists\(os\.path\.join\(args\.source_path, "sparse"\)\):.*?elif os\.path\.exists\(os\.path\.join\(args\.source_path, "transforms_train\.json"\)\):.*?scene_info = sceneLoadTypeCallbacks\["Blender"\]\(args\.source_path, args\.white_background\)',
    new_code.strip(),
    text, flags=re.DOTALL
)

with open('scene/__init__.py', 'w') as f:
    f.write(text)
