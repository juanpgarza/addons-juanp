from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = ["product.template"]    
    _name = 'product.template'

    imagen_producto_ids = fields.Many2many('ir.attachment', string="Adjunto",
                                         help='Adjuntar archivos', copy=False)

    @api.multi 
    def write(self, vals):
        # raise ValidationError('entro')
        res = super(ProductTemplate,self).write(vals)
        
        if 'imagen_producto_ids' in vals.keys():
            
            # borro todas las imagenes del producto
            self.env['product.image'].search([('product_tmpl_id','=',self.id)]).unlink()

            attach_ids = vals.get('imagen_producto_ids')[0][2]

            # import pdb; pdb.set_trace()
            
            for attach_id in attach_ids:
                
                attach = self.env['ir.attachment'].browse(attach_id)
                
                vals1 = {'name': attach.name, 'product_tmpl_id': self.id, 'image': attach.datas}
                self.env['product.image'].create(vals1)
            
        return res