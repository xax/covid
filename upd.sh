#!/bin/bash
#
cVersion="1.0.0"
cCopyright="Copyright (C) XA, III 2020. All rights reserved."
cName="${0##*/}"
declare -r cName cVersion cCopyright

upd_sub_repo () {
  local repo="$1"
  if [[ -n $repo && -d "$repo" ]]; then
    printf "* Updating sub repository \"$repo\"...\n"
    pushd "$repo" && git pull;
    popd
    printf "+ Done.\n\n"
  fi
}


upd_sub_repo "COVID-19"
upd_sub_repo "covid-api"
