odoo.define('web.ac_cobranza_diaria_it', function (require) {
"use strict";

var core = require('web.core');
var form_common = require('web.form_common');
var formats = require('web.formats');
var Model = require('web.Model');

var QWeb = core.qweb;
var _t = core._t;

var ShowErrorRecaudacion = form_common.AbstractField.extend({
    render_value: function() {
        var self = this;
        var info = JSON.parse(this.get('value'));

        if (info !== false) {
            this.$el.html(QWeb.render('ShowRecaudacionInfo', {
                'content': info.content, 
                'title': info.title
            }));

            _.each(this.$('.js_recaudacion_info'), function(k, v){
                var options = {
                    'content': QWeb.render('RecaudacionPopOver', {
                            'content': info.content[v],
                            }),
                    'html': true,
                    'placement': 'left',
                    'title': _t('Error de Recaudación'),
                    'trigger': 'focus',
                    'delay': { "show": 0, "hide": 100 },
                };
                $(k).popover(options);
                $(k).on('shown.bs.popover', function(event){                    
                });
            });
        }
        else {
            this.$el.html('');
        }
    },
});

core.form_widget_registry.add('recaudacion_error', ShowErrorRecaudacion);






var core = require('web.core');
var formats = require('web.formats');
var pyeval = require('web.pyeval');
var ListView = require('web.ListView');
var Column = ListView.Column;

var list_widget_registry = core.list_widget_registry;

var Recaudacion_error_tree = Column.extend({
    _format: function (row_data, options) {

        var self = this;
        var info = JSON.parse(row_data[this.id].value);
        var temp = ""
        if (info !== false) {
            temp = QWeb.render('ShowRecaudacionInfo', {
                'content': info.content,
                'render': QWeb.render('RecaudacionPopOver', {
                            'content': info.content[0],
                            'title': info.title,
                            }),
                'title': info.title,
            });

                var options = {
                    'content': QWeb.render('RecaudacionPopOver', {
                            'content': info.content[0],
                            }),
                    'html': true,
                    'placement': 'left',
                    'title': _t('Error de Recaudación'),
                    'trigger': 'focus',
                    'delay': { "show": 0, "hide": 100 },
                };
            
            return temp
        };
        return temp;
        
    }
});

list_widget_registry.add('field.recaudacion_error_tree', Recaudacion_error_tree);



}); 








