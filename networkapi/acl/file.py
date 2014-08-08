# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''
import os, logging


class FileError(Exception):
    
    def __init__(self, error):
        self.error = error
    def __str__(self):
        msg = u"%s" % (self.error) 
        return msg.encode("utf-8", "replace")

logger = logging.getLogger(__name__)

class File():
    
    @classmethod
    def read(cls, file_name):
        '''Reading File
        
        @param file_name: File name
        
        @raise FileError: Failed to reading file
        '''
        try:
            
            file_name = "./%s" % file_name
            
            file_acl = open(file_name,"r")
            content = file_acl.read()
            file_acl.close()
            
            return content

        except Exception, e:
            logger.error(e)
            raise FileError(e)

    @classmethod
    def write(cls, file_name, content):
        '''Writing File
        
        @param file_name: File name
        @param content: File content
        
        @raise FileError: Failed to writing file
        '''
        try:
            
            file_name = "./%s"  % file_name
            
            file_acl = open(file_name,"w")
            file_acl.write(content)
            file_acl.close()
            
        except Exception, e:
            logger.error(e)
            raise FileError(e)

    @classmethod
    def create(cls, file_name):
        '''Creating File

        @param file_name: File name
        
        @raise FileError: Failed to creating file
        '''
        try:
            
            file_name = "./%s" % file_name
            
            file_acl = open(file_name,"w")
            file_acl.close()
            
        except Exception, e:
            logger.error(e)
            raise FileError(e)

    @classmethod
    def remove(cls, file_name):
        '''Removing File

        @param file_name: File name
        
        @raise FileError: Failed to removing file
        '''
        try:
            
            file_name = "./%s" % file_name
            
            erro = os.system("rm %s" % file_name )
            
        except Exception, e:
            logger.error(e)
            raise FileError(e)