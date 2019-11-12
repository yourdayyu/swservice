from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class PartnerSource(models.Model):
    _name = 'swservice.partner.source'
    _description = 'Partner Source'
    _order = 'name'
    _parent_store = True

    name = fields.Char(string='来源名称', translate=True, required=True)
    parent_id = fields.Many2one('swservice.partner.source', string='上级来源', index=True, ondelete='restrict')
    child_ids = fields.One2many('swservice.partner.source', 'parent_id', string='下级来源')
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")
    parent_path = fields.Char(index=True)

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
        if self._context.get('partner_source_display') == 'short':
            return super(PartnerSource, self).name_get()

        res = []
        for source in self:
            names = []
            current = source
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((source.id, ' / '.join(reversed(names))))
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