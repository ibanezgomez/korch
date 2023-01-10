import os.path
import configparser

class Config:
    def __init__(self,file):
        self.fname = file
        self.cfg = configparser.ConfigParser()
        self.cfg.read(os.path.join(os.path.dirname(__file__), self.fname))
        
    def getSections(self):
        try: return self.cfg.sections()
        except: return []
        
    def getSection(self,sec):
        try: return dict(self.cfg.items(sec))
        except: return {}
    
    def addSection(self,sec):
        try:
            self.cfg.add_section(sec)
            return True
        except:
            return False
    
    def delSection(self,sec):
        return self.cfg.remove_section(sec)
        
    def isSection(self,sec):
        return self.cfg.has_section(sec)
    
    def getOptions(self,sec):
        return self.cfg.options(sec)
    
    def getOption(self,sec,opt):
        try:
            return self.cfg.get(sec,opt)
        except:
            return ""
            
    def setOption(self,sec,opt,val):
        try:
            self.cfg.set(sec,opt,str(val))
            return True
        except:
            return False
    
    def delOption(self,sec,opt):
        return self.cfg.remove_option(sec,opt)
        
    def isOption(self,sec,opt):
        return self.cfg.has_option(sec,opt)
        
    def getItems(self,sec):
        res = {}
        items = self.cfg.items(sec)
        for i in items:
            if i[0]: res[i[0]]=i[1]
        return res
        
    def save(self):
        with open(os.path.join(os.path.dirname(__file__), self.fname), 'w') as configfile:
            self.cfg.write(configfile)
        
        
