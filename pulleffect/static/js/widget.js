/* Copyright (C) 2014 Wesleyan University
* 
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* 
*   http://www.apache.org/licenses/LICENSE-2.0
* 
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

(function() {
    var PullEffect = {};
    global = {
        rooms: [],
        gcals: []
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
                var apiURL = 'https://webapps.wesleyan.edu/wapi/v1/public/ems/room/' + room;
                model.view.renderTitle(_.where(global.rooms, {id: parseInt(room)})[0].name);
                // fetch room info from somewhere and then: and then what!? and then what!?
                $.getJSON(apiURL).success(function(data){
                    data.records = data.records.map(function(event) {
                        var now = moment();
                        if(now.isAfter(event.event_start) && now.isBefore(event.event_end)) {
                            event.current = true;
                        } else {
                            event.current = false;
                        }
                        return event;
                    });
                    // sort events by starting time
                    data.records = _.sortBy(data.records, function(event) {
                        return (new Date(event.event_start)).getTime();
                    });
                    model.view.renderContent(data, self.templateSelector);
                }).fail(function(jqxhr) {
                    model.view.renderError(jqxhr);
                });
            },
            configAfterRender: function(model, $form) {
                //make room selection an input/select with typeahead
                $form.filter("[name='selectedRoom']").select2({
                    width: '100%'
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

                var devices = {
                    'mac': 'fa fa-apple',
                    'pc': 'fa fa-windows',
                    'printer': 'fa fa-print',
                    'roomtrol': 'fa fa-flash',
                    'projector': 'fa fa-video-camera'
                };

                var dtype = message.device;
                if (_.isNull(dtype))
                    return '';

                var icon = devices[dtype.toLowerCase()];
                
                if(_.isUndefined(icon)) 
                    return '';
               
                return icon;
            },
            templateSelector: "#messages-widget",
            handler: function (model) {
                var self = this;
                $.getJSON(messagesRoute).done(function(data){
                    model.view.renderContent({
                        messages: data,
                        setSeverity: self.setSeverity,
                        getDeviceIcon: self.getDeviceIcon
                    }, self.templateSelector);
                }).fail(function(jqxhr) {
                    model.view.renderError(jqxhr);
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
                'maxNumber' : 5,
                'nextHours': 50
            },
            handler: function(model) {
                var self = this;
                $.getJSON('https://spec.wesleyan.edu/api/events?minutes=' + (parseInt(model.get('nextHours')) * 60))
                    .done(function(data) {
                        // sort events by starting time
                        data = _.sortBy(data, function(event) {
                            return Date.parse(event.start);
                        });
                        data = _.first(data, parseInt(model.get('maxNumber')));
                        //htmlspecialchars_decode can be added from Jack's code
                        model.view.renderContent({events: data, nextHours: model.get('nextHours')}, self.templateSelector);
                    })
                    .fail(function(jqxhr) {
                        model.view.renderError(jqxhr);
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
            configurable: true,
            templateSelector: '#calendar-widget',
            configurationTemplate: '#calendar-config',
            activeCalendar: undefined,
            handler: function (model) {
                var self = this;
                var selectedId = model.get('selectedGcal');
                this.activeCalendar = _.where(global.gcals, {id: selectedId})[0];
                if (!this.activeCalendar){
                    model.view.renderContent({events: [], calendarSet: false}, this.templateSelector);
                    
                }
                else{
                    var gcal = this.activeCalendar
                    var now = moment().format("YYYY-MM-DDTHH:mm:ssZ")
                    var apiURL = calEventsRoute + "?id=" + escape(gcal.id) + "&now=" + now;
                    
                    $.getJSON(apiURL).success(function(data){
                        
                        model.view.renderContent({events: data.items, calendarSet: true}, self.templateSelector);

                    });
                    model.view.renderTitle(gcal.name);
                 }
            },
            configHandler: function(model, formInfo) {
                //if there's any different stuff you need to do with config values, you can do it here.
                formInfo.forEach(function (input) {
                    model.set(input.name, input.value);
                });
                model.typeObject.handler(model);
            }
        },
        'shifts': {
            title: 'Shifts',
            configurable: true,
            templateSelector: '#shifts-widget',
            configurationTemplate: '#shifts-config',
            activeCalendar: undefined,
            handler: function (model) {
                var self = this;
                var selectedId = model.get('selectedGcal');
                this.activeCalendar = _.where(global.gcals, {id: selectedId})[0];
                if (!this.activeCalendar){
                    model.view.renderContent({events: [], calendarSet: false}, this.templateSelector);
                }
                else{
                    var gcal = this.activeCalendar
                    var apiURL = shiftsRoute + "?id=" + escape(gcal.id);
                    
                    $.getJSON(apiURL).success(function(data){
                        
                        // TODO(cumhurk): Cumhur can you provide the proper rendering shit
                        //model.view.renderContent({events: data.items, calendarSet: true}, self.templateSelector);
                    });
                    model.view.renderTitle(gcal.name);
                 }
            },
            configHandler: function(model, formInfo) {
                //if there's any different stuff you need to do with config values, you can do it here.
                formInfo.forEach(function (input) {
                    model.set(input.name, input.value);
                });
                model.typeObject.handler(model);
            }
        },
        'leaderboard': {
            title: 'Ticket Resolutions',
            templateSelector: '#leaderboard-widget',
            configurable: true,
            configurationTemplate: '#leaderboard-config',
            defaultConfiguration: {
                'mode' : 'kiosk'
            },
            handler: function(model) {
                var self = this;
                


                $.getJSON(recordsRoute).done(function(data) {
                    console.log(data);

                    // if(this.model.get('mode') === 'all') {
                    //     $(this.model.view.selector).find('section').attr('style', 'overflow: scroll !important');
                    // } else { //kiosk mode
                    //     $(this.model.view.selector).find('section').attr('style', 'overflow: hidden !important');
                    //     data = _.first(data, 10);
                    // }
                    data = [{username:"a", count:2}]
                    model.view.renderContent({staff: data}, self.templateSelector);
                }).fail(function(jqxhr) {
                    model.view.renderError(jqxhr);
                });
            },
            configHandler: function(model, formInfo) {
                formInfo.forEach(function (input) {
                    model.set(input.name, parseInt(input.value));
                });
                model.typeObject.handler(model);
            }
        },
        'notes': {
            title: 'Notes',
            templateSelector: '#notes-widget',
            configurable: true,
            configurationTemplate: '#notes-config',
            handler: function(model) {
                var self = this;
                $.getJSON('notes/?limit=10').done(function(data){
                    model.view.renderContent({notes: data}, self.templateSelector, function(view) {
                        $(view.selector).find('input').keyup(function(e) {
                            if(e.which !== 13) {
                                return;
                            }
                            //if pressed enter
                            //make an POST request to back end
                            $.post( "notes/", {
                                text: this.val()
                            }).done(function( data ) {
                                self.handler(model);
                            });
                        })
                    });
                }).fail(function(jqxhr) {
                    model.view.renderError(jqxhr);
                });
            },
            configHandler: function(model, formInfo) {
                formInfo.forEach(function (input) {
                    model.set(input.name, parseInt(input.value));
                });
                model.typeObject.handler(model);
            }
        }
    };

    PullEffect.Mode = {
        setIfKiosk: function() {
            if(JSON.parse($.cookie('kiosk')) === true) {
                $('#modifyCSSRule').html('.option {display:none;}');
                $('.fa-bullhorn').removeClass('btn-danger');
                $('.fa-bullhorn').addClass('btn-success');
            } else {
                $('#modifyCSSRule').html('');
                $('.fa-bullhorn').addClass('btn-danger');
                $('.fa-bullhorn').removeClass('btn-success');
            }
        }
    };

    PullEffect.refreshAllWidgets = function() {
        PullEffect.Widgets.each(function(model) {
            model.typeObject.handler(model);
        });
    };

    $(document).ready(function() {
        $('nav li div').tooltip();

        $.getJSON(roomsRoute, function (data) {
            global.rooms = data;
            // rooms.json is already sorted, but if needed:
            //global.rooms = _(data).sortBy('name');
            PullEffect.Widgets = new Widgets;

            setInterval(PullEffect.refreshAllWidgets, 10*60000); //every 10 min
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
        $('nav .btn-primary').click(function(e) {         
            PullEffect.Widgets.create({
                type: e.target.getAttribute('data-type')
            });
        });

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

        // Kiosk Mode Configurations
        if(_.isUndefined($.cookie('kiosk'))) {
            $.cookie('kiosk', 'false', {expires: 9000, path: '/'});
        }
        PullEffect.Mode.setIfKiosk();

        $('.fa-bullhorn').click(function() {
            $.cookie('kiosk', JSON.stringify(!JSON.parse($.cookie('kiosk'))), {expires: 9000, path: '/'});
            PullEffect.Mode.setIfKiosk();
        })

        // Removing all widgets
        $('.fa-trash-o').click(function () {
            $('#clear-modal').modal('show');
            
        });
        $('#clear-modal .btn-danger').click(function() {
            $('.generic').hide();
            gridster.remove_all_widgets();
            PullEffect.Widgets.reset();
            $.removeCookie('widgets');
            $('#clear-modal').modal('hide');
        });

        // Sign out
        $('.fa-power-off').click(function () {
            window.location.href = $(this).attr('href');
        });
    });

    gridster = $(".gridster ul").gridster({
        widget_base_dimensions: [80, 80],
        widget_margins: [5, 5],
        helper: 'clone',
        avoid_overlapped_widgets: true,
        resize: {
            enabled: true,
            min_size: [3, 3],
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
                this.delete();
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
        save: function (attr) {
           this.set(attr);
           this.store();
        },
        delete: function () {
            this.destroy();
            this.store();
        },
        store: function() {
            var content = encodeURIComponent(JSON.stringify(PullEffect.Widgets));
           $.removeCookie('widgets');
           $.cookie('widgets', content, {expires: 9000, path: '/'});
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
        },
        fetch : function() {
            try {
                var content = JSON.parse(decodeURIComponent($.cookie('widgets')));
                this.reset(content);
            } catch(e) {
                console.log(e);
                this.reset([]);
            }  
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
                model.delete();
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
            if(e.target) {
                var current = this.model.get('expanded');
                if(_.isUndefined(current)) {
                    this.model.save({expanded: true});
                } else {
                    this.model.save({expanded: !current});
                }
            }
            console.log(this.model.get('type') + ' widget expanded');
            $(this.selector).toggleClass('overlay');
            $(this.selector).find('.close, .config').toggle();
            $('.toggle, nav').toggle();
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

            var self = this;
            var letMeKnow = setInterval(function () {
                var lookFor = $(self.selector);
                if(lookFor.length > 0) {
                    clearInterval(letMeKnow);
                    if(self.model.get('expanded') === true) {
                        self.expand({});
                    }
                } 
            }, 10);
        },
        renderTitle: function(title) {
            $(this.selector).find('header').find('span').html(title);
        },
        renderContent: function(data, templateSelector, afterRender) {
            var rendered = _.template($(templateSelector).html())(data);
            $(this.selector).find('section').html(rendered);
            if(!_.isUndefined(afterRender)) {
                afterRender(this);
            }
        },
        renderError: function (jqxhr) {
            console.log(jqxhr);
            $(this.selector).find('section').html('There is a problem with this widget.');
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

            if(!_.isUndefined(this.model.typeObject.configAfterRender)) {
                //the function to initialize any special form elements, such as Select2, if needed
                this.model.typeObject.configAfterRender(this.model, this.form);
            }

            //show the modal window
            $('.modal').modal('hide');
            $('#config-modal').modal('show');
        }
    });
})();
