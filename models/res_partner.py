from odoo import fields, models
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from . import swservice_base_stage


class ResPartner(models.Model):
    _inherit = 'res.partner'
    swservice_user_id = fields.Many2one('res.users', string='服务负责人')
    swservice_priority = fields.Selection(swservice_base_stage.AVAILABLE_PRIORITIES, string='客户星级', index=True,
                                default=swservice_base_stage.AVAILABLE_PRIORITIES[0][0])
    swservice_expiry_date = fields.Date(string='服务到期日')     # 最近服务到期日
    swservice_start_date = fields.Date(string='服务开始日')      # 最近服务开始日期
    swservice_period = fields.Integer(string='服务期限（天或次）')  # 服务期限
    swservice_base_category_partnersource = fields.Many2one(
        'swservice.base.category.entry', string='客户来源',
        domain="[('category_key', '=', 'partner_source')]")
    swservice_base_category_partnerstate = fields.Many2one(
        'swservice.base.category.entry', string='客户状态',
        domain="[('category_key', '=', 'partner_state')]")
    swservice_product_ids = fields.Many2many('product.product', string='已购产品类')
    swservice_product_desc = fields.Text(string='购买模块描述')

    # 更多联系方式
    swservice_contact_qq = fields.Char('QQ')
    swservice_contact_wechat = fields.Char('微信')
    swservice_contact_bangwo8 = fields.Char('帮我吧ID')


    # 下面代码从sale模块来，统计服务单
    swservice_ticket_count = fields.Integer(compute='_compute_swservice_ticket_count', string='服务单量')
    swservice_ticket_ids = fields.One2many('swservice.ticket', 'partner_id', 'Service Ticket')
    swservice_warn = fields.Selection(WARNING_MESSAGE, 'Service Warnings', default='no-message', help=WARNING_HELP)
    swservice_warn_msg = fields.Text('Message for Service Ticket')

    def _compute_swservice_ticket_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])
        swservice_ticket_groups = self.env['swservice.ticket'].read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        partners = self.browse()
        for group in swservice_ticket_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.swservice_ticket_count += group['partner_id_count']
                    partners |= partner
                partner = partner.parent_id
        (self - partners).swservice_ticket_count = 0
