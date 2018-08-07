# -*- encoding: utf-8 -*-
{
	'name': 'Formulario del alumno',
	'category': 'account',
	'author': 'ITGRUPO-PRESCOTT',
	'depends': ['base','res_partner_it'],
	'version': '1.0',
	'description':"""
	Imprime guia en remision en caso de que la orden de entrega sea para un cliente
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
	'ac_student_view.xml'
	],
	'installable': True
}
