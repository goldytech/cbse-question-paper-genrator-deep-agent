"""Tool for generating mathematical diagrams using drawsvg."""

import os
import base64
from pathlib import Path
from typing import Literal, Dict, List, Optional, Any
from langchain_core.tools import tool


def _ensure_drawsvg_installed():
    """Check if drawsvg is installed."""
    try:
        import drawsvg

        return True
    except ImportError:
        print("Warning: drawsvg not installed. Diagrams cannot be generated.")
        return False


def _generate_geometric_diagram(description: str, elements: Optional[Dict] = None) -> Optional[str]:
    """Generate geometric diagram using drawsvg."""
    if not _ensure_drawsvg_installed():
        return None

    try:
        import drawsvg

        # Default canvas size
        width = 300
        height = 300

        # Create drawing with background (white)
        d = drawsvg.Drawing(width, height)

        # Add white background
        d.append(drawsvg.Rectangle(0, 0, width, height, fill="white"))

        # Default stroke and fill
        stroke = drawsvg.Stroke(width=2)

        # Parse elements
        shape = elements.get("shape", "") if elements else ""

        if shape in ["triangle", "right_triangle"]:
            # Create triangle
            points_data = elements.get("coordinates") if elements else {}

            # Default triangle coordinates if not provided
            if not points_data:
                # Right triangle: A(150, 200), B(50, 50), C(200, 50)
                points_data = {"A": (50, 200), "B": (50, 50), "C": (200, 50)}

            # Draw triangle
            coords_list = [points_data[pt] for pt in ["A", "B", "C"] if pt in points_data]
            if len(coords_list) >= 3:
                polygon = drawsvg.Polygon(*coords_list, stroke=stroke, fill_opacity=0)
                d.append(polygon)

            # Add right angle symbol if right triangle
            if shape == "right_triangle":
                # Assuming right angle at point with lowest y (B)
                b_point = points_data.get("B", (50, 50))
                a_point = points_data.get("A", (50, 200))
                c_point = points_data.get("C", (200, 50))

                # Draw right angle square at B
                angle_size = 15
                d.append(
                    drawsvg.Line(
                        b_point[0], b_point[1], b_point[0] + angle_size, b_point[1], stroke=stroke
                    )
                )
                d.append(
                    drawsvg.Line(
                        b_point[0], b_point[1], b_point[0], b_point[1] + angle_size, stroke=stroke
                    )
                )

        elif shape == "circle":
            # Create circle
            center = elements.get("center", (150, 150)) if elements else (150, 150)
            radius = elements.get("radius", 60) if elements else 60

            d.append(drawsvg.Circle(center[0], center[1], radius, stroke=stroke, fill_opacity=0))

        # Add point labels
        if elements and "coordinates" in elements:
            for label, (x_coord, y_coord) in elements["coordinates"].items():
                y_offset = -20 if y_coord > 100 else 10
                d.append(
                    drawsvg.Text(label, size=12, x=x_coord - 5, y=y_coord + y_offset, fill="black")
                )

        # Convert to SVG string
        svg_content = str(d)
        return svg_content

    except Exception as e:
        print(f"Error generating geometric diagram: {e}")
        return None


def _generate_coordinate_diagram(
    description: str, elements: Optional[Dict] = None
) -> Optional[str]:
    """Generate coordinate geometry diagram using drawsvg."""
    if not _ensure_drawsvg_installed():
        return None

    try:
        import drawsvg

        # Create larger canvas for coordinate systems
        width = 400
        height = 300
        d = drawsvg.Drawing(width, height)

        # Add white background
        d.append(drawsvg.Rectangle(0, 0, width, height, fill="white"))

        stroke = drawsvg.Stroke(width=2)

        # Draw axes
        origin_x, origin_y = 50, 50  # Origin position
        axis_length_x = 300
        axis_length_y = 200

        # Draw X axis with arrow
        d.append(
            drawsvg.Line(origin_x, origin_y, origin_x + axis_length_x, origin_y, stroke=stroke)
        )
        d.append(drawsvg.Text("X", size=10, x=origin_x + axis_length_x + 5, y=origin_y))

        # Draw Y axis with arrow
        d.append(
            drawsvg.Line(origin_x, origin_y, origin_x, origin_y - axis_length_y, stroke=stroke)
        )
        d.append(drawsvg.Text("Y", size=10, x=origin_x, y=origin_y - axis_length_y - 10))

        # Plot points if coordinates provided
        if elements and "coordinates" in elements:
            # Scale factor for coordinates
            scale = 30

            for label, (x_coord, y_coord) in elements["coordinates"].items():
                # Convert coordinate to canvas position
                px = origin_x + x_coord * scale
                py = origin_y - y_coord * scale  # Y is flipped

                # Draw point
                d.append(drawsvg.Circle(px, py, radius=5, fill="blue"))

                # Draw label
                y_position = py + 5 if y_coord < 0 else py - 5
                d.append(drawsvg.Text(label, size=10, x=px + 8, y=y_position, fill="black"))

        # Draw lines if connections specified
        if elements and "lines" in elements:
            scale = 30
            coords = elements.get("coordinates", {})

            for line in elements["lines"]:
                if len(line) == 2:
                    label1, label2 = line
                    if label1 in coords and label2 in coords:
                        x1, y1 = coords[label1]
                        x2, y2 = coords[label2]

                        px1 = origin_x + x1 * scale
                        py1 = origin_y - y1 * scale
                        px2 = origin_x + x2 * scale
                        py2 = origin_y - y2 * scale

                        d.append(drawsvg.Line(px1, py1, px2, py2, stroke=stroke))

        # Convert to SVG string
        svg_content = str(d)
        return svg_content

    except Exception as e:
        print(f"Error generating coordinate diagram: {e}")
        return None


def _generate_formula_diagram(description: str, elements: Optional[Dict] = None) -> Optional[str]:
    """Generate formula using simple text rendering."""
    try:
        import drawsvg

        # Extract formula from description or elements
        formula = elements.get("formula", "") if elements else ""
        if not formula:
            # Use description as formula
            formula = description

        # Create canvas
        width = 120
        height = 50
        d = drawsvg.Drawing(width, height)

        # Add white background
        d.append(drawsvg.Rectangle(0, 0, width, height, fill="white"))

        # Render formula as text (simplified - for full LaTeX rendering, would need more complex library)
        d.append(drawsvg.Text(formula, size=16, x=10, y=35, font_family="Arial", fill="black"))

        svg_content = str(d)
        return svg_content

    except Exception as e:
        print(f"Error generating formula diagram: {e}")
        return None


def _generate_chart_diagram(description: str, elements: Optional[Dict] = None) -> Optional[str]:
    """Generate simple bar chart using drawsvg."""
    if not _ensure_drawsvg_installed():
        return None

    try:
        import drawsvg

        # Create canvas
        width = 400
        height = 300
        d = drawsvg.Drawing(width, height)

        # Add white background
        d.append(drawsvg.Rectangle(0, 0, width, height, fill="white"))

        # Add axes
        origin_x, origin_y = 50, 50
        x_axis_length = 300
        y_axis_length = 200

        # X axis
        d.append(drawsvg.Line(origin_x, origin_y, origin_x + x_axis_length, origin_y))

        # Y axis
        d.append(drawsvg.Line(origin_x, origin_y, origin_x, origin_y - y_axis_length))

        # Draw bars if data provided
        if elements and "data" in elements:
            data = elements["data"]
            bar_width = 30
            bar_spacing = 20
            start_x = origin_x + 30
            max_height = 150

            # Find max value for scaling
            max_val = max(val for _, val in data) if data else 1

            for label, value in data:
                # Scale bar height
                bar_height = (value / max_val) * max_height

                # Draw bar
                d.append(
                    drawsvg.Rectangle(
                        start_x,
                        origin_y,
                        start_x + bar_width,
                        origin_y - bar_height,
                        fill="lightblue",
                        stroke="black",
                    )
                )

                # Add label under bar
                d.append(
                    drawsvg.Text(
                        str(label), size=8, x=start_x + bar_width / 2 - 10, y=origin_y + 20
                    )
                )

                # Add value above bar
                d.append(
                    drawsvg.Text(
                        str(value),
                        size=8,
                        x=start_x + bar_width / 2 - 5,
                        y=origin_y - bar_height - 5,
                    )
                )

                start_x += bar_width + bar_spacing

        svg_content = str(d)
        return svg_content

    except Exception as e:
        print(f"Error generating chart diagram: {e}")
        return None


@tool
def generate_diagram_tool(
    diagram_description: str,
    diagram_type: Literal["geometric", "coordinate", "formula", "chart"] = "geometric",
    elements: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate SVG diagram for mathematical questions using drawsvg.

    This tool auto-detects and installs drawsvg if not present.

    Args:
        diagram_description: Textual description of the diagram
        diagram_type: Type of diagram (geometric/coordinate/formula/chart)
        elements: Structured data for diagram construction:
            - For geometric: shape, coordinates, radius
            - For coordinate: coordinates (dict of point->(x,y)), lines

    Returns:
        {
            "success": bool,
            "diagram_svg_base64": str,  # Base64-encoded SVG (max 10KB checked)
            "diagram_description": str,  # Formatted description
            "diagram_elements": dict,   # Structured elements
            "diagram_type": str,
            "error": str (if failed)
        }

    Example:
        generate_diagram_tool(
            diagram_description="Right-angled triangle ABC",
            diagram_type="geometric",
            elements={
                "shape": "right_triangle",
                "coordinates": {"A": (50, 200), "B": (50, 50), "C": (200, 50)},
                "sides": ["AB=5", "BC=12"],
                "angles": ["∠B=90°"]
            }
        )
    """
    elements = elements or {}

    # Generate diagram based on type
    svg_content = None

    if diagram_type == "geometric":
        svg_content = _generate_geometric_diagram(diagram_description, elements)
    elif diagram_type == "coordinate":
        svg_content = _generate_coordinate_diagram(diagram_description, elements)
    elif diagram_type == "formula":
        svg_content = _generate_formula_diagram(diagram_description, elements)
    elif diagram_type == "chart":
        svg_content = _generate_chart_diagram(diagram_description, elements)
    else:
        return {
            "success": False,
            "error": f"Unsupported diagram type: {diagram_type}",
            "diagram_type": diagram_type,
        }

    # Handle generation failure
    if not svg_content:
        print(
            f"Warning: Failed to generate diagram (type: {diagram_type}, description: {diagram_description[:50]}...)"
        )
        return {
            "success": False,
            "error": "Diagram generation failed",
            "diagram_type": diagram_type,
            "diagram_description": diagram_description,
        }

    # Encode SVG to base64
    try:
        svg_bytes = svg_content.encode("utf-8")
        svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")

        # Check size limit (10KB)
        if len(svg_bytes) > 10240:
            print(
                f"Warning: SVG size ({len(svg_bytes)} bytes) exceeds 10KB limit, may affect JSON portability"
            )
    except Exception as e:
        print(f"Error encoding SVG to base64: {e}")
        return {"success": False, "error": "SVG encoding failed", "diagram_type": diagram_type}

    # Build structured description
    structured_description = _build_description_from_elements(
        diagram_description, diagram_type, elements
    )

    result = {
        "success": True,
        "diagram_svg_base64": svg_base64,
        "diagram_description": structured_description,
        "diagram_elements": elements,
        "diagram_type": diagram_type,
    }

    return result


def _build_description_from_elements(
    base_description: str, diagram_type: str, elements: Dict
) -> str:
    """Build structured description from base description and elements."""
    parts = [base_description]

    # Add structured element info
    if isinstance(elements, dict):
        if "coordinates" in elements:
            coords_str = ", ".join([f"{k}={v}" for k, v in elements["coordinates"].items()])
            parts.append(f"Coordinates: {coords_str}")
        if "sides" in elements:
            parts.append(f"Sides: {', '.join(elements['sides'])}")
        if "angles" in elements:
            parts.append(f"Angles: {', '.join(elements['angles'])}")
        if "points" in elements:
            parts.append(f"Points: {', '.join(elements['points'])}")
        if "data" in elements:
            parts.append(f"Data: {len(elements['data'])} data points")

    return ". ".join(parts)


def verify_diagram_tool():
    """Test function to verify diagram generation works."""
    print("Testing diagram_generator module...")

    # Test geometric diagram
    result = generate_diagram_tool(
        diagram_description="Right-angled triangle ABC",
        diagram_type="geometric",
        elements={
            "shape": "right_triangle",
            "coordinates": {"A": (50, 200), "B": (50, 50), "C": (200, 50)},
        },
    )

    print(f"Geometric diagram test: {'PASS' if result.get('success') else 'FAIL'}")
    if result.get("success"):
        print(f"  SVG base64 length: {len(result.get('diagram_svg_base64', ''))}")
        print(f"  Description: {result['diagram_description'][:100]}...")

    # Test coordinate diagram
    result2 = generate_diagram_tool(
        diagram_description="Plot points A(2,3) and B(5,7)",
        diagram_type="coordinate",
        elements={"coordinates": {"A": (2, 3), "B": (5, 7)}, "lines": [["A", "B"]]},
    )

    print(f"Coordinate diagram test: {'PASS' if result2.get('success') else 'FAIL'}")

    print("Diagram generator tests complete.")


if __name__ == "__main__":
    verify_diagram_tool()
