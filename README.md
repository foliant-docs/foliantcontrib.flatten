# Project Flattener for Foliant

This preprocessor converts a Foliant project source directory into a single Markdown file containing all the sources, preserving order and inheritance.

This preprocessor is used by backends that require a single Markdown file as input instead of a directory. The Pandoc backend is one such example.


## Installation

```shell
$ pip install foliantcontrib.flatten
```


## Config

This preprocessor is required by Pandoc backend, so if you use it, you don't need to install Flatten or enable it in the project config manually.

However, it's still a regular preprocessor, and you can run it manually by listing it in `preprocessors`:


```yaml
preprocessors:
  - flatten
```

The preprocessor has a number of options:

```yaml
preprocessors:
  - flatten:
      flat_src_file_name: flattened.md
      keep_sources: False
```

`flat_src_file_name`
:    the name of the flattened file that is created in the tmp directory. Default: `__all__.md`.

`keep_sources`
:   keep markdown sources in the temp dir after flattening. If `False` — all markdown files except the flattened will be deleted from working dir. Default: `False`.

> **Note**
>
> Flatten preprocessor uses includes, so when you install Pandoc backend, Includes preprocessor will also be installed, along with Flatten.
