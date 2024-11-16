import os
import subprocess
import platform
from colorama import init, Fore, Style
try:
    import readline
except ImportError:
    import pyreadline3 as readline
import glob
import re
import psutil
import datetime
import getpass

# Initialize colorama for Windows color support
init()

class CustomTerminal:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.command_history = []
        self.running = True
        self.custom_commands = {
            'exit': self.exit_terminal,
            'clear': self.clear_screen,
            'history': self.show_history,
            'help': self.show_help,
            'nff': self.show_neofetch,
        }
        # Initialize readline with our custom completer
        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')
        # Set word delimiters for completion
        readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>?')

    def predict_command(self, partial_cmd):
        if not partial_cmd:
            return []
        
        # Find matches in history
        matches = [cmd for cmd in self.command_history 
                  if cmd.startswith(partial_cmd)]
        
        # Find matches in custom commands
        custom_matches = [cmd for cmd in self.custom_commands.keys() 
                         if cmd.startswith(partial_cmd)]
        
        # Combine unique matches
        all_matches = list(set(matches + custom_matches))
        return sorted(all_matches, key=len)

    def complete(self, text, state):
        # Get the current line buffer
        line = readline.get_line_buffer()
        
        # If we're at the start of the line, complete commands
        if line.strip() == text:
            matches = self.predict_command(text)
            matches.extend([f for f in glob.glob(text + '*') if os.path.isfile(f)])
            matches.extend([d + os.sep for d in glob.glob(text + '*') if os.path.isdir(d)])
        # Otherwise, complete file/directory names
        else:
            # Extract the last word for completion
            last_word = text.split()[-1] if text else ''
            path = os.path.expanduser(last_word)
            
            if os.path.isabs(path):
                base_path = os.path.dirname(path)
                pattern = os.path.basename(path) + '*'
            else:
                base_path = self.current_dir
                pattern = path + '*'
            
            try:
                # Get files and directories
                matches = []
                if os.path.isdir(base_path):
                    search_path = os.path.join(base_path, pattern)
                    matches.extend([f + ('/' if os.path.isdir(f) else ' ') 
                                  for f in glob.glob(search_path)])
            except Exception:
                matches = []
        
        # Return the state-th match or None if no more matches
        try:
            return matches[state]
        except IndexError:
            return None

    def clear_screen(self):
        os.system('cls' if platform.system() == 'Windows' else 'clear')

    def show_prompt(self):
        return f"{Fore.GREEN}{self.current_dir}{Style.RESET_ALL}> "

    def exit_terminal(self):
        self.running = False
        print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")

    def show_history(self):
        for i, cmd in enumerate(self.command_history, 1):
            print(f"{i}. {cmd}")

    def show_help(self):
        """Show available commands and their descriptions."""
        print(f"\n{Fore.CYAN}Available Commands:{Style.RESET_ALL}")
        print(f"  {'Command':<15} Description")
        print(f"  {'-'*15} {'-'*30}")
        commands = {
            'exit': 'Exit the terminal',
            'clear': 'Clear the screen',
            'history': 'Show command history',
            'help': 'Show this help message',
            'nff': 'Show system information in a neofetch-like format',
            '<TAB>': 'Auto-complete commands and paths',
            '<UP/DOWN>': 'Navigate through command history'
        }
        for cmd, desc in commands.items():
            print(f"  {cmd:<15} {desc}")
        print()

    def get_windows_logo(self):
        return [
            f"{Fore.CYAN}                                ..,",
            f"{Fore.CYAN}                    ....,,:;+ccllll",
            f"{Fore.CYAN}      ...,,+:;  cllllllllllllllllll",
            f"{Fore.CYAN},cclllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}                                    ",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}llllllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}`'ccllllllllll  lllllllllllllllllll",
            f"{Fore.CYAN}      `' \\\\*::  :ccllllllllllllllll",
            f"{Fore.CYAN}                       ````''*::cll",
            f"{Fore.CYAN}                                 ``"
        ]

    def get_system_info(self):
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_freq = f"{cpu_freq.current:.2f}MHz"
        else:
            cpu_freq = "Unknown"

        memory = psutil.virtual_memory()
        memory_total = f"{memory.total / (1024**3):.2f}GB"
        memory_used = f"{memory.used / (1024**3):.2f}GB"

        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time

        info = {
            f"{Fore.GREEN}OS{Style.RESET_ALL}": f"{platform.system()} {platform.release()}",
            f"{Fore.GREEN}Host{Style.RESET_ALL}": platform.node(),
            f"{Fore.GREEN}Kernel{Style.RESET_ALL}": platform.version(),
            f"{Fore.GREEN}Uptime{Style.RESET_ALL}": f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m",
            f"{Fore.GREEN}CPU{Style.RESET_ALL}": platform.processor(),
            f"{Fore.GREEN}CPU Frequency{Style.RESET_ALL}": cpu_freq,
            f"{Fore.GREEN}Memory{Style.RESET_ALL}": f"{memory_used} / {memory_total}",
            f"{Fore.GREEN}User{Style.RESET_ALL}": getpass.getuser(),
            f"{Fore.GREEN}Shell{Style.RESET_ALL}": "Cloudy Terminal",
        }
        return info

    def show_neofetch(self):
        """Display system information in a neofetch-like format"""
        logo = self.get_windows_logo()
        info = self.get_system_info()
        
        # Calculate the maximum length of information lines
        max_info_length = max(len(f"{k}: {v}") for k, v in info.items())
        
        # Combine logo and information side by side
        print("\n")
        for i in range(max(len(logo), len(info))):
            if i < len(logo):
                logo_line = logo[i]
            else:
                logo_line = " " * 40
                
            if i < len(info):
                key = list(info.keys())[i]
                value = info[list(info.keys())[i]]
                info_line = f"{key}: {value}"
            else:
                info_line = ""
                
            print(f"{logo_line}    {info_line}")
        print(f"{Style.RESET_ALL}\n")

    def execute_command(self, command):
        if not command:
            return

        self.command_history.append(command)
        parts = command.split()
        cmd = parts[0].lower()

        if cmd in self.custom_commands:
            self.custom_commands[cmd]()
        else:
            try:
                result = subprocess.run(parts, shell=True, text=True, capture_output=True)
                if result.stdout:
                    print(result.stdout, end='')
                if result.stderr:
                    print(f"{Fore.RED}{result.stderr}{Style.RESET_ALL}", end='')
            except Exception as e:
                print(f"{Fore.RED}Error executing command: {e}{Style.RESET_ALL}")

    def run(self):
        self.clear_screen()
        self.show_neofetch()
        print(f"{Fore.CYAN}Welcome to Cloudy Terminal! Type 'help' for available commands.{Style.RESET_ALL}")

        while self.running:
            try:
                command = input(self.show_prompt()).strip()
                self.execute_command(command)
            except KeyboardInterrupt:
                print("\nUse 'exit' command to quit")
            except Exception as e:
                print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    terminal = CustomTerminal()
    terminal.run()
