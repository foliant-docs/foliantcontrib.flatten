from pathlib import Path
from typing import List, Dict
Chapter = str or Dict[str, str] or Dict[str, List['Chapter']]

from foliant.preprocessors.base import BasePreprocessor
from foliant.preprocessors import includes


def flatten(chapters: List[Chapter], working_dir: Path, buffer=[], heading_level=1) -> List[str]:
    for chapter in chapters:
        if isinstance(chapter, str):
            chapter_path = (working_dir / chapter).absolute()
            buffer.append(f'<include sethead="{heading_level}">{chapter_path}</include>')

        elif isinstance(chapter, dict):
            (title, value), = (*chapter.items(),)

            if title:
                buffer.append(f'{"#"*heading_level} {title}')

            if isinstance(value, str):
                chapter_path = (working_dir / value).absolute()
                buffer.append(
                    f'<include sethead="{heading_level}" nohead="true">{chapter_path}</include>'
                )

            elif isinstance(value, list):
                flatten(value, working_dir, buffer, heading_level+1)

    return buffer


class Preprocessor(BasePreprocessor):
    defaults = {'flat_src_file_name': '__all__.md'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('flatten')
        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def apply(self):
        chapters = self.config['chapters']

        self.logger.debug('Generating flat source with includes.')

        flat_src = '\n'.join(flatten(chapters, self.working_dir))

        self.logger.debug('Resolving includes.')

        flat_src_file_path = self.working_dir / self.options['flat_src_file_name']

        flat_src = includes.Preprocessor(
            self.context,
            self.logger,
            {'recursive': False}
        ).process_includes(flat_src_file_path, flat_src)

        for markdown_file in self.working_dir.rglob('*.md'):
            self.logger.debug(f'Removing {markdown_file}')
            markdown_file.unlink()

        with open(flat_src_file_path, 'w', encoding='utf8') as flat_src_file:
            self.logger.debug(f'Saving flat source into {flat_src_file_path}')
            flat_src_file.write(flat_src)
