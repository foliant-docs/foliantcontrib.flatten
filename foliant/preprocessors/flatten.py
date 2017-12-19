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

    def apply(self):
        chapters = self.config['chapters']
        flat_src = '\n'.join(flatten(chapters, self.working_dir))

        flat_src = includes.Preprocessor(
            self.project_path,
            self.config,
            {'recursive': False}
        ).process_includes(flat_src)

        for markdown_file in self.working_dir.rglob('*.md'):
            markdown_file.unlink()

        flat_src_file_path = self.working_dir / self.options['flat_src_file_name']

        with open(flat_src_file_path, 'w', encoding='utf8') as flat_src_file:
            flat_src_file.write(flat_src)
