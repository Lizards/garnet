#!/bin/bash
set -e


source "../utils.sh"


function main() {
    local FIXTURES=(
        personality/fixtures/*
        djangobot/fixtures/admin-user.json
    )

    bootstrap_mysql_container $DB_ROOT_PASSWORD $DB_MAX_TRIES
    setup_local_settings $APP_NAME

    . $HOME/venv/bin/activate

    init_mysql_data $DB_ROOT_PASSWORD $DB_NAME "${FIXTURES[@]}"

    python manage.py runserver 0.0.0.0:$APP_PORT
}

main "$@"
exit $?
