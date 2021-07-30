from pathlib import Path
from xlib.file import SplittedFile

def split_large_files():
    repo_root = Path(__file__).parent.parent
    
    files_list = [ (repo_root / 'modelhub' / 'onnx' / 'S3FD' / 'S3FD.onnx', 48*1024*1024), 
                   (repo_root / 'modelhub' / 'torch' / 'S3FD' / 'S3FD.pth', 48*1024*1024), 
                   (repo_root / 'modelhub' / 'cv' / 'FaceMarkerLBF' / 'lbfmodel.yaml', 34*1024*1024), 
                 ]
                 
    for filepath, part_size in files_list:
        print(f'Splitting {filepath}...')
        SplittedFile.split(filepath, part_size=part_size, delete_original=False)
    
    print('Done')