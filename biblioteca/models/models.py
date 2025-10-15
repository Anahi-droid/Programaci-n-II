# -*- coding: utf-8 -*-
from odoo import models, fields, api

class biblioteca(models.Model):
    _name = 'biblioteca.libro'
    _description = 'biblioteca.biblioteca'
    _rec_name = 'lastname'

    firstname = fields.Char(sritng='Nombre Libro')  # NO MODIFICADO
    author = fields.Many2one('biblioteca.autor', string='Autor Libro')
    value = fields.Integer(string='Numero ejemplares')
    value2 = fields.Float(compute="_value_pc", store=True, string="Costo")
    description = fields.Text(string='Descripcion libro')

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100


class BibliotecaAutor(models.Model):
    _name= 'biblioteca.autor'
    _description = 'biblioteca.autor'
    _rec_name= 'firstname'

    firstname = fields.Char()
    lastname = fields.Char()

    @api.depends('firstname', 'lastname')
    def _compute_display_name(self):
        for record in self:
            record.display_name= f"{record.firstname}{record.lastname}"


class BibliotecaUsuario(models.Model):
    _name = 'biblioteca.usuario'
    _description = 'Usuarios de la biblioteca'

    nombre = fields.Char(string='Nombre completo')
    cedula = fields.Char(string='Cédula')
    email = fields.Char(string='Correo electrónico')


class BibliotecaPersonal(models.Model):
    _name = 'biblioteca.personal'
    _description = 'Personal de la biblioteca'

    nombre = fields.Char(string='Nombre completo')
    cargo = fields.Char(string='Cargo')


class BibliotecaPrestamo(models.Model):
    _name = 'biblioteca.prestamo'
    _description = 'Préstamos de libros'

    libro_id = fields.Many2one('biblioteca.libro', string='Libro')
    usuario_id = fields.Many2one('biblioteca.usuario', string='Usuario')
    fecha_prestamo = fields.Date(string='Fecha de préstamo')
    fecha_devolucion = fields.Date(string='Fecha de devolución')



