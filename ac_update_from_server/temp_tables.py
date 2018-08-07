# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
import base64
import sys
from odoo.exceptions import UserError
import pprint
from odoo.exceptions import ValidationError

class temp_student(models.Model):
    _name = 'temp.student'
    table_id = fields.Integer('Id de la tabla')
    codigo = fields.Integer('Codigo del estudiante')
    nro_dni = fields.Char('Numero de DNI')
    nombres = fields.Char('Nombres')
    apellido_pat = fields.Char('Apellido Paterno')
    apellido_mat = fields.Char('Apellido Materno')
    cod_familiar = fields.Char('Codigo de familia')
    cod_pago = fields.Char('Codigo de Pago')

    grado_id = fields.Char('Codigo Informacion')
    seccion_id = fields.Char('Codigo Informacion')
    etapa_id = fields.Char('Codigo Informacion')
    direccion = fields.Char('Direccion')
    estado_estudiante = fields.Boolean(u'Estado de Estudiante')
    pais_nac = fields.Char('Pais de nacimiento')
    distrito_direccion = fields.Char('Distrito de direccion')
    provincia_direccion = fields.Char('Provincia de direccion')
    departamento_direccion = fields.Char('Departamento de direccion')
    fec_nac = fields.Date('Fecha de nacimiento')
    table_apoderado_id = fields.Char('Id de la tabla del apoderado')
    type_documento_id = fields.Integer('tipo documento')


class temp_apoderado(models.Model):
    _name = 'temp.apoderado'
    table_id = fields.Char('Id de la tabla')
    nro_dni = fields.Char('Numero de DNI')
    nombres = fields.Char('Nombres')
    apellido_pat = fields.Char('Apellido Paterno')
    apellido_mat = fields.Char('Apellido Materno')
    email = fields.Char('Email')
    apo_dir = fields.Char('Direccion')
    distrito_direccion = fields.Char('Distrito de direccion')
    provincia_direccion = fields.Char('Provincia de direccion')
    departamento_direccion = fields.Char('Departamento de direccion')
    pais_nac = fields.Char('Pais de nacimiento')



