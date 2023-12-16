from builder import SQLQueryBuilder


use_organic_users_only = False
country_to_check = 'GB'

qb = SQLQueryBuilder()
query = (
    qb
    .add_select(
        qb.select_field('platform'),
        qb.select_field('uniqExact(user_id)', 'n'),
    )
    .add_from('analytics.Users')
    .add_where(
        qb.where_expr("install_time >= '2023-01-01'")
        & qb.where_expr_if(use_organic_users_only, "install_network = 'organic'")
        & qb.where_expr_if(country_to_check == 'US', "country = 'US'", "country = 'GB'")
        & (
            qb.where_expr("platform = 'android'")
            | qb.where_expr("platform = 'ios'")
            | qb.where_expr("platform = 'web'")
        ).bracket()
        & qb.where_expr('last_active_time >= today() - INTERVAL 7 DAY')
        & qb.where_expr(
            'user_id IN ' +
            qb.subquery()
            .add_select('user_id')
            .add_from('analytics.Purchases')
            .add_where(qb.where_expr('purchase_time >= today() - INTERVAL 30 DAY'))
            .build()
        )
    )
    .add_group_by('platform')
    .build()
)

print(query)
