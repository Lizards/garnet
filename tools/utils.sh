#!/bin/bash

set -e


function color_echo() {
    local -A COLORS=(
        ['RED']='\e[0;31m'
        ['YELLOW']='\e[1;33m'
        ['BLUE']='\e[1;34m'
    )
    local NC='\e[0m'
    local color=$1
    local message="${*:2}"
    echo -e "${COLORS[$color]}${message}${NC}"
}


function bootstrap_mysql_container() {
    color_echo RED 'Waiting for MySQL to be available'
    local db_root_password=$1
    local db_max_tries=$2
    local tries=$db_max_tries
    while [ "${tries}" -gt 0 ] && ! mysql -h db -u root --password="${db_root_password}" -e "SELECT User FROM mysql.user" mysql; do
        color_echo YELLOW "MySQL attempts remaining: ${tries}"
        tries=$((tries-1))
        sleep 5
    done
    echo
    if [ $tries -le 0 ]; then
        echo >&2 "error: unable to contact MySQL after ${db_max_tries} tries"
        exit 1
    fi
}


function setup_local_settings() {
    local local_settings_file="${1}/local_settings.py"
    if [ ! -f "$local_settings_file" ]; then
        echo "File not found!"
        color_echo YELLOW "Symlinking ${local_settings_file}.example to ${local_settings_file}"
        ln -s local_settings.py.example "$local_settings_file"
    else
        color_echo BLUE "${local_settings_file} already exists"
    fi
}


function init_mysql_data() {
    local db_root_password=$1
    local db_name=$2
    local fixtures="${*:3}"
    if ! mysql -h db -u root --password="$db_root_password" "$db_name" -e "DESCRIBE django_migrations"; then
        color_echo BLUE "Initial run; applying migrations to database ${db_name}"
        python manage.py migrate
        color_echo BLUE "Loading fixture data from files:"
        color_echo BLUE "${fixtures}"
        python manage.py loaddata $fixtures
    fi
}
