#!/bin/bash
#
# POST the status of a subrun to the processingstatus.py monitoring application
#
# Follows HTTP Semantics: http://tools.ietf.org/html/rfc2616
#
# If there is a Client Error, this script fails immediately.
#
# If there is a Server Error, this script retries up to MAX_NUM_RETRIES times.
#
# If this script is unable to contact the server at PS_MON_APP_ROOT_URI, then a 
# Server Error is considered to have occurred.
#
# Intended to be called by send_mon_info.pl:
#
# ./post_status.sh MONDIR RUN SUBRUN RUNTYPE STAGE OUTPUT
#
# Where output is '' or 'RESULT TIME EVENTS_READ EVENTS_WRITTEN'
#
# Example:
#
# ./post_status.sh MONDAYTESTPAGE 5107 1 SPILL CALIBRATION '-1 5 6 12345'
#
# Exit status:
# 
# 0 - Request went through successfully
# 1 - Request did not go through due to a Server Error
# 2 - Request did not go through due to a Client Error

# if PS_MON_APP_ROOT_URI has been exported by a parent process then use that, otherwise use this default
PS_MON_APP_ROOT_URI=${PS_MON_APP_ROOT_URI:-'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/'}
# PS_MON_APP_ROOT_URI=${PS_MON_APP_ROOT_URI:-'http://localhost:8000/processing/status/'}

# 5 minutes = 14
# 1 hour = 124
# 2 hours = 254
# 3 hours = 374
declare -i MAX_NUM_RETRIES=14

if [ $# -ne 6 ] ; 
then
  echo -e "Wrong number of parameters.\nTry ./post_status.sh MONDIR RUN SUBRUN RUNTYPE STAGE OUTPUT"
  exit 1
fi

function post_status()
{
  local curl_command="curl -w '\n%{http_code}' --silent -H 'Accept: text/plain' -k --data-binary '$6' -X POST '$PS_MON_APP_ROOT_URI$1?$2/$3/$4/$5'"
  echo $curl_command
  local curl_output
  declare -i curl_return_code=-1
  declare -i http_response_code=-1

  declare -i num_attempts=0
  declare -i wait_seconds=1

  local formatted_server_response
  local formatted_codes

  while [ 1 ]
  do

    num_attempts=$num_attempts+1
    
    curl_output=$( eval $curl_command )
    curl_return_code=$?
    http_response_code=$( echo "$curl_output" | tail -n 1 )

    if [ $curl_return_code -eq 0 -a \( $http_response_code -eq 201 -o $http_response_code -eq 200 \) ]
    then
      echo "Curl request attempt #$num_attempts when through."
      return 0
    else
      if [ $curl_return_code -eq 0 ]
      then
        formatted_server_response=$( echo "server response: ${curl_output%???}" | tr -d '\n' )
      else
        formatted_server_response='server response: <no response>'
      fi
      formatted_codes="http response code: $http_response_code, curl return code: $curl_return_code"
      echo "Curl request attempt #$num_attempts did not go through."
      echo "--> $formatted_codes"
      echo "--> $formatted_server_response"
    fi
    
    if [ $curl_return_code -eq 0 -a \( $http_response_code -ge 400 -a $http_response_code -le 499 \) ]
    then
      echo "--> Client Error (post_status.sh aborted):"
      echo "--> Please check the command-line parameters sent to post_status.sh"
      return 2
    fi

    if [ $num_attempts -eq $MAX_NUM_RETRIES ]
    then
      echo "--> MAX_NUM_RETRIES reached, aborting."
      return 1
    else
      sleep $wait_seconds
      if [ $wait_seconds -le 32 ]
      then
        wait_seconds=$wait_seconds*2
      fi
    fi      

  done  
}

post_status $1 $2 $3 $4 $5 "$6"
