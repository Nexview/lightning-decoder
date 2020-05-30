#!/bin/sh
year=$1
month=$2
day=$3
hour=$4
minute=$5

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

mkdir -p "$DIR"/data

for i in {0..15} ; do
  first_date=$(date -j -f '%Y-%m-%d %H:%M:%S' "$year-$month-$day $hour:$minute:00" "+%s")
  seconds="$((first_date-i*60))"
  new_year=$(date -j -f '%s' "$seconds" "+%Y")
  new_month=$(date -j -f '%s' "$seconds" "+%m")
  new_day=$(date -j -f '%s' "$seconds" "+%d")
  new_hour=$(date -j -f '%s' "$seconds" "+%H")
  new_minute=$(date -j -f '%s' "$seconds" "+%M")

  julian=$(date -j -f '%Y-%m-%d' "$new_year-$new_month-$new_day" "+%j")

  aws s3 ls s3://noaa-goes16/GLM-L2-LCFA/"$new_year"/"$julian"/"$new_hour"/ | grep OR_GLM-L2-LCFA_G16_s"$new_year""$julian""$new_hour""$new_minute" | awk '{print $4}' | while read -r line ; do
    aws s3 cp s3://noaa-goes16/GLM-L2-LCFA/"$new_year"/"$julian"/"$new_hour"/"$line" "$DIR"/data
  done
done

python process.py "$6"
rm -rf "$DIR"/data