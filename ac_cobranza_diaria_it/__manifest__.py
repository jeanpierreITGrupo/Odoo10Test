# -*- encoding: utf-8 -*-
{
	'name': 'Importacion de Recaudacion',
	'category': 'account',
	'author': 'ITGRUPO-PRESCOTT',
	'depends': ['import_base_it','ac_update_from_server'],
	'version': '1.0',
	'description':"""
	Importa Recaudaciones Diarias
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
	'ac_cobranza_view.xml'
	],
	'qweb':['ac_cobranza_template.xml'],
	'installable': True
}
