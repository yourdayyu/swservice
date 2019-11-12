from odoo import fields, models, api, exceptions
from . import swservice_base_stage
# from datetime import date, datetime, timedelta
# 服务到期 date.today() + timedelta(days=365) Odoo 还在odoo.tools.date_utils模块中提供了一些额外的便利函数
# from odoo.tools import date_utils
# date_utils.add(date.today(), months=12)


class Ticket(models.Model):
    _name = 'swservice.ticket'
    _description = 'SWService Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char('主题', required=True, index=True)
    active = fields.Boolean('Active?', default=True)
    request_time = fields.Datetime(
        '申请时间', default=lambda self: fields.Datetime.now(),)
    partner_id = fields.Many2one(
        'res.partner', string='客户', required=True, index=True, domain=[('is_company', '=', True), ('customer_rank', '>=', 1)])
    partner_contact_id = fields.Many2one(
        'res.partner', string='客户联系人', required=False,
        domain=[('is_company', '=', False)  # , ('parent_id', '=', partner_id) # 根据客户过滤联系人不在模型里增加筛选条件,加在值更新方法清空，和视图的domain中
                ])
    user_id = fields.Many2one('res.users', string='服务负责人', default=lambda self: self.env.user)
    partner_image = fields.Binary(related='partner_id.image_1920')
    user_image = fields.Binary(related='user_id.image_1920')

    # 客户值变化的时候重新选择联系人
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        partnerid = self.partner_contact_id.parent_id
        if len(partnerid) != 0:
            if partnerid != self.partner_id:
                self.partner_contact_id = ''
                return {
                    'warning':{
                        'title': '客户变化',
                        'message': '请选择垓客户的联系人'
                    }
                }

    prob_descr = fields.Html('问题描述')
    prob_solution = fields.Html('解决方案')
    issolved = fields.Selection(
        [('yes', '已解决'),
         ('no', '未解决')],
        '是否解决？')
    follow_suggest = fields.Text('后续建议')
    feedback = fields.Text('客户反馈')

    @api.model
    def _default_stage_id(self):
        stage = self.env['swservice.base.stage']
        return stage.search([], limit=1)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = stages._search([], order=order)
        return stages.browse(stage_ids)

    stage_id = fields.Many2one('swservice.base.stage', string='Stage', ondelete='restrict', tracking=True, index=True, copy=False,
        group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())

    state = fields.Selection(related='stage_id.state')


    # 结束服务按钮
    def button_done(self):
        Stage = self.env['swservice.base.stage']
        done_stage = Stage.search(
            [('state', '=', 'done')], limit=1)
        for ticket in self:
            ticket.stage_id = done_stage
        return True

    # 开始处理服务按钮
    def button_doing(self):
        Stage = self.env['swservice.base.stage']
        doing_stage = Stage.search(
            [('state', '=', 'doing')], limit=1)
        for ticket in self:
            ticket.stage_id = doing_stage
        return True

    # 该客户其他服务单
    num_other_tickets = fields.Integer(
        compute='_compute_num_other_tickets')

    def _compute_num_other_tickets(self):
        for rec in self:
            domain = [
                ('partner_id', '=', rec.partner_id.id),
                ('state', 'in', ['new', 'doing', 'done']),
                ('id', '!=', rec.id)]
            rec.num_other_tickets = self.search_count(domain)

    # 看板
    priority = fields.Selection(swservice_base_stage.AVAILABLE_PRIORITIES, string='优先级', index=True,
                                default=swservice_base_stage.AVAILABLE_PRIORITIES[0][0])
    kanban_state = fields.Selection(
        [('normal', '正常处理'),
         ('blocked', '困难阻滞'),
         ('done', '准备完成')],
        'Kanban State',
        default='normal')
    color = fields.Integer('Color Index', default=0)