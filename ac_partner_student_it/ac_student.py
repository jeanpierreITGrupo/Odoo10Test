# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class res_partner(models.Model):
    _inherit = ['res.partner']

    @api.model
    def _defauld_type_document(self):
        boleta_de_venta = self.env['einvoice.catalog.01'].search([('code','=','03')],limit=1)
        if boleta_de_venta:
            return boleta_de_venta.id

    student = fields.Boolean('Es estudiante')
    apoderado = fields.Boolean('Es un apoderado')

    code_student = fields.Char(u'Código EDUSOFTNET')
    code_payment = fields.Char(u'Código de Pago')
    code_family = fields.Char(u'Código Familia')
    grado_id = fields.Char("Grado")
    seccion_id = fields.Char(u"Sección")
    etapa_id = fields.Char("Etapa")
    country_nac_id = fields.Many2one('res.country', "País de nacimiento")
    date_nac = fields.Date('Fecha de nacimiento')
    apoderado_id = fields.Many2one('res.partner', domain="[('apoderado', '=', 'True')]", string="Apoderado")
    codigo_info = fields.Char('Codigo Info')
    table_student_id = fields.Integer('Tabla Estudiante id')
    table_apoderado_id = fields.Char('Tabla Apoderado id')
    temp_apoderado_id = fields.Char('Apoderado id, del estudiante')
    email_apoderado = fields.Char(related='apoderado_id.email',string='Email apoderado')
    it_type_document = fields.Many2one('einvoice.catalog.01','Tipo documento para facturacion',default=_defauld_type_document)

    @api.one
    def unlink(self):
        if self.apoderado:
            raise ValidationError("No se puede eliminar un apoderado")
        return super(res_partner, self).unlink()
