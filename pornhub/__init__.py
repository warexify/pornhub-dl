"""Entry point for pornhub downloader."""
import os
import sys

from pornhub.db import db_location, create_db
from pornhub.arguments import parser


def main():
    """Parse args, check if everything is ok and start pornhub."""
    args = parser.parse_args()

    if not os.path.exists(db_location):
        create_db()

    # Check if pueue is available:
    # command_factory('status')({}, root_dir=os.path.expanduser('~'))
    try:
        args.func(vars(args))
    except KeyboardInterrupt:
        print('Keyboard interrupt. Shutting down')
        sys.exit(0)
