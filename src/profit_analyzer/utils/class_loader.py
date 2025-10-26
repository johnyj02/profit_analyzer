import importlib
import inspect
import pkgutil
from typing import Any, Dict

def discover_classes(package_root:str) -> Dict[str, type]:
    """Walk all modules under the given package root and map class name -> class type."""
    class_map = {}
    pkg = importlib.import_module(package_root)
    for finder, name, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        try:
            mod = importlib.import_module(name)
        except Exception:
            continue
        for attr_name, obj in inspect.getmembers(mod, inspect.isclass):
            # only include classes defined in this module (avoid stdlib etc.)
            if obj.__module__ == mod.__name__:
                class_map[attr_name] = obj
    return class_map

def resolve_interpolations(args: dict, config: dict) -> dict:
    """Resolve ${path.to.value} placeholders in args using the config tree."""
    import re
    def get_from_path(path: str, tree: dict):
        node = tree
        for p in path.split('.'):
            node = node[p]
        return node

    def repl(match):
        path = match.group(1)
        return str(get_from_path(path, config))

    s = repr(args)
    out = re.sub(r"\$\{([^}]+)\}", repl, s)
    # eval back to dict safely using literal_eval
    from ast import literal_eval
    return literal_eval(out)

def initialize_from_config(config: dict, package_root: str = "profit_analyzer") -> Any:
    class_map = discover_classes(package_root)
    instances = []
    for module in config.get("modules", []):
        class_name = module["class"]
        args = module.get("args", {})
        args = resolve_interpolations(args, config)
        if class_name not in class_map:
            raise ImportError(f"Class {class_name} not found in discovered modules under {package_root}")
        cls = class_map[class_name]
        instances.append(cls(**args))
    return instances
