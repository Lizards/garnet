#!/bin/bash
set -e


source "../utils.sh"


function main() {
    setup_local_settings $DJANGO_PATH

    . $HOME/venv/bin/activate

    color_echo YELLOW "Starting sopel bot!"
    sopel --config $HOME/sopelbot/garnet.cfg
}

main "$@"
exit $?
