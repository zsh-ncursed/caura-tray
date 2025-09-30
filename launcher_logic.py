import subprocess
import shlex
import logging
import os
from typing import List, Union

class ApplicationLauncher:
    """
    Handles safe launching of applications with proper error handling.
    """
    
    def __init__(self):
        pass
    
    def launch_application(self, command: str) -> bool:
        """
        Launch an application using the provided command.
        
        Args:
            command (str): The command to execute
            
        Returns:
            bool: True if the application was launched successfully, False otherwise
        """
        try:
            # Parse the command to handle arguments properly
            # Use shlex.split for safe command splitting
            cmd_parts = shlex.split(command)
            
            # Launch the application using subprocess
            process = subprocess.Popen(
                cmd_parts,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                start_new_session=True  # Start in a new session to avoid hanging
            )
            
            # Log successful launch
            logging.info(f"Launched application with command: {command}")
            return True
            
        except FileNotFoundError:
            logging.error(f"Command not found: {command}")
            return False
        except PermissionError:
            logging.error(f"Permission denied for command: {command}")
            return False
        except Exception as e:
            logging.error(f"Error launching application '{command}': {e}")
            return False
    
    def validate_command(self, command: str) -> bool:
        """
        Validate if the command is safe to execute.
        This is a basic validation - in a more advanced implementation,
        we could have more sophisticated checks.
        
        Args:
            command (str): The command to validate
            
        Returns:
            bool: True if the command appears safe, False otherwise
        """
        if not command or not command.strip():
            return False
        
        # Check for potentially dangerous commands
        dangerous_patterns = [
            'rm -rf',
            'rm -rf /',
            ':(){:|:&};'
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                logging.warning(f"Potentially dangerous command detected: {command}")
                return False
        
        return True
    
    def launch_with_validation(self, command: str) -> bool:
        """
        Launch an application after validating the command.
        
        Args:
            command (str): The command to execute
            
        Returns:
            bool: True if the application was launched successfully, False otherwise
        """
        if not self.validate_command(command):
            logging.error(f"Command failed validation: {command}")
            return False
        
        return self.launch_application(command)

# For backward compatibility
def launch_application(command: str) -> bool:
    """
    Standalone function to launch an application.
    Wrapper around ApplicationLauncher for backward compatibility.
    
    Args:
        command (str): The command to execute
        
    Returns:
        bool: True if the application was launched successfully, False otherwise
    """
    launcher = ApplicationLauncher()
    return launcher.launch_with_validation(command)