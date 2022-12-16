with get_start_groups as (
    select
        client_id
        , date
        , debt_flg
        , case
            when debt_flg = 1 and prev_debt_flg = 0 then 1
            else 0
        end as start_group_flg
    from (
      select
        client_id
        , date
        , debt_flg
        , lag(debt_flg,1,0) over (partition by client_id order by date) as prev_debt_flg
      from debt_table
    ) as lagged_table
),

get_groups as (
    select
        client_id
        , date
        , debt_flg
        , sum(start_group_flg) over (partition by client_id order by date) as group_number
    from get_start_groups
)

select 
    client_id
    , date
    , debt_flg
    , case
        when debt_flg = 0 then 0
        else sum(debt_flg) over (partition by client_id, group_number order by date)
    end as debt_streak
from get_groups
