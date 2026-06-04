import re
with open('arguments/__init__.py', 'r') as f:
    text = f.read()

new_args = '''
    def __init__(self, parser, sentinel=False):
        self.sh_degree = 3
        self._source_path = ""
        self._model_path = ""
        self._images = "images"
        self._thermal = "thermal"
        self._resolution = -1
        self._white_background = False
        self.data_device = "cuda"
        self.eval = False
        self.use_thermal_pose = False
'''

text = re.sub(
    r'def __init__\(self, parser, sentinel=False\):\n\s+self\.sh_degree = 3\n\s+self\._source_path = ""\n\s+self\._model_path = ""\n\s+self\._images = "images"\n\s+self\._thermal = "thermal"\n\s+self\._resolution = -1\n\s+self\._white_background = False\n\s+self\.data_device = "cuda"\n\s+self\.eval = False',
    new_args.strip(),
    text, flags=re.DOTALL
)

with open('arguments/__init__.py', 'w') as f:
    f.write(text)
