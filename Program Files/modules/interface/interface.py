import re
import shutil
import time
from typing import Literal, Any

from modules.other.project import Project

from .foreground import foreground
from .colors import Color
from .styles import Style
from .aligntment import Alignment
from .background import background
from .clear import clear


class Interface:
    terminal_size = shutil.get_terminal_size()
    terminal_width: int = terminal_size.columns
    terminal_height: int = terminal_size.lines

    width: int = terminal_width - 48
    
    BORDER_COLOR: str = foreground(Color.BORDER)
    DEFAULT: str = '\033[0m'
    BACKGROUND: str = '#1f1f1f'
    ANSI_COLOR_REGEX = re.compile(r'\x1b\[[0-9;]*m')  # ChatGPT

    data: list[dict[str, Any]] = []


    def __init__(
            self,
            section: str,
            description: str = None,
            color: str = Color.SECTION_TITLE,
            style: Literal[
                Style.BOLD,
                Style.ITALIC,
                Style.UNDERLINE,
                Style.DOUBLE_UNDERLINE,
                Style.OVERLINE,
                Style.STRIKETHROUGH,
                Style.HIDDEN,
                Style.DIM,
                Style.BLINK
                ] = '',
            alignment: Literal[
                Alignment.LEFT,
                Alignment.RIGHT,
                Alignment.CENTER
            ] = Alignment.LEFT,
            background_color: str = None
        ) -> None:

        self.section = section
        self.description = description

        background(background_color or self.BACKGROUND)

        title_color = foreground(Color.TITLE)

        if color != '':
            color = foreground(color)
        else:
            color = self.DEFAULT

        self.data = []
        
        self.data.append(
            {
                'gap': '-',
                'type': 'divider',
                'color': self.BORDER_COLOR,
            }
        )
        self.data.append(
            {
                'data': Project.NAME,
                'color': title_color,
                'alignment': Alignment.LEFT
            }
        )
        self.data.append(
            {
                'data': f'Version: {Project.VERSION}',
                'color': title_color,
                'alignment': Alignment.LEFT
            }
        )


        self.data.append(
            {
                'gap': '-',
                'type': 'divider',
                'color': self.BORDER_COLOR,
            }
        )
        self.data.append(
            {
                'type': 'divider',
                'color': self.BORDER_COLOR,
            }
        )
        self.data.append(
            {
                'data': section,
                'color': color,
                'alignment': alignment,
                'style': style
            }
        )
        if description != None:
            self.data.append(
                {
                    'data': description,
                    'color': color,
                    'alignment': alignment,
                    'style': style
                }
            )
        self.data.append(
            {
                'type': 'divider',
                'color': self.BORDER_COLOR,
            }
        )
        self.data.append(
            {
                'gap': '-',
                'type': 'divider',
                'color': self.BORDER_COLOR,
            }
        )

        self._on_update()


    def _on_update(self) -> None:
        self.terminal_size = shutil.get_terminal_size()
        self.terminal_width: int = self.terminal_size.columns
        self.terminal_height: int = self.terminal_size.lines

        self.width = self.terminal_width - 48

        clear()

        for line in self.data:
            color = line.get('color', '')

            if line.get('type', None) == 'divider':
                data: str | list[str] = f'{self.BORDER_COLOR}{'+' if line.get('gap', ' ') == '-' else '|'}{line.get('gap', ' ')}{color}{line.get('style', '')}{line.get('gap', ' ')*self.width}{self.BORDER_COLOR}{line.get('gap', ' ')}{'+' if line.get('gap', ' ') == '-' else '|'}{self.DEFAULT}'
            else:
                text = line['data']

                if len(self._strip_ansi(text)) > self.width:
                    text = self._wrapped_text(text)
                
                if isinstance(text, list):
                    data = [self._format_line(item, line) for item in text]

                else:
                    data = self._format_line(text, line)
            
            if isinstance(data, list):
                for line in data:
                    print(f'{' '*(int((self.terminal_width-self.width)/2))}{line}')
            else:
                print(f'{' '*(int((self.terminal_width-self.width)/2))}{data}')


    def _strip_ansi(self, text: str) -> str:  # Generated by ChatGPT
        """Remove ANSI color codes from the string for length calculation."""
        return re.sub(self.ANSI_COLOR_REGEX, '', text)


    def _format_line(self, text: str, line: dict) -> str:  # Generated by ChatGPT, then modified because it was terrible
        """Format the line with color and alignment, ignoring color codes for padding."""
        visible_text_length = len(self._strip_ansi(text))
        padding_length = self.width - visible_text_length

        if line.get('alignment', Alignment.LEFT) == Alignment.RIGHT:
            formatted_text = f'{self.BORDER_COLOR}|{line.get('gap', ' ')}{' ' * padding_length}{line.get('color', '')}{line.get('style', '')}{text}{self.DEFAULT}{self.BORDER_COLOR}{line.get('gap', ' ')}|{self.DEFAULT}'
        elif line.get('alignment', Alignment.LEFT) == Alignment.CENTER:
            left_padding = padding_length // 2
            right_padding = padding_length - left_padding
            formatted_text = f'{self.BORDER_COLOR}|{line.get('gap', ' ')}{' ' * left_padding}{line.get('color', '')}{line.get('style', '')}{text}{self.DEFAULT}{' ' * right_padding}{self.BORDER_COLOR}{line.get('gap', ' ')}|{self.DEFAULT}'
        else:
            formatted_text = f'{self.BORDER_COLOR}|{line.get('gap', ' ')}{line.get('color', '')}{line.get('style', '')}{text}{self.DEFAULT}{' ' * padding_length}{self.BORDER_COLOR}{line.get('gap', ' ')}|{self.DEFAULT}'

        return formatted_text
    

    def _wrapped_text(self, data: str) -> list[str]:
        words = data.split()
        current_line = words[0]

        result = []
        for word in words[1:]:
            if len(current_line) + len(f' {word}') < self.width:
                current_line += f' {word}'
            else:
                result.append(current_line)
                current_line = word
        result.append(current_line)
        return result
    

    def add_line(
            self,
            text: str,
            color: str = '',
            style: Literal[
                Style.BOLD,
                Style.ITALIC,
                Style.UNDERLINE,
                Style.DOUBLE_UNDERLINE,
                Style.OVERLINE,
                Style.STRIKETHROUGH,
                Style.HIDDEN,
                Style.DIM,
                Style.BLINK
                ] = '',
            alignment: Literal[
                Alignment.LEFT,
                Alignment.RIGHT,
                Alignment.CENTER
            ] = Alignment.LEFT,
            is_divider: bool = False
        ) -> None:

        if color != '':
            color = foreground(color)
        else:
            color = self.DEFAULT

        if is_divider == True:
            self.data.append(
                {
                    'gap': text,
                    'type': 'divider',
                    'color': self.BORDER_COLOR,
                }
            )
        
        else:
            self.data.append(
                {
                    'data': text,
                    'color': color,
                    'alignment': alignment,
                    'style': style
                }
            )

        self._on_update()


    def add_divider(self) -> None:
        self.data.append(
            {
                'gap': '-',
                'type': 'divider',
                'color': self.BORDER_COLOR,
            }
        )
        self._on_update()
    

    def remove_last(self, count: int = 1) -> None:
        for i in range(count):
            self.data.pop()
        self._on_update()


    def get_input(self,  # This looks so goofy
        text: str,
        text_color: str = '',
        text_style: Literal[
            Style.BOLD,
            Style.ITALIC,
            Style.UNDERLINE,
            Style.DOUBLE_UNDERLINE,
            Style.OVERLINE,
            Style.STRIKETHROUGH,
            Style.HIDDEN,
            Style.DIM,
            Style.BLINK
            ] = '',
        input_color: str = '',
        input_style: Literal[
            Style.BOLD,
            Style.ITALIC,
            Style.UNDERLINE,
            Style.DOUBLE_UNDERLINE,
            Style.OVERLINE,
            Style.STRIKETHROUGH,
            Style.HIDDEN,
            Style.DIM,
            Style.BLINK
            ] = '',
        indent: int = 0) -> str:

        if text_color != '':
            text_color = foreground(text_color)
        if input_color != '':
            input_color = foreground(input_color)

        line: str = f'{' '*indent}{text_color}{text_style}{text}{self.DEFAULT}{input_color}{input_style}'
        response = input(f'{' '*(int(((self.terminal_width-self.width)/2)+2))}{line}')
        
        print(self.DEFAULT, end='')
        
        return response
    
    def reset(self) -> None:
        var: int = 8 if self.data[6].get('type', None) == 'divider' else 9
        self.data = self.data[:var]
        self._on_update()
    

    def change_section_description(self, description: str = None) -> None:
        section_description: dict = self.data[6]

        if section_description.get('type', None) != 'divider':
            self.data.pop(6)

        if description is not None:
            self.data.insert(
                6,
                {
                    'data': description,
                    'color': self.data[5].get('color', Color.SECTION_TITLE),
                    'alignment': self.data[5].get('alignment', Alignment.LEFT),
                    'style': self.data[5].get('style', '')
                }
            )
            self.data.insert(
                7,
                {
                    'gap': ' ',
                    'type': 'divider'
                }
            )
            self.data.insert(
                8,
                {
                    'gap': '-',
                    'type': 'divider',
                    'color': self.BORDER_COLOR,
                }
            )