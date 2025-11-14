# server.py
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
import requests
import json
import base64
from urllib.parse import urlparse
from typing import Optional
from io import BytesIO
from PIL import Image

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
    camera_axis: str = None,
    image_size: int = None
) -> list:
    """Capture a screenshot from 3D Slicer for visual inspection.

    This MCP tool gives the model a "what you see is what you get"
    view of Slicer, so it can reason about the current GUI state
    (panels, slice views, 3D rendering, overlays, etc.) and take
    follow‑up actions.

    Behavior by ``view_type``:

    - "application":
        Capture the full Slicer application window, including all
        dock widgets, slice views and 3D views, as a compressed JPEG.

    - "slice":
        Capture a single slice view (Red/Yellow/Green) as it currently
        appears on screen. The screenshot includes whatever UI elements
        are visible in that view (crosshair, orientation markers,
        labels, segment overlays, etc.).

    - "3d":
        Capture the 3D rendering view. Optionally, a camera axis can
        be specified to look from a standard anatomical direction.

    Parameters:
        view_type (str): Type of screenshot to capture. Options:
            - "application" (default): Full application window.
            - "slice": One named slice view.
            - "3d": The 3D rendering view.

        view_name (str): For slice views, which slice to capture.
            Options: "red", "yellow", "green". Only used when
            ``view_type="slice"``.

        camera_axis (str): For 3D views, camera view direction.
            Options: "L" (Left), "R" (Right), "A" (Anterior),
            "P" (Posterior), "I" (Inferior), "S" (Superior).
            Only used when ``view_type="3d"``.

        image_size (int | None): Target pixel size for the output image.
            - For slice views, this is treated as a maximum for the
              longer side of the captured pixmap; the image is scaled
              with preserved aspect ratio up to this size.
            - For application and 3D views, the screenshot is captured
              at the current window size and may be downscaled if its
              longest side exceeds an internal maximum (for size
              control). Callers should not rely on an exact pixel
              size, only that larger values produce higher‑resolution
              images within reasonable limits.

        Returns:
                list[mcp.types.Content]:
                        - ``TextContent``: A short, human‑readable description of
                            what was captured (e.g. which view and approximate size).
                        - ``ImageContent``: The screenshot image in base64‑encoded
                            JPEG format when capture succeeds, or omitted if only an
                            error message is returned.

        Note:
                This tool is primarily intended for multimodal models. Callers
                should inspect the returned screenshot with their vision
                capabilities (rather than relying only on the text summary)
                when reasoning about Slicer's state, UI layout, overlays, or
                other visual details.

        The internal capture mechanism (e.g. which Slicer APIs or
        endpoints are used) is considered an implementation detail and may
        evolve over time without breaking this public contract.
    """
    try:
        # Determine behavior based on view_type
        if view_type == "application":
            api_url = f"{SLICER_WEB_SERVER_URL}/screenshot"
            params = {}
            description = "full application window"
            
        elif view_type == "slice":
            if not view_name:
                return [TextContent(type="text", text="Error: view_name is required for slice screenshots (red, yellow, or green)")]

            # Use internal /exec-based slice screenshot implementation to
            # capture the render window with full GUI elements.
            python_code = _build_slice_screenshot_python_code(
                view_name=view_name,
                image_size=image_size,
            )
            result = execute_python_code(python_code)
            return _parse_slice_screenshot_result(result)
                
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
            # Optimize image to reduce size
            try:
                # Open image from response bytes
                img = Image.open(BytesIO(response.content))
                
                # Convert RGBA to RGB if necessary (for JPEG compatibility)
                if img.mode == 'RGBA':
                    # Create white background
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = rgb_img
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Resize if image is too large (max dimension 1920px)
                max_dimension = 1920
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Compress image to JPEG with quality 85
                output_buffer = BytesIO()
                img.save(output_buffer, format='JPEG', quality=85, optimize=True)
                compressed_bytes = output_buffer.getvalue()
                
                # Convert to base64
                image_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
                
                # Return using MCP's content types
                return [
                    TextContent(
                        type="text",
                        text=f"Screenshot of {description} captured successfully (compressed)"
                    ),
                    ImageContent(
                        type="image",
                        data=image_base64,
                        mimeType="image/jpeg"
                    )
                ]
            except Exception as img_error:
                # Fallback to original image if compression fails
                return [TextContent(
                    type="text", 
                    text=f"Screenshot captured but compression failed: {str(img_error)}. Using original image."
                )]
        else:
            # Unexpected response type
            return [TextContent(type="text", text=f"Error: Unexpected response type: {response.headers.get('Content-Type')}")]
            
    except requests.exceptions.HTTPError as e:
        return [TextContent(type="text", text=f"HTTP Error {e.response.status_code}: {str(e)}")]
    except requests.exceptions.RequestException as e:
        return [TextContent(type="text", text=f"Connection error: {str(e)}. Make sure Slicer Web Server is running.")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def _build_slice_screenshot_python_code(
    view_name: str,
    image_size: int = None,
) -> str:
    """Build Python code to capture a slice view screenshot via ``/exec``.

    The generated code runs inside 3D Slicer using the Web Server ``/exec`` API.
    It locates the requested slice widget (Red/Yellow/Green), forces a render,
    grabs the corresponding ``sliceView`` Qt widget, optionally rescales the
    pixmap, and returns a JSON object containing a base64-encoded JPEG image and
    basic metadata.

    The code does **not** modify any slice offsets, orientations, crosshair
    state, or orientation markers; it simply captures the current visual state
    of the slice view.

    Args:
        view_name: Name of the slice view ("red", "yellow", or "green").
        image_size: Optional maximum size (in pixels) for the longer image
            dimension. When provided, the pixmap is scaled with preserved
            aspect ratio so that the longer side equals ``image_size``.

    Returns:
        A Python code string suitable for sending to the Slicer Web Server
        ``/exec`` endpoint.
    """
    # Prepare optional parameter code (only resize is handled here)
    resize_code = ""
    if image_size:
        resize_code = f"""
        # Resize image
        pixmap = pixmap.scaled(
            {image_size}, {image_size},
            qt.Qt.KeepAspectRatio,
            qt.Qt.SmoothTransformation
        )"""
    
    # Build complete Python code
    python_code = f"""
import qt
import base64
import json

try:
    # Get slice widget
    layoutManager = slicer.app.layoutManager()
    sliceWidget = layoutManager.sliceWidget('{view_name.capitalize()}')
    
    if not sliceWidget:
        __execResult = json.dumps({{"error": f"Slice widget '{view_name.capitalize()}' not found"}})
    else:
        # Force render update
        sliceWidget.sliceView().forceRender()
        slicer.app.processEvents()
        
        # Capture slice view
        sliceView = sliceWidget.sliceView()
        pixmap = sliceView.grab(){resize_code}
        
        # Convert to QImage
        qimage = pixmap.toImage()
        
        # Save as JPEG to reduce size
        buffer = qt.QBuffer()
        buffer.open(qt.QIODevice.WriteOnly)
        qimage.save(buffer, "JPEG", 85)
        
        # Base64 encode - convert QByteArray to bytes properly
        byte_array = buffer.data()
        image_bytes = byte_array.data()  # Extract raw bytes from QByteArray
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Return result
        __execResult = json.dumps({{
            "success": True,
            "image": image_base64,
            "format": "jpeg",
            "view": "{view_name}",
            "size": {{"width": qimage.width(), "height": qimage.height()}}
        }})
        
except Exception as e:
    import traceback
    __execResult = json.dumps({{
        "error": str(e),
        "traceback": traceback.format_exc()
    }})
"""
    return python_code


def _parse_slice_screenshot_result(result: dict) -> list:
    """
    Parse slice screenshot execution result.
    
    Args:
        result: Dictionary returned from execute_python_code
    
    Returns:
        List of MCP content items (TextContent and/or ImageContent)
    """
    if not result["success"]:
        return [TextContent(
            type="text",
            text=f"Code execution failed: {result['message']}"
        )]
    
    try:
        # Parse JSON response
        data = json.loads(result["message"])
        
        if "error" in data:
            error_msg = f"Screenshot failed: {data['error']}"
            if "traceback" in data:
                error_msg += f"\n\nTraceback:\n{data['traceback']}"
            return [TextContent(type="text", text=error_msg)]
        
        # Extract image and metadata
        image_base64 = data["image"]
        metadata = data.get("size", {})
        
        # Build concise description text
        description = f"Successfully captured {data['view']} slice view "
        description += f"({metadata.get('width', '?')}x{metadata.get('height', '?')})"
        
        return [
            TextContent(type="text", text=description),
            ImageContent(
                type="image",
                data=image_base64,
                mimeType="image/jpeg"
            )
        ]
        
    except json.JSONDecodeError as e:
        return [TextContent(
            type="text",
            text=f"JSON parsing failed: {str(e)}\n\nResponse length: {len(result.get('message', ''))} characters"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Processing failed: {str(e)}"
        )]
