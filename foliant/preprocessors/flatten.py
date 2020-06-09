import re

from pathlib import Path
from typing import List, Dict

from foliant.preprocessors.base import BasePreprocessor
from foliant.preprocessors import includes

Chapter = str or Dict[str, str] or Dict[str, List['Chapter']]


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
                flatten(value, working_dir, buffer, heading_level + 1)

    return buffer


class Preprocessor(BasePreprocessor):
    defaults = {
        'flat_src_file_name': '__all__.md',
        'keep_sources': False
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('flatten')
        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def _process_local_links(self, source: str) -> str:
        '''
        Cut out file path from local links keeping only the anchor.

        Since we are flattening all chapters into one file, all local links
        (links to other chapters or local Markdown files) will stop working.
        We assume that all content which is referenced by local links
        was flattened into the current document. It means that we may remove
        file paths from all local links and keep only anchors.

        This doesn’t cover the case with duplicate anchors in flattened document.

        :param source: source file where the links should be processed.
        :returns: processed source with paths cut out from all local links.
        '''
        def _fix_links(match) -> str:
            if match.group('path').startswith('http'):
                # external links are left unchanged
                return match.group(0)

            fixed_link = f'[{match.group("caption")}]({match.group("anchor")})'
            return fixed_link

        pattern = re.compile(r'\[(?P<caption>.+?)\]\((?P<path>[^\)]+?)(?P<anchor>#[^\)]+)\)')
        return pattern.sub(_fix_links, source)

    def apply(self):
        self.logger.debug('Applying preprocessor')

        chapters = self.config['chapters']

        self.logger.debug('Generating flat source with Includes')

        flat_src = '\n'.join(flatten(chapters, self.working_dir))

        self.logger.debug('Resolving include statements')

        flat_src_file_path = self.working_dir / self.options['flat_src_file_name']

        flat_src = includes.Preprocessor(
            self.context,
            self.logger,
            {'recursive': False}
        ).process_includes(flat_src_file_path, flat_src)

        flat_src = self._process_local_links(flat_src)

        if not self.options['keep_sources']:
            for markdown_file in self.working_dir.rglob('*.md'):
                self.logger.debug(f'Removing the file: {markdown_file}')

                markdown_file.unlink()

        with open(flat_src_file_path, 'w', encoding='utf8') as flat_src_file:
            self.logger.debug(f'Saving flat source into the file: {flat_src_file_path}')

            flat_src_file.write(flat_src)

        self.logger.debug('Preprocessor applied')
