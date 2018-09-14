#!/bin/bash
set -e


source "${HOME}/utils.sh"


function main() {
    . $HOME/venv/bin/activate

    sleep 30 # Give the admin container time to initialize the fixtures on first run

    rm $HOME/sopel-garnet.pid # sometimes pidfile hangs around; just do this to make sure it'll start
    color_echo YELLOW "Starting sopel bot!"
    sopel --config "${HOME}/sopelbot/garnet.cfg"
}

main "$@"
exit $?
