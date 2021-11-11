import argparse
import os
import platform
from pathlib import Path

from xlib import appargs as lib_appargs
from xlib import os as lib_os

# onnxruntime==1.8.0 requires CUDA_PATH_V11_2, but 1.8.1 don't
# keep the code if they return that behaviour
# if __name__ == '__main__':
#     if platform.system() == 'Windows':
#         if 'CUDA_PATH' not in os.environ:
#             raise Exception('CUDA_PATH should be set to environ')
#         # set environ for onnxruntime
#         # os.environ['CUDA_PATH_V11_2'] = os.environ['CUDA_PATH']

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser( "run", help="Run the application.")
    run_subparsers = run_parser.add_subparsers()

    def run_DeepFaceLive(args):
        userdata_path = Path(args.userdata_dir)
        lib_appargs.set_arg_bool('NO_CUDA', args.no_cuda)

        print('Running DeepFaceLive.')
        from apps.DeepFaceLive.DeepFaceLiveApp import DeepFaceLiveApp
        DeepFaceLiveApp(userdata_path=userdata_path).run()

    p = run_subparsers.add_parser('DeepFaceLive')
    p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
    p.add_argument('--no-cuda', action="store_true", default=False, help="Disable CUDA.")
    p.set_defaults(func=run_DeepFaceLive)

    dev_parser = subparsers.add_parser("dev")
    dev_subparsers = dev_parser.add_subparsers()

    def run_split_large_files(args):
        from scripts import dev
        dev.split_large_files()

    p = dev_subparsers.add_parser('split_large_files')
    p.set_defaults(func=run_split_large_files)

    def run_merge_large_files(args):
        from scripts import dev
        dev.merge_large_files(delete_parts=args.delete_parts)

    p = dev_subparsers.add_parser('merge_large_files')
    p.add_argument('--delete-parts', action="store_true", default=False)
    p.set_defaults(func=run_merge_large_files)

    def run_extract_FaceSynthetics(args):
        from scripts import dev

        inputdir_path = Path(args.input_dir)
        faceset_path = Path(args.faceset_path)

        dev.extract_FaceSynthetics(inputdir_path, faceset_path)

    p = dev_subparsers.add_parser('extract_FaceSynthetics')
    p.add_argument('--input-dir', default=None, action=fixPathAction, help="FaceSynthetics directory.")
    p.add_argument('--faceset-path', default=None, action=fixPathAction, help="output .dfs path")
    p.set_defaults(func=run_extract_FaceSynthetics)

    train_parser = subparsers.add_parser( "train", help="Train neural network.")
    train_parsers = train_parser.add_subparsers()

    def train_FaceAligner(args):
        lib_os.set_process_priority(lib_os.ProcessPriority.IDLE)
        from apps.trainers.FaceAligner.FaceAlignerTrainerApp import FaceAlignerTrainerApp
        FaceAlignerTrainerApp(workspace_path=Path(args.workspace_dir), faceset_path=Path(args.faceset_path))

    p = train_parsers.add_parser('FaceAligner')
    p.add_argument('--workspace-dir', default=None, action=fixPathAction, help="Workspace directory.")
    p.add_argument('--faceset-path', default=None, action=fixPathAction, help=".dfs path")
    p.set_defaults(func=train_FaceAligner)

    def bad_args(arguments):
        parser.print_help()
        exit(0)
    parser.set_defaults(func=bad_args)

    args = parser.parse_args()
    args.func(args)

class fixPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))

if __name__ == '__main__':
    main()

# import code
# code.interact(local=dict(globals(), **locals()))
