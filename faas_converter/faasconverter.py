#! /usr/bin/env python3

import imp
import copy as cp
import ast
import importlib
import os
from inspect import signature, isfunction


def printout(*s):
    red = "\033[1;31m"
    reset = "\033[0;0m"
    s += (reset,)
    print(red + "»» faasconverter:", *s)


def printcontents(s):
    green = "\033[1;32m"
    reset = "\033[0;0m"
    print(green + s + reset)


def addwrappers(entry, parameters, providers):
    s = ""
    check_context = False
    dictparameters = {}

    def wrapper(x): return "# FaaS-Converter wrapper for {}\n".format(x)

    # AWS Lambda
    if "aws" in providers:
        dictparameters['aws'] = []
        for parameter in parameters:
            if (parameter != "context" and parameter != "event"):
                dictparameters['aws'].extend((
                    ["event['{}']".format(parameter)]))
            else:
                dictparameters['aws'].extend((
                    ["{}".format(parameter)]))
        if (entry != "lambda_handler" and
                not ("context" and "event" in parameters)):
            s += wrapper("aws")
            s += "def lambda_handler(event, context):\n"
            s += "\treturn {}({})\n".format(
                                        entry, ",".join(dictparameters['aws']))
            s += "\n"

    # IBM Cloud Functions
    if "ibm" in providers:
        if ("context" in parameters and entry == "lambda_handler"):
            del parameters["context"]
        dictparameters['ibm'] = ["dict['{}']".format(parameter) for parameter
                                 in parameters]
        if (entry != "handler" and
                not ("dict" in parameters)):
            s += wrapper("ibm")
            s += "def handler(dict):\n"
            s += "\td={}\n"
            s += "\td[\"results\"] = {}({})\n".format(
                                    entry, ",".join(dictparameters['ibm']))
            s += "\treturn d\n"
            s += "\n"

    # OVH Cloud Functions
    if "ovh" in providers:
        if ("context" in parameters and entry == "lambda_handler"):
            del parameters["context"]
        dictparameters['ovh'] = ["input['{}']".format(parameter) for parameter
                                 in parameters]
        if (entry != "handler" and
                not ("input" in parameters)):
            s += wrapper("ovh")
            s += "def handler(input):\n"
            s += "\td={}\n"
            s += "\td[\"results\"] = {}({})\n".format(
                                    entry, ",".join(dictparameters['ovh']))
            s += "\treturn str(d)\n"
            s += "\n"

    # Fission Cloud Functions
    if "fission" in providers:
        if ("context" in parameters and entry == "lambda_handler"):
            del parameters["context"]
        dictparameters['fission'] = ["dataDict['{}']".format(parameter)
                                     for parameter in parameters]
        if (entry != "main"):
            s += wrapper("fission")
            s += "def main():\n"
            s += "\timport json\n"
            s += "\timport flask\n"
            s += "\tinput = flask.request.get_data()\n"
            s += "\tdataDict = json.loads(input)\n"
            s += "\td={}\n"
            s += "\td[\"results\"] = {}({})\n".format(
                                entry, ",".join(dictparameters['fission']))
            s += "\treturn str(d)\n"
            s += "\n"

    # Azure Functions
    if "azure" in providers:
        if ("context" in parameters and entry == "lambda_handler"):
            del parameters["context"]
        dictparameters['azure'] = ["dict['{}']".format(parameter) for parameter
                                   in parameters]
        if (entry != "main"):
            s += wrapper("azure")
            s += "def main():\n"
            s += "\tfrom AzureHTTPHelper import HTTPHelper\n"
            s += "\timport json\n"
            s += "\tinput = HTTPHelper().post\n"
            s += "\tdatainput = open(os.environ[\"res\"]).read()\n"
            s += "\tdict = json.loads(datainput)\n"
            s += "\td = {}({})\n".format(
                                    entry, ",".join(dictparameters['azure']))
            s += "\tresponse = open(os.environ[\"res\"], \"w\")\n"
            s += "\tresponse.write(str(d))\n"
            s += "\tresponse.close()\n"
            s += "\n"
        if (len(providers) == 1):
            s += "main()"
    return (s)


def check_line(string, f):
    pos = f.tell()
    line = f.readline()
    while line:
        if (string in line and not ("#" in line)):
            break
        pos = f.tell()
        line = f.readline()
    return pos


def multiple(mod, providers, filename, all_together):
    for entry in mod.__dict__:
        function_portable(mod, providers, filename, entry, all_together)


def just_one(mod, providers, filename, entry, jw, all_together):
    if (not jw):
        function_portable(mod, providers, filename, entry, all_together)
    else:
        try:
            entrytype = mod.__dict__[entry]
        except KeyError as e:
            printout("Function not found, KeyError")
            printout(str(e))
            os._exit(1)
        if isfunction(entrytype):
            sig = signature(entrytype)
            fileobj = open(filename, "r")
            basename = os.path.basename(filename)
            printout("convert function", entry, sig)
            if (not all_together):
                for provider in providers:
                    convmodule = "{}_{}_portable.py".format(
                                    basename.replace(".py", ""), provider)
                    if (os.path.exists(convmodule)):
                        printout("File {} exists".format(convmodule))
                        continue
                    wrappers = addwrappers(entry, sig.parameters, provider)
                    if wrappers == "":
                        printout("Not an available provider or the file \
already has the sintax for the provider {}".format(provider))
                        continue
                    f = open(convmodule, 'w')
                    s = fileobj.read() + 2*"\n" + wrappers
                    print(s, file=f)
                    printout("converted to module: {}".format(convmodule))
                    printcontents(s)
                    f.close()
            else:
                convmodule = "{}_portable.py".format(
                                basename.replace(".py", ""))
                if (os.path.exists(convmodule)):
                    printout("File {} exists".format(convmodule))
                else:
                    printout("convert function", entry, sig)
                    wrappers = addwrappers(entry, sig.parameters, providers)
                    if wrappers == "":
                        printout("Not an available provider or the file \
already has the sintax for the provider {}".format(providers))
                    else:
                        f = open(convmodule, 'w')
                        s = fileobj.read() + 2*"\n" + wrappers
                        print(s, file=f)
                        printout("converted to module: {}".format(convmodule))
                        printcontents(s)
                        f.close()
            fileobj.close()


def function_portable(mod, providers, filename, entry, all_together):
    try:
        entrytype = mod.__dict__[entry]
    except KeyError as e:
        printout("Function not found, KeyError")
        printout(str(e))
        os._exit(1)
    if isfunction(entrytype):
        sig = signature(entrytype)
        printout("convert function", entry, sig)
        fileobj = open(filename, "r")
        num_lines = sum(1 for line in fileobj)
        final_line = fileobj.tell()
        s = ""
        fileobj.seek(0)
        parameter_def = check_line("def", fileobj)
        fileobj.seek(parameter_def)
        start_entry_line = check_line(("def " + entry), fileobj)
        line = fileobj.readline()
        while line:
            if (len(line) == len(line.lstrip()) or
                    fileobj.tell() == final_line):
                final_entry_line = fileobj.tell()
                break
            line = fileobj.readline()
        fileobj.seek(0)
        line = fileobj.readline()
        while line:
            if fileobj.tell() == (parameter_def):
                break
            else:
                s += line
                line = fileobj.readline()
        if (not all_together):
            for provider in providers:
                k = cp.deepcopy(s)
                fileobj.seek(start_entry_line)
                line = fileobj.readline()
                convmodule = "{}_{}_portable.py".format(
                                entry, provider)
                if (os.path.exists(convmodule)):
                    printout("File {} exists".format(convmodule))
                    continue
                wrappers = addwrappers(entry, sig.parameters, provider)
                if wrappers == "":
                    printout("Not an available provider or the file \
already has the sintax for the provider {}".format(provider))
                    continue
                f = open(convmodule, 'w')
                while line:
                    if (fileobj.tell() == final_entry_line):
                        if final_line == fileobj.tell():
                            k += line
                        k += 2*"\n" + wrappers
                        break
                    else:
                        k += line
                        line = fileobj.readline()
                print(k, file=f)
                printout("converted to module: {}".format(convmodule))
                printcontents(k)
                f.close()
        else:
            fileobj.seek(start_entry_line)
            line = fileobj.readline()
            convmodule = "{}_portable.py".format(
                            entry)
            if (os.path.exists(convmodule)):
                printout("File {} exists".format(convmodule))
            else:
                wrappers = addwrappers(entry, sig.parameters, providers)
                if wrappers == "":
                    printout("Not an available provider or the file \
already has the sintax for the provider {}".format(providers))
                else:
                    f = open(convmodule, 'w')
                    while line:
                        if (fileobj.tell() == final_entry_line):
                            if final_line == fileobj.tell():
                                s += line
                            s += 2*"\n" + wrappers
                            break
                        else:
                            s += line
                            line = fileobj.readline()
                    print(s, file=f)
                    f.close()
                    printout("converted to module: {}".format(convmodule))
                    printcontents(s)
        fileobj.close()


def converter(module, providers, function, jw, insecure,
              all_together):
    basemodule = module.replace(".py", "")
    printout("track module: {}".format(basemodule))
    if (not insecure):
        try:
            for i in ast.parse(open(module).read()).body:
                if (not isinstance(i, ast.FunctionDef) and
                        not isinstance(i, ast.Import) and
                        not isinstance(i, ast.ImportFrom)):
                    printout("Error, insecure file. Executable code found on \
runtime import")
                    printout(str(i))
                    os._exit(1)
        except IOError as e:
            printout("File not found")
            printout(str(e))
            os._exit(1)
    (fileobj, filename, desc) = imp.find_module(basemodule, ["."])
    mod = imp.load_module(basemodule, fileobj, filename, desc)
    if function == "":
        multiple(mod, providers, filename, all_together)
    else:
        just_one(mod, providers, filename, str(function), jw, all_together)
