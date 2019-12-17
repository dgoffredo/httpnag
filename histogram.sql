.mode columns
.width auto 100
.headers on

with Largest as (
  select max(Frequency) from (
    select count(*) as Frequency
    from Responses
    group by round(DurationSeconds * 200) * 1000 / 200))
select round(DurationSeconds * 200) * 1000 / 200 as Milliseconds,
       replace(quote(zeroblob(count(*) * 50 / (select * from Largest))), '0', '*') as Bars
from Responses
group by Milliseconds;
