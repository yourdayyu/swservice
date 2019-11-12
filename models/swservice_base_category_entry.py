from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class BaseCategoryEntry(models.Model):
    _name = 'swservice.base.category.entry'
    _description = 'Base Category Entry'
    _order = 'category_id,sequence,name'
    _parent_store = True

    category_id = fields.Many2one('swservice.base.category', string='应用领域', required=True)
    category_key = fields.Char('应用领域KEY', related='category_id.key', readonly=True)
    name = fields.Char(string='具体分类名称', translate=True, required=True, index=True)
    parent_id = fields.Many2one('swservice.base.category.entry', string='上级具体分类', index=True, ondelete='restrict'
                                #, domain=[('category_id', '=', category_id)] 不能加这里要用方法
                                )
    child_ids = fields.One2many('swservice.base.category.entry', 'parent_id', string='下级具体分类')
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
            return super(BaseCategoryEntry, self).name_get()

        res = []
        for cat in self:
            names = []
            current = cat
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((cat.id, ' / '.join(reversed(names))))
        return res

    # 根据选择的领域，过滤上级分类明细
    @api.onchange('category_id')
    def onchange_category_id(self):
        self.parent_id = ''  # 清空原来选择好的上级分类
        domain = [('category_id', '=', self.category_id.id)]  #设置域给上级明细分类使用，只能选择该领域分类下的上级分类
        return{
            'domain': {'parent_id': domain}
        }
