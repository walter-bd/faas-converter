#! /usr/bin/env python3

import imp
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


def multiple(mod, providers, filename):
    for entry in mod.__dict__:
        function_portable(mod, providers, filename, entry)


def just_one(mod, providers, filename, entry, jw=False):
    if (not jw):
        function_portable(mod, providers, filename, entry)
    else:
        entrytype = mod.__dict__[entry]
        if isfunction(entrytype):
            for provider in providers:
                sig = signature(entrytype)
                convmodule = "{}_{}_portable.py".format(filename, provider)
                if (os.path.exists(convmodule)):
                    printout("File exists")
                    continue
                f = open(convmodule, 'w')
                printout("convert function", entry, sig)
                fileobj = open(filename, "r")
                wrappers = addwrappers(entry, sig.parameters, provider)
                s = fileobj.read() + 2*"\n" + wrappers
                print(s, file=f)
                f.close()
                fileobj.close()
                printout("converted to module: {}".format(convmodule))
                printcontents(s)


def function_portable(mod, providers, filename, entry):
    entrytype = mod.__dict__[entry]
    if isfunction(entrytype):
        sig = signature(entrytype)
        printout("convert function", entry, sig)
        for provider in providers:
            fileobj = open(filename, "r")
            convmodule = "{}_{}_portable.py".format(entry, provider)
            if (os.path.exists(convmodule)):
                printout("File exists")
                continue
            wrappers = addwrappers(entry, sig.parameters, provider)
            if wrappers == "":
                printout("{} is not an available provider for the converter\
                         ".format(provider))
                continue
            f = open(convmodule, 'w')
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
            fileobj.seek(start_entry_line)
            line = fileobj.readline()
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
            fileobj.close()
            printout("converted to module: {}".format(convmodule))
            printcontents(s)


def converter(module, providers, function="", jw=False):
    basemodule = module.replace(".py", "")
    printout("track module: {}".format(basemodule))
    (fileobj, filename, desc) = imp.find_module(basemodule, ["."])
    mod = imp.load_module(basemodule, fileobj, filename, desc)
    if function == "":
        multiple(mod, providers, filename)
    else:
        just_one(mod, providers, filename, str(function), jw)
