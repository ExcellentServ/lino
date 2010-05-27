## Copyright 2009-2010 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

import os

from django.utils.translation import ugettext as _

import lino
from lino import actions, layouts #, commands
from lino import reports
#~ from lino import forms
from lino.ui import base
from lino.core import actors
from lino.utils import menus
from lino.utils import chooser
from lino.utils import jsgen
from lino.utils import build_url
from lino.utils.jsgen import py2js, js_code, id2js
from lino.ui.extjs import ext_elems, ext_requests
from lino.ui.extjs import ext_viewport

from lino.modlib.properties import models as properties

WC_TYPE_GRID = 'grid'


class ActionRenderer(object):
    def __init__(self,ui,action):
        assert isinstance(action,actions.Action), "%r is not an Action" % action
        self.action = action
        self.ui = ui
        
    def js_render(self):
        yield "function(caller) { return new Lino.%s(caller,%s);}" % (self.__class__.__name__,py2js(self.config))
    
class DownloadRenderer(ActionRenderer):
  
    def js_render(self):
        url = '/'.join(('/api',self.action.actor.app_label,self.action.actor._actor_name))+'/'
        yield "function(caller) { "
        #~ yield "  console.log(caller.get_selected());"
        yield "  var l = caller.get_selected();"
        yield "  if (l.length == 0) Lino.notify('No selection.');"
        yield "  for (var i = 0; i < l.length; i++) "
        yield "    window.open(%r+l[i]+'?fmt=%s');" % (url,self.action.name)
        #~ yield "  caller.get_selected().forEach(function(pk) {"
        #~ yield "    console.log(pk);"
        #~ yield "    window.open(%r+pk+'.pdf');" % url
        #~ yield "  })"
        yield "}" 

class DeleteRenderer(ActionRenderer):
  
    def js_render(self):
        yield "function(caller) { Lino.delete_selected(caller); }"
        #~ yield "function() { Lino.delete_selected(this); }"

class WindowWrapper(ActionRenderer):
  
    window_config_type = None
    
    def __init__(self,action,ui,lh,main,**kw):
        ActionRenderer.__init__(self,ui,action)
        assert self.window_config_type is not None, "%s.window_config_type is None" % self.__class__
        self.main = main
        #~ self.permalink_name = str(action).replace('.','/')
        self.permalink_name = str(action)
        self.lh = lh
        self.bbar_buttons = []
        self.config = self.get_config()
        
        
    def __str__(self):
        return self.ext_name + "(" + self.__class__.__name__ + ")"
        
    def get_config(self,**d):
        wc = lh2win(self.lh)
        wc = self.ui.load_window_config(self.action,**wc)
        d.update(permalink_name=self.permalink_name)
        d.update(wc=wc)
        #~ url = '/ui/' + '/'.join((self.action.actor.app_label,self.action.actor._actor_name,self.action.name))
        #~ d.update(url_action=url) # ,ext_requests.FMT_JSON))
        #~ d.update(handler=js_code("Lino.%s" % self.action)) 
        return d
        
def lh2win(lh,**kw):
    kw.update(height=300)
    kw.update(width=400)
    if lh is not None:
        #~ kw.update(title=lh.get_title(None))
        if lh.height is not None:
            kw.update(height=lh.height*EXT_CHAR_HEIGHT + 7*EXT_CHAR_HEIGHT)
        if lh.width is not None:
            kw.update(width=lh.width*EXT_CHAR_WIDTH + 10*EXT_CHAR_WIDTH)
        if lh.start_focus is not None:
            kw.update(defaultButton=lh.start_focus.name)
    return kw
  
class SlaveWrapper(WindowWrapper):
  
    def js_render(self):
        yield "function(caller) { "
        for ln in jsgen.declare_vars(self.config):
            yield '  '+ln
        yield "return new Lino.%s(caller,function(ww) { return %s});}" % (self.__class__.__name__,py2js(self.config))
        

class MasterWrapper(WindowWrapper):
  
    def __init__(self,rh,action,lh,**kw):
        WindowWrapper.__init__(self,action,lh.ui,lh,lh._main,**kw)
        
    def js_render(self):
        yield "function(caller) { "
        for ln in jsgen.declare_vars(self.config):
            yield '  '+ln
        yield "new Lino.%s(caller,function(ww) { return %s}).show();}" % (self.__class__.__name__,py2js(self.config))
        
            
    
class GridWrapperMixin(WindowWrapper):
    """
    Used by both GridMasterWrapper and GridSlaveWrapper
    """
  
    window_config_type = WC_TYPE_GRID
    
    def __init__(self,rh):
        self.rh = rh
    
    def get_config(self):
      
        d = super(GridWrapperMixin,self).get_config()
        #~ url = '' self.ui.get_action_url(a,ext_requests.FMT_RUN)
        if False:
          d.update(actions=[dict(
            opens_a_slave=a.opens_a_slave,
            handler=js_code("Lino.%s" % a),
            name=a.name,
            label=unicode(a.label),
            #~ url="/".join(("/ui",a.actor.app_label,a.actor._actor_name,a.name))
          ) for a in self.rh.get_actions() if not a.hidden])
        #~ i = 0
        #~ actions = []
        #~ for a in self.rh.get_actions():
            #~ if not a.hidden:
                #~ i += 1
                #~ btn = dict(text=a.label)
                #~ if a.opens_a_slave: 
                    #~ btn.update(toggleHandler=js_code('Lino.toggle_button_handler(caller,%d)' % i))
                    #~ btn.update(enableToggle = True)
                #~ else:
                    #~ btn.update(handler=js_code('Lino.button_handler(caller,%d)' % i))
                #~ actions.append(btn)
        #~ d.update(actions=actions)
        #~ d.update(actions=[dict(label=a.label,name=a.name) for a in self.bbar_buttons])
        #~ d.update(fields=[js_code(f.as_js()) for f in self.rh.store.fields])
        #~ d.update(colModel=self.lh._main.column_model)
        d.update(content_type=self.rh.report.content_type)
        d.update(title=unicode(self.rh.get_title(None)))
        #~ d.update(url_data=self.ui.get_actor_url(self.rh.report)) # +'/data') 
        d.update(main_panel=self.lh._main)
        return d
        
class GridMasterWrapper(GridWrapperMixin,MasterWrapper):
  
    def __init__(self,rh,action,**kw):
        self.action = action
        GridWrapperMixin.__init__(self,rh)
        MasterWrapper.__init__(self,rh,action,rh.list_layout,**kw)
      
  


class GridSlaveWrapper(GridWrapperMixin,SlaveWrapper):
  
    def __init__(self,rh,action,**kw):
        assert isinstance(action,reports.SlaveGridAction)
        self.name = action.actor._actor_name
        rh = action.slave.get_handle(rh.ui)
        #~ ah = action.actor.get_handle(ui)
        #~ self.lh = rh.list_layout
        GridWrapperMixin.__init__(self,rh)
        lh = rh.list_layout
        SlaveWrapper.__init__(self, action, rh.ui, lh, lh._main, **kw)
        #~ self.bbar_buttons = slave_rh.window_wrapper.bbar_buttons
        #~ self.slave_windows = slave_rh.window_wrapper.slave_windows
        #~ slave_lh._main.update(bbar=self.bbar_buttons)
        #~ self.actions = [dict(type=a.action_type,name=a.name,label=a.label) for a in rh.get_actions()]
        #~ print 20100419, self.__class__, self.name
        
            
    def get_config(self):
        #~ d = super(GridSlaveWrapper,self).get_config()
        d = GridWrapperMixin.get_config(self)
        d.update(name=self.name)
        return d
        
        
class DetailSlaveWrapper(SlaveWrapper):
  
    window_config_type = 'detail'
    
    def __init__(self,ui,action,**kw):
        lh = action.layout.get_handle(ui)
        SlaveWrapper.__init__(self, action, ui, lh, lh._main)
        self.actions = [] # [dict(type=a.action_type,name=a.name,label=a.label) for a in rh.get_actions()]
        
    def get_config(self):
        d = super(DetailSlaveWrapper,self).get_config()
        d.update(main_panel=self.lh._main)
        d.update(name=self.action.name)
        d.update(title=u"%s - %s" % (self.action.actor.get_title(None),self.action.label))
        return d
        
class unused_InsertWrapper(MasterWrapper):
  
    window_config_type = 'insert'
    
    def __init__(self,rh,action,**kw):
        assert isinstance(action,reports.InsertRow)
        lh = action.layout.get_handle(rh.ui)
        MasterWrapper.__init__(self, rh, action, lh)
        
    def get_config(self):
        d = super(InsertWrapper,self).get_config()
        d.update(main_panel=self.lh._main)
        d.update(name=self.action.name)
        d.update(title=self.action.label + _(' into ') + self.action.actor.get_title(None))
        d.update(fk_name=self.action.actor.fk_name);
        #~ d.update(formdata=)
        d.update(actions=[
          dict(
            name='submit',
            label='Submit',
            method='POST',
            url="/".join(("/api",self.action.actor.app_label,self.action.actor._actor_name))+'.json'
          ),
          ])
        return d
        
class DetailWrapper(MasterWrapper):
  
    window_config_type = 'detail'
    
    def __init__(self,rh,action,**kw):
        assert isinstance(action,reports.OpenDetailAction)
        if len(rh.report.detail_layouts) == 1:
            lh = rh.report.detail_layouts[0].get_handle(rh.ui)
            main = ext_elems.FormPanel(lh._main) # ,autoScroll=True)
            WindowWrapper.__init__(self,action,rh.ui,lh,main,**kw)        
        else:
            #~ tl = layouts.TabLayout(rh.report.detail_layouts)
            #~ lh = layouts.TabPanelHandle(rh,rh.report.detail_layouts)
            lh = rh.report.detail_layouts[0].get_handle(rh.ui)
            tabs = [l.get_handle(rh.ui)._main for l in rh.report.detail_layouts]
            main = ext_elems.FormPanel(ext_elems.TabPanel(tabs)) # ,autoScroll=True)
            WindowWrapper.__init__(self,action,rh.ui,None,main,**kw) 
        
    def get_config(self):
        d = MasterWrapper.get_config(self)
        url = build_url('/api',self.action.actor.app_label,self.action.actor._actor_name)
        d.update(url_data=url) 
        d.update(main_panel=self.main)
        d.update(name=self.action.name)
        d.update(fk_name=self.action.actor.fk_name);
        #~ d.update(formdata=)
        return d
        
        
class InsertWrapper(DetailWrapper):
    def get_config(self):
        d = DetailWrapper.get_config(self)
        d.update(title=_('%s into %s') %(self.action.label,self.action.actor.get_title(None)))
        d.update(record_id=-99999)
        return d

        


class PropertiesWrapper(SlaveWrapper):
    "Handle requests like GET /api/contacts/Persons/pgrid.extjs"
    window_config_type = 'props'
    name = 'pgrid'
    
    def __init__(self,rh,action,**kw):
        
        assert isinstance(action,properties.PropertiesAction)
        #~ assert isinstance(action,properties.PropsEdit)
        self.action = action
        self.ui = rh.ui
        self.model = action.actor.model
        #~ self.model = action.actor.model # rr.master
        #~ self.rh = action.rh
        
        kw.update(closeAction='hide')
        self.source = {}
        self.customEditors = {}
        self.propertyNames = {}
        
        for pv in properties.PropValuesByOwner().request(rh.ui,master=self.model):
            p = pv.prop
            self.source[p.name] = pv.value
            label = p.label or p.name
            level = len(p.name.split('.')) - 1
            if level:
                label = ('-' * level) + p.name
            self.propertyNames[p.name] = label
            #~ pvm = p.value_type.model_class()
            pvm = pv.__class__ 
            if pvm is properties.CHAR:
                choices = pvm.choices_list(p) # [unicode(choice) for choice in pv.value_choices(p)]
                if choices:
                    editor = ext_elems.ComboBox(store=choices,mode='local',selectOnFocus=True)
                    editor = 'new Ext.grid.GridEditor(%s)' % py2js(editor)
                    self.customEditors[p.name] = js_code(editor)
                    
        #~ print 20100226, self.model,len(self.source), self.source
        grid = dict(xtype='propertygrid')
        #~ grid.update(clicksToEdit=2)
        grid.update(source=self.source)
        grid.update(autoExpandColumn=1)
        #~ grid.update(viewConfig=dict(autoFit=True))
        grid.update(autoHeight=True)
        grid.update(customEditors=self.customEditors)
        listeners = dict(
          #~ afteredit=js_code('function(e){Lino.submit_property(this,e)}'),scope=js_code('this'))
          afteredit=js_code('Lino.submit_property_handler(caller)'))
        grid.update(listeners=listeners)
        #~ grid.update(pageSize=10)
        if len(self.propertyNames) > 0:
            grid.update(propertyNames=self.propertyNames)
        self.grid = grid
        panel = dict(xtype='panel',autoScroll=True,items=grid) #,layout='fit')
        main = jsgen.Value(panel)
        
        SlaveWrapper.__init__(self,action,rh.ui,None,main)
                    
                    
    def has_properties(self):
        return len(self.source) > 0
        
        
    def get_config(self):
        d = SlaveWrapper.get_config(self)
        d.update(main_panel=self.main)
        d.update(name=self.action.name)
        d.update(url_data=self.ui.get_actor_url(properties.PropValuesByOwner())) #+'/data') 
        return d


class unused_DetailMasterWrapper(MasterWrapper):
  
    window_config_type = 'form'
    
    def __init__(self,lh,dl,**kw):
        MasterWrapper.__init__(self,lh,dl,**kw)
        for a in dl.get_actions():
            self.bbar_buttons.append(ext_elems.FormActionElement(lh,a.name,a)) 
            #dict(text=a.label,handler=h))
            #~ if a.key:
                #~ keys.append(key_handler(a.key,h))
        lh._main.update(bbar=self.bbar_buttons)
        
    def unused_js_main(self):
        for ln in MasterWrapper.js_main(self):
            yield ln
        yield "this.refresh = function() { console.log('DetailMasterWrapper.refresh() is not implemented') };"
        yield "this.get_current_record = function() { return this.current_record;};"
        yield "this.get_selected = function() {"
        yield "  return this.current_record.id;"
        yield "}"
        yield "this.load_record = function(record) {"
        yield "  this.current_record = record;" 
        yield "  if (record) this.main_panel.form.loadRecord(record)"
        yield "  else this.main_panel.form.reset();"
        yield "};"
        #~ yield "this.load_record(%s);" % py2js(ext_store.Record(self.datalink.store,object))
        yield "var fn = Ext.data.Record.create(%s)" % \
            py2js([js_code(f.as_js()) for f in self.rh.store.fields])
        d = self.rh.store.row2dict(self.rh.row)
        yield "this.load_record(fn(%s));" % py2js(d)
        
        


def key_handler(key,h):
    return dict(handler=h,key=key.keycode,ctrl=key.ctrl,alt=key.alt,shift=key.shift)


