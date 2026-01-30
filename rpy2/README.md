# rpy2

This is a demo python Shiny application that uses `rpy2`. It shows a visualization from python and from R.

The `_dependencies.R` file is there so the `manifest.json` file can be successfully generated:
```
rsconnect::writeManifest(".", appMode="python-shiny")
```
