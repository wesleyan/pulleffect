(function() {
    var PullEffect = {};
    global = {
        rooms: []
    };

    PullEffect.Types = {
        'roomInfo': {
            title: 'Room Info',
            configurable: true,
            expandable: true,
            templateSelector: '#room-info-widget',
            configurationTemplate: '#room-info-config',
            defaultConfiguration: {
                'selectedRoom' : 77
            },
            handler: function (model) {
                var self = this;
                var room = model.get('selectedRoom');
                var today = moment().format('YYYY/MM/DD');
                var apiURL = 'https://webapps.wesleyan.edu/wapi/v1/public/ems/room/' + room + '/booking_start/' + today + '/booking_end/' + today;
                model.view.renderTitle(_.where(global.rooms, {id: parseInt(room)})[0].name);
                
                //fetch room info from somewhere and then:
                $.getJSON(apiURL, function (data) {
                    //example data, needed to be updated from room database
                    model.view.renderContent(data, self.templateSelector);
                });
            },
            configHandler: function(model, formInfo) {
                //if there's any different stuff you need to do with config values, you can do it here.
                formInfo.forEach(function (input) {
                    model.set(input.name, parseInt(input.value));
                });
                model.typeObject.handler(model);
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
            templateSelector: '#special-events-widget',
            expandable: true,
            configurable: true,
            configurationTemplate: '#special-events-config',
            defaultConfiguration: {
                'maxNumber' : 5
            },
            handler: function(model) {
                var self = this;
                $.getJSON('http://ims-dev.wesleyan.edu:8080/api/events?minutes=3000')
                    .success(function(data) {
                        data = _.first(data, parseInt(model.get('maxNumber')));
                        //htmlspecialchars_decode can be added from Jack's code
                        model.view.renderContent({events: data}, self.templateSelector);
                    })
                    .error(function(err) {
                        console.log(err); //or whatever
                    });
            },
            configHandler: function(model, formInfo) {
                //if there's any different stuff you need to do with config values, you can do it here.
                formInfo.forEach(function (input) {
                    model.set(input.name, input.value);
                });
                model.typeObject.handler(model);
            }
        },
        'calendar': {
            title: 'Calendar',
            templateSelector: '#calendar-widget',
            configurable: true,
            defaultConfiguration: {
                'selected' : 'main'
            },
            configurationTemplate: '#calendar-config',
            handler: function (model) {
                var self = this;
                //fetch calendar from somewhere and then:
                var data = []; //TEMPORARY
                    model.view.renderContent({events: data}, self.templateSelector);
            },
            configHandler: function(model, formInfo) {
                //if there's any different stuff you need to do with config values, you can do it here.
                formInfo.forEach(function (input) {
                    model.set(input.name, input.value);
                });
                model.typeObject.handler(model);
            }
        }
    };

    $(document).ready(function() {
        $('nav li div').tooltip();

        $.getJSON('./static/rooms.json', function (data) {
            global.rooms = data;
            PullEffect.Widgets = new Widgets;
        });

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
        widget_base_dimensions: [80, 80],
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
            var self = this;
            this.typeObject = PullEffect.Types[this.get('type')];
            if(_.isUndefined(this.typeObject)) {
                //if no such widget is registered in the available widgets
                this.destroy();
                return; 
            }
            if(this.typeObject.configurable) {
                var toSetDefault = _.pairs(this.typeObject.defaultConfiguration);
                toSetDefault.forEach(function (pair) {
                    if(_.isUndefined(self.get(pair[0]))) {
                        self.set(pair[0], pair[1]);
                    }
                });
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
            e["click " + this.selector + " .expand"] = 'expand';
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
            $('.toggle, nav').show();
        },
        config: function(e) {
            //the widget should have some configurations specific to itself if it's said to be configurable.
            var configview = new ConfigView({model: this.model});
        },
        expand: function (e) {
            console.log(this.model.get('type') + ' widget expanded');
            $(this.selector).toggleClass('overlay');
            $('.toggle, nav').toggle();
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

    var ConfigView = Backbone.View.extend({
        el: $('#config-modal'),
        events: {
            'click .submit': 'submit'
        },
        submit: function(e) {
            e.preventDefault();
            $('.modal').modal('hide');
            this.undelegateEvents();
            this.model.typeObject.configHandler(this.model, this.form.serializeArray());
            PullEffect.Widgets.save();

            console.log('updated ' + this.model.get('type'));
        },
        initialize: function() {
            //check the widget model
            console.log('config ' + this.model.get('type'));

            //render a view with the configuration in #config-modal
            var temp = _.template($(this.model.typeObject.configurationTemplate).html())($.extend({}, this.model.attributes, global));
            $(this.el).find('.modal-body').html(temp);
            //save the form element for later serializing
            this.form = $(this.el).find('div[role="form"]').find("select, textarea, input");
            //show the modal window
            $('.modal').modal('hide');
            $('#config-modal').modal('show');
        }
    });
})();