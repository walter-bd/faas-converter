# FaaS Python Converter

A lib to convert python functions to the right sintaxis for deployment in AWS, Azure, OVH or Fission

## Getting Started

Using from terminal 
```
./faasconverter --file test.py --function foo --providers aws,  azure --just-wrap False
```

### Installing

```
pip install faasconverter 
```
or 
```
pip3 install faasconverter 
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

