# Project Flattener for Foliant

This preprocessor converts a Foliant project source directory into a single Markdown file containing all the sources, preserving order and inheritance.

This preprocessor is used by backends that require a single Markdown file as input instead of a directory. The Pandoc backend is one such example.

## Installation

```bash
$ pip install foliantcontrib.flatten
```

## Config

This preprocessor is required by Pandoc backend, so if you use it, you don’t need to install Flatten or enable it in the project config manually.

However, it’s still a regular preprocessor, and you can run it manually by listing it in `preprocessors`:

```yaml
preprocessors:
    - flatten
```

The preprocessor has a number of options with the following default values:

```yaml
preprocessors:
    - flatten:
        flat_src_file_name: __all__.md
        keep_sources: false
```

`flat_src_file_name`
:    Name of the flattened file that is created in the temporary working directory.

`keep_sources`
:   Flag that tells the preprocessor to keep Markdown sources in the temporary working directory after flattening. If set to `false`, all Markdown files excepting the flattened will be deleted from the temporary working directory.

> **Note**
>
> Flatten preprocessor uses Includes, so when you install Pandoc backend, Includes preprocessor will also be installed, along with Flatten.
