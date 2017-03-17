# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    fg_procurement_group_id = fields.Many2one(
        string="Finished Good Procurement Group",
        comodel_name="procurement.group",
        readonly=True,
        copy=False,
        states={
            "draft": [("readonly", False)],
        },
    )
    use_rm_procurement_group = fields.Boolean(
        string="Use Raw Material Procurement Group",
        readonly=True,
        copy=False,
        states={
            "draft": [("readonly", False)],
        },
    )

    @api.multi
    def action_confirm(self):
        super(MrpProduction, self).action_confirm()
        for mo in self:
            if mo.use_rm_procurement_group:
                mo.write(self._prepare_fg_procurement_group())
            if not mo.move_created_ids:
                continue
            if not mo.fg_procurement_group_id:
                continue
            for fg in mo.move_created_ids:
                fg.write(self._prepare_fg_move_proc_group())

    @api.multi
    def action_ready(self):
        super(MrpProduction, self).action_ready()
        for mo in self:
            if not mo.move_created_ids:
                continue
            if not mo.fg_procurement_group_id:
                continue
            for fg in mo.move_created_ids:
                fg.write(self._prepare_fg_move_proc_group())

    @api.multi
    def _prepare_fg_move_proc_group(self, group_id=False):
        self.ensure_one()
        if not group_id:
            group_id = self.fg_procurement_group_id and \
                self.fg_procurement_group_id.id or False
        result = {
            "group_id": group_id,
        }
        return result

    @api.model
    def _fg_move_picking_reassign(
            move, group_id,
            location_id, location_dest_id):
        move._picking_assign(
            move,
            group_id,
            location_id,
            location_dest_id,
        )

    @api.multi
    def _prepare_fg_procurement_group(self):
        self.ensure_one()
        group_id = self.raw_material_procurement_group_id and \
            self.raw_material_procurement_group_id.id or False
        result = {
            "fg_procurement_group_id": group_id,
        }
        return result
