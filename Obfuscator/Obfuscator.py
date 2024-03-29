
from Obfuscator.StringEncrypter import StringEncrypter
from Parser.Parser import Parser

from Obfuscator.Locals import Local
from Obfuscator.MathEncrypter import MathEncrypter

from Obfuscator.Vm.BytecodeRW import BytecodeUtilities
from Obfuscator.Vm.Bytecode.Compiler import Compiler

from Obfuscator.Rewriter.Flattener import Flattener

from luaparser import ast

import random


class Obfuscator:
    """
    The is the Main obfuscator class.
    It has the following functions:
    1. Obfuscate() -> This is the main function for obfuscating your code.

    
    """

    def __init__(self, Source, Options):
        self.Parser = Parser(Source)
        self.Options = Options
        self.AstTree = self.Parser.Parse() # Being sure that this ran before searching something in the AST
        self.Source = Source
        self.IntKey = random.randint(10, 50)
        self.StrKey = random.randint(10, 50)
        

        # Decryptors
        self.IntDecryptor = ""
        self.StrDecryptor = ""

    def Obfuscate(self):
        self.AstTree = Local(self.Parser, self.AstTree).PutLocalOnTop()
        self.Parser.AstTree = self.AstTree

        if self.Options["Encryption"]["Integer"]:
            # Replacing the AstTree with the new one
            self.AstTree, self.IntDecryptor = MathEncrypter(self.Parser, self.IntKey).EncryptMath()
            self.Source = ast.to_lua_source(self.AstTree)
            
        
        if self.Options["Encryption"]["String"]:
            self.Source, self.StrDecryptor = StringEncrypter(self.Source ,self.Parser, self.StrKey).EncryptStrings()
            # Parsing the new source to get the new AST
            self.Parser = Parser(self.Source)
            self.AstTree = self.Parser.Parse()

        
        self.Source = self.IntDecryptor + self.StrDecryptor + self.Source

        if self.Options["Vm"]:
            OutputName = "asd.lua"
            with open(OutputName, 'w') as f:
                f.write(self.Source)
                f.close()

            LuaC_Output = "aaa.out"
            Compiler.Compile(OutputName, FileName = LuaC_Output)

            BytecodeFile = open(LuaC_Output, "rb") # Read as binary
            bytecode = BytecodeFile.read()
            BytecodeFile.close()

            import os
            if os.path.exists(LuaC_Output): os.remove(LuaC_Output) 
            else: raise Exception("The file (" + LuaC_Output + ") does not exist!")

            if os.path.exists(OutputName): os.remove(OutputName)
            else: raise Exception("The file (" + OutputName + ") does not exist!")


            VMUtilities = BytecodeUtilities(bytecode)
            LChunk = VMUtilities.Deserialize()

            SerializedChunk = VMUtilities.Serialize()
            ObfuscatorBytecode = "\\"
            ObfuscatorBytecode += '\\'.join(map(str, SerializedChunk))

            # Writing the serialized chunk to a file
            with open("SerializedChunk.out", 'w') as f:
                f.write(ObfuscatorBytecode)
                f.close()


            """
            # Flattener Test. This will be removed later
            FlattenedAST = Flattener(self.Parser, self.AstTree).FlattenCF()
            newcode = ast.to_lua_source(FlattenedAST)
            with open("CFF_TEST.lua", 'w') as f:
                f.write(newcode)
                f.close()
            """

            print("Debug Breakpoint")



        return self.Source