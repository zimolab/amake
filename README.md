# amake: A tool help you write more flexible and maintainable Makefiles

command help:

```text
"""amake: a makefile assistant tool to help you write more flexible and maintainable makefiles.

Usage:
    amake [-C <dir> | --current-dir=<dir>] [-s <schemafile> | --schema=<schemafile>] [-c <configfile> | --config=<configfile>]
    amake init [-C <dir> | --current-dir=<dir>] [-t <template> | --template=<template>] [--no-edit] [<schemafile>]
    amake init-config [-C <dir> | --current-dir=<dir>] [<schemafile>] [<configfile>]
    amake edit [-C <dir> | --current-dir=<dir>] [-T | --text-editor] [<schemafile>]
    amake process [-C <dir> | --current-dir=<dir>] [--vars=<vars,...>] [<schemafile>] [<configfile>]
    amake generate [-C <dir> | --current-dir=<dir>] [-o <outputfile> | --output=<outputfile>] [-Y | --yes] [<schemafile>] [<configfile>]
    amake appconfig (--set=<config-paris> | --reset | --list | --edit) [-y | --yes]

Commands:
    init        Initialize a new amake project in the current directory. An amake project means a directory
                with an amake schema file. if not specified, the amake schema file will be named "amake.schema.json".

    init-config Initialize a new amake config file in the current directory. An amake config file means a file with
                a JSON object, which contains the values of variables defined in the amake schema. If not specified,
                the amake config file will be named "amake.config.json". If <schemafile> is not specified, use default
                amake schema file "amake.schema.json" in the current directory. If <configfile> is not specified, use
                "amake.config.json" in the current directory.

    edit        Edit the amake schema file in a GUI editor or a text editor(with -T or --text-editor option).

    process     Apply the processors on variables in the config file. The processor of a variable is defined
                in the amake schema using the "__processor__" field. If <schemafile> is not specified, use
                "amake.schema.json" in the current directory. If <configfile> is not specified, use "amake.config.json"
                in the current directory. This command is usually used for debugging purpose, it shows the processor call
                chain, the result of each processor and the final result of the variables. The final result is0 the actual
                value will be used passed to the makefile. How the processor works: Assuming we have defined  a variable
                 "INCLUDES" in the amake schema, and the initial value of it is a python list ["dir1", "dir2", "dir3"].
                Apparently, a python list is not a valid variable type in the makefile, so we need to convert it to a string
                when it is passed to the makefile. We may also want to add a "-I" prefix to each element of the list.
                To achieve this, we can define a processor chain on the "INCLUDES" variable in the amake schema as follows:
                    {
                        ...
                        variables: {
                            "INCLUDES": {
                                "__type__": "dirs_t",
                                "__processor__": "prefix_each '-I' | join ' ' | strip"

                            }
                        }
                        ...
                    }
                As you can see, we define three processors on the "INCLUDES" variable, and chained them with the pipe
                symbol "|". The first processor "prefix_each" is used to adds a prefix to each element of the list, "-I"
                is an argument of this processor which specifies the prefix(if a processor needs more than one argument,
                the arguments should be separated by a whitespace not a comma), so the output of this processor will be
                a list of ["-Idir1", "-Idir2", "-Idir3"]. The second processor "join" is used to join the elements of a
                list with the specified separator, in this case, it takes the output value of the previous "prefix_each"
                processor as the input, and joins the elements with a whitespace separator, so the output of this
                processor will be a string "-Idir1 -Idir2 -Idir3". The third processor "strip"  takes the output of the
                previous "join" processor as its input, and removes the leading and trailing spaces(if any). Since the
                "strip" processor is the last processor in the chain, its output will be the final value of the "INCLUDES"
                variable and be passed to the makefile.

    generate    Generate a build script based on the amake schema and the variable values in the config file.

    appconfig   A command to manage the amake app configuration.



Options:
    -s <schemafile>, --schema=<schemafile>   Specify the amake schema file to use. If not specified, use "amake.schema.json"
                                             in the current directory.

    -c <configfile>, --config=<configfile>   Specify the amake config file to use. If not specified, use "amake.config.json".

    -C <dir>, --current-dir=<dir>            Specify the current directory, if not specified, use the current working
                                             directory.

    -t <template> | --template=<template>    Specify the schema template to use. If not specified, use the default
                                             template. The default template is a blank schema, which means no variables
                                             predefined in the schema. Another template is "classic", which has some
                                             predefined variables as demonstration, with those variables definitions
                                             user can learn some basic concepts of how to define variables.

    -T, --text-editor                        Whether to use a system text editor instead of the GUI editor to edit
                                             the schema file.

    --no-edit                                When specified, it will not open the schema editor to edit the schema file
                                             after initialization.

    --vars=<vars,...>                        Specify the variables to run processors on. If not specified, all variables
                                             will be processed.

    -o <outputfile> | --output=<outputfile>  Specify the output file for the generated build script. If not specified,
                                             use "build.sh" in the current directory.

    -Y, --yes                                When specified, it will not ask for confirmation before some important
                                             operations, such as generating the build script or resetting the app config .etc.

    --set=<config-paris>                     This option is used with the "appconfig" command. It is used to set the value
                                             of a specific config item. Syntax: --set="config1=value1,config2=value2,...".
                                             For example, user can change the locale of the app by the following command:
                                                amake appconfig --set=locale=en_US

    --reset                                  This option is used with the "appconfig" command. It is used to reset the
                                             app config. Sometimes, the app config file maybe corrupted, this option will
                                             remove the app config file and create a new one with default values.

    --list                                   This option is used with the "appconfig" command. It is used to list all
                                             config items and their current values.

    --edit                                   This option is used with the "appconfig" command. It is used to edit the
                                             app config file in a text editor.

"""
```

## Introduction

## Features

## Usage

## Examples

## License

