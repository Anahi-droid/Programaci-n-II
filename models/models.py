# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import requests


class BibliotecaLibro(models.Model):
    _name = 'biblioteca.libro'
    _description = 'biblioteca.libro'
    _rec_name = 'codigo_libro'

    codigo_libro = fields.Char(string='Código del Libro')
    firstname = fields.Char(string='Título del Libro')
    author = fields.Many2one('biblioteca.autor', string='Nombre del Autor')
    publicacion = fields.Char(string='Año de Publicación')
    ejemplares = fields.Integer(string='Número de Ejemplares')
    costo = fields.Char(string='Precio')
    isbn = fields.Char(string='ISBN')
    categoria = fields.Char(string='Categoría')
    description = fields.Text(string='Descripción del Libro')

    def importar_desde_openlibrary(self):
        for record in self:
            if not record.isbn:
                raise UserError("Debe ingresar un ISBN para buscar.")

            url = f"https://openlibrary.org/isbn/{record.isbn}.json"
            response = requests.get(url)

            if response.status_code != 200:
                raise UserError("No se encontró un libro con ese ISBN.")

            data = response.json()

            # Título y año de publicación
            record.firstname = data.get('title') or record.firstname
            record.publicacion = data.get('publish_date') or record.publicacion

            # Autor
            if data.get('authors'):
                autor_key = data['authors'][0].get('key', '').replace('/authors/', '')
                try:
                    autor_info = requests.get(f"https://openlibrary.org/authors/{autor_key}.json").json()
                    nombre_completo = autor_info.get('name', autor_key)
                except:
                    nombre_completo = autor_key

                # Separar firstname y lastname
                partes = nombre_completo.split()
                firstname = " ".join(partes[:-1]) if len(partes) > 1 else nombre_completo
                lastname = partes[-1] if len(partes) > 1 else ""

                # Buscar o crear autor
                autor_obj = self.env['biblioteca.autor'].search([
                    ('firstname', '=', firstname),
                    ('lastname', '=', lastname)
                ], limit=1)

                if not autor_obj:
                    autor_obj = self.env['biblioteca.autor'].create({
                        'firstname': firstname,
                        'lastname': lastname
                    })

                record.author = autor_obj.id

            # Descripción
            desc = data.get('description')
            if isinstance(desc, dict):
                desc = desc.get('value')

            record.description = desc or record.description or "Sin descripción"
            record.categoria = record.categoria or "Sin categoría"
            record.costo = record.costo or "0.00"
            


class BibliotecaAutor(models.Model):
    _name = 'biblioteca.autor'
    _description = 'Registro de autores'
    _rec_name = 'firstname'

    firstname = fields.Char(string='Nombres', required=True)
    lastname = fields.Char(string='Apellidos')
    nacimiento = fields.Date(string='Fecha de Nacimiento')
    libros = fields.Many2many(
        'biblioteca.libro',
        'libros_autores_rel',
        column1='autor_id',
        column2='libro_id',
        string='Libros Publicados'
    )

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.firstname or ''} {record.lastname or ''}".strip()
            result.append((record.id, name))
        return result



class BibliotecaPrestamo(models.Model):
    _name = 'biblioteca.prestamo'
    _description = 'Registro de préstamos'
    
    usuario_id = fields.Many2one('biblioteca.usuarios', string='Usuario')
    name = fields.Char(string='Préstamo', required=True)
    libro_id = fields.Many2one('biblioteca.libro', string='Libro')
    fecha_prestamo = fields.Datetime(default=datetime.now())
    fecha_devolucion = fields.Datetime(string='Fecha de Devolución')
    fecha_maxima = fields.Datetime(compute='_compute_fecha_devolucion')
    usuario_encargado = fields.Many2one('res.users', string='Encargado',default = lambda self: self.env.uid)
    estado = fields.Selection([
        ('p', 'Prestado'),
        ('d', 'Devuelto'),
        ('r', 'Retrasado'),
        ('m', 'Multa')
    ], string='Estado', default='p')

    
    @api.depends('fecha_maxima' , 'fecha_prestamo')
    def _compute_fecha_devolucion(self):
        for record in self:
            record.fecha_maxima = record.fecha_prestamo + timedelta(days=2)
            
    def write(self, vals):
        seq = self.env.ref('biblioteca.sequence_codigo_prestamos').next_by_code('biblioteca.prestamo')
        vals['name'] = seq 
        return super(BibliotecaPrestamo, self).write(vals)

    def generar_prestamo(self):
        print("Generando Préstamo")
        self.write({'estado': 'p'})


class BibliotecaMulta(models.Model):
    _name = 'biblioteca.multa'
    _description = 'Registro de multas'
    _rec_name = 'name_multa'
    
    name_multa = fields.Char(string='Código de la Multa')
    multa = multa = fields.Float(string='Multa', default=0.0)
    valor_multa = fields.Float(string='Valor de la Multa')
    fecha_multa = fields.Date(string='Fecha de la Multa')
    prestamo = fields.Many2one('biblioteca.prestamo', string='Préstamo')
    multa_boleana = fields.Boolean(string='Tiene Multa', default=False)

class BibliotecaUsuarios(models.Model):
    _name = 'biblioteca.usuarios'
    _description = 'Registro de usuarios'
    _rec_name = 'firstname'
    

    firstname = fields.Char(string='Nombres', required=True)
    lastname = fields.Char(string='Apellidos', required=True)
    identificacion = fields.Char(string='Identificación', required=True)
    telefono = fields.Char(string='Teléfono')
    email = fields.Char(string='Correo Electrónico')
    direccion = fields.Text(string='Dirección')
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento')
    prestamos = fields.One2many('biblioteca.prestamo', 'usuario_id', string='Préstamos')


    @api.constrains('identificacion')
    def _check_identificacion(self):
        for record in self:
            cedula = record.identificacion
            if not cedula:
                raise ValidationError("Debe ingresar una cédula antes de guardar el registro.")
            if not cedula.isdigit():
                raise ValidationError("La cédula solo debe contener números.")
            if len(cedula) != 10:
                raise ValidationError("La cédula debe tener exactamente 10 dígitos.")





