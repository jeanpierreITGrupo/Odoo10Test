# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import pyodbc
from odoo.exceptions import ValidationError
import csv 
import json
import codecs

class estudiante_apoderado(models.Model):
	_name = 'estudiante.apoderado'

	_rec_name = 'apo_nombres'

	apo_documento= fields.Char('Apo. Documento')
	apo_nacionalidad= fields.Many2one('res.country','Apo. Nacionalidad')
	apo_nombres= fields.Char('Apo. Nombres')
	apo_ape_paterno= fields.Char('Apo. Apellido Paterno')
	apo_ape_materno= fields.Char('Apo. Apellido Materno')
	apo_email= fields.Char('Apo. Email')
	apo_domicilio= fields.Char('Apo. Domicilio')
	apo_domidistrito= fields.Many2one('res.country.state','Apo. Distrito')
	apo_domiprovincia= fields.Many2one('res.country.state','Apo. Provincia')
	apo_domidepartamento= fields.Many2one('res.country.state','Apo. Departamento')
	estu_code = fields.Char(u'Código Estudiante')

class res_partner(models.Model):
	_inherit = 'res.partner'

	val_apoderado_id = fields.Many2one('estudiante.apoderado','Apoderado')


class vst_estudiante(models.Model):
	_name = 'vst.estudiante'

	estu_codigo= fields.Char(u'Código Estudiante')
	estu_documento = fields.Char('Nro. Documento')
	estu_nacionalidad= fields.Char('Nacionalidad')
	estu_nombres= fields.Char('Nombres')
	estu_ap_paterno= fields.Char('Apellido Paterno')
	estu_ap_materno= fields.Char('Apellido Materno')
	estu_domicilio= fields.Char('Domicilio')
	estu_domidistrito= fields.Char('Distrito')
	estu_domiprovincia= fields.Char('Provincia')
	estu_domidepartamento= fields.Char('Departamento')
	estu_homastico= fields.Date('Fecha Nacimiento')
	estu_bancario= fields.Char('Ope. Bancario')
	estu_cofamiliar= fields.Char(u'Código Familiar')
	estu_nivel= fields.Char('Nivel')
	estu_grado= fields.Char('Grado')
	estu_aula= fields.Char('Aula')
	estu_estado= fields.Char('Estado')
	apo_documento= fields.Char('Apo. Documento')
	apo_nacionalidad= fields.Char('Apo. Nacionalidad')
	apo_nombres= fields.Char('Apo. Nombres')
	apo_ape_paterno= fields.Char('Apo. Apellido Paterno')
	apo_ape_materno= fields.Char('Apo. Apellido Materno')
	apo_email= fields.Char('Apo. Email')
	apo_domicilio= fields.Char('Apo. Domicilio')
	apo_domidistrito= fields.Char('Apo. Distrito')
	apo_domiprovincia= fields.Char('Apo. Provincia')
	apo_domidepartamento= fields.Char('Apo. Departamento')


class estudiante_diaria(models.Model):
	_name = 'estudiante.diaria'

	@api.model
	def get_fecha(self):
		from datetime import datetime, timedelta
		fecha = datetime.now()- timedelta(hours=29)
		return str(fecha)[:10]
		
	name = fields.Date('Fecha', default=get_fecha)
	have_error = fields.Boolean('Tiene errores',compute="get_errores")
	estudiante_ids = fields.One2many('estudiante.diaria.estudiante','estudiante_id','estudiantes',domain=[('error','=',False)])
	errores_ids = fields.One2many('estudiante.diaria.estudiante','estudiante_id','Errores',domain=[('error','!=',False)])
	state = fields.Selection([('borrador','Borrador'),('importado','Importado')],'Estado',default='borrador')
	

	@api.one
	def get_errores(self):
		self.have_error = False
		if len(self.errores_ids)>0:
			self.have_error = True


	@api.one
	def sacar_estudiante(self):
		self.state = 'importado'
		parameters = self.env['ac.parameters'].search([])[0]
		directory_path = parameters.path_csv
		server,database,username,password = parameters.server,parameters.database,parameters.username,parameters.password
		#server,database,username,password = 'dev04\sqlexpress','TestEdusoft','admin','programar'
		text_conection ='DRIVER={ODBC Driver 13 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password


		import sys
		sys.setdefaultencoding('iso-8859-1')
		direction_archivo = directory_path + 'estudiante.csv'
		cursor = pyodbc.connect(text_conection).cursor()
		cursor.execute("""

			select LTRIM(RTRIM(CAST(estu_codigo as varchar(8000)))),	     LTRIM(RTRIM(CAST(estu_documento as varchar(8000)))),	   LTRIM(RTRIM(CAST(estu_nacionalidad as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_nombres as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_ap_paterno as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_ap_materno as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_domicilio as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_domidistrito as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_domiprovincia as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_domidepartamento as varchar(8000)))),	estu_homastico,	LTRIM(RTRIM(CAST(estu_bancario as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_cofamiliar as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_nivel as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_grado as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_aula as varchar(8000)))),	LTRIM(RTRIM(CAST(estu_estado as varchar(8000)))),	   LTRIM(RTRIM(CAST(apo_documento as varchar(8000)))),	LTRIM(RTRIM(CAST(apo_nacionalidad as varchar(8000)))),	LTRIM(RTRIM(CAST(apo_nombres as varchar(8000)))),	LTRIM(RTRIM(CAST(apo_ape_paterno as varchar(8000)))),	LTRIM(RTRIM(CAST(apo_ape_materno as varchar(8000)))),	LTRIM(RTRIM(CAST(apo_email as varchar(8000)))),	LTRIM(RTRIM(CAST(apo_domicilio as varchar(8000)))),	LTRIM(RTRIM(CAST(apo_domidistrito as varchar(8000)))),	LTRIM(RTRIM(CAST(apo_domiprovincia as varchar(8000)))),	LTRIM(RTRIM(CAST(apo_domidepartamento as varchar(8000))))
			from Alumnos_soft
			""")

		list_estudiante = cursor.fetchall()
		file_csv = open(direction_archivo, "w")
		out = csv.writer(file_csv, lineterminator='\n')
		out.writerows(list_estudiante)
		file_csv.close()



		nopen = open(direction_archivo, "rb")
		contenido = nopen.read()
		nopen.close()

		flag = False
		try:
			import codecs
			f = codecs.open(directory_path + 'estudiante.csv',encoding='utf-8',errors='strict')
			f.read()
		except UnicodeDecodeError:
			flag= True

		if flag:
			import codecs
			BLOCKSIZE = 1048576 # or some other, desired size in bytes
			with codecs.open(directory_path + 'estudiante.csv', "r", "iso-8859-1") as sourceFile:
				with codecs.open(directory_path + 'estudianteno.csv', "w", "utf-8") as targetFile:
					while True:
						contents = sourceFile.read(BLOCKSIZE)
						if not contents:
							break
						targetFile.write(contents)
		else:			
			file_cv1 = open(directory_path + 'estudianteno.csv','wb')
			file_cv1.write(contenido)
			file_cv1.close()






		self.env.cr.execute(""" 
							DELETE FROM vst_estudiante;                            
							COPY vst_estudiante(estu_codigo,estu_documento,estu_nacionalidad,estu_nombres,estu_ap_paterno,estu_ap_materno,estu_domicilio,estu_domidistrito,estu_domiprovincia,estu_domidepartamento,estu_homastico,estu_bancario,estu_cofamiliar,estu_nivel,estu_grado,estu_aula,estu_estado,apo_documento,apo_nacionalidad,apo_nombres,apo_ape_paterno,apo_ape_materno,apo_email,apo_domicilio,apo_domidistrito,apo_domiprovincia,apo_domidepartamento) FROM '"""+directory_path + 'estudianteno.csv'+"""' with delimiter ',' CSV;                           
			""")

		self.env.cr.execute("""
				select distinct estu_codigo
				from vst_estudiante
				group by estu_codigo
				having count(*)>1
			""")

		duplicados = self.env.cr.fetchall()
		duplicados = [i[0] for i in duplicados]

		self.env.cr.execute("""
				delete from estudiante_diaria_estudiante where estudiante_id = """+str(self.id)+"""
			""")

		self.env.cr.execute("""
			 update vst_estudiante set estu_nacionalidad = 'PERU'
			 where estu_nacionalidad = 'PERUANA'
			""")


		self.env.cr.execute("""
			 update vst_estudiante set apo_nacionalidad = 'PERU'
			 where apo_nacionalidad = 'PERUANA'
			""")


		self.env.cr.execute(""" 
				select distinct(ve.estu_nacionalidad) from  vst_estudiante ve
				left join res_country rc on UPPER(rc.name) = UPPER(ve.estu_nacionalidad)
				where rc.id is null and ( estu_nacionalidad is not null  or estu_nacionalidad != '' )
			""")

		for i in self.env.cr.fetchall():
			self.env['res.country'].create({'name': i[0]})


		peru = self.env['res.country'].search([('name','=ilike',u'Peru')])[0]


		self.env.cr.execute("""
				select distinct UPPER(a) ,UPPER(b) ,UPPER(c)  from 
				( 
					select estu_domidistrito a ,estu_domiprovincia b,estu_domidepartamento c  from vst_estudiante
					union all 
					select apo_domidistrito a ,apo_domiprovincia b ,apo_domidepartamento c  from vst_estudiante 
				)T
			""")

		for i in self.env.cr.fetchall():
			if i[0] and i[1] and i[2]:
				depart = False
				cont = self.env['res.country.state'].search([('name','=ilike',i[2]),('state_id','=',False),('province_id','=',False)])
				if len(cont)>0:
					depart = cont[0]
				else:
					depart = self.env['res.country.state'].create({'name':i[2],'country_id':peru.id,'code':i[2][:3]})

				prov = False
				cont = self.env['res.country.state'].search([('name','=ilike',i[1]),('state_id','=',depart.id),('province_id','=',False)])
				if len(cont)>0:
					prov = cont[0]
				else:
					prov =  self.env['res.country.state'].create({'name':i[1],'country_id':peru.id,'state_id':depart.id,'code':i[2][:3]+i[1][:3]})

				distri = False
				distri = self.env['res.country.state'].search([('name','=ilike',i[0]),('state_id','=',depart.id),('province_id','=',prov.id)])
				if len(cont)>0:
					distri = cont[0]
				else:
					prov =  self.env['res.country.state'].create({'name':i[0],'country_id':peru.id,'state_id':depart.id,'province_id':prov.id,'code':i[2][:3]+i[1][:3]+i[0][:3]})






		self.env.cr.execute("""  
			drop table if exists estudiante_adaptacion;

			create table estudiante_adaptacion AS 

				select ve.*
				from vst_estudiante ve
				left join res_partner rp on rp.code_student = ve.estu_codigo
				where rp.id is null
		 """)

		
		self.env.cr.execute("""
			select ve.estu_codigo from vst_estudiante ve
			group by ve.estu_codigo
			having count(*)>1
			""")
		dupli_nro = self.env.cr.fetchall()

		self.env.cr.execute("""
				select estu_codigo,estu_documento,estu_nacionalidad,estu_nombres,estu_ap_paterno,estu_ap_materno,estu_domicilio,estu_domidistrito,estu_domiprovincia,estu_domidepartamento,estu_homastico,estu_bancario,estu_cofamiliar,estu_nivel,estu_grado,estu_aula,estu_estado,apo_documento,apo_nacionalidad,apo_nombres,apo_ape_paterno,apo_ape_materno,apo_email,apo_domicilio,apo_domidistrito,apo_domiprovincia,apo_domidepartamento from estudiante_adaptacion 
			""")		

		for i in self.env.cr.fetchall():
			noimportar = False
			error = ''
			if not i[0]:
				error += u'El estudiante no tiene Código\n'
				noimportar = True
			else:
				if [i[0]] in dupli_nro:
					error += u'El Código del estudiante esta duplicado\n'
					noimportar = True

			if not i[1]:
				error += u'No tiene Nro. de Documento\n'

			if not i[2]:
				error += u'No tiene Nacionalidad\n'

			if not i[3]:
				error += u'No tiene Nombres\n'

			if not i[4]:
				error += u'No tiene Apellido Paterno\n'

			if not i[5]:
				error += u'No tiene Apellido Materno\n'

			if not i[6]:
				error += u'No tiene Dirección de Domicilio\n'
				
			if i[17] or  i[18] or  i[19] or  i[20] or  i[21]:
				if not i[17]:
					error += u'No tiene el Apoderado Documento\n'
				
				if not i[18]:
					error += u'No tiene el Apoderado Nacionalidad\n'
				
				if not i[19]:
					error += u'No tiene el Apoderado Nombres\n'
				
				if not i[20]:
					error += u'No tiene el Apoderado Apellido Paterno\n'
				
				if not i[21]:
					error += u'No tiene el Apoderado Apellido Materno\n'

			if error == '':
				error = False

			data = {			
			'estu_codigo':i[0],
			'estu_documento':i[1],
			'estu_nacionalidad':i[2],
			'estu_nombres':i[3],
			'estu_ap_paterno':i[4],
			'estu_ap_materno':i[5],
			'estu_domicilio':i[6],
			'estu_domidistrito':i[7],
			'estu_domiprovincia':i[8],
			'estu_domidepartamento':i[9],
			'estu_homastico':i[10],
			'estu_bancario':i[11],
			'estu_cofamiliar':i[12],
			'estu_nivel':i[13],
			'estu_grado':i[14],
			'estu_aula':i[15],
			'estu_estado':i[16],
			'apo_documento':i[17],
			'apo_nacionalidad':i[18],
			'apo_nombres':i[19],
			'apo_ape_paterno':i[20],
			'apo_ape_materno':i[21],
			'apo_email':i[22],
			'apo_domicilio':i[23],
			'apo_domidistrito':i[24],
			'apo_domiprovincia':i[25],
			'apo_domidepartamento':i[26],
			 'estudiante_id':self.id,
			 'error':error,
			 'importar':noimportar,
			}

			self.env['estudiante.diaria.estudiante'].create(data)

		dni = str( self.env['einvoice.catalog.06'].search([('code','=','1')])[0].id )

		self.env.cr.execute("""
			            insert into estudiante_apoderado(apo_documento, apo_nacionalidad, apo_nombres,apo_ape_paterno, apo_ape_materno, apo_email, apo_domicilio,
			            apo_domidistrito, apo_domiprovincia, apo_domidepartamento, estu_code)
			            select 
			            	apo_documento, rc.id , apo_nombres,apo_ape_paterno,apo_ape_materno, apo_email, apo_domicilio,rcs3.id , rcs2.id, rcs1.id , estu_codigo
			            from		            
						estudiante_diaria_estudiante ede
						left join res_country rc  on upper(unaccent(rc.name)) = upper(unaccent(ede.apo_nacionalidad))
						left join res_country_state rcs1 on upper(unaccent(rcs1.name)) =  upper(unaccent(apo_domidepartamento)) and rcs1.state_id is null
																														and rcs1.province_id is null

						left join res_country_state rcs2 on upper(unaccent(rcs2.name)) =  upper(unaccent(apo_domiprovincia)) and rcs2.state_id = rcs1.id
																														and rcs1.id is not null
																														and rcs2.province_id is null

						left join res_country_state rcs3 on upper(unaccent(rcs3.name)) =  upper(unaccent(apo_domidistrito)) and rcs3.state_id = rcs1.id
																														and rcs1.id is not null
																														and rcs3.province_id = rcs2.id
																														and rcs2.id is not null

						where  estudiante_id = """+ str(self.id)+ """
						;
						""")

		boleta = self.env['einvoice.catalog.01'].search([('code','=','03')])[0]

		self.env.cr.execute("""

            insert into res_partner(name,company_id,active,display_name,type,type_document_partner_it,nro_documento,code_student,code_family,
            code_payment,student,notify_email,invoice_warn,sale_warn,picking_warn,purchase_warn,table_student_id,grado_id,seccion_id,etapa_id,
            street,val_apoderado_id,date_nac,     country_id, state_id, province_id, district_id,it_type_document)
			select 
				coalesce(estu_nombres,'') || ', ' || coalesce(estu_ap_paterno,'') || ' ' || coalesce(estu_ap_materno,'') ,
				1, CASE when estu_estado = 'activo' then true else false end, coalesce(estu_nombres,'') || ', ' || coalesce(estu_ap_paterno,'') || ' ' || coalesce(estu_ap_materno,'') 
				,'contact', 
				CASE WHEN estu_nacionalidad in ('PERUANA','PERU') then """+dni+""" else Null::integer end, estu_documento, estu_codigo, estu_cofamiliar,estu_bancario,
				True,'no-always', 'no-message','no-message','no-message','no-message', Null::integer, estu_grado, estu_aula, estu_nivel, estu_domicilio,
				ea.id, estu_homastico, rc.id, rcs1.id, rcs2.id, rcs3.id,"""+str(boleta.id)+"""
			from 
			estudiante_diaria_estudiante ede
			left join estudiante_apoderado ea  on ea.estu_code = ede.estu_codigo

			left join res_country rc  on upper(unaccent(rc.name)) = upper(unaccent(ede.estu_nacionalidad))
						left join res_country_state rcs1 on upper(unaccent(rcs1.name)) =  upper(unaccent(estu_domidepartamento)) and rcs1.state_id is null
																														and rcs1.province_id is null

						left join res_country_state rcs2 on upper(unaccent(rcs2.name)) =  upper(unaccent(estu_domiprovincia)) and rcs2.state_id = rcs1.id
																														and rcs1.id is not null
																														and rcs2.province_id is null

						left join res_country_state rcs3 on upper(unaccent(rcs3.name)) =  upper(unaccent(estu_domidistrito)) and rcs3.state_id = rcs1.id
																														and rcs1.id is not null
																														and rcs3.province_id = rcs2.id
																														and rcs2.id is not null


			where ede.estudiante_id = """ +str(self.id)+ """
			""")


		self.env.cr.execute("""

			update res_partner set name = T.A, display_name= T.A , nro_documento= T.C, code_family=T.D, code_payment=T.E, grado_id=T.F, seccion_id= T.G ,
			 etapa_id=T.H,	street=T.I,  date_nac=T.J,   country_id =  T.K,    state_id =T.L , province_id= T.M , district_id = T.N , active = T.O
			from ( 




				select 
				coalesce(estu_nombres,'') || ', ' || coalesce(estu_ap_paterno,'') || ' ' || coalesce(estu_ap_materno,'') as A,
				CASE when estu_estado = 'activo' then true else false end as O,

				estu_documento as C, 
				estu_codigo as code, 
				estu_cofamiliar as D,
				estu_bancario as E,
				estu_grado as F, 
				estu_aula as G, 
				estu_nivel as H, 
				estu_domicilio as I,
				estu_homastico as J, 
				rc.id as K, 
				rcs1.id as L, 
				rcs2.id as M, rcs3.id as N
			from 
			estudiante_diaria_estudiante ede
			left join res_country rc  on upper(unaccent(rc.name)) = upper(unaccent(ede.estu_nacionalidad))
						left join res_country_state rcs1 on upper(unaccent(rcs1.name)) =  upper(unaccent(estu_domidepartamento)) and rcs1.state_id is null
																														and rcs1.province_id is null

						left join res_country_state rcs2 on upper(unaccent(rcs2.name)) =  upper(unaccent(estu_domiprovincia)) and rcs2.state_id = rcs1.id
																														and rcs1.id is not null
																														and rcs2.province_id is null

						left join res_country_state rcs3 on upper(unaccent(rcs3.name)) =  upper(unaccent(estu_domidistrito)) and rcs3.state_id = rcs1.id
																														and rcs1.id is not null
																														and rcs3.province_id = rcs2.id
																														and rcs2.id is not null


			   ) T where T.code = res_partner.code_student

			""")



		self.env.cr.execute("""
			            update estudiante_apoderado set apo_documento=T.A, apo_nacionalidad=T.B, apo_nombres=T.C,apo_ape_paterno=T.D, 
			            apo_ape_materno=T.E, apo_email=T.F, apo_domicilio=T.G,
			            apo_domidistrito=T.H, apo_domiprovincia=T.I, apo_domidepartamento= T.J
			            from ( 


			            select 
			            	apo_documento as A, 
			            	rc.id  as B, 
			            	apo_nombres as C,
			            	apo_ape_paterno as D,
			            	apo_ape_materno as E, 
			            	apo_email as F, 
			            	apo_domicilio as G,
			            	rcs3.id  as H, 
			            	rcs2.id as I, 
			            	rcs1.id  as J, estu_codigo as code
			            from		            
						estudiante_diaria_estudiante ede
						left join res_country rc  on upper(unaccent(rc.name)) = upper(unaccent(ede.apo_nacionalidad))
						left join res_country_state rcs1 on upper(unaccent(rcs1.name)) =  upper(unaccent(apo_domidepartamento)) and rcs1.state_id is null
																														and rcs1.province_id is null

						left join res_country_state rcs2 on upper(unaccent(rcs2.name)) =  upper(unaccent(apo_domiprovincia)) and rcs2.state_id = rcs1.id
																														and rcs1.id is not null
																														and rcs2.province_id is null

						left join res_country_state rcs3 on upper(unaccent(rcs3.name)) =  upper(unaccent(apo_domidistrito)) and rcs3.state_id = rcs1.id
																														and rcs1.id is not null
																														and rcs3.province_id = rcs2.id
																														and rcs2.id is not null

						)T where T.code = estudiante_apoderado.estu_code
						;
						""")



	@api.one
	def unlink(self):
		if self.state != 'borrador':
			raise ValidationError(u'No se puede eliminar una sincronización de estudiantes realizada')

		for i in self.errores_ids:
			i.unlink()
		for i in self.estudiante_ids:
			i.unlink()
		t = super(estudiante_diaria,self).unlink()
		return t


class estudiante_diaria_estudiante(models.Model):
	_name = 'estudiante.diaria.estudiante'

	importar = fields.Boolean('Importar')
	estu_codigo= fields.Char(u'Código Estudiante')
	estu_documento = fields.Char('Nro. Documento')
	estu_nacionalidad= fields.Char('Nacionalidad')
	estu_nombres= fields.Char('Nombres')
	estu_ap_paterno= fields.Char('Apellido Paterno')
	estu_ap_materno= fields.Char('Apellido Materno')
	estu_domicilio= fields.Char('Domicilio')
	estu_domidistrito= fields.Char('Distrito')
	estu_domiprovincia= fields.Char('Provincia')
	estu_domidepartamento= fields.Char('Departamento')
	estu_homastico= fields.Date('Fecha Nacimiento')
	estu_bancario= fields.Char('Ope. Bancario')
	estu_cofamiliar= fields.Char(u'Código Familiar')
	estu_nivel= fields.Char('Nivel')
	estu_grado= fields.Char('Grado')
	estu_aula= fields.Char('Aula')
	estu_estado= fields.Char('Estado')
	apo_documento= fields.Char('Apo. Documento')
	apo_nacionalidad= fields.Char('Apo. Nacionalidad')
	apo_nombres= fields.Char('Apo. Nombres')
	apo_ape_paterno= fields.Char('Apo. Apellido Paterno')
	apo_ape_materno= fields.Char('Apo. Apellido Materno')
	apo_email= fields.Char('Apo. Email')
	apo_domicilio= fields.Char('Apo. Domicilio')
	apo_domidistrito= fields.Char('Apo. Distrito')
	apo_domiprovincia= fields.Char('Apo. Provincia')
	apo_domidepartamento= fields.Char('Apo. Departamento')

	error = fields.Char('Error')
	error_json = fields.Char('Error Json', compute="get_error_json")
	
	estudiante_id = fields.Many2one('estudiante.diaria','Padre')

	@api.one
	@api.depends('error')
	def get_error_json(self):
		if self.error:
			elem = self.error.split("\n")
			cont_f = []
			for i in elem:
				if i != '':
					cont_f.append(i)
			info = {'title': 'Errores','content':[cont_f]}
			self.error_json = json.dumps(info)
		else:
			self.error_json = False

