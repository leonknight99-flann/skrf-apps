import glob
import importlib
import os.path
import sys
import traceback
from collections import OrderedDict

from . import analyzer_cmt

loaded_analyzers = OrderedDict()

try:
    this_path = os.path.normpath(os.path.dirname(__file__))
    print(f"Loading analyzers from {this_path:s}")
    analyzer_modules = glob.glob(this_path + "/analyzer_*.py")

    print(analyzer_modules)

    sys.path.insert(0, this_path)
    for analyzer in analyzer_modules:
        module_name = os.path.basename(analyzer)[:-3]

        try:
            importlib.import_module(module_name)
            module = importlib.import_module(module_name)
        except Exception:
            etype, value, tb = sys.exc_info()
            err_msg = "\n".join(traceback.format_exception(etype, value, tb))
            print(f"did not import {module_name:s}\n\n{err_msg:s}")
            continue

        if module.Analyzer.NAME in loaded_analyzers.keys():
            print(f"overwriting Analyzer {module.Analyzer.NAME:s} in selection")

        loaded_analyzers[module.Analyzer.NAME] = module.Analyzer
    sys.path.pop(0)
except ImportError:
    pass

print(loaded_analyzers)

# analyzers = OrderedDict()
# this_path = os.path.normpath(os.path.dirname(__file__))
# analyzer_modules = glob.glob(this_path + "/analyzer_*.py")
# sys.path.insert(0, this_path)
# for analyzer in analyzer_modules:
#     module_name = os.path.basename(analyzer)[:-3]
#     module = importlib.import_module(module_name)
#     analyzers[module.Analyzer.NAME] = module.Analyzer
# sys.path.pop(0)
