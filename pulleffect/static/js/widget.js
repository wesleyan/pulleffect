(function() {
    var PullEffect = {};

    PullEffect.Types = {
        'messages': {
            configurable: false,
            handler: function () {
                
            }
        },
        'specialEvents': {
            configurable: true,
            templateSelector: '#special-events-widget',
            handler: function(model) {
                var self = this;
                $.getJSON('http://ims-dev.wesleyan.edu:8080/api/events?minutes=180')
                    .success(function(data) {
                        //htmlspecialchars_decode can be added from Jack's code
                        model.view.renderContent({events: data}, self.templateSelector);
                    })
                    .error(function(err) {
                        console.log(err); //or whatever
                    });
            }
        },
        'calendar': {
            configurable: true,
            templateSelector: '#calendar-widget',
            handler: function (model) {
                var self = this;
                //fetch calendar from somewhere and then:
                var data = []; //TEMPORARY
                    model.view.renderContent({events: data}, self.templateSelector);
            }
        }
    };

    $(document).ready(function() {
        $('nav li button').tooltip();
        PullEffect.Widgets = new Widgets;

        $('button[draggable=true]').on({
            dragstart: function() {
                $(this).css('opacity', '0.5');
            },
            dragleave: function() {
                $(this).removeClass('over');
            },
            dragenter: function() {
                $(this).addClass('over');
            },
            dragend: function() {
                $(this).css('opacity', '1');

                PullEffect.Widgets.create({
                    type: $(this).attr('data-type')
                });
            }
        });
    });

    jQuery.event.props.push('dataTransfer');

    gridster = $(".gridster ul").gridster({
        widget_base_dimensions: [100, 100],
        widget_margins: [5, 5],
        helper: 'clone',
        avoid_overlapped_widgets: true,
        resize: {
            enabled: true,
            stop: function() {
                PullEffect.Widgets.save();
            }
        },
        serialize_params: function($w, wgd) {
            //the function to edit to change the way gridster serializes the widgets
            //widget name etc can be added here
            return _.extend(wgd, {
                time: parseInt($w.attr('data-time')), //this should be a unique millisecond timestamp
                type: $w.attr('data-type')
            });
        },
        draggable: {
            handle: 'header',
            stop: function() {
                PullEffect.Widgets.save();
            }
        }
    }).data('gridster');

    var Widget = Backbone.Model.extend({
        initialize: function() {
            this.typeObject = PullEffect.Types[this.get('type')];
            if(_.isUndefined(this.typeObject)) {
                //if no such widget is registered in the available widgets
                this.destroy();
                return; 
            }

            this.set('time', (new Date()).getTime());
            this.view = new WidgetView({
                model: this
            });
            this.fetchContent();
        },
        fetchContent: function() {
            var self = this;
            //fetch data and update the model

            //some ajax stuff
            
            this.typeObject.handler(this);
        }
    });

    var Widgets = Backbone.Collection.extend({
        model: Widget,
        localStorage: new Backbone.LocalStorage("widgets"),
        initialize: function() {
            gridster.remove_all_widgets();
            this.fetch();
        },
        save: function() {
            gridster.serialize().forEach(function(w) {
                var model = PullEffect.Widgets.findWhere({
                    time: w.time
                });
                model.save({
                    col: w.col,
                    row: w.row,
                    size_x: w.size_x,
                    size_y: w.size_y
                });
            });
        }
    });

    var WidgetView = Backbone.View.extend({
        el: $('.page-wrap'),
        templateSkeleton: _.template($('#generic-widget').html()),
        events: function() {
            var e = {};
            this.selector = "li[data-time='" + this.model.get('time') + "']";
            e["click " + this.selector + " .close"] = 'close';
            e["click " + this.selector + " .config"] = 'config';
            e["dblclick"] = 'resizeToggle'; //this can be changed later
            return e;
        },
        close: function(e) {
            //find the widget in the DOM
            var $toRemove = $(e.target).parent().parent();
            $toRemove.find('.close').unbind();
            $toRemove.hide(); //hiding first so that users don't feel the delay

            var model = PullEffect.Widgets.findWhere({
                time: parseInt($toRemove.attr('data-time'))
            });

            if (!_.isUndefined(model)) { //if multiple events have been delegated
                //remove the widget from the collection
                model.destroy();
                //remove the widget from the DOM
                gridster.remove_widget($toRemove);
            }
        },
        config: function(e) {
            console.log('config ' + this.model.get('type'));
            //the widget should have some configurations specific to itself if it's said to be configurable.
                //check the widget model
                //get the widget configuration options and current configuration
                //render a view with the configuration in #config-modal

                //show the modal window    
                $('.modal').modal('hide');
                $('#config-modal').modal('show')
        },
        resizeToggle: function(e) {
            //$(e.target) may be needed in the future
            this.resizable = !this.resizable;
            if (this.resizable === true) {
                $('.gs-resize-handle').show();
            } else {
                $('.gs-resize-handle').hide();
            }
        },
        initialize: function() {
            this.resizable = false;
            this.renderSkeleton();
        },
        renderSkeleton: function() {
            var m = this.model.attributes;
            var c = this.model.typeObject.configurable;
            var $toAdd = $(this.templateSkeleton({
                widget: m,
                configurable: c
            }));

            if (_.isUndefined(m.size_x) || _.isUndefined(m.size_y) || _.isUndefined(m.col) || _.isUndefined(m.row)) {
                gridster.add_widget($toAdd, 4, 4);
            } else {
                gridster.add_widget($toAdd, m.size_x, m.size_y, m.col, m.row);
            }
        },
        renderContent: function(data, templateSelector) {
            var rendered = _.template($(templateSelector).html())(data);
            $(this.selector).find('section').html(rendered);
        }
    });
})();