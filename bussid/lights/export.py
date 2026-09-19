from pathlib import Path
from shared.package_export import export_light_package
def export(light_type:str,output:Path)->Path: return export_light_package(light_type,output,"bussid")
