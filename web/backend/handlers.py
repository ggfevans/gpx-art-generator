"""
API route handlers for GPX Art Generator.

This module contains the route handlers for the API endpoints, including
file upload, artwork generation, and file retrieval.
"""

import os
import io
import json
import uuid
import shutil
import tempfile
import asyncio
import subprocess
import logging
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Set, Tuple

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from pydantic import ValidationError

from models import GenerateOptions, GenerateResponse, FileInfo, ExportFormat

# Initialize router
router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
UPLOADS_DIR = Path("./uploads")
OUTPUT_DIR = Path("./output")
CLI_COMMAND = "gpx-art"  # Assumes gpx-art is in PATH
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
VALID_EXTENSIONS = {".gpx"}
TASK_STATUS: Dict[str, Dict[str, Any]] = {}  # In-memory task status tracking

# Create directories if they don't exist
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    Validate the uploaded file.
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        Tuple containing (is_valid, error_message)
    """
    # Check filename and extension
    filename = file.filename or ""
    file_ext = Path(filename).suffix.lower()
    
    if not filename:
        return False, "No filename provided"
    
    if file_ext not in VALID_EXTENSIONS:
        return False, f"Invalid file extension. Supported: {', '.join(VALID_EXTENSIONS)}"
    
    # Check content type
    content_type = file.content_type or ""
    if content_type and not (
        content_type == "application/gpx+xml" or 
        content_type == "application/xml" or
        content_type == "text/xml" or
        "gpx" in content_type.lower()
    ):
        logger.warning(f"Suspicious content type: {content_type} for file {filename}")
        # We'll still accept it but log a warning
    
    return True, None


async def save_upload_file(file: UploadFile) -> Path:
    """
    Save uploaded file to disk.
    
    Args:
        file: The uploaded file to save
        
    Returns:
        Path to the saved file
        
    Raises:
        HTTPException: If file is too large or can't be saved
    """
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    file_ext = Path(file.filename or "").suffix
    
    if not file_ext:
        file_ext = ".gpx"
        
    safe_filename = f"{timestamp}_{unique_id}{file_ext}"
    file_path = UPLOADS_DIR / safe_filename
    
    # Read file content with size check
    file_size = 0
    file_content = b""
    
    chunk_size = 1024 * 1024  # 1MB chunks
    async for chunk in file.stream():
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024)}MB"
            )
        file_content += chunk
    
    # Write to file
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        return file_path
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file"
        )


def parse_options(options_str: str) -> GenerateOptions:
    """
    Parse options JSON string into GenerateOptions object.
    
    Args:
        options_str: JSON string with options
        
    Returns:
        Parsed GenerateOptions object
        
    Raises:
        HTTPException: If options can't be parsed
    """
    try:
        options_dict = json.loads(options_str)
        return GenerateOptions(**options_dict)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid options JSON: {str(e)}"
        )
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid options: {str(e)}"
        )


def build_cli_command(input_file: Path, output_prefix: str, options: GenerateOptions) -> List[str]:
    """
    Build the GPX Art CLI command from options.
    
    Args:
        input_file: Path to the input GPX file
        output_prefix: Output filename prefix (without extension)
        options: Generation options
        
    Returns:
        Command as a list of strings
    """
    cmd = [CLI_COMMAND, "convert", str(input_file), output_prefix]
    
    # Add styling options
    if options.color:
        cmd.extend(["--color", options.color])
    
    if options.background:
        cmd.extend(["--background", options.background])
    
    if options.thickness:
        cmd.extend(["--thickness", options.thickness])
    
    if options.style:
        cmd.extend(["--style", options.style])
    
    # Add marker options
    if options.markers:
        cmd.append("--markers")
        if options.markers_unit:
            cmd.extend(["--markers-unit", options.markers_unit])
    else:
        cmd.append("--no-markers")
    
    # Add overlay options
    if options.overlay:
        cmd.extend(["--overlay", ",".join(options.overlay)])
    
    if options.overlay_position:
        cmd.extend(["--overlay-position", options.overlay_position])
    
    # Add format options
    if options.formats:
        cmd.extend(["--format", ",".join(options.formats)])
    
    return cmd


async def execute_cli_command(
    cmd: List[str],
    task_id: str,
    output_dir: Path
) -> Tuple[bool, List[FileInfo], Optional[str]]:
    """
    Execute the GPX Art CLI command.
    
    Args:
        cmd: Command to execute
        task_id: Task identifier
        output_dir: Directory for output files
        
    Returns:
        Tuple of (success, file_infos, error_message)
    """
    logger.info(f"Executing command: {' '.join(cmd)}")
    
    # Update task status
    TASK_STATUS[task_id]["status"] = "processing"
    
    try:
        # Execute command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Process output
        output = stdout.decode().strip()
        error = stderr.decode().strip()
        
        if process.returncode != 0:
            logger.error(f"Command failed with code {process.returncode}: {error}")
            return False, [], error or "Command execution failed"
        
        # Find generated files based on the output prefix
        # The output prefix is the second-to-last argument in the command
        output_prefix = cmd[-1]
        if not os.path.isabs(output_prefix):
            # If relative path, resolve from current directory
            output_prefix = os.path.abspath(output_prefix)
        
        # Find generated files
        file_infos = []
        
        # Get formats from the command options
        formats = []
        for i, arg in enumerate(cmd):
            if arg == "--format" and i + 1 < len(cmd):
                formats = cmd[i + 1].split(",")
                break
        
        if not formats:
            formats = ["png"]  # Default format
        
        for fmt in formats:
            output_file = f"{output_prefix}.{fmt}"
            output_path = Path(output_file)
            
            if output_path.exists():
                # Copy the file to the output directory
                file_id = f"{task_id}_{fmt}"
                dest_path = output_dir / f"{file_id}.{fmt}"
                
                shutil.copy2(output_path, dest_path)
                
                # Get file size
                file_size = dest_path.stat().st_size
                
                # Create file info
                file_info = FileInfo(
                    id=file_id,
                    name=os.path.basename(output_file),
                    size=file_size,
                    url=f"/files/{file_id}.{fmt}",
                    format=fmt
                )
                file_infos.append(file_info)
        
        return True, file_infos, None
    
    except Exception as e:
        logger.exception(f"Error executing command: {str(e)}")
        return False, [], f"Error executing command: {str(e)}"


async def process_gpx_file(
    task_id: str,
    input_file: Path,
    options: GenerateOptions
) -> None:
    """
    Process a GPX file in the background.
    
    Args:
        task_id: Task identifier
        input_file: Path to the input GPX file
        options: Generation options
    """
    try:
        # Create an output directory for this task
        output_dir = OUTPUT_DIR
        
        # Create a unique output prefix
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_prefix = f"{output_dir}/{task_id}_{timestamp}"
        
        # Build and execute the command
        cmd = build_cli_command(input_file, output_prefix, options)
        success, files, error = await execute_cli_command(cmd, task_id, output_dir)
        
        # Update task status
        if success:
            TASK_STATUS[task_id].update({
                "status": "completed",
                "files": files,
                "message": "Processing completed successfully"
            })
        else:
            TASK_STATUS[task_id].update({
                "status": "failed",
                "message": error or "Unknown error"
            })
    
    except Exception as e:
        logger.exception(f"Error processing task {task_id}: {str(e)}")
        TASK_STATUS[task_id].update({
            "status": "failed",
            "message": f"Error: {str(e)}"
        })
    
    finally:
        # Clean up the input file
        if input_file.exists():
            try:
                input_file.unlink()
            except Exception as e:
                logger.error(f"Error removing input file {input_file}: {str(e)}")


@router.post("/generate", response_model=GenerateResponse)
async def generate_artwork(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: str = Form("{}")
) -> GenerateResponse:
    """
    Generate artwork from a GPX file.
    
    Args:
        background_tasks: FastAPI background tasks handler
        file: Uploaded GPX file
        options: JSON string containing generation options
        
    Returns:
        GenerateResponse: Information about generated files
        
    Raises:
        HTTPException: If file validation fails or processing error occurs

