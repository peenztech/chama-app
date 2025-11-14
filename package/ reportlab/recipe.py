from pythonforandroid.recipe import PythonRecipe

class ReportLabRecipe(PythonRecipe):
    # Name of the recipe
    name = "reportlab"
    
    # Version (doesn't matter much here because we're not downloading)
    version = "4.4.4"

    # Dummy URL; will not be used
    url = ""

    # Tell P4A not to call hostpython via targetpython
    call_hostpython_via_targetpython = False
    
    # Use the version installed in hostpython
    install_in_hostpython = True

    # No need to download or build
    depends = []
    
    # Skip any patching / build steps
    def build_arch(self, arch):
        self.ctx.symlink_recipe_python_libs(self, arch)

# Make an instance for P4A
recipe = ReportLabRecipe()
