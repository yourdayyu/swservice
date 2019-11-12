from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class BaseCategory(models.Model):
    _name = 'swservice.base.category'
    _description = 'Base Category'
    _order = 'name'
    _parent_store = True

    name = fields.Char(string='分类名称', translate=True, required=True)
    key = fields.Char(string='key', required=True)
    parent_id = fields.Many2one('swservice.base.category', string='上级分类', index=True, ondelete='restrict')
    child_ids = fields.One2many('swservice.base.category', 'parent_id', string='下级分类')
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")
    parent_path = fields.Char(index=True)
    state = fields.Selection(
        [('new', 'New'),
         ('doing', 'Doing'),
         ('done', 'Done'),
         ('cancel', 'Cancel')],
        default='new',)
    sequence = fields.Integer('显示顺序', default=10, help="Used to order. Lower is better.")
    description = fields.Text(string='描述')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive tags.'))

    def name_get(self):
        """ Return the categories' display name, including their direct parent by default.

                    If ``context['partner_category_display']`` is ``'short'``, the short
                    version of the category name (without the direct parent) is used.
                    The default is the long version.
        """
        if self._context.get('base_category_display') == 'short':
            return super(BaseCategory, self).name_get()

        res = []
        for cat in self:
            names = []
            current = cat
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((cat.id, ' / '.join(reversed(names))))
        return res
''' 加上这段，上级下拉就空白
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        partner_source_ids = = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(partner_source_ids).with_user(name_get_uid))
'''