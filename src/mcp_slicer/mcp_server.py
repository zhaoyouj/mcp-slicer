# server.py
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
import requests
import json
import base64
from urllib.parse import urlparse
from typing import Optional

# Create an MCP server
mcp = FastMCP("SlicerMCP")

SLICER_WEB_SERVER_URL = "http://localhost:2016/slicer"


def get_proxy_config(url: str) -> Optional[dict]:
    """
    Get proxy configuration for requests based on URL.
    
    For localhost/127.0.0.1 connections, always disable proxy to avoid
    connection issues when system proxy is configured but not running.
    
    For other connections, return None to use system default proxy settings
    (if configured via environment variables).
    
    Args:
        url: The target URL for the request
        
    Returns:
        dict: Proxy configuration dict for requests library
        - For localhost: {'http': None, 'https': None} to disable proxy
        - For other hosts: None to use system defaults
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    
    # Always bypass proxy for localhost connections
    if hostname in ("localhost", "127.0.0.1", "::1") or hostname.startswith("127."):
        return {'http': None, 'https': None}
    
    # For other connections, return None to use system proxy settings
    # if available via HTTP_PROXY, HTTPS_PROXY environment variables
    return None

# Add list_nodes tool
@mcp.tool()
def list_nodes(filter_type: str = "names", class_name: str = None, 
              name: str = None, id: str = None) -> dict:
    """
    List MRML nodes via the Slicer Web Server API.

    The filter_type parameter specifies the type of node information to retrieve.
    Possible values include "names" (node names), "ids" (node IDs), and "properties" (node properties).
    The default value is "names".

    The class_name, name, and id parameters are optional and can be used to further filter nodes.
    The class_name parameter allows filtering nodes by class name.
    The name parameter allows filtering nodes by name.
    The id parameter allows filtering nodes by ID.

    Examples:
    - List the names of all nodes: {"tool": "list_nodes", "arguments": {"filter_type": "names"}}
    - List the IDs of nodes of a specific class: {"tool": "list_nodes", "arguments": {"filter_type": "ids", "class_name": "vtkMRMLModelNode"}}
    - List the properties of nodes with a specific name: {"tool": "list_nodes", "arguments": {"filter_type": "properties", "name": "MyModel"}}
    - List nodes with a specific ID: {"tool": "list_nodes", "arguments": {"filter_type": "ids", "id": "vtkMRMLModelNode123"}}

    Returns a dictionary containing node information.
    If filter_type is "names" or "ids", the returned dictionary contains a "nodes" key, whose value is a list containing node names or IDs.
    Example: {"nodes": ["node1", "node2", ...]} or {"nodes": ["id1", "id2", ...]}
    If filter_type is "properties", the returned dictionary contains a "nodes" key, whose value is a dictionary containing node properties.
    Example: {"nodes": {"node1": {"property1": "value1", "property2": "value2"}, ...}}
    If an error occurs, a dictionary containing an "error" key is returned, whose value is a string describing the error.
    """
    try:
        # Build API endpoint based on filter type
        endpoint_map = {
            "names": "/mrml/names",
            "ids": "/mrml/ids",
            "properties": "/mrml/properties"
        }
        
        if filter_type not in endpoint_map:
            return {"error": "Invalid filter_type specified"}
            
        api_url = f"{SLICER_WEB_SERVER_URL}{endpoint_map[filter_type]}"
        
        # Build query parameters
        params = {}
        if class_name:
            params["class"] = class_name
        if name:
            params["name"] = name
        if id:
            params["id"] = id

        # Send GET request to Slicer Web Server
        # Smart proxy handling: disable for localhost, use system default for others
        response = requests.get(api_url, params=params, proxies=get_proxy_config(api_url))
        response.raise_for_status()
        
        # Process response based on filter type
        if filter_type == "properties":
            return {"nodes": response.json()}
            
        return {"nodes": response.json()}

    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON response: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        return {"error": f"Node listing failed: {str(e)}"}


# Add execute_python_code tool
@mcp.tool()
def execute_python_code(code: str) -> dict:
    """
    Execute Python code in 3D Slicer.

    Parameters:
    code (str): The Python code to execute.

    The code parameter is a string containing the Python code to be executed in 3D Slicer's Python environment.
    The code should be executable by Python's `exec()` function. To get return values, the code should assign the result to a variable named `__execResult`.

    Examples:
    - Create a sphere model: {"tool": "execute_python_code", "arguments": {"code": "sphere = slicer.vtkMRMLModelNode(); slicer.mrmlScene.AddNode(sphere); sphere.SetName('MySphere'); __execResult = sphere.GetID()"}}
    - Get the number of nodes in the current scene: {"tool": "execute_python_code", "arguments": {"code": "__execResult = len(slicer.mrmlScene.GetNodes())"}}
    - Calculate 1+1: {"tool": "execute_python_code", "arguments": {"code": "__execResult = 1 + 1"}}

    Returns:
        dict: A dictionary containing the execution result.

        If the code execution is successful, the dictionary will contain the following key-value pairs:
        - "success": True
        - "message": The result of the code execution. If the code assigns the result to `__execResult`, the value of `__execResult` is returned, otherwise it returns empty.

        If the code execution fails, the dictionary will contain the following key-value pairs:
        - "success": False
        - "message": A string containing an error message indicating the cause of the failure. The error message may come from the Slicer Web Server or the Python interpreter.

    Examples:
    - Successful execution: {"success": True, "message": 2}  # Assuming the result of 1+1 is 2
    - Successful execution: {"success": True, "message": "vtkMRMLScene1"} # Assuming the created sphere id is vtkMRMLScene1
    - Python execution error: {"success": False, "message": "Server error: name 'slicer' is not defined"}
    - Connection error: {"success": False, "message": "Connection error: ..."}
    - HTTP error: {"success": False, "message": "HTTP Error 404: Not Found"}
    """
    api_url = f"{SLICER_WEB_SERVER_URL}/exec"
    headers = {'Content-Type': 'text/plain'}
    try:
        # Smart proxy handling: disable for localhost, use system default for others
        response = requests.post(api_url, data=code.encode('utf-8'), headers=headers, proxies=get_proxy_config(api_url))
        result_data = response.json()
        
        if isinstance(result_data, dict) and not result_data.get("success", True):
            return {
                "success": False,
                "message": result_data.get("message", "Unknown Python execution error")
                }
            
        return {
            "success": True,
            "message": result_data.get("__execResult") if isinstance(result_data, dict) and "__execResult" in result_data else result_data
            }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "message": f"HTTP Error {e.response.status_code}: {str(e)}"
            }
    except json.JSONDecodeError:
        return {
            "success": False,
            "message": f"Invalid JSON response: {response.text}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Connection error: {str(e)}"
            }


# Add capture_screenshot tool
@mcp.tool()
def capture_screenshot(
    view_type: str = "application",
    view_name: str = None,
    slice_offset: float = None,
    slice_orientation: str = None,
    camera_axis: str = None,
    image_size: int = None
) -> list:
    """
    Capture a screenshot from 3D Slicer's views.

    This tool provides real-time visual feedback of the current state of Slicer,
    enabling AI to observe the GUI and make informed decisions in a complete REACT loop.

    Parameters:
    view_type (str): Type of screenshot to capture. Options:
        - "application" (default): Full application window including all panels and views
        - "slice": A specific slice view (Red/Yellow/Green)
        - "3d": The 3D rendering view
    
    view_name (str): For slice views, specify which view to capture.
        Options: "red", "yellow", "green"
        Only used when view_type="slice"
    
    slice_offset (float): For slice views, offset in mm relative to slice origin.
        Only used when view_type="slice"
    
    slice_orientation (str): For slice views, specify orientation.
        Options: "axial", "sagittal", "coronal"
        Only used when view_type="slice"
    
    camera_axis (str): For 3D views, specify camera view direction.
        Options: "L" (Left), "R" (Right), "A" (Anterior), "P" (Posterior), 
                 "I" (Inferior), "S" (Superior)
        Only used when view_type="3d"
    
    image_size (int): Pixel size of output image (for slice and 3D views).
        Only used when view_type="slice" or view_type="3d"

    Returns:
        A list containing text and/or image content. The image is returned
        in MCP's standard format for proper display in AI clients.

    Examples:
    - Capture full application: {"tool": "capture_screenshot", "arguments": {"view_type": "application"}}
    - Capture Red slice view: {"tool": "capture_screenshot", "arguments": {"view_type": "slice", "view_name": "red"}}
    - Capture 3D view from anterior: {"tool": "capture_screenshot", "arguments": {"view_type": "3d", "camera_axis": "A"}}
    - Capture axial slice: {"tool": "capture_screenshot", "arguments": {"view_type": "slice", "view_name": "red", "slice_orientation": "axial"}}
    """
    try:
        # Determine the API endpoint based on view_type
        if view_type == "application":
            api_url = f"{SLICER_WEB_SERVER_URL}/screenshot"
            params = {}
            description = "full application window"
            
        elif view_type == "slice":
            if not view_name:
                return [TextContent(type="text", text="Error: view_name is required for slice screenshots (red, yellow, or green)")]
            
            api_url = f"{SLICER_WEB_SERVER_URL}/slice"
            params = {"view": view_name.lower()}
            description = f"{view_name} slice view"
            
            # Add optional parameters
            if slice_offset is not None:
                params["offset"] = slice_offset
            if slice_orientation:
                params["orientation"] = slice_orientation.lower()
                description += f" ({slice_orientation})"
            if image_size:
                params["size"] = image_size
                
        elif view_type == "3d":
            api_url = f"{SLICER_WEB_SERVER_URL}/threeD"
            params = {}
            description = "3D view"
            
            # Add optional parameters
            if camera_axis:
                params["lookFromAxis"] = camera_axis.upper()
                description += f" from {camera_axis} axis"
                
        else:
            return [TextContent(type="text", text=f"Error: Invalid view_type '{view_type}'. Must be 'application', 'slice', or '3d'")]

        # Make the request to Slicer Web Server
        # Smart proxy handling: disable for localhost, use system default for others
        response = requests.get(api_url, params=params, proxies=get_proxy_config(api_url))
        response.raise_for_status()
        
        # Check if response is an image
        if response.headers.get('Content-Type', '').startswith('image/'):
            # Convert image bytes to base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            
            # Return using MCP's content types
            return [
                TextContent(
                    type="text",
                    text=f"Screenshot of {description} captured successfully"
                ),
                ImageContent(
                    type="image",
                    data=image_base64,
                    mimeType="image/png"
                )
            ]
        else:
            # Unexpected response type
            return [TextContent(type="text", text=f"Error: Unexpected response type: {response.headers.get('Content-Type')}")]
            
    except requests.exceptions.HTTPError as e:
        return [TextContent(type="text", text=f"HTTP Error {e.response.status_code}: {str(e)}")]
    except requests.exceptions.RequestException as e:
        return [TextContent(type="text", text=f"Connection error: {str(e)}. Make sure Slicer Web Server is running.")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
