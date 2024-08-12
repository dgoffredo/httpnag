#!/bin/sh

sqlite3 httpnag.sqlite <<'END_SQL'
.mode tabs
.headers off
.output errors.txt

select
  cast(StartingWhenEpochSeconds as integer),
  MessageId
from Errors
order by StartingWhenEpochSeconds;
END_SQL

>errors.plt cat <<'END_GNUPLOT'
set timefmt '%s'
set xdata time
set yrange [0:5]
plot 'errors.txt' using 1:2
END_GNUPLOT

gnuplot --persist errors.plt -

