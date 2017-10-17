# -*- coding: utf-8 -*-
# This file is part of the account_invoice_ar module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['Pos', 'PosSequence']


class Pos(ModelSQL, ModelView):
    'Point of Sale'
    __name__ = 'account.pos'

    company = fields.Many2One('company.company', 'Company', required=True)
    number = fields.Integer('Punto de Venta AFIP', required=True,
        help=u'Prefijo de emisión habilitado en AFIP')
    pos_sequences = fields.One2Many('account.pos.sequence', 'pos',
        'Point of Sale', context={'company': Eval('company', -1)},
        depends=['company'])
    pos_type = fields.Selection([
        ('manual', u'Manual'),
        ('electronic', u'Electronic'),
        ('fiscal_printer', u'Fiscal Printer'),
        ], 'Pos Type', required=True)
    pos_type_string = pos_type.translated('pos_type')
    pyafipws_electronic_invoice_service = fields.Selection([
        ('', ''),
        ('wsfe', u'Mercado interno -sin detalle- RG2485 (WSFEv1)'),
        #('wsmtxca', u'Mercado interno -con detalle- RG2904 (WSMTXCA)'),
        ('wsbfe', u'Bono Fiscal -con detalle- RG2557 (WSMTXCA)'),
        ('wsfex', u'Exportación -con detalle- RG2758 (WSFEXv1)'),
        ], u'AFIP Web Service', depends=['pos_type'], states={
            'invisible': Eval('pos_type') != 'electronic',
            'required': Eval('pos_type') == 'electronic',
            },
        help=u'Habilita la facturación electrónica por webservices AFIP')

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_pos_type():
        return 'manual'

    def get_rec_name(self, name):
        if self.pos_type and self.number:
            return '[%s] %s' % (str(self.number), self.pos_type_string)

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('pos_type',) + tuple(clause[1:])]


class PosSequence(ModelSQL, ModelView):
    'Point of Sale Sequences'
    __name__ = 'account.pos.sequence'

    pos = fields.Many2One('account.pos', 'Point of Sale',
        ondelete='CASCADE', select=True, required=True)
    invoice_type = fields.Selection([
        ('', ''),
        ('1', u'01-Factura A'),
        ('2', u'02-Nota de Débito A'),
        ('3', u'03-Nota de Crédito A'),
        ('4', u'04-Recibos A'),
        ('5', u'05-Nota de Venta al Contado A'),
        ('6', u'06-Factura B'),
        ('7', u'07-Nota de Débito B'),
        ('8', u'08-Nota de Crédito B'),
        ('9', u'09-Recibos B'),
        ('10', u'10-Notas de Venta al Contado B'),
        ('11', u'11-Factura C'),
        ('12', u'12-Nota de Débito C'),
        ('13', u'13-Nota de Crédito C'),
        ('15', u'15-Recibo C'),
        ('19', u'19-Factura E'),
        ('20', u'20-Nota de Débito E'),
        ('21', u'21-Nota de Crédito E'),
        ], 'Tipo Comprobante AFIP', select=True, required=True,
        help='Tipo de Comprobante AFIP')
    invoice_type_string = invoice_type.translated('invoice_type')
    invoice_sequence = fields.Property(fields.Many2One('ir.sequence',
        'Sequence', required=True,
        domain=[
            ('code', '=', 'account.invoice'),
            ['OR',
                ('company', '=', Eval('context', {}).get('company', -1)),
                ('company', '=', None),
                ],
            ],
        context={'code': 'account.invoice'}))

    def get_rec_name(self, name):
        return self.invoice_type_string[3:]
