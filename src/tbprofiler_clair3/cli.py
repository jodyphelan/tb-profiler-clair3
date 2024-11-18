import argparse
import logging
import os
import subprocess as sp
import requests
import sys
from rich.logging import RichHandler
import rich_argparse

# get $CONDA_PREFIX from environment
__clair3_base_path__ = os.path.join(os.environ.get("CONDA_PREFIX"), "share/tbprofiler_clair3/")
__clair3_model_path__ = os.path.join(__clair3_base_path__, "models/")
__clair3_rerio_model_path__ = __clair3_base_path__ + "rerio/clair3_models/"

if not os.path.exists(__clair3_base_path__):
    original_dir = os.getcwd()
    logging.debug("Creating Clair3 model directory at %s" % __clair3_base_path__)
    os.makedirs(__clair3_base_path__, exist_ok=True)
    os.makedirs(__clair3_model_path__, exist_ok=True)
    os.chdir(__clair3_base_path__)
    # Download the Clair3 models
    sp.run('git clone https://github.com/nanoporetech/rerio.git', shell=True)
    os.chdir(original_dir)

def get_available_models():
    available_models = [d.replace('_model','') for d in os.listdir(__clair3_rerio_model_path__)]
    return available_models

def get_downloaded_models():
    downloaded_models = os.listdir(__clair3_model_path__)
    return downloaded_models

def get_non_downloaded_models():
    available_models = get_available_models()
    downloaded_models = get_downloaded_models()
    non_downloaded_models = list(set(available_models) - set(downloaded_models))
    return non_downloaded_models

def download(args):
    # Download the Clair3 model
    # This is where the download code would go
    os.chdir(__clair3_model_path__)
    if args.all:
        models = get_non_downloaded_models()
    elif args.model:
        non_downloaded_models = get_non_downloaded_models()
        if args.model in non_downloaded_models:
            models = [args.model]
        else:
            logging.error(f"{args.model} is already downloaded")
            sys.exit(1)

    for model in models:
        url = open(f"{__clair3_rerio_model_path__}/{model}_model").read().strip()
        logging.debug(f"Downloading {model} from {url}")
        r = requests.get(url)
        with open(f"{model}.tgz", 'wb') as f:
            f.write(r.content)
        logging.debug(f"Downloaded {model}")
        # Extract the model
        sp.run(f"tar -xzf {model}.tgz", shell=True)
        os.remove(f"{model}.tgz")
    
def list_models(args):
    not_downloaded_models = get_non_downloaded_models()
    downloaded_models = get_downloaded_models()
    for model in downloaded_models:
            sys.stdout.write(f'{model}\tdownloaded\n')
    for model in not_downloaded_models:
            sys.stdout.write(f'{model}\tnot downloaded\n')



def main():
    logging.basicConfig(
        level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
    )
    parser = argparse.ArgumentParser(description='tb-profiler Clair3 plugin', formatter_class=rich_argparse.ArgumentDefaultsRichHelpFormatter)
    # add subparsers
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "download" command
    parser_download = subparsers.add_parser('download', help='Download Clair3 model')
    # add mutually exclusive group for the model to download
    model_group = parser_download.add_mutually_exclusive_group(required=True)
    model_group.add_argument('--all', action='store_true', help='Download all available models')
    model_group.add_argument('--model', type=str, help='Download specific model')
    parser_download.add_argument('-v','--verbose', action='store_true', help='Verbose output')
    parser_download.set_defaults(func=download)

    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list', help='List available models')
    parser_list.add_argument('-v','--verbose', action='store_true', help='Verbose output')
    parser_list.set_defaults(func=list_models)

    args = parser.parse_args()

    if hasattr(args, 'verbose') and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


