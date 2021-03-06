#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Original Copyright (c) 2016 Johann Petrak
# Modified Copyright (c) 2018 David Smerkous
# Modified Copyright (c) 2019 Mayk Choji
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""A tool to change or add license headers in all supported files in or below a directory."""

from __future__ import unicode_literals
from __future__ import print_function

import os
import shutil
import sys
import logging
import argparse
import re
import fnmatch
from string import Template
from shutil import copyfile
import io
import subprocess
import datetime

__author__ = 'Johann Petrak, David Smerkous, Mayk Choji'
__license__ = 'MIT'
__version__ = '0.4'


log = logging.getLogger(__name__)


try:
    unicode
except NameError:
    unicode = str

# for each processing type, the detailed settings of how to process files of that type
typeSettings = {
    "java": {
        "extensions": [".java",".scala",".groovy",".jape"],
        "keepFirst": None,
        "blockCommentStartPattern": re.compile('^\s*/\*'),  ## used to find the beginning of a header bloc
        "blockCommentEndPattern": re.compile(r'\*/\s*$'),   ## used to find the end of a header block
        "lineCommentStartPattern": re.compile(r'\s*//'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "/*\n",   ## inserted before the first header text line
        "headerEndLine": " */\n",    ## inserted after the last header text line
        "headerLinePrefix": " * ",   ## inserted before each header text line
        "headerLineSuffix": None,            ## inserted after each header text line, but before the new line
    },
    "javascript": {
        "extensions": [".js",".ts",".jsx",".jsx"],
        "keepFirst": None,
        "blockCommentStartPattern": re.compile('^\s*/\*'),  ## used to find the beginning of a header bloc
        "blockCommentEndPattern": re.compile(r'\*/\s*$'),   ## used to find the end of a header block
        "lineCommentStartPattern": re.compile(r'\s*//'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "/*\n",   ## inserted before the first header text line
        "headerEndLine": " */\n",    ## inserted after the last header text line
        "headerLinePrefix": " * ",   ## inserted before each header text line
        "headerLineSuffix": None,            ## inserted after each header text line, but before the new line
    },
    "script": {
        "extensions": [".sh",".csh",".py",".pl"],
        "keepFirst": re.compile(r'^#!'),
        "blockCommentStartPattern": None,
        "blockCommentEndPattern": None,
        "lineCommentStartPattern": re.compile(r'\s*#'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "##\n",   ## inserted before the first header text line
        "headerEndLine": "##\n",    ## inserted after the last header text line
        "headerLinePrefix": "## ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    },
    "xml": {
        "extensions": [".xml"],
        "keepFirst": re.compile(r'^\s*<\?xml.*\?>'),
        "blockCommentStartPattern": re.compile(r'^\s*<!--'),
        "blockCommentEndPattern": re.compile(r'-->\s*$'),
        "lineCommentStartPattern": None,    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "<!--\n",   ## inserted before the first header text line
        "headerEndLine": "  -->\n",    ## inserted after the last header text line
        "headerLinePrefix": "-- ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    },
    "sql": {
        "extensions": [".sql"],
        "keepFirst": None,
        "blockCommentStartPattern": None, #re.compile('^\s*/\*'),
        "blockCommentEndPattern": None, #re.compile(r'\*/\s*$'),
        "lineCommentStartPattern": re.compile(r'\s*--'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "--\n",   ## inserted before the first header text line
        "headerEndLine": "--\n",    ## inserted after the last header text line
        "headerLinePrefix": "-- ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    },
    "c": {
        "extensions": [".c",".cc",".cpp",".c++",".h",".hpp"],
        "keepFirst": None,
        "blockCommentStartPattern": re.compile(r'^\s*/\*'),
        "blockCommentEndPattern": re.compile(r'\*/\s*$'),
        "lineCommentStartPattern": re.compile(r'\s*//'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "/*\n",   ## inserted before the first header text line
        "headerEndLine": " */\n",    ## inserted after the last header text line
        "headerLinePrefix": " * ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    },
    "ruby": {
        "extensions": [".rb"],
        "keepFirst": "^#!",
        "blockCommentStartPattern": re.compile('^=begin'),
        "blockCommentEndPattern": re.compile(r'^=end'),
        "lineCommentStartPattern": re.compile(r'\s*#'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "##\n",   ## inserted before the first header text line
        "headerEndLine": "##\n",    ## inserted after the last header text line
        "headerLinePrefix": "## ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    },
    "csharp": {
        "extensions": [".cs"],
        "keepFirst": None,
        "blockCommentStartPattern": None,
        "blockCommentEndPattern": None,
        "lineCommentStartPattern": re.compile(r'\s*//'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": None,   ## inserted before the first header text line
        "headerEndLine": None,    ## inserted after the last header text line
        "headerLinePrefix": "// ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    },
    "vb": {
        "extensions": [".vb"],
        "keepFirst": None,
        "blockCommentStartPattern": None,
        "blockCommentEndPattern": None,
        "lineCommentStartPattern": re.compile(r"^\s*\'"),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": None,   ## inserted before the first header text line
        "headerEndLine": None,    ## inserted after the last header text line
        "headerLinePrefix": "' ",   ## inserted before each header text line
        "headerLineSuffix": None            ## inserted after each header text line, but before the new line
    },
    "erlang": {
        "extensions": [".erl", ".src", ".config", ".schema"],
        "keepFirst": None,
        "blockCommentStartPattern": None,  ## used to find the beginning of a header bloc
        "blockCommentEndPattern": None,   ## used to find the end of a header block
        "lineCommentStartPattern": None,    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "%% -*- erlang -*-\n%% %CopyrightBegin%\n%%\n",   ## inserted before the first header text line
        "headerEndLine": "%%\n%% %CopyrightEnd%\n\n",    ## inserted after the last header text line
        "headerLinePrefix": "%% ",   ## inserted before each header text line
        "headerLineSuffix": None,            ## inserted after each header text line, but before the new line
    },
    "python": {
        "extensions": [".py"],
        "keepFirst": re.compile(r'^#!'),
        "keepMore": re.compile(r'^#.*coding.+'),  ## keep special lines after the first line
        "blockCommentStartPattern": None,  ## used to find the beginning of a header bloc
        "blockCommentEndPattern": None,   ## used to find the end of a header block
        "lineCommentStartPattern": re.compile(r'^\s*#'),    ## used to find header blocks made by line comments
        "lineCommentEndPattern": None,
        "headerStartLine": "#\n",   ## inserted before the first header text line
        "headerEndLine": "#\n",    ## inserted after the last header text line
        "headerLinePrefix": "# ",   ## inserted before each header text line
        "headerLineSuffix": None,            ## inserted after each header text line, but before the new line
    }
}

yearsPattern = re.compile(r"Copyright\s*(?:\(\s*[C|c|©]\s*\)\s*)?([0-9][0-9][0-9][0-9](?:-[0-9][0-9]?[0-9]?[0-9]?))",re.IGNORECASE)
licensePattern = re.compile(r"license",re.IGNORECASE)
emptyPattern = re.compile(r'^\s*$')

## -----------------------

## maps each extension to its processing type. Filled from tpeSettings during initialization
ext2type = {}
patterns = []

def parse_command_line(argv):
    """Parse command line argument. See -h option.

    Arguments:
      argv: arguments on the command line must include caller file name.

    """
    import textwrap

    ## first get all the names of our own templates
    ## for this get first the path of this file
    templatesDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"templates")
    ## get all the templates in the templates directory
    templates = [f for f in get_paths("*.tmpl",templatesDir)]
    templates = [os.path.splitext(os.path.basename(t))[0] for t in templates]
    templates_str = ", ".join(sorted(templates))
    ## get all supported extensions
    patterns = set()
    for t in typeSettings:
        settings = typeSettings[t]
        exts = settings["extensions"]
        for ext in exts:
            patterns.add("*"+ext)
    patterns_str = ", ".join(sorted(patterns))

    example = textwrap.dedent("""
        {}
        Examples:
        # Add a new license header or replace any existing one based on 
        # the lgpl-v3 template.
        # Process all files of supported type in or below the current directory.
        # Use "Eager Hacker" as the copyright owner.
        {}
        {} -t lgpl-v3 -c "Eager Hacker"
        """).format('='*50, '='*50, os.path.basename(argv[0]))

    formatter_class = argparse.RawDescriptionHelpFormatter

    extra_templ = textwrap.fill("Supported template names (TMPL): " + templates_str, 75)
    extra_pat = textwrap.fill(("If EXCLUDE is not specified, license header will "
                                + "be added to all files with following extensions: "
                                + patterns_str), 75)
    extra_info = extra_templ + "\n\n" + extra_pat + "\n\n" + example
    parser = argparse.ArgumentParser(description="Python license header updater",
                                     epilog=extra_info,
                                     formatter_class=formatter_class)
    parser.add_argument("-V", "--version", action="version",
                        version="%(prog)s {}".format(__version__))
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity (can be specified "
                        "multiple times)")
    parser.add_argument("-d", "--dir", dest="dir", nargs=1, type=str, default=".",
                        help="The directory to recursively process.")
    parser.add_argument("-t", "--tmpl", dest="tmpl", nargs=1, type=str, default=None,
                        help="Template name or file to use.")
    parser.add_argument("-y", "--years", dest="years", nargs=1, type=str, default=None,
                        help="Year or year range to use.")
    parser.add_argument("-o", "--owner", dest="owner", nargs=1, type=str, default=None,
                        help="Name of copyright owner to use.")
    parser.add_argument("-n", "--projname", dest="projectname", nargs=1, type=str, default=None,
                        help="Name of project to use.")
    parser.add_argument("-u", "--projurl", dest="projecturl", nargs=1, type=str, default=None,
                        help="Url of project to use.")
    parser.add_argument("-f", "--include-file", dest="includefile", type=bool, default=True,
                        help="Include the file name in the header or not")
    parser.add_argument("-e", "--exclude", action="append", type=str, default=None,
                        help="Exclude files that have this pattern")
    arguments = parser.parse_args(argv[1:])

    # Sets log level to WARN going more verbose for each new -V.
    log.setLevel(max(3 - arguments.verbose_count, 0) * 10)
    return arguments


def get_paths(patterns, start_dir="."):
    """Retrieve files that match any of the glob patterns from the start_dir and below."""
    for root, dirs, files in os.walk(start_dir):
        names = []
        for pattern in patterns:
            names += fnmatch.filter(files, pattern)
        for name in names:
            path = os.path.join(root, name)
            yield path

# return an array of lines, with all the variables replaced
# throws an error if a variable cannot be replaced
def read_template(templateFile, fileName, dict):
    with io.open(templateFile,'r') as f:
        lines = f.readlines()
    try:
        dict["file_name"] = fileName if dict["includefile"] else "This file"
    except:
        dict["file_name"] = "This file" # don't ask for permission ask for forgiveness
    lines = [Template(line).substitute(dict) for line in lines]  ## use safe_substitute if we do not want an error
    return lines

# format the template lines for the given type
def for_type(templatelines,type):
    lines = []
    settings = typeSettings[type]
    headerStartLine = settings["headerStartLine"]
    headerEndLine = settings["headerEndLine"]
    headerLinePrefix = settings["headerLinePrefix"]
    headerLineSuffix = settings["headerLineSuffix"]
    if headerStartLine is not None:
        lines.append(headerStartLine)
    for l in templatelines:
        tmp = l
        if headerLinePrefix is not None:
            tmp = headerLinePrefix + tmp
        if headerLineSuffix is not None:
            tmp = tmp + headerLineSuffix
        lines.append(tmp)
    if headerEndLine is not None:
        lines.append(headerEndLine)
    return lines


## read a file and return a dictionary with the following elements:
## lines: array of lines
## skip: number of lines at the beginning to skip (always keep them when replacing or adding something)
##   can also be seen as the index of the first line not to skip
## headStart: index of first line of detected header, or None if non header detected
## headEnd: index of last line of detected header, or None
## yearsLine: index of line which contains the copyright years, or None
## haveLicense: found a line that matches a pattern that indicates this could be a license header
## settings: the type settings
## If the file is not supported, return None
def read_file(file):
    skip = 0
    headStart = None
    headEnd = None
    yearsLine = None
    haveLicense = False
    extension = os.path.splitext(file)[1]
    logging.debug("File extension is %s",extension)
    ## if we have no entry in the mapping from extensions to processing type, return None
    type = ext2type.get(extension)
    logging.debug("Type for this file is %s",type)
    if not type:
        return None
    settings = typeSettings.get(type)
    with io.open(file,'r', encoding='utf8') as f:
        lines = f.readlines()
    ## now iterate throw the lines and try to determine the various indies
    ## first try to find the start of the header: skip over shebang or empty lines
    keepFirst = settings.get("keepFirst")
    keepMore = settings.get("keepMore")
    blockCommentStartPattern = settings.get("blockCommentStartPattern")
    blockCommentEndPattern = settings.get("blockCommentEndPattern")
    lineCommentStartPattern = settings.get("lineCommentStartPattern")
    i = 0
    for line in lines:
        if i==0 and keepFirst and keepFirst.findall(line):
            skip = skip + 1
        elif i>0 and keepMore and keepMore.findall(line):
            skip = skip + 1
        elif emptyPattern.findall(line):
            pass
        elif blockCommentStartPattern and blockCommentStartPattern.findall(line):
            headStart = i
            break
        elif lineCommentStartPattern and lineCommentStartPattern.findall(line):
            headStart = i
            break
        elif not blockCommentStartPattern and lineCommentStartPattern and lineCommentStartPattern.findall(line):
            headStart = i
            break
        else:
            ## we have reached something else, so no header in this file
            #logging.debug("Did not find the start giving up at line %s, line is >%s<",i,line)
            return {"type":type, "lines":lines, "skip":skip, "headStart":None, "headEnd":None, "yearsLine": None, "settings":settings, "haveLicense": haveLicense}
        i = i+1
    #logging.debug("Found preliminary start at %s",headStart)
    ## now we have either reached the end, or we are at a line where a block start or line comment occurred
    # if we have reached the end, return default dictionary without info
    if i == len(lines):
        #logging.debug("We have reached the end, did not find anything really")
        return {"type":type, "lines":lines, "skip":skip, "headStart":headStart, "headEnd":headEnd, "yearsLine": yearsLine, "settings":settings, "haveLicense": haveLicense}
    # otherwise process the comment block until it ends
    if blockCommentStartPattern:
        for j in range(i,len(lines)):
            #logging.debug("Checking line %s",j)
            if licensePattern.findall(lines[j]):
                haveLicense = True
            elif blockCommentEndPattern.findall(lines[j]):
                return {"type":type, "lines":lines, "skip":skip, "headStart":headStart, "headEnd":j, "yearsLine": yearsLine, "settings":settings, "haveLicense": haveLicense}
            elif yearsPattern.findall(lines[j]):
                haveLicense = True
                yearsLine = j
        # if we went through all the lines without finding an end, maybe we have some syntax error or some other
        # unusual situation, so lets return no header
        #logging.debug("Did not find the end of a block comment, returning no header")
        return {"type":type, "lines":lines, "skip":skip, "headStart":None, "headEnd":None, "yearsLine": None, "settings":settings, "haveLicense": haveLicense}
    else:
        for j in range(i,len(lines)-1):
            if lineCommentStartPattern.findall(lines[j]) and licensePattern.findall(lines[j]):
                haveLicense = True
            elif not lineCommentStartPattern.findall(lines[j]):
                return {"type":type, "lines":lines, "skip":skip, "headStart":i, "headEnd":j-1, "yearsLine": yearsLine, "settings":settings, "haveLicense": haveLicense}
            elif yearsPattern.findall(lines[j]):
                haveLicense = True
                yearsLine = j
        ## if we went through all the lines without finding the end of the block, it could be that the whole
        ## file only consisted of the header, so lets return the last line index
        return {"type":type, "lines":lines, "skip":skip, "headStart":i, "headEnd":len(lines)-1, "yearsLine": yearsLine, "settings":settings, "haveLicense": haveLicense}

def make_backup(file):
    copyfile(file,file+".bak")

def main():
    """Main function."""
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    ## init: create the ext2type mappings
    for t in typeSettings:
        settings = typeSettings[t]
        exts = settings["extensions"]
        for ext in exts:
            ext2type[ext] = t
            patterns.append("*"+ext)
    try:
        error = False
        settings = {
        }
        templateLines = None
        arguments = parse_command_line(sys.argv)
        if arguments.dir:
            start_dir = arguments.dir[0]
        else:
            start_dir = "."
        if arguments.years:
            settings["years"] = arguments.years[0]
        if arguments.owner:
            settings["owner"] = arguments.owner[0]
        if arguments.projectname:
            settings["projectname"] = arguments.projectname[0]
        if arguments.projecturl:
            settings["projecturl"] = arguments.projecturl[0]
        if arguments.includefile:
            settings["includefile"] = arguments.includefile

        if arguments.exclude:
            exclude = arguments.exclude
        else:
            exclude = []

        if arguments.tmpl:
            opt_tmpl = arguments.tmpl[0]
            ## first get all the names of our own templates
            ## for this get first the path of this file
            templatesDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"templates")
            print("file path: ",os.path.abspath(__file__))
            ## get all the templates in the templates directory
            templates = [f for f in get_paths("*.tmpl",templatesDir)]
            templates = [(os.path.splitext(os.path.basename(t))[0],t) for t in templates]
            ## filter by trying to match the name against what was specified
            tmpls = [t for t in templates if opt_tmpl in t[0]]

        if not error:
            #logging.debug("Got template lines: %s",templateLines)
            ## now do the actual processing: if we did not get some error, we have a template loaded or no template at all
            ## if we have no template, then we will have the years.
            ## now process all the files and either replace the years or replace/add the header
            logging.debug("Processing directory %s",start_dir)
            logging.debug("Patterns: %s",patterns)
            for file in get_paths(patterns,start_dir):
                passed = True
                for exc in exclude:
                    if exc in file:
                        passed = False
                if not passed:
                    continue
                logging.debug("Processing file: %s",file)
                fileName = os.path.basename(file)
                
                dict = read_file(file)
                if not dict:
                    logging.debug("File not supported %s",file)
                    continue
                # logging.debug("DICT for the file: %s",dict)
                logging.debug("Info for the file: headStart=%s, headEnd=%s, haveLicense=%s, skip=%s",dict["headStart"],dict["headEnd"],dict["haveLicense"],dict["skip"])
                lines = dict["lines"]

                ## if we have a template name specified, try to get or load the template
                if arguments.tmpl:
                    if len(tmpls) == 1:
                        tmplName = tmpls[0][0]
                        tmplFile = tmpls[0][1]
                        print("Using template ",tmplName)
                        templateLines = read_template(tmplFile,fileName,settings)
                    else:
                        if len(tmpls) == 0:
                            ## check if we can interpret the option as file
                            if os.path.isfile(opt_tmpl):
                                print("Using file ",os.path.abspath(opt_tmpl))
                                templateLines = read_template(os.path.abspath(opt_tmpl),fileName,settings)
                            else:
                                print("Not a built-in template and not a file, cannot proceed: ", opt_tmpl)
                                print("Built in templates: ", ", ".join([t[0] for t in templates]))
                                error = True
                                break
                        else:
                            ## notify that there are multiple matching templates
                            print("There are multiple matching template names: ",[t[0] for t in tmpls])
                            error = True
                            break
                else: # no tmpl parameter
                    if not arguments.years:
                        print("No template specified and no years either, nothing to do")
                        error = True
                        break

                ## if we have a template: replace or add
                if templateLines:
                    # make_backup(file)
                    with io.open(file,'w', encoding='utf8') as fw:
                        ## if we found a header, replace it
                        ## otherwise, add it after the lines to skip
                        headStart = dict["headStart"]
                        headEnd = dict["headEnd"]
                        haveLicense = dict["haveLicense"]
                        type = dict["type"]
                        skip = dict["skip"]
                        if headStart is not None and headEnd is not None and haveLicense:
                            print("Replacing header in file ",file)
                            ## first write the lines before the header
                            fw.writelines(lines[0:headStart])
                            ## now write the new header from the template lines
                            fw.writelines(for_type(templateLines,type))
                            ## now write the rest of the lines
                            fw.writelines(lines[headEnd+1:])
                        else:
                            print("Adding header to file ",file)
                            fw.writelines(lines[0:skip])
                            fw.writelines(for_type(templateLines,type))
                            fw.writelines(lines[skip:])
                    ## TODO: remove backup unless option -b
                else: ## no template lines, just update the line with the year, if we found a year
                    yearsLine = dict["yearsLine"]
                    if yearsLine is not None:
                        # make_backup(file)
                        with io.open(file, 'w', encoding='utf8') as fw:
                            print("Updating years in file ",file)
                            fw.writelines(lines[0:yearsLine])
                            fw.write(yearsPattern.sub(arguments.years,lines[yearsLine]))
                        ## TODO: remove backup
    finally:
        logging.shutdown()


if __name__ == "__main__":
    sys.exit(main())
