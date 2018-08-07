# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
import base64
import sys
from odoo.exceptions import UserError
import pprint
from odoo.exceptions import ValidationError
import csv
import pyodbc
from datetime import datetime, timedelta

class ac_update_log(models.Model):
    _name = 'ac.update.log'
    name = fields.Char('Nombre')
    date = fields.Datetime('Fecha de actualizacion')
    registros = fields.Char('registros', compute='cal_registros')
    msj = fields.Char('Mensaje')
    situation = fields.Boolean(u'Situación')
    # type = fields.Selection([('estudiante','Estudiante'),('recaudacion_diaria','Recaudacion Diaria')],string="Tipo")

    update_log_ups = fields.One2many('ac.update.log.up', 'ac_update_log_id', 'Actualizados')
    update_log_downs = fields.One2many('ac.update.log.down', 'ac_update_log_id', 'Errores')

    def init(self):
        self._cr.execute("""CREATE OR REPLACE FUNCTION insertar_errores_sincronizar()
                        RETURNS VOID  as 
                        $BODY$
                        BEGIN
                            COPY ac_update_log_down(nro_doc,nombres,ape_pat,codigo,pais_nac,direccion,state,nro_doc_apo,nombres_apo,ape_pat_apo,ac_update_log_id) FROM '""" +self.path_dowload_csv()[2] + """' with delimiter ',' CSV;                   
                                                
                        END;
                        $BODY$
                        LANGUAGE plpgsql;""")

        self._cr.execute("""CREATE OR REPLACE FUNCTION sincronizar_apoderados()
                        RETURNS VOID  as 
                        $BODY$
                        BEGIN
                        
                            DELETE FROM temp_apoderado;
                            
                            COPY temp_apoderado(table_id,nro_dni,nombres,apellido_pat,apellido_mat,email,apo_dir,pais_nac,departamento_direccion,provincia_direccion,distrito_direccion) FROM '""" +self.path_dowload_csv()[1] + """' with delimiter ',' CSV;
                            update res_partner set name=concat(a.nombres,', ',a.apellido_pat,' ',a.apellido_mat),display_name=concat(a.nombres,', ',a.apellido_pat,' ',a.apellido_mat),
                                                                         nro_documento=a.nro_dni,email=a.email,street=a.apo_dir
                                                from temp_apoderado  as a  where a.table_id = res_partner.table_apoderado_id;
                                                
                            insert into res_partner(name,company_id,active,display_name,type,type_document_partner_it,nro_documento,apoderado,notify_email,invoice_warn,sale_warn,picking_warn,purchase_warn,table_apoderado_id,street,email)
                                        select concat(a.nombres,', ',a.apellido_pat,' ',a.apellido_mat) as name,1 as company_id,True as active,concat(a.nombres,', ',a.apellido_pat,' ',a.apellido_mat) as display_name,'contact' as type,
                                               2 as type_document_partner_it,a.nro_dni as nro_documento,True as apoderado,'no-always' as notify_email,'no-message' as invoice_warn,'no-message' as sale_warn,'no-message' as picking_warn,
                                               'no-message' as purchase_warn,a.table_id as table_apoderado_id,a.apo_dir as street,a.email as email
                                        from temp_apoderado a
                                            left join res_partner b on a.table_id = b.table_apoderado_id
                                            where b.id is null;

                            update res_partner set district_id=d.id,province_id=p.id,state_id = de.id
                                                from temp_apoderado  as a,
                                                     res_country_state  as d,
                                                     res_country_state  as p,
                                                     res_country_state  as de
                                                where a.table_id = res_partner.table_apoderado_id  and d.province_id=p.id and p.state_id=de.id and a.distrito_direccion=upper(d.name) and a.provincia_direccion=upper(p.name) and a.departamento_direccion=upper(de.name);
                            
                            update res_partner set country_nac_id = b.id
                                                from temp_apoderado  as a,
						                        res_country   as b
                                                where a.table_id = res_partner.table_apoderado_id and a.pais_nac=upper(b.name);
                                                
                                                
                        END;
                        $BODY$
                        LANGUAGE plpgsql;""")

        self._cr.execute("""CREATE OR REPLACE FUNCTION sincronizar_estudiantes()
                        RETURNS VOID  as 
                        $BODY$
                        BEGIN
                        
                            DELETE FROM temp_student;
                            
                            COPY temp_student(table_id,codigo,nro_dni,nombres,apellido_pat,apellido_mat,cod_familiar,cod_pago,grado_id,seccion_id,etapa_id,direccion,estado_estudiante,table_apoderado_id,pais_nac,departamento_direccion,provincia_direccion,distrito_direccion,fec_nac) FROM '""" +self.path_dowload_csv()[0] + """' with delimiter ',' CSV;
                            
                            update temp_student set type_documento_id = 2 where upper(pais_nac) = 'PERU';
                            
                            update res_partner set name=concat(a.nombres,', ',a.apellido_pat,' ',a.apellido_mat),active=a.estado_estudiante,display_name=concat(a.nombres,', ',a.apellido_pat,' ',a.apellido_mat),
                                                                         nro_documento=a.nro_dni,code_student=a.codigo,code_family=a.cod_familiar,code_payment=a.cod_pago,grado_id=a.grado_id,seccion_id=a.seccion_id,etapa_id=a.etapa_id,street=a.direccion,temp_apoderado_id = a.table_apoderado_id,date_nac=a.fec_nac,type_document_partner_it=a.type_documento_id
                                                from temp_student  as a  where a.table_id = res_partner.table_student_id;
                                                
                            insert into res_partner(name,company_id,active,display_name,type,type_document_partner_it,nro_documento,code_student,code_family,code_payment,student,notify_email,invoice_warn,sale_warn,picking_warn,purchase_warn,table_student_id,grado_id,seccion_id,etapa_id,street,table_apoderado_id,date_nac)
                                        select concat(a.nombres,', ',a.apellido_pat,' ',a.apellido_mat) as name,1 as company_id,a.estado_estudiante as active,concat(a.nombres,', ',a.apellido_pat,' ',a.apellido_mat) as display_name,'contact' as type,
                                               a.type_documento_id as type_document_partner_it,a.nro_dni as nro_documento,a.codigo as code_student,a.cod_familiar as code_family,a.cod_pago as code_payment,True as student,'no-always' as notify_email,'no-message' as invoice_warn,
                                               'no-message' as sale_warn,'no-message' as picking_warn,'no-message' as purchase_warn,a.table_id as table_student_id,a.grado_id as grado_id,a.seccion_id as seccion_id,a.etapa_id as etapa_id,a.direccion as street,a.table_apoderado_id as table_apoderado_id,a.fec_nac as date_nac
                                        from temp_student a
                                            left join res_partner b on a.table_id = b.table_student_id
                                            where b.id is null;

                        update res_partner set apoderado_id = apoderado.id
                        from res_partner as apoderado where res_partner.temp_apoderado_id = apoderado.table_apoderado_id;

                        update res_partner set district_id=d.id,province_id=p.id,state_id = de.id
                                                from temp_student as a,
                                                     res_country_state  as d,
                                                     res_country_state  as p,
                                                     res_country_state  as de
                                                where a.table_id = res_partner.table_student_id and d.province_id=p.id and p.state_id=de.id and a.distrito_direccion=upper(d.name) and a.provincia_direccion=upper(p.name) and a.departamento_direccion=upper(de.name);
                                                
                        update res_partner set country_nac_id = b.id
                                                from temp_student  as a,
						                        res_country   as b
                                                where a.table_id = res_partner.table_student_id and a.pais_nac=upper(b.name);

                                    
                                END;
                                $BODY$
                                LANGUAGE plpgsql;""")

    @api.one
    def cal_registros(self):
        if not self.situation:
            log_down = self.env['ac.update.log.down']
            log_down_error = log_down.search_count([('ac_update_log_id', '=', self.id)])
            info = 'Error(' + str(log_down_error) + ')'
        else:
            info = ""

        self.registros = info

    def config_parameter(self):
        parameters = self.env['ac.parameters'].search([], limit=1)
        if not parameters:
            parameters = self.env['ac.parameters'].create({'name': 'Parametros', 'path_csv': "C:\\Users\\Public\\"})
            # raise ValidationError("Falta ingresar parametros para la coneccion a las base de datos")
        return parameters

    def path_dowload_csv(self):
        directory_path = self.config_parameter().path_csv or "C:\\Users\\Public\\"
        directory_path_student = directory_path + 'list_student.csv'
        directory_path_apoderado = directory_path + 'list_apoderado.csv'
        directory_path_errores = directory_path + 'list_errores.csv'
        return [directory_path_student, directory_path_apoderado, directory_path_errores]

    def text_conection(self):
        sys.setdefaultencoding('iso-8859-1')
        parameters = self.config_parameter()
        server, database, username, password = parameters.server, parameters.database, parameters.username, parameters.password
        # server,database,username,password = 'dev04\sqlexpress','TestEdusoft','admin','programar'
        text_conection = 'DRIVER={ODBC Driver 13 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password

        return text_conection

    @api.one
    def sincronizar_with_server(self):
        # try:
            self.search_errores()
            self.update_dis_depto_pais()
            self.sincronizar_with_server_apoderado()
            self.sincronizar_with_server_student()
            # self.date = datetime.today() - timedelta(hours=5)
            self.date = datetime.today()
            if not self.update_log_downs:
                self.msj = 'TODO FUE UN EXITO'
                self.situation = True
            else:
                self.msj = 'HUBO ERRORES'
                self.situation = False

        # except Exception as e:
        #     self.msj = 'HUBO ERRORES(' + str(e) + ')'

    @api.one
    def search_errores(self):
        self.env.cr.execute('DELETE FROM ac_update_log_down where ac_update_log_id = ' + str(self.id))
        query = """select nro_doc,nombres,ape_pat,codigo,pais_nac_estudiante,direccion,'Alumno: codigo EDUSOFTNET repetido' as tipo,apo_nro_dni,apo_nombres,apo_ape_pat,""" + str(self.id) + """ as update_id from TablaEdusoft_test
                       where codigo in(SELECT codigo FROM TablaEdusoft_test group by codigo having COUNT(codigo) > 1)
                       union
                       select nro_doc,nombres,ape_pat,codigo,pais_nac_estudiante,direccion,'Alumno: codigo EDUSOFTNET repetido' as tipo,apo_nro_dni,apo_nombres,apo_ape_pat,""" + str(self.id) + """ as update_id from TablaEdusoft_test
                       where nro_doc in(SELECT nro_doc FROM TablaEdusoft_test group by nro_doc having COUNT(nro_doc) > 1)
                       union
                       select nro_doc,nombres,ape_pat,codigo,pais_nac_estudiante,direccion,'Alumno: Falta informacion necesaria' as tipo,apo_nro_dni,apo_nombres,apo_ape_pat,""" + str(self.id) + """ as update_id from TablaEdusoft_test
                       where datalength (RTRIM(isnull (nro_doc,'')))=0 or datalength (RTRIM(isnull (nombres,'')))=0 or datalength (RTRIM(isnull (ape_pat,'')))=0 or datalength (RTRIM(isnull (codigo,'')))=0 or datalength (RTRIM(isnull (pais_nac_estudiante,'')))=0 or datalength (RTRIM(isnull (direccion,'')))=0 or datalength (RTRIM(isnull (apo_nro_dni,'')))=0 or datalength (RTRIM(isnull (apo_nombres,'')))=0  or datalength (RTRIM(isnull (apo_ape_pat,'')))=0
                       union
                       select apo_nro_dni as nro_doc,apo_nombres as nombres,apo_ape_pat as ape_pat,'' as codigo,'' as pais_nac_estudiante,apo_dir as direccion,'Apoderado: nro documento repetido' as tipo,apo_nro_dni,apo_nombres,apo_ape_pat,""" + str(self.id) + """ as update_id from  TablaEdusoft_test
                       where apo_nro_dni in(SELECT apo_nro_dni FROM TablaEdusoft_test group by apo_nro_dni having COUNT(apo_nro_dni) > 1)
                   """
        query_funcion = "select * from insertar_errores_sincronizar()"
        self.create_file_csv(self.path_dowload_csv()[2], query, query_funcion)

    @api.one
    def sincronizar_with_server_student(self):
        self.env.cr.execute("select distinct(codigo) from ac_update_log_down where codigo is not null and ac_update_log_id= " + str(self.id))
        estudiantes_error = self.env.cr.dictfetchall()
        estudiantes_codigo = "','".join(list['codigo'] for list in estudiantes_error)

        query = """SELECT codigo,codigo,nro_doc,nombres,ape_pat,ape_mat,cod_familia,cod_pago,grado_id,seccion_id,etapa_id,direccion,case when estado='activo' then 1 else 0 end,apo_nro_dni,UPPER(pais_nac_estudiante),UPPER(departamento_dir_estudiante),UPPER(provincia_dir_estudiante),UPPER(distrito_dir_estudiante),fec_nac_estudiante 
        FROM TablaEdusoft_test where codigo not in('""" + estudiantes_codigo + """')"""
        query_funcion = "select * from sincronizar_estudiantes()"
        self.create_file_csv(self.path_dowload_csv()[0], query, query_funcion)

    @api.one
    def sincronizar_with_server_apoderado(self):
        self.env.cr.execute("select distinct(nro_doc) from ac_update_log_down where codigo is null and ac_update_log_id= " + str(self.id))
        apoderado_error = self.env.cr.dictfetchall()
        apoderado_codigo = "','".join(list['nro_doc'] for list in apoderado_error)

        query = """SELECT apo_nro_dni, apo_nro_dni, apo_nombres, apo_ape_pat, apo_ape_mat, apo_email, apo_dir,UPPER(pais_nac_apoderado),UPPER(departamento_dir_apoderado),UPPER(provincia_dir_apoderado),UPPER(distrito_dir_apoderado) 
        FROM TablaEdusoft_test where apo_nro_dni is not null and codigo not in('""" + apoderado_codigo + """')"""
        query_funcion = "select * from sincronizar_apoderados()"
        self.create_file_csv(self.path_dowload_csv()[1], query, query_funcion)

    def create_file_csv(self, path_dowload_csv, query, query_funcion):
        sys.setdefaultencoding('iso-8859-1')
        direction_archivo = path_dowload_csv
        print self.text_conection(),query
        cursor = pyodbc.connect(self.text_conection()).cursor()
        cursor.execute(query)
        list_student = cursor.fetchall()
        file_csv = open(direction_archivo, "w")
        out = csv.writer(file_csv, lineterminator='\n')
        # out = csv.writer(open(direction_archivo, "w"), quoting=csv.QUOTE_NONNUMERIC,lineterminator = '\n')
        out.writerows(list_student)
        file_csv.close()
        self.env.cr.execute(query_funcion)

    @api.one
    def update_dis_depto_pais(self):
        # PARA PAISES
        sys.setdefaultencoding('iso-8859-1')
        self.env.cr.execute("select distinct(name) from res_country where name not like '%(%'")
        paises_actuales = self.env.cr.dictfetchall()
        nombre_paises = "','".join(list['name'] for list in paises_actuales)

        cursor = pyodbc.connect(self.text_conection()).cursor()
        cursor.execute("""SELECT distinct(pais_nac_estudiante)  FROM TablaEdusoft_test where pais_nac_estudiante not in('""" + nombre_paises + """')
                            UNION
                            SELECT distinct(pais_nac_apoderado)  FROM TablaEdusoft_test where pais_nac_apoderado not in('""" + nombre_paises + """')""")
        countries_new = cursor.fetchall()
        for country in countries_new:
            self.env['res.country'].create({'name': country[0]})

        # PARA DEPARTAMENTOS
        cursor = pyodbc.connect(self.text_conection()).cursor()
        self.env.cr.execute("""select distinct upper(concat(a.name,b.name,c.name)) as name
                            from res_country_state a 
                             join res_country_state  b on a.id = b.state_id
                             join res_country_state  c on b.id = c.province_id""")
        ids_estates = self.env.cr.dictfetchall()
        ids_estates = "','".join(list['name'] for list in ids_estates)

        cursor.execute("""select distinct UPPER(departamento_dir_apoderado),UPPER(provincia_dir_apoderado),UPPER(distrito_dir_apoderado)
                        FROM TablaEdusoft_test
                        where UPPER({fn CONCAT(departamento_dir_estudiante,{fn CONCAT(provincia_dir_estudiante,distrito_dir_estudiante)})}) not in('""" + ids_estates + """')
                        UNION 
                        select distinct UPPER(departamento_dir_apoderado),UPPER(provincia_dir_apoderado),UPPER(distrito_dir_apoderado)
                        FROM TablaEdusoft_test
                        where UPPER({fn CONCAT(departamento_dir_apoderado,{fn CONCAT(provincia_dir_apoderado,distrito_dir_apoderado)})}) not in('""" + ids_estates + """')""")
        country_states = cursor.fetchall()
        for country_state in country_states:
            departamento = False
            if country_state[0]:
                departamento = self.env['res.country.state'].search([('name', '=', country_state[0]), ('state_id', '=', False), ('province_id', '=', False)])
                if not departamento:
                    departamento = self.env['res.country.state'].create({'name': country_state[0], 'country_id': 175, 'code': country_state[0][:4]})

            province = False
            if country_state[1]:
                search_province = [('name', '=', country_state[1]), ('province_id', '=', False)]
                if departamento:
                    search_province.append(('state_id', '=', departamento.id))

                province = self.env['res.country.state'].search(search_province)
                if not province:
                    vals = {'name': country_state[1], 'country_id': 175, 'code': country_state[1][:5]}
                    if departamento:
                        vals['state_id'] = departamento.id
                    province = self.env['res.country.state'].create(vals)

            distrite = False
            if country_state[2]:
                search_distrite = [('name', '=', country_state[2])]
                if province:
                    search_distrite.append(('province_id', '=', province.id))
                distrite = self.env['res.country.state'].search(search_distrite)
                if not distrite:
                    vals = {'name': country_state[2], 'country_id': 175, 'code': country_state[2][:6]}
                    if departamento:
                        vals['state_id'] = departamento.id
                    if province:
                        vals['province_id'] = province.id
                    distrite = self.env['res.country.state'].create(vals)
    @api.model
    def automatic_task(self):
        log = self.create()
        log.sincronizar_with_server()

class ac_update_log_up(models.Model):
    _name = 'ac.update.log.up'
    name = fields.Char('Nombre')
    situation = fields.Boolean(u'Situación', default=True)
    ac_update_log_id = fields.Many2one('ac.update.log', 'Log de Actualizacion')

class ac_update_log_down(models.Model):
    _name = 'ac.update.log.down'
    nro_doc = fields.Char('DNI')
    nombres = fields.Char('Estudiante')
    ape_pat = fields.Char('Ape. Paterno')
    codigo = fields.Char(u'Código EDUSOFTNET')
    pais_nac = fields.Char(u'País Nacimiento')
    direccion = fields.Char(u'Dirección')
    state = fields.Char('Estado')
    nombres_apo = fields.Char('Apoderado')
    ape_pat_apo = fields.Char('Ape. Paterno')
    nro_doc_apo = fields.Char('DNI')
    ac_update_log_id = fields.Many2one('ac.update.log', 'Log de Actualizacion')
