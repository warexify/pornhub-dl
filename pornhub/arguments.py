"""Commandline argument handling."""
import argparse

parser = argparse.ArgumentParser(description='Download your favorite pornhub stuff.')
parser.add_argument('url', type=str, help='Url of the video')
parser.add_argument('-n', '--name', type=str, help='name')

# Initialize supbparser
subparsers = parser.add_subparsers(
    title='Subcommands', description='Various client')

