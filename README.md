# FaaS Python Converter

A lib to convert python functions to the right sintaxis for deployment in AWS, Azure, IBM(OpenWhisk), OVH or Fission

## Getting Started

Example of use from terminal 
```
./faasconverter --file test.py --function foo --providers aws,  azure --just-wrap False --all-together True
```
Options 

**file** File to convert to the selected provider sintax

**function** Selected function to convert to the providers sintax

**just-wrap** To only add the sintax wrapper on the end of the selected file

**providers** List of selected providers to which to convert the functions, available = aws, ibm, azure, ovh, fission

**all-together** Put all the wrappers together and add it to the the end of each file

### Installing

```
pip3 install faas-converter 
```

## Authors

* **Josef Spillner** - [ZHAW/SPLAB](https://github.com/serviceprototypinglab)
* **Walter Benitez** - [GitHUB](https://github.com/walter-bd)

## License

Copyright 2018 Josef Spillner, Walter Benitez

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

