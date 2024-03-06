 # Do the "Normal" installation; for linux and all that.
  # @see https://stackoverflow.com/questions/51913361/difference-between-pip-install-options-ignore-installed-and-force-reinstall
  conda env create -f environment.yml || conda env update -f environment.yml
