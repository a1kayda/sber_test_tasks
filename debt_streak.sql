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
        , lag(debt_flg,1,0) over (order by date partition by client_id) as prev_debt_flg
      from table
    )
),

get_groups as (
    select
        client_id
        , date
        , debt_flg
        , sum(start_group_flg) over (order by date partition by client_id) as group_number
    from get_start_groups
)

select 
    client_id
    , date
    , debt_flg
    , case
        when debt_flg = 0 then 0
        else sum(debt_flg) over (order by date partition by client_id, group_number)
    end as debt_streak
from get_groups