## Copyright 2009-2012 Luc Saffre
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
from django.conf import settings
from lino.ui import base
#~ from lino.ui.console import renderers_text

#~ class Panel:
    #~ pass
    
#~ class Element:
    #~ def __init__(self,*args,**kw):
        #~ self.args = args
        #~ self.kw = kw

#~ class FieldElement(Element):
    #~ def __init__(self,field,*args,**kw):
        #~ self.field = field
        #~ Element.__init__(self,*args,**kw)

#~ class MethodElement(Element):
    #~ def __init__(self,field,*args,**kw):
        #~ self.field = field
        #~ Element.__init__(self,*args,**kw)

#~ class ConsoleUI(base.UI):
  
    #~ GridElement = Element
    #~ VirtualFieldElement = Element
    #~ MethodElement = Element
    #~ ButtonElement = Element
    #~ Panel = Panel
    #~ Store = Element
    #~ Spacer = Element
    #~ StaticTextElement = Element
    #~ InputElement = Element
  
    #~ def main_panel_class(self,layout):
        #~ return Panel
    #~ def report_as_text(self,rpt):
        #~ rh = self.get_report_handle(rpt)
        #~ rr = renderers_text.TextReportRequest(rh,*args,**kw)
        #~ return rr.render()
        
from lino.utils.tables import TableRequest

class PseudoRequest:
    def __init__(self,name):
        self.user = settings.LINO.user_model.objects.get(username=name)


   
class Console(base.UI):

#~ class Console(object):
    _handle_attr_name = '_console_handle'
    
    #~ def __init__(self,username):
        #~ settings.LINO.setup()
        #~ self.request = PseudoRequest(username)
        
    #~ def setup_handle(self,h,ar):
        #~ pass
        
    #~ def request(self,actor,**kw):
        #~ if isinstance(actor,basestring):
            #~ actor = settings.LINO.modules.resolve(actor)
        #~ return actor.request(self,**kw)
        
    def run(self,action,pk):
        elem = action.actor.model.objects.get(pk=pk)
        #~ ar = TableRequest(self,action.actor,self.request,action)
        ar = TableRequest(self,action.actor,None,action)
        return action.run(elem,ar)
        
    def action_response(self,kw):
        """
        checking first whether there are only allowed keys 
        (defined in :attr:`ACTION_RESPONSES`)
        """
        self.check_action_response(kw)
        msg = kw.get('message')
        if msg: 
            print msg
        url = kw.get('open_url') or kw.get('open_davlink_url')
        if url:
            os.startfile(url)
        return kw
        

#~ ui = ConsoleUI()