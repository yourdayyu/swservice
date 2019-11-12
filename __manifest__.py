{
    'name': '服务',
    'description': '服务管理平台',
    'author': 'yyd',
    'depends': ['base', 'mail', 'crm', 'sale_management'],
    'application': True,

    'data': [
        'security/swservice_security.xml',
        'security/ir.model.access.csv',
        'views/swservice_menu.xml',
        'views/partner_view.xml',
        'views/ticket_view.xml',
        'views/ticket_kanban_view.xml',
        'views/base_category_entry_view.xml',
        'data/swservice_base_stage.xml',

    ],
}