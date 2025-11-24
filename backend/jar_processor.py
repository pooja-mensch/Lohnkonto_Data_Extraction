"""
JAR Processor Service
Handles interaction with Lohnkonten-1.0.3.jar for PDF processing
"""

import subprocess
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class JarProcessor:
    """
    Service to process PDF files using the Lohnkonten JAR.
    """

    def __init__(self, jar_path: str = None, template_path: str = None, output_dir: str = None):
        """
        Initialize the JAR processor.

        Args:
            jar_path: Path to the Lohnkonten JAR file (default: ./Lohnkonten-1.0.3.jar)
            template_path: Path to the template file (default: ./template.xlsx)
            output_dir: Directory for output files (default: ./output)
        """
        # Get the base directory (where main.py or api.py is located)
        self.base_dir = Path(__file__).parent

        # Set default paths relative to base directory
        self.jar_path = jar_path or str(self.base_dir / "Lohnkonten-1.0.3.jar")
        self.template_path = template_path or str(self.base_dir / "template.xlsx")
        self.output_dir = output_dir or str(self.base_dir / "output")

        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Verify JAR exists
        if not os.path.exists(self.jar_path):
            raise FileNotFoundError(f"JAR file not found: {self.jar_path}")

        # Verify template exists
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Template file not found: {self.template_path}")

    def check_java_installation(self) -> Dict[str, Any]:
        """
        Check if Java is installed and get version info.

        Returns:
            Dictionary with Java installation status
        """
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            version_output = result.stderr if result.stderr else result.stdout

            return {
                "installed": True,
                "version_info": version_output.strip()
            }
        except FileNotFoundError:
            return {
                "installed": False,
                "message": "Java is not installed or not in PATH"
            }
        except Exception as e:
            return {
                "installed": False,
                "message": f"Error checking Java: {str(e)}"
            }

    def process_pdf(self, pdf_path: str, password: str = "", working_dir: str = None) -> Dict[str, Any]:
        """
        Process a PDF file using the JAR and return the results.

        Args:
            pdf_path: Path to the PDF file
            password: PDF password (empty string if no password)
            working_dir: Working directory for output files (default: current directory)

        Returns:
            Dictionary with processing results containing:
            - success: boolean
            - error: string (if failed)
            - notes: list of strings (if successful)
            - files: list of filenames (if successful)
            - client_name: string (if successful)
            - year: int (if successful)
        """
        try:
            # Verify PDF exists
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": "pdf_not_found",
                    "message": f"PDF file not found: {pdf_path}"
                }

            # Convert paths to absolute paths
            pdf_path = os.path.abspath(pdf_path)
            jar_path = os.path.abspath(self.jar_path)
            template_path = os.path.abspath(self.template_path)

            # Use provided working directory or current directory
            cwd = working_dir if working_dir else os.getcwd()

            # Build the command
            # java -jar Lohnkonten-1.0.3.jar <pdf_path> <password> <template_path>
            command = [
                "java",
                "-jar",
                jar_path,
                pdf_path,
                password if password else "",
                template_path
            ]

            # Execute the JAR
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                cwd=cwd  # Run from the specified working directory
            )

            # The JAR outputs JSON to stdout
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, return detailed error info
                return {
                    "success": False,
                    "error": "invalid_json_response",
                    "message": f"Failed to parse JAR output: {str(e)}",
                    "raw_output": result.stdout[:500],  # First 500 chars
                    "stderr": result.stderr[:500] if result.stderr else None
                }

            # If successful, add file paths
            if output.get("success") and "files" in output:
                file_paths = []
                for filename in output["files"]:
                    # Files are generated in the working directory (cwd)
                    filepath = os.path.join(cwd, filename)

                    if os.path.exists(filepath):
                        file_paths.append(filepath)
                    else:
                        print(f"Warning: Expected file not found: {filepath}")
                        print(f"Files in cwd: {os.listdir(cwd)}")

                # Add the file paths to output
                output["file_paths"] = file_paths

            return output

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "timeout",
                "message": "PDF processing timed out after 60 seconds. The PDF might be too large or complex."
            }
        except Exception as e:
            return {
                "success": False,
                "error": "internal",
                "message": f"Unexpected error during processing: {str(e)}"
            }

    def get_output_file_path(self, filename: str) -> Optional[str]:
        """
        Get the full path to an output file.

        Args:
            filename: Name of the output file

        Returns:
            Full path to the file if it exists, None otherwise
        """
        filepath = os.path.join(self.output_dir, filename)
        return filepath if os.path.exists(filepath) else None

    def list_output_files(self) -> list:
        """
        List all Excel files in the output directory.

        Returns:
            List of dictionaries with file information
        """
        try:
            files = []
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.xlsx'):
                    filepath = os.path.join(self.output_dir, filename)
                    files.append({
                        "filename": filename,
                        "size": os.path.getsize(filepath),
                        "created": os.path.getctime(filepath),
                        "path": filepath
                    })
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def cleanup_old_files(self, max_age_days: int = 7):
        """
        Clean up output files older than specified days.

        Args:
            max_age_days: Maximum age of files to keep
        """
        import time
        cutoff_time = time.time() - (max_age_days * 86400)

        try:
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath) and os.path.getctime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                        print(f"Cleaned up old file: {filename}")
                    except Exception as e:
                        print(f"Error removing {filename}: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")


# Singleton instance
_jar_processor = None

def get_jar_processor() -> JarProcessor:
    """
    Get the singleton JAR processor instance.

    Returns:
        JarProcessor instance
    """
    global _jar_processor
    if _jar_processor is None:
        _jar_processor = JarProcessor()
    return _jar_processor
