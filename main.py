import os
import platform

# onnxruntime==1.8.0 requires CUDA_PATH_V11_2, but 1.8.1 don't
# keep the code if they return that behaviour
# if __name__ == '__main__':
#     if platform.system() == 'Windows':
#         if 'CUDA_PATH' not in os.environ:
#             raise Exception('CUDA_PATH should be set to environ')
#         # set environ for onnxruntime
#         # os.environ['CUDA_PATH_V11_2'] = os.environ['CUDA_PATH']

import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser( "run", help="Run the application.")

    run_subparsers = run_parser.add_subparsers()

    def run_DeepFaceLive(args):
        userdata_path = Path(args.userdata_dir)
        print('Running DeepFaceLive.')
        from apps.DeepFaceLive.DeepFaceLiveApp import DeepFaceLiveApp
        DeepFaceLiveApp(userdata_path=userdata_path).run()

    p = run_subparsers.add_parser('DeepFaceLive')
    p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
    p.set_defaults(func=run_DeepFaceLive)

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
