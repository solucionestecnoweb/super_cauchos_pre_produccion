# -*- coding: utf-8 -*-


import logging
import base64
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class libro_ventas(models.TransientModel):
    _inherit = 'account.wizard.libro.ventas'

    def conv_div_nac(self,valor,selff):
        selff.invoice_id.currency_id.id
        fecha_contable_doc=selff.invoice_id.date
        monto_factura=selff.invoice_id.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',selff.invoice_id.date)],order='id ASC')
        #raise UserError(_('lista_tasa: %s')%lista_tasa)
        if lista_tasa:
            for det in lista_tasa:
                rate=(det.rate)
        rate=round(rate,3)  # LANTA
        #rate=round(valor_aux,2)  # ODOO SH
        resultado=valor*rate
        return resultado

class libro_ventas(models.TransientModel):
    _inherit = "account.wizard.libro.compras"

    def conv_div_nac(self,valor,selff):
        selff.invoice_id.currency_id.id
        fecha_contable_doc=selff.invoice_id.date
        monto_factura=selff.invoice_id.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',selff.invoice_id.date)],order='id ASC')
        #raise UserError(_('lista_tasa: %s')%lista_tasa)
        if lista_tasa:
            for det in lista_tasa:
                rate=(det.rate)
        rate=round(rate,3)  # LANTA
        #rate=round(valor_aux,2)  # ODOO SH
        resultado=valor*rate
        return resultado

class LibroVentasModelo(models.Model):
    _inherit = "account.wizard.pdf.compras"

    def conv_div(self,valor):
        self.invoice_id.currency_id.id
        fecha_contable_doc=self.invoice_id.date
        monto_factura=self.invoice_id.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',selff.invoice_id.date)],order='id ASC')
        #raise UserError(_('lista_tasa: %s')%lista_tasa)
        if lista_tasa:
            for det in lista_tasa:
                rate=(det.rate)
        rate=round(rate,3)  # LANTA
        #rate=round(valor_aux,2)  # ODOO SH
        resultado=valor*rate
        return resultado


# ************************************  PARA EL REPORTE DE RETENCION IVA  ****************************************
class VatRetentionInvoiceLine(models.Model):
    """This model is for a line invoices withholed."""
    _inherit = 'vat.retention.invoice.line'

    def conv_moneda(self,valor):
        resultado=0
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',self.move_id.date)],order='id ASC')
        if lista_tasa:
            for det in lista_tasa:
                resultado=(det.rate*valor)
        return resultado

    def valida_excento(self,id_tax,id_retention):
        tipo=self.tax_id.aliquot
        valor_excento=0
        cant_reduced=0
        cant_general=0
        cant_additional=0
        resultado=''
        lista_det = self.env['vat.retention.invoice.line'].search([('retention_id','=',self.retention_id.id)])
        for det in lista_det:
            if det.tax_id.amount==0:
                valor_excento=valor_excento+det.amount_untaxed

            if det.tax_id.aliquot=='reduced':
                cant_reduced=cant_reduced+1
            if det.tax_id.aliquot=='general':
                cant_general=cant_general+1
            if det.tax_id.aliquot=='additional':
                cant_additional=cant_additional+1

        if tipo=='general' and cant_general>0:
            resultado=str(self.float_format(self.conv_moneda(valor_excento)))
        if tipo=='reduced' and cant_reduced>0 and cant_general==0:
            resultado=str(self.float_format(self.conv_moneda(valor_excento)))
        if tipo=='additional' and cant_additional>0 and cant_reduced==0 and cant_general==0:
            resultado=str(self.float_format(self.conv_moneda(valor_excento)))

        return str(resultado)

class RetentionVat(models.Model):
    """This is a main model for rentetion vat control."""
    _inherit = 'vat.retention'

    def conv_moneda(self,valor):
        resultado=0
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',self.move_id.date)],order='id ASC')
        if lista_tasa:
            for det in lista_tasa:
                resultado=(det.rate*valor)
        return resultado

# ************************************  PARA EL REPORTE DE RETENCION MUNICIPAL  ****************************************
class MunicipalityTaxLine(models.Model):
    _inherit = 'municipality.tax.line'

    def conv_moneda(self,valor):
        resultado=0
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',self.invoice_id.date)],order='id ASC')
        if lista_tasa:
            for det in lista_tasa:
                resultado=(det.rate*valor)
        return resultado


class MUnicipalityTax(models.Model):
    _inherit = 'municipality.tax'

    def conv_moneda(self,valor):
        resultado=0
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',self.invoice_id.date)],order='id ASC')
        if lista_tasa:
            for det in lista_tasa:
                resultado=(det.rate*valor)
        return resultado

# ************************************  PARA EL REPORTE DE RETENCION ISLR  ****************************************

class VatRetentionInvoiceLine(models.Model):
    """This model is for a line invoices withholed."""
    _inherit = 'isrl.retention.invoice.line'

    def conv_moneda(self,valor):
        resultado=0
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',self.retention_id.move_id.date)],order='id ASC')
        if lista_tasa:
            for det in lista_tasa:
                resultado=(det.rate*valor)
        return resultado

    """def conv_moneda(self,valor):
        resultado=valor
        return resultado"""

class RetentionVat(models.Model):
    """This is a main model for rentetion vat control."""
    _inherit = 'isrl.retention'

    def conv_moneda(self,valor):
        resultado=0
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',self.move_id.date)],order='id ASC')
        if lista_tasa:
            for det in lista_tasa:
                resultado=(det.rate*valor)
        return resultado

    def conv_moneda_inv(self,valor):
        resultado=0
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',self.move_id.date)],order='id ASC')
        if lista_tasa:
            for det in lista_tasa:
                resultado=(valor/det.rate)
        return resultado

    def registro_movimiento_linea_retencion(self,id_movv,consecutivo_asiento):
        #raise UserError(_('ID MOVE = %s')%id_movv)
        name = consecutivo_asiento
        valores = self.total_ret() #self.conv_div_extranjera(self.total_ret()) #self.vat_retentioned #VALIDAR CONDICION
        cero = 0.0
        #raise UserError(_('valores = %s')%valores)
        if self.invoice_id.type=="out_invoice" or self.invoice_id.type=="out_refund" or self.invoice_id.type=="out_receipt":
            cuenta_ret_cliente=self.partner_id.account_isrl_receivable_id.id# cuenta retencion cliente
            cuenta_ret_proveedor=self.partner_id.account_isrl_payable_id.id#cuenta retencion proveedores
            cuenta_clien_cobrar=self.partner_id.property_account_receivable_id.id
            cuenta_prove_pagar = self.partner_id.property_account_payable_id.id
            name_retenido=self.invoice_id.company_id.partner_id.name
            #rate_valor=self.partner_id.vat_retention_rate
        if self.type=="in_invoice" or self.type=="in_refund" or self.type=="in_receipt":
            cuenta_ret_cliente=self.invoice_id.company_id.partner_id.account_isrl_receivable_id.id# cuenta retencion cliente
            cuenta_ret_proveedor=self.invoice_id.company_id.partner_id.account_isrl_payable_id.id#cuenta retencion proveedores
            cuenta_clien_cobrar=self.invoice_id.company_id.partner_id.property_account_receivable_id.id
            cuenta_prove_pagar = self.invoice_id.company_id.partner_id.property_account_payable_id.id
            name_retenido=self.partner_id.name
            #rate_valor=self.company_id.partner_id.vat_retention_rate

        tipo_empresa=self.invoice_id.type
        #raise UserError(_('papa = %s')%tipo_empresa)
        if tipo_empresa=="in_invoice" or tipo_empresa=="in_receipt":#aqui si la empresa es un proveedor
            cuenta_haber=cuenta_ret_proveedor
            cuenta_debe=cuenta_prove_pagar            
            balance_a=cero-valores
            balance_b=valores-cero

        if tipo_empresa=="in_refund":
            cuenta_haber=cuenta_prove_pagar
            cuenta_debe=cuenta_ret_proveedor
            balance_a=cero-valores
            balance_b=valores-cero

        if tipo_empresa=="out_invoice" or tipo_empresa=="out_receipt":# aqui si la empresa es cliente
            cuenta_haber=cuenta_clien_cobrar
            cuenta_debe=cuenta_ret_cliente
            balance_a=valores-cero
            balance_b=cero-valores

        if tipo_empresa=="out_refund":
            cuenta_haber=cuenta_ret_cliente
            cuenta_debe=cuenta_clien_cobrar
            balance_a=valores-cero
            balance_b=cero-valores
        #balances=cero-valores
        balances=balance_a
        valores=self.conv_moneda_inv(valores)
        value = {
             'name': name,
             'ref' : "Retención del %s %% ISLR de la Factura %s" % (name_retenido,self.move_id.name),
             'move_id': int(id_movv),
             'date': self.move_id.date,
             'partner_id': self.partner_id.id,
             'account_id': cuenta_haber,
             #'amount_currency': 0.0,
             #'date_maturity': False,
             'credit': valores,
             'debit': 0.0, # aqi va cero   EL DEBITO CUNDO TIENE VALOR, ES QUE EN ACCOUNT_MOVE TOMA UN VALOR
             'balance':-valores, # signo negativo
             'price_unit':balances,
             'price_subtotal':balances,
             'price_total':balances,

        }
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(value)

        #balances=valores-cero
        balances=balance_b
        value['account_id'] = cuenta_debe
        value['credit'] = 0.0 # aqui va cero
        value['debit'] = valores
        value['balance'] = valores
        value['price_unit'] = balances
        value['price_subtotal'] = balances
        value['price_total'] = balances

        move_line_id2 = move_line_obj.create(value)

# ************************************  PARA EL REPORTE DE TXT DE IVA  ****************************************

class BsoftContratoReport2(models.TransientModel):
    _inherit = 'snc.wizard.retencioniva'

    def conv_moneda(self,valor,rec):
        resultado=0
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',rec.invoice_id.date)],order='id ASC')
        if lista_tasa:
            for det in lista_tasa:
                resultado=(det.rate*valor)
        return resultado

    def tipo_format(self,valor):
        if valor and valor=='in_refund':
            return '03'
        return '01'

    def float_format(self,valor):
        if valor:
            result = '{:,.2f}'.format(valor)
            #_logger.info('Result 1: %s' % result)
            result = result.replace(',','')
            #_logger.info('Result 2: %s' % result)
            return result
        return valor

    def float_format2(self,valor):
        #valor=self.base_tax
        if valor:
            result = '{:,.2f}'.format(valor)
            #result = result.replace(',','*')
            #esult = result.replace('.',',')
            #result = result.replace('*','.')
            result = result.replace(',','')
        else:
            result="0.00"
        return result

    def completar_cero(self,campo,digitos):
        valor=len(campo)
        campo=str(campo)
        nro_ceros=digitos-valor+1
        for i in range(1,nro_ceros,1):
            campo=" "+campo
        return campo

    def formato_periodo(self,valor):
            fecha = str(valor)
            fecha_aux=fecha
            ano=fecha_aux[0:4]
            mes=fecha[5:7]
            dia=fecha[8:10]  
            resultado=ano+mes
            return resultado

    def rif_format(self,aux,aux_type):
        nro_doc=aux
        tipo_doc=aux_type
        nro_doc=nro_doc.replace('V','')
        nro_doc=nro_doc.replace('v','')
        nro_doc=nro_doc.replace('E','')
        nro_doc=nro_doc.replace('e','')
        nro_doc=nro_doc.replace('G','')
        nro_doc=nro_doc.replace('g','')
        nro_doc=nro_doc.replace('J','')
        nro_doc=nro_doc.replace('j','')
        nro_doc=nro_doc.replace('P','')
        nro_doc=nro_doc.replace('p','')
        nro_doc=nro_doc.replace('-','')
        if tipo_doc=="v":
            tipo_doc="V"
        if tipo_doc=="e":
            tipo_doc="E"
        if tipo_doc=="g":
            tipo_doc="G"
        if tipo_doc=="j":
            tipo_doc="J"
        if tipo_doc=="p":
            tipo_doc="P"
        if tipo_doc=="c":
            tipo_doc="C"
        resultado=str(tipo_doc)+str(nro_doc)
        return resultado

    def action_generate_txt(self):
        #raise UserError(_(' id retencion:'))

        ret_cursor = self.env['account.move'].search([('date','>=',self.date_from),('date','<=',self.date_to),('company_id','=',self.env.company.id),('type','in',('in_invoice','in_refund','in_receipt')),('state','=','posted'),],order="date asc")
        if not ret_cursor:
            raise UserError(_(' No hay registros de retenciones para esta compañia'))
        #_logger.info("\n\n\n {} \n\n\n".format(self.rec_cursor))
        #raise UserError(_(' id retencion:%s')%rec_cursor.vat_ret_id.id) 

        self.file_name = 'txt_generacion.txt'
        retiva = self.env['vat.retention']
        retiva = str(retiva.name)

        #ruta="C:/Odoo 13.0e/server/odoo/loca_13/l10n_ve_txt_iva/wizard/txt_generacion.txt" #ruta local
        #ruta="/mnt/extra-addons/l10n_ve_txt_iva/wizard/txt_generacion.txt"
        #ruta="/home/odoo/src/user/LocalizacionV13/l10n_ve_txt_iva/wizard/txt_generacion.txt"
        ruta="/home/odoo/src/txt_generacion.txt" # ruta odoo sh
        #raise UserError(_('mama = %s')%rec.type)

        with open(ruta, "w") as file:

            for ret in ret_cursor:
                if ret.vat_ret_id:
                    if ret.vat_ret_id.state=="posted":
                        if ret.type=="in_invoice":
                            trans='01'
                        if ret.type=="in_refund":
                            trans='03'
                        if ret.type=='in_receipt':
                            trans='02'

                        acum_exemto=0
                        
                        busca_exento = self.env['vat.retention.invoice.line'].search([('retention_id','=',ret.vat_ret_id.id)])
                        for det in busca_exento:
                            if det.tax_id.aliquot=="exempt":
                                acum_exemto=acum_exemto+det.amount_untaxed

                        rec_cursor = self.env['vat.retention.invoice.line'].search([('retention_id','=',ret.vat_ret_id.id)])
                        for rec in rec_cursor:

                            if rec.tax_id.aliquot!="exempt":
                                rif_compania=self.rif_format(rec.invoice_id.company_id.vat,rec.invoice_id.company_id.partner_id.doc_type)
                                file.write(rif_compania + "\t")#1

                                periodo=self.formato_periodo(self.date_to)
                                file.write(periodo + "\t")#2

                                fecha = rec.invoice_id.date
                                fecha = str(fecha)
                                file.write(fecha + "\t")#3

                                file.write("C" + "\t")#4

                                file.write(trans + "\t") #5

                                rif_proveedor= self.rif_format(rec.invoice_id.partner_id.vat,rec.invoice_id.partner_id.doc_type)
                                file.write(rif_proveedor + "\t") #6

                                invoicer_number=str(rec.invoice_id.invoice_number)
                                #invoicer_number=completar_cero(invoicer_number,10)
                                file.write(invoicer_number + "\t") #7

                                invoice_sequence = str(rec.invoice_id.invoice_ctrl_number)
                                #invoice_sequence = completar_cero(invoice_sequence,10)
                                file.write(invoice_sequence + "\t") #8

                                total = str(self.float_format2(self.conv_moneda(rec.amount_vat_ret+rec.amount_untaxed+acum_exemto,rec)))
                                #total = completar_cero(total,12)
                                file.write(total + "\t") #9

                                importe_base = str(self.float_format2(self.conv_moneda(rec.amount_untaxed,rec))) # PREGUNTAR rec.total_base
                                #importe_base = completar_cero(importe_base,12)
                                file.write(importe_base + "\t") #10

                                monto_ret=str(self.float_format2(self.conv_moneda(rec.retention_amount,rec))) # PREGUNTAR
                                #monto_ret = completar_cero(monto_ret,12)
                                file.write(monto_ret + "\t") #11

                                if rec.invoice_id.ref==False:
                                    fact_afec='0'
                                else:
                                    fact_afec = str(rec.invoice_id.ref)
                                #fact_afec = completar_cero(fact_afec,5)
                                file.write(fact_afec + "\t") #12

                                nro_comprobante = str(rec.retention_id.name)
                                file.write(nro_comprobante + "\t") #13

                                #total_exento= str(rec.total_exento)
                                """if rec.tax_id.aliquot=="exempt":
                                    total_exento=rec.amount_untaxed
                                else:
                                    total_exento=0.00"""
                                total_exento=acum_exemto
                                total_exento=str(self.float_format2(self.conv_moneda(total_exento,rec)))
                                file.write(total_exento + "\t")#14

                                porcentage_iva=rec.tax_id.amount
                                porcentage_iva = str(round(porcentage_iva))
                                #porcentage_iva = completar_cero(porcentage_iva,5)
                                file.write(porcentage_iva + "\t") #15 PREGUNTAR"""

                                file.write('0' + "\n") #16



        self.write({'file_data': base64.encodestring(open(ruta, "rb").read()),
                    'file_name': "Retenciones de IVA desde %s hasta %s.txt"%(self.date_from,self.date_to),
                    })

        return self.show_view('Archivo Generado', self._name, 'vat_retention.snc_wizard_retencioniva_form_view', self.id)

#******************************** LIBRO RESUMEN RETENCIONES IVA ************************************************
class WizardReport_1(models.TransientModel): # aqui declaro las variables del wizar que se usaran para el filtro del pdf
    _inherit = 'wizard.resumen.iva'

    def conv_div_nac(self,valor,selff):
        selff.invoice_id.currency_id.id
        fecha_contable_doc=selff.invoice_id.date
        monto_factura=selff.invoice_id.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',selff.invoice_id.date)],order='id ASC')
        #raise UserError(_('lista_tasa: %s')%lista_tasa)
        if lista_tasa:
            for det in lista_tasa:
                rate=(det.rate)
        rate=round(rate,3)  # LANTA
        #rate=round(valor_aux,2)  # ODOO SH
        resultado=valor*rate
        return resultado

class WizardReport_2(models.TransientModel): # aqui declaro las variables del wizar que se usaran para el filtro del pdf
    _inherit = 'wizard.resumen.municipal'

    def conv_div_nac(self,valor,selff):
        selff.invoice_id.currency_id.id
        fecha_contable_doc=selff.invoice_id.date
        monto_factura=selff.invoice_id.amount_total
        valor_aux=0
        #raise UserError(_('moneda compañia: %s')%self.company_id.currency_id.id)
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',selff.invoice_id.date)],order='id ASC')
        #raise UserError(_('lista_tasa: %s')%lista_tasa)
        if lista_tasa:
            for det in lista_tasa:
                rate=(det.rate)
        rate=round(rate,3)  # LANTA
        #rate=round(valor_aux,2)  # ODOO SH
        resultado=valor*rate
        return resultado