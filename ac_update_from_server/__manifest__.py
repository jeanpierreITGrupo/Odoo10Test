# -*- encoding: utf-8 -*-
{
	'name': 'Actualizar desde servidor',
	'category': 'account',
	'author': 'ITGRUPO-PRESCOTT',
	'depends': ['base','res_partner_it','ac_partner_student_it'],
	'version': '1.0',
	'description':"""
	1.- Instalar ODBC DRIVER 13 para SQL SERVER
	Ubuntu y WIndows
	Configurar el origen de datos.
	(Probar con Virtual Box)

2.- Instalar libreria para Python (pypyodbc).
	Colocarlo dentro de la carpeta Server.

3.- Configurar string de conexion en ODOO --> Academico--> Parametros
	- Solo debe de existir un solo origen.
	- Esto está en la tabla ac_parameters

4.- Crear una tarea para actualizar automaticamente
	Nombre del Objeto : ac.update.log
	Nombre del Metodo : automatic_task
	
	Actualiza desde el servidor
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
	'ac_update_log_view.xml',
	'ac_parameters_view.xml',
	],
	'installable': True
}
