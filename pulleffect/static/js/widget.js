(function() {
    var PullEffect = {};

    PullEffect.Types = {
        'roomInfo': {
            title: 'Room Info',
            configurable: false,
            templateSelector: '#room-info-widget',
            handler: function (model) {
                var self = this;
                //fetch room info from somewhere and then:
                var data = []; //TEMPORARY
                    model.view.renderTitle('Room ALB304');
                    model.view.renderContent({events: data}, self.templateSelector);
            }
        },
        'messages': {
            title: 'Messages',
            configurable: false,
            setSeverity: function(message){
                if (message.severity == 3 || message.severity == 4)
                    return "text-warning"
                else if (message.severity == 5)
                    return "text-danger"
                else return ""

            },
            getDeviceIcon: function(message){
                switch (message.device_type){
                    case "mac": return "fa fa-apple"; break;
                    case "pc": return "fa fa-windows"; break;
                    case "printer": return "fa fa-print"; break;
                    case "roomtrol": return "fa fa-flash"; break;
                    default: return  "";
                }
            },
            templateSelector: "#messages-widget",
            handler: function (model) {
                var self = this;
                $.getJSON('/messages/10').success(function(data){
                        model.view.renderContent({messages:data, setSeverity:self.setSeverity, getDeviceIcon:self.getDeviceIcon}, self.templateSelector)
                    }).error(function(err){
                        console.log(err);
                });
            }
        },

        'specialEvents': {
            title: 'Special Events',
            configurable: true,
            templateSelector: '#special-events-widget',
            handler: function(model) {
                var self = this;
                $.getJSON('http://ims-dev.wesleyan.edu:8080/api/events?minutes=3000')
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
            title: 'Calendar',
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
        $('nav li div').tooltip();
        PullEffect.Widgets = new Widgets;

        //USING VANILLA JS FOR EVENTS BECAUSE OF CROSS-BROWSER ISSUES WITH FIREFOX

        /*
        document.addEventListener("drag", function(e) {
        });
        document.addEventListener("dragenter", function(e) {
        });
        document.addEventListener("dragleave", function(e) {
        });
        */
        document.addEventListener("dragstart", function(e) {
            e.dataTransfer.setData('text/plain', null); //necessary for firefox
            e.target.style.opacity = .5;
        });

        document.addEventListener("dragend", function(e) {
            e.target.style.opacity = 1;
            PullEffect.Widgets.create({
                type: e.target.getAttribute('data-type')
            });
        });

        document.addEventListener("dragover", function(e) {
            e.preventDefault();
        });

        document.addEventListener("drop", function(e) {
            e.preventDefault();
        });

        $('.fa-trash-o').click(function () {
            $('#clear-modal').modal('show');
            
        });
        $('.fa-power-off').click(function () {
            $.post( "/gplus/signout", function() {});
        });
        $('#clear-modal .btn-danger').click(function() {
            $('.generic').hide();
            gridster.remove_all_widgets();
            PullEffect.Widgets.reset();
            localStorage.clear();
            $('#clear-modal').modal('hide');
        });
    });

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
            var $toAdd = $(this.templateSkeleton({
                widget: m,
                typeObject: this.model.typeObject
            }));

            if (_.isUndefined(m.size_x) || _.isUndefined(m.size_y) || _.isUndefined(m.col) || _.isUndefined(m.row)) {
                gridster.add_widget($toAdd, 4, 4);
            } else {
                gridster.add_widget($toAdd, m.size_x, m.size_y, m.col, m.row);
            }
        },
        renderTitle: function(title) {
            $(this.selector).find('header').find('span').html(title);
        },
        renderContent: function(data, templateSelector) {
            var rendered = _.template($(templateSelector).html())(data);
            $(this.selector).find('section').html(rendered);
        }
    });
})();