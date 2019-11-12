from odoo import fields, models

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class BaseStage(models.Model):
    _name = 'swservice.base.stage'
    _description = 'Base Stage'
    _rec_name = 'name'
    _order = 'sequence, name'

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10, help="Used to order stages. Lower is better.")
    is_done = fields.Boolean('Is Done Stage?')
    fold = fields.Boolean()
    active = fields.Boolean(default=True)

    state = fields.Selection(
        [('new', 'New'),
         ('doing', 'Doing'),
         ('done', 'Done'),
         ('cancel', 'Cancel')],
        default='new',
    )
