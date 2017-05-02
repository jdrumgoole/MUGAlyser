# $1 arg to stats
# $2 the country
# $* the years
statscmd=$1
shift
country="$1"
shift
while (( "$#" )); do

    python mug_analytics_main.py --stats $statscmd --start 1-Jan-$1 --end 31-Dec-$1 --country "$country" --format CSV --root $1_"${country}"_
    shift

done

