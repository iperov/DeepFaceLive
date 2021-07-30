from pathlib import Path
from xlib.file import SplittedFile

repo_root = Path(__file__).parent.parent
large_files_list = [ (repo_root / 'modelhub' / 'onnx' / 'S3FD' / 'S3FD.onnx', 48*1024*1024), 
                     (repo_root / 'modelhub' / 'torch' / 'S3FD' / 'S3FD.pth', 48*1024*1024), 
                     (repo_root / 'modelhub' / 'cv' / 'FaceMarkerLBF' / 'lbfmodel.yaml', 34*1024*1024), 
                    ]
                 
def merge_large_files(delete_parts=False):
    for filepath, _ in large_files_list:
        print(f'Merging {filepath}...')
        SplittedFile.merge(filepath, delete_parts=delete_parts)
    print('Done')
    
def split_large_files(delete_original=False):
    for filepath, part_size in large_files_list:
        print(f'Splitting {filepath}...')
        SplittedFile.split(filepath, part_size=part_size, delete_original=delete_original)
    print('Done')