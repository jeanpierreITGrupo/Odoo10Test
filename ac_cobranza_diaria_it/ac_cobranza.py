# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import pyodbc
from odoo.exceptions import ValidationError
import csv 
import json

class account_invoice(models.Model):
	_inherit = 'account.invoice'

	estudiante_id = fields.Many2one('res.partner','Estudiante')



class vst_recaudacion(models.Model):
	_name = 'vst.recaudacion'

	id_recaudacion = fields.Integer('Id Recaudacion')
	codigo_estudiante = fields.Char('Codigo Estudiante')
	id_servicio = fields.Integer('Id Servicio')
	nombre_servicio = fields.Char('Nombre Servicio')
	num_op = fields.Char('Num. Operacion')
	saldo = fields.Float('Saldo o Importe')
	serie = fields.Char('Serie Edusoftnet')
	numero = fields.Char('Numero Edusoftnet')
	estado_comprobante = fields.Char('Estado Comprobante')
	fecha_pago = fields.Date('Fecha de Pago')
	cod_interno_pago = fields.Char('Cod. Interno Pago')


class recaudacion_diaria(models.Model):
	_name = 'recaudacion.diaria'

	@api.model
	def get_fecha(self):
		from datetime import datetime, timedelta
		fecha = datetime.now()- timedelta(hours=29)
		return str(fecha)[:10]
		
	name = fields.Date('Fecha', default=get_fecha)
	error_recaudacion = fields.Integer(u'Errores de Recaudación',compute="get_error_recaudacion")
	error_validacion = fields.Integer(u'Errores de Validación',compute="get_error_validacion")
	error_emision_odoo = fields.Integer(u'Errores de Emisión',compute="get_error_emision_odoo")
	error_nubefact = fields.Integer(u'Errores de NubeFact',compute="get_error_nubefact")
	error_pagar = fields.Integer(u'Errores de Pago',compute="get_error_pagar")

	recaudacion_ids = fields.One2many('recaudacion.diaria.recaudacion','recaudacion_id','Recaudaciones',domain=[('error_recaudacion','=',False),('error_validacion','=',False),('error_emision_odoo','=',False),('error_nubefact','=',False),('error_pagar','=',False)])
	
	errores_recaudacion_ids = fields.One2many('recaudacion.diaria.recaudacion','recaudacion_id','Errores',domain=[('error_recaudacion','!=',False)])
	errores_validacion_ids = fields.One2many('recaudacion.diaria.recaudacion','recaudacion_id','Errores',domain=[('error_validacion','!=',False)])
	errores_emision_odoo_ids = fields.One2many('recaudacion.diaria.recaudacion','recaudacion_id','Errores',domain=[('error_emision_odoo','!=',False)])
	errores_nubefact_ids = fields.One2many('recaudacion.diaria.recaudacion','recaudacion_id','Errores',domain=[('error_nubefact','!=',False)])
	errores_pagar_ids = fields.One2many('recaudacion.diaria.recaudacion','recaudacion_id','Errores',domain=[('error_pagar','!=',False)])

	@api.one
	def get_error_recaudacion(self):
		self.error_recaudacion = len(self.errores_recaudacion_ids)

	@api.one
	def get_error_validacion(self):
		self.error_validacion = len(self.errores_validacion_ids)

	@api.one
	def get_error_emision_odoo(self):
		self.error_emision_odoo = len(self.errores_emision_odoo_ids)

	@api.one
	def get_error_nubefact(self):
		self.error_nubefact = len(self.errores_nubefact_ids)

	@api.one
	def get_error_pagar(self):
		self.error_pagar = len(self.errores_pagar_ids)



	@api.one
	def hacernada(self):
		return



	@api.one
	def recaudar(self):
		parameters = self.env['ac.parameters'].search([])[0]
		directory_path = parameters.path_csv
		server,database,username,password = parameters.server,parameters.database,parameters.username,parameters.password
		#server,database,username,password = 'dev04\sqlexpress','TestEdusoft','admin','programar'
		text_conection ='DRIVER={ODBC Driver 13 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password

		import sys
		sys.setdefaultencoding('iso-8859-1')
		direction_archivo = directory_path + 'recaudacion.csv'
		cursor = pyodbc.connect(text_conection).cursor()
		cursor.execute("""
			select idpago,LTRIM(RTRIM(codigo)),idservicio,LTRIM(RTRIM(servicio)),LTRIM(RTRIM(opebancaria)),monto,LTRIM(RTRIM(serie)),LTRIM(RTRIM(documento)),LTRIM(RTRIM(estado)),fechabanco,LTRIM(RTRIM(banco)) from Recaudacion where CONVERT(DATETIME,fechabanco,111) = CONVERT(DATETIME,'"""+ str(self.name) +"""',111);
			""")
		#inafecto
		list_recaudacion = cursor.fetchall()
		file_csv = open(direction_archivo, "w")
		out = csv.writer(file_csv, lineterminator='\n')
		# out = csv.writer(open(direction_archivo, "w"), quoting=csv.QUOTE_NONNUMERIC,lineterminator = '\n')
		out.writerows(list_recaudacion)
		file_csv.close()



		nopen = open(directory_path + 'recaudacion.csv', "rb")
		contenido = nopen.read()
		nopen.close()

		flag = False
		try:
			import codecs
			f = codecs.open(directory_path + 'recaudacion.csv',encoding='utf-8',errors='strict')
			f.read()
		except UnicodeDecodeError:
			flag= True

		if flag:
			import codecs
			BLOCKSIZE = 1048576 # or some other, desired size in bytes
			with codecs.open(directory_path + 'recaudacion.csv', "r", "iso-8859-1") as sourceFile:
				with codecs.open(directory_path + 'recaudacionno.csv', "w", "utf-8") as targetFile:
					while True:
						contents = sourceFile.read(BLOCKSIZE)
						if not contents:
							break
						targetFile.write(contents)
		else:			
			file_cv1 = open(directory_path + 'recaudacionno.csv','wb')
			file_cv1.write(contenido)
			file_cv1.close()




		self.env.cr.execute(""" 
							DELETE FROM vst_recaudacion;                            
							COPY vst_recaudacion(id_recaudacion,codigo_estudiante,id_servicio,nombre_servicio,num_op,saldo,serie,numero,estado_comprobante,fecha_pago,cod_interno_pago) FROM '"""+directory_path + 'recaudacionno.csv'+"""' with delimiter ',' CSV;                           
			""")

		self.env.cr.execute("""
				select distinct id_recaudacion
				from vst_recaudacion
				group by id_recaudacion
				having count(*)>1
			""")

		duplicados = self.env.cr.fetchall()
		duplicados = [i[0] for i in duplicados]

		self.env.cr.execute("""
				delete from recaudacion_diaria_recaudacion where recaudacion_id = """+str(self.id)+""" and factura_id is null
			""")

		self.env.cr.execute("""  
			drop table if exists recaudacion_adaptacion;

			create table recaudacion_adaptacion AS 

				select vc.id_recaudacion,vc.codigo_estudiante,vc.id_servicio,vc.nombre_servicio,vc.num_op,vc.saldo,vc.serie,vc.numero,vc.estado_comprobante,vc.fecha_pago,vc.cod_interno_pago 
				from vst_recaudacion vc
				left join recaudacion_diaria_recaudacion cde on cde.id_recaudacion::integer = vc.id_recaudacion::integer
				where cde.id is null -- or ( cde.error is not null and cde.recaudacion_id = """+str(self.id)+""" );
		 """)

		
		self.env.cr.execute("""
			                   select ra.serie, ra.numero, every(ra.codigo_estudiante = T.cod) from (
			select serie, numero, max(codigo_estudiante) as cod from recaudacion_adaptacion
			group by serie, numero) T
			inner join recaudacion_adaptacion ra on ra.serie = T.serie and ra.numero = T.numero
			where coalesce(ra.serie,'') != '' and coalesce(ra.numero,'') != ''
			group by ra.serie, ra.numero
			having every(ra.codigo_estudiante = T.cod) = False
			""")
		dupli_nro = self.env.cr.fetchall()
		dupli_of = []
		for i in dupli_nro:
			dupli_of.append( (i[0],i[1]) )

		self.env.cr.execute("""
				select id_recaudacion,codigo_estudiante,id_servicio,nombre_servicio,num_op,saldo,serie,numero,estado_comprobante,fecha_pago,cod_interno_pago from recaudacion_adaptacion 
			""")		
		for i in self.env.cr.fetchall():
			error = ''
			if not i[0]:
				error += u'Falta identificador de recaudación\n'
			else:
				if i[0] in duplicados:
					error += u'Recaudación duplicada\n'
			if not i[1]:
				error += u'Falta código del estudiante\n'
			if not i[2]:
				error += u'Falta identificador de servicio\n'
			if not i[3]:
				error += u'Falta nombre de servicio\n'
			#if not i[4]:
			#	error += u'Falta número de operación\n'
			if not i[5]:
				error += u'Falta saldo\n'
			else:
				try:
					a = float(i[5])
					if a<= 0:
						error += 'Saldo no puede ser negativo o cero\n'	
				except Exception as e:
					error += 'Formato incorrecto para saldo\n'
			if not i[6]:
				error += 'Falta la serie\n'
			if not i[7]:
				error += u'Falta el número\n'

			if i[6] and i[7] and (i[6],i[7]) in dupli_of:
				error += u'Serie y Número Duplicado con otro Alumno Diferente\n'

			if not i[8]:
				error += 'Falta el Estado de Comprobante\n'
			else:
				if i[8] not in ('activo','anulado'):
					error += 'El estado debe ser Activo / Anulado\n'

			if not i[9]:
				error += 'Falta la fecha de pago\n'
			if not i[10]:
				error += 'Falta Cod. Interno de Pago\n'
			else:
				if i[10] not in ('03','09','11'):
					error += 'El Cod. Interno debe ser 03, 09 o 11\n'

			partner = self.env['res.partner'].search([('code_student','=',i[1])])			
			if len(partner) == 0:
				error += 'No existe el Estudiante\n'
			elif len(partner)== 1:
				if not partner[0].it_type_document.id:
					error += 'El Estudiante no tiene Tipo de Documento\n'
			elif len(partner)>1:
				if i[1]:
					error += u'Código de estudiante duplicado o vacio\n'

			if error == '':
				error = False


			data = {
			 'id_recaudacion':i[0],
			 'codigo_estudiante':i[1],
			 'id_servicio':i[2],
			 'nombre_servicio':i[3],
			 'num_op':i[4],
			 'saldo':i[5],
			 'serie':i[6],
			 'numero':i[7],
			 'estado_comprobante':i[8],
			 'fecha_pago':i[9],
			 'cod_interno_pago':i[10],
			 'recaudacion_id':self.id,
			 'error_recaudacion':error,			 
			}
			if len(partner)== 1:
				data['alumno'] = partner[0].id

			self.env['recaudacion.diaria.recaudacion'].create(data)




	@api.one 
	def validacion(self):

		todos_recau = []

		for i in self.errores_validacion_ids:
			i.error_validacion = False

		self.refresh()

		for i in self.recaudacion_ids.filtered(lambda x: x.state in ('recaudado','validado') ):
			errores = ''

			partner = self.env['res.partner'].search([('code_student','=',i.codigo_estudiante)])			
			if len(partner) == 0:
				errores += 'No existe el Estudiante\n'
				errores += 'No existe el tipo de documento para el CPE\n'
				errores += 'No existe la serie CPE\n'
			else:
				partner = partner[0]
				i.alumno = partner.id
				i.tipo_doc = partner.it_type_document.id
				if not partner.it_type_document.id:
					errores += 'No existe el tipo de documento para el CPE\n'
					errores += 'No existe la serie CPE\n'
				else:
					serie = self.env['serie.recaudacion'].search([('serie_edusoft','=',i.serie),('tipo_doc','=',partner.it_type_document.id)])
					if len(serie)== 0 or not serie[0].serie_odoo.id:
						errores += 'No existe la serie CPE\n'
						if len(serie) == 0:
							data = {
								'serie_edusoft':i.serie,
								'tipo_doc':partner.it_type_document.id,
							}
							self.env['serie.recaudacion'].create(data)
					else:
						i.serie_odoo = serie[0].serie_odoo.id

			banco = self.env['banco.recaudacion'].search([('banco_edusoft','=',i.cod_interno_pago)])
			if len(banco)== 0 or not banco[0].diario.id:
				errores += 'No existe Cod. Interno de Banco configurado para el CPE\n'
				if len(banco) == 0:
					data = {
						'banco_edusoft':i.cod_interno_pago,
					}
					self.env['banco.recaudacion'].create(data)


			i.error_validacion = errores if errores != '' else False

			producto = self.env['product.product'].search([('servicio_edusoft','=',i.id_servicio),('name','=',i.nombre_servicio)])
			if len(producto)>0:
				producto = producto[0]
			else:
				producto = self.env['product.product'].create({'default_code':str(i.id_servicio),'servicio_edusoft':i.id_servicio,'name':i.nombre_servicio,'type':'service','purchase_ok':False,'sale_ok':True,})

			i.cuenta_producto = producto.property_account_income_id.id if producto.property_account_income_id.id else producto.categ_id.property_account_income_categ_id.id


			i.state = 'validado'

	@api.one
	def facturar(self):		
		self._cr.autocommit(False)
		last_factura = False
		last_name = False
		last_partner = False
		factura = False
		todos_recau = []
		
		for i in self.errores_emision_odoo_ids:
			i.error_emision_odoo  = False

		self.refresh()

		betados = []

		for i in self.errores_recaudacion_ids:
			if i.serie and i.numero:
				betados.append( [i.serie + '-' + i.numero] )
		for i in self.errores_validacion_ids:
			if i.serie and i.numero:
				betados.append( [i.serie + '-' + i.numero] )

		ultimo_contenedor = False# puede fallar uno y el de mas abajo continuarla
		
		for i in self.recaudacion_ids.filtered(lambda x: x.state in ('validado','emitido') ):			

			if not i.factura_id.id:
				if [i.serie + '-' + i.numero] in betados:
					i.error_emision_odoo = 'Otra linea con el mismo serie y numero se encuentra con errores pendientes.\n'
				else:
					try:
						ultimo_contenedor =i
						partners = []
						partners.append(i.alumno.id)
						if i.alumno.parent_id.id:
							partners.append(i.alumno.parent_id.id)

						factura = False
						if last_factura and last_name == 'Edusoftnet: ' + i.serie + '-' + i.numero and last_partner == i.alumno.id if not i.alumno.parent_id.id else i.alumno.parent_id.id:
							factura = last_factura
						else:
							existe = self.env['account.invoice'].search([('name','=','Edusoftnet: ' + i.serie + '-' + i.numero),('estudiante_id','=',i.alumno.id)])
							if len(existe)>0:
								factura = existe[0]
							else:
								if last_factura:
									last_factura.action_invoice_open()
								data = {
									'partner_id':i.alumno.id if not i.alumno.parent_id.id else i.alumno.parent_id.id,
									'it_type_document':i.alumno.it_type_document.id,
									'serie_id':i.serie_odoo.id,
									'reference':i.serie_odoo.sequence_id.prefix+ "0"*(i.serie_odoo.sequence_id.padding - len(str(i.serie_odoo.sequence_id.number_next_actual))) + str(i.serie_odoo.sequence_id.number_next_actual),
									'currency_id':self.env['res.currency'].search([('name','=','PEN')])[0].id,
									'sunat_transaction_type':'1',
									'journal_id':self.env['account.journal'].search([('type','=','sale')])[0].id,
									'account_id':(i.alumno if not i.alumno.parent_id.id else i.alumno.parent_id).property_account_receivable_id.id,
									'estado_ple_venta':'1',
									'name':'Edusoftnet: ' + i.serie + '-' + i.numero,
									'estudiante_id':i.alumno.id,
								}
								last_factura = self.env['account.invoice'].create(data)

								factura = last_factura
								last_name = 'Edusoftnet: ' + i.serie + '-' + i.numero
								last_partner = i.alumno.id if not i.alumno.parent_id.id else i.alumno.parent_id.id

						if factura == last_factura:
							producto = self.env['product.product'].search([('servicio_edusoft','=',i.id_servicio),('name','=',i.nombre_servicio)])
							if len(producto)==0:
								raise ValidationError(u'El producto ' + i.nombre_servicio + ' no existe.')
							producto = producto[0]
							data ={
								'product_id':producto.id,
								'quantity':1,
								'price_unit':float(i.saldo),
								'account_id':i.cuenta_producto.id,
								'name':producto.name,
								'invoice_id':factura.id,
								'invoice_line_tax_ids':[(6, 0, [ self.env['account.tax'].search([('name','=','INAF')])[0].id ])],
							}
							self.env['account.invoice.line'].create(data)

						i.factura_id = factura.id
						i.state = 'emitido'
						self._cr.commit()
					except Exception as e:
						self._cr.rollback()
						if factura and factura == last_factura:
							partners = []
							partners.append(i.alumno.id)
							if i.alumno.parent_id.id:
								partners.append(i.alumno.parent_id.id)

							betados.append([i.serie + '-' + i.numero,partners])
							last_factura.unlink()

						i.error_emision_odoo = str(e)
						i.state = 'emitido'
						sinerrores = False
						self._cr.commit()

		self._cr.commit()
		if ultimo_contenedor and last_factura and last_factura.state != 'draft':
			try:
				last_factura.action_invoice_open()				
				ultimo_contenedor.state = 'emitido'
			except:

				self._cr.rollback()
				last_factura.unlink()
				ultimo_contenedor.state = 'emitido'
				ultimo_contenedor.error_emision_odoo = str(e)				
				self._cr.commit()

		for i in self.recaudacion_ids:
			if i.factura_id.id:
				i.num_odoo = i.factura_id.reference

		
		self._cr.commit()


	@api.one
	def unlink(self):
		raise ValidationError(u'No se puede eliminar una recaudación')
		t = super(recaudacion_diaria,self).unlink()
		return t

class recaudacion_diaria_recaudacion(models.Model):
	_name = 'recaudacion.diaria.recaudacion'

	id_recaudacion = fields.Integer('Id Recaudacion')
	codigo_estudiante = fields.Char(u'Código Estudiante')
	id_servicio = fields.Integer('Id Servicio')
	nombre_servicio = fields.Char('Servicio')
	num_op = fields.Char('Num. Op.')
	saldo = fields.Float('Saldo')
	serie = fields.Char('Serie Edusoftnet')
	numero = fields.Char('Num. Edusoftnet')
	estado_comprobante = fields.Char('Estado Comprobante')
	fecha_pago = fields.Date('Fecha Pago')
	cod_interno_pago = fields.Char('Cod. Interno Pago')
	
	error_recaudacion = fields.Char('Error')
	error_recaudacion_json = fields.Char('Error Json', compute="get_error_recaudacion_json")

	error_validacion = fields.Char('Error')
	error_validacion_json = fields.Char('Error Json', compute="get_error_validacion_json")

	error_emision_odoo = fields.Char('Error')
	error_emision_odoo_json = fields.Char('Error Json', compute="get_error_emision_json")

	error_nubefact = fields.Char('Error')
	error_nubefact_json = fields.Char('Error Json', compute="get_error_nubefact_json")

	error_pagar = fields.Char('Error')
	error_pagar_json = fields.Char('Error Json', compute="get_error_pagar_json")


	recaudacion_id = fields.Many2one('recaudacion.diaria','Recaudacion')

	alumno = fields.Many2one('res.partner','Estudiante')
	cuenta_producto = fields.Many2one('account.account','Cta. Contable')
	tipo_doc = fields.Many2one('einvoice.catalog.01','Tipo Documento')
	serie_odoo = fields.Many2one('it.invoice.serie','Serie CPE')
	num_odoo = fields.Char('Numero CPE')

	factura_id = fields.Many2one('account.invoice','Factura Pago')
	pago_id = fields.Many2one('account.payment','Pago')
	

	state = fields.Selection([('recaudado','Recaudado'),('validado','Validado'),('emitido','Emitido Odoo'),('nubefact','NubeFact'),('pagado','Pagado')],'Estado',default='recaudado')

	_order = 'id_recaudacion'

	@api.one
	@api.depends('error_recaudacion')
	def get_error_recaudacion_json(self):
		if self.error_recaudacion:
			elem = self.error_recaudacion.split("\n")
			cont_f = []
			for i in elem:
				if i != '':
					cont_f.append(i)
			info = {'title': u'Errores Recaudación','content':[cont_f]}
			self.error_recaudacion_json = json.dumps(info)
		else:
			self.error_recaudacion_json = False


	@api.one
	@api.depends('error_validacion')
	def get_error_validacion_json(self):
		if self.error_validacion:
			elem = self.error_validacion.split("\n")
			cont_f = []
			for i in elem:
				if i != '':
					cont_f.append(i)
			info = {'title': u'Errores Validación','content':[cont_f]}
			self.error_validacion_json = json.dumps(info)
		else:
			self.error_validacion_json = False


	@api.one
	@api.depends('error_emision_odoo')
	def get_error_emision_json(self):
		if self.error_emision_odoo:
			elem = self.error_emision_odoo.split("\n")
			cont_f = []
			for i in elem:
				if i != '':
					cont_f.append(i)
			info = {'title': u'Errores Emisión Odoo','content':[cont_f]}
			self.error_emision_odoo_json = json.dumps(info)
		else:
			self.error_emision_odoo_json = False


	@api.one
	@api.depends('error_nubefact')
	def get_error_nubefact_json(self):
		if self.error_nubefact:
			elem = self.error_nubefact.split("\n")
			cont_f = []
			for i in elem:
				if i != '':
					cont_f.append(i)
			info = {'title': u'Errores NubeFact','content':[cont_f]}
			self.error_nubefact_json = json.dumps(info)
		else:
			self.error_nubefact_json = False


	@api.one
	@api.depends('error_pagar')
	def get_error_pagar_json(self):
		if self.error_pagar:
			elem = self.error_pagar.split("\n")
			cont_f = []
			for i in elem:
				if i != '':
					cont_f.append(i)
			info = {'title': u'Errores Pago','content':[cont_f]}
			self.error_pagar_json = json.dumps(info)
		else:
			self.error_pagar_json = False





class banco_recaudacion(models.Model):
	_name = 'banco.recaudacion'

	banco_edusoft = fields.Char('Cod. Interno de Banco')
	diario = fields.Many2one('account.journal','Diario de Banco CPE')

	_rec_name = 'banco_edusoft'

class serie_recaudacion(models.Model):
	_name = 'serie.recaudacion'

	serie_edusoft = fields.Char('Serie Edusoftnet')
	tipo_doc = fields.Many2one('einvoice.catalog.01','Tipo Documento')
	serie_odoo = fields.Many2one('it.invoice.serie','Serie CPE')

	_rec_name = 'serie_edusoft'

class product_product(models.Model):
	_inherit = 'product.product'

	servicio_edusoft = fields.Integer('Servicio Edusoft')
