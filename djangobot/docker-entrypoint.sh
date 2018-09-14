#!/bin/bash
set -e


source "${HOME}/utils.sh"


function main() {
    local FIXTURES=(
        personality/fixtures/*
        djangobot/fixtures/*
    )

    bootstrap_mysql_container $DB_ROOT_PASSWORD $DB_MAX_TRIES

    . $HOME/venv/bin/activate
    init_mysql_data $DB_ROOT_PASSWORD $DB_NAME "${FIXTURES[@]}"

    color_echo YELLOW "Connect to IRC at 0.0.0.0 port 6667 and join channel #chat to talk to the bot!"
    python manage.py runserver 0.0.0.0:$APP_PORT
}

main "$@"
exit $?
