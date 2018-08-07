# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
import base64
import sys
from odoo.exceptions import UserError
import pprint
from odoo.exceptions import ValidationError

class ac_parameters(models.Model):
    _name = 'ac.parameters'
    name = fields.Char('Nombre')
    server = fields.Char('Direccion SqlServer')
    database = fields.Char('Base de datos')
    username = fields.Char('Usuario')
    password = fields.Char('Contraseña')
    path_csv = fields.Char('Direction del archivo')



