"""
MicroDashboard - A renderer system for PicoDash
Handles workspace configuration, rendering, and transitions

Features:
- Workspace configuration from YAML
- Multiple renderer types with different behaviors
- Consistent UI elements across all renderers
"""

import gc
import time


class MicroDashboard:
    """Main dashboard controller that manages workspaces and rendering"""

    def __init__(self, display, width, height, wifi_connected=False, auto_cycle=True):
        """Initialize the dashboard with display and basic settings"""
        self.display = display
        self.width = width
        self.height = height
        self.wifi_connected = wifi_connected
        self.auto_cycle = auto_cycle

        # Colors - will be initialized later
        self.colors = {}

        # Workspaces and renderers
        self.workspaces = []
        self.current_workspace_index = 0
        self.renderer_classes = {}

        # Default workspace configuration
        self.default_workspaces = [
            {"name": "Welcome", "display_time": 5, "renderer": "WelcomeRenderer"},
            {"name": "Time", "display_time": 10, "renderer": "TimeRenderer"},
            {"name": "Date", "display_time": 8, "renderer": "DateRenderer"},
            {"name": "System", "display_time": 7, "renderer": "SystemRenderer"},
        ]

    def initialize_colors(self):
        """Initialize color pens - must be called after display is set up"""
        # Create pens for display
        self.colors["BLACK"] = self.display.create_pen(0, 0, 0)
        self.colors["WHITE"] = self.display.create_pen(255, 255, 255)
        self.colors["RED"] = self.display.create_pen(255, 0, 0)
        self.colors["GREEN"] = self.display.create_pen(0, 255, 0)
        self.colors["BLUE"] = self.display.create_pen(0, 0, 255)
        self.colors["YELLOW"] = self.display.create_pen(255, 255, 0)
        self.colors["PURPLE"] = self.display.create_pen(255, 0, 255)
        self.colors["DARK_ORANGE"] = self.display.create_pen(255, 140, 0)

    def register_renderer(self, name, renderer_class):
        """Register a renderer class by name"""
        self.renderer_classes[name] = renderer_class

    def load_workspaces(self, config):
        """Load workspaces from configuration"""
        if not config or "workspaces" not in config:
            # Use defaults if no valid config
            self.workspaces = self.default_workspaces
            return

        self.workspaces = config["workspaces"]

    def next_workspace(self):
        """Switch to the next workspace"""
        if not self.workspaces:
            # If no workspaces defined, use defaults
            self.workspaces = self.default_workspaces

        if self.workspaces:
            self.current_workspace_index = (self.current_workspace_index + 1) % len(self.workspaces)
            self.render_current_workspace()
        return self.current_workspace_index

    def get_current_display_time(self):
        """Get the display time for the current workspace in seconds"""
        if not self.workspaces:
            return 5  # Default if no workspaces

        workspace = self.workspaces[self.current_workspace_index]
        return workspace.get("display_time", 5)  # Default to 5 seconds if not specified

    def get_current_workspace_name(self):
        """Get the name of the current workspace"""
        if not self.workspaces:
            return "Unnamed"

        return self.workspaces[self.current_workspace_index].get("name", "Unnamed")

    def render_current_workspace(self):
        """Render the current workspace using its specified renderer"""
        # Check if workspaces exist
        if not self.workspaces:
            # If no workspaces defined, use defaults
            self.workspaces = self.default_workspaces

        if not self.workspaces:
            # Still no workspaces, show error
            self._render_error("No workspaces defined")
            return

        # Get current workspace configuration
        workspace = self.workspaces[self.current_workspace_index]
        renderer_name = workspace.get("renderer")

        # Find the renderer class
        if renderer_name in self.renderer_classes:
            renderer_class = self.renderer_classes[renderer_name]

            # Initialize the renderer with current workspace settings
            renderer = renderer_class(
                self.display,
                self.width,
                self.height,
                self.colors,
                self.wifi_connected,
                self.auto_cycle,
            )

            # Pass any additional parameters from the workspace config
            renderer_params = {
                k: v for k, v in workspace.items() if k not in ["name", "display_time", "renderer"]
            }

            # Render the workspace
            renderer.render(renderer_params)
        else:
            # Fallback if renderer not found
            self._render_error(f"Renderer not found: {renderer_name}")

    def _render_error(self, message):
        """Render an error message"""
        self.display.set_pen(self.colors["BLACK"])
        self.display.clear()
        self.display.set_pen(self.colors["RED"])
        self.display.text("ERROR:", 10, 10)
        self.display.text(message[:30], 10, 40)
        if len(message) > 30:
            self.display.text(message[30:60], 10, 60)
        self.display.update()


class BaseRenderer:
    """Base class for all renderers"""

    def __init__(self, display, width, height, colors, wifi_connected, auto_cycle):
        """Initialize with display and basic settings"""
        self.display = display
        self.width = width
        self.height = height
        self.colors = colors
        self.wifi_connected = wifi_connected
        self.auto_cycle = auto_cycle

    def render(self, params):
        """Render method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement render()")

    def draw_border(self):
        """Draw a border around the screen"""
        self.display.line(0, 0, self.width - 1, 0)
        self.display.line(0, 0, 0, self.height - 1)
        self.display.line(self.width - 1, 0, self.width - 1, self.height - 1)
        self.display.line(0, self.height - 1, self.width - 1, self.height - 1)

    def draw_navigation(self):
        """Draw standard navigation/status text at bottom of screen"""
        # Set color for bottom text
        self.display.set_pen(self.colors["DARK_ORANGE"])

        # Show 'Next' button on left side
        self.display.text("A: Next", 10, self.height - 25)

        # Show auto-cycle status on right side
        auto_text = f"Auto: {('ON' if self.auto_cycle else 'OFF')}"
        self.display.text(auto_text, self.width - 70, self.height - 25)


class WelcomeRenderer(BaseRenderer):
    """Renderer for welcome screen"""

    def render(self, params):
        """Render welcome screen with configurable title and messages"""
        self.display.set_pen(self.colors["BLACK"])
        self.display.clear()
        self.display.set_pen(self.colors["WHITE"])

        # Draw border
        self.draw_border()

        # Draw title and version (customizable)
        title = params.get("title", "PicoDash")
        version = params.get("version", "v1.0")
        self.display.text(title, 10, 10)
        self.display.text(version, self.width - 40, 10)

        # Draw instructions (customizable)
        instructions = params.get(
            "instructions",
            ["Controls:", "A: Next Screen", "B: System Info", "Y: Toggle Auto-Cycle"],
        )

        # Display instructions
        y_pos = 35
        for instruction in instructions:
            if y_pos < self.height - 30:  # Ensure we don't overlap with bottom text
                self.display.text(instruction, 10 if "Controls" in instruction else 20, y_pos)
                y_pos += 20

        # Draw navigation
        self.draw_navigation()

        # Show WiFi status on left side (shortened)
        self.display.set_pen(self.colors["DARK_ORANGE"])
        if self.wifi_connected:
            wifi_text = "WiFi: ON"
        else:
            wifi_text = "WiFi: OFF"
        self.display.text(wifi_text, 10, self.height - 25)

        self.display.update()


class TimeRenderer(BaseRenderer):
    """Renderer for time display"""

    def render(self, params):
        """Render current time"""
        self.display.set_pen(self.colors["BLACK"])
        self.display.clear()
        self.display.set_pen(self.colors["WHITE"])

        # Draw border
        self.draw_border()

        # Get and format current time
        current = time.localtime()

        # Allow custom time format from params
        time_format = params.get("format", "{:02d}:{:02d}:{:02d}")
        label = params.get("label", "Current Time")

        # Use the format to generate time string
        if time_format == "{:02d}:{:02d}:{:02d}":
            # Default HH:MM:SS format
            time_str = time_format.format(current[3], current[4], current[5])
        else:
            # Custom format (basic support)
            time_str = time_format

        # Draw header
        self.display.text(label, 10, 10)

        # Draw time in centered text
        self.display.set_pen(self.colors["WHITE"])
        self.display.text(time_str, self.width // 2 - 30, self.height // 2 - 10)

        # Draw navigation
        self.draw_navigation()

        # Show WiFi status in corner
        if self.wifi_connected:
            self.display.set_pen(self.colors["GREEN"])
        else:
            self.display.set_pen(self.colors["RED"])
        self.display.text("WiFi", self.width - 40, 10)

        self.display.update()


class DateRenderer(BaseRenderer):
    """Renderer for date display"""

    def render(self, params):
        """Render current date"""
        self.display.set_pen(self.colors["BLACK"])
        self.display.clear()
        self.display.set_pen(self.colors["WHITE"])

        # Draw border
        self.draw_border()

        # Get current date
        current = time.localtime()

        # Allow custom date format from params
        date_format = params.get("format", "{:04d}-{:02d}-{:02d}")
        label = params.get("label", "Current Date")
        show_weekday = params.get("show_weekday", True)

        # Use the format to generate date string
        if date_format == "{:04d}-{:02d}-{:02d}":
            # Default YYYY-MM-DD format
            date_str = date_format.format(current[0], current[1], current[2])
        else:
            # Custom format (basic support)
            date_str = date_format

        # Draw header
        self.display.text(label, 10, 10)

        # Draw date
        self.display.set_pen(self.colors["WHITE"])
        self.display.text(date_str, self.width // 2 - 50, self.height // 2 - 20)

        # Draw weekday if enabled
        if show_weekday:
            weekdays = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            weekday = weekdays[current[6]]  # current[6] is weekday (0-6, Monday is 0)
            self.display.text(weekday, self.width // 2 - 30, self.height // 2 + 10)

        # Draw navigation
        self.draw_navigation()

        self.display.update()


class SystemRenderer(BaseRenderer):
    """Renderer for system information"""

    def render(self, params):
        """Render system information"""
        self.display.set_pen(self.colors["BLACK"])
        self.display.clear()
        self.display.set_pen(self.colors["WHITE"])

        # Draw border
        self.draw_border()

        # Get memory info
        gc.collect()
        mem_free = gc.mem_free()
        mem_alloc = gc.mem_alloc()
        mem_total = mem_free + mem_alloc
        mem_percent = int((mem_alloc / mem_total) * 100)

        # Calculate KB values
        mem_free_kb = round(mem_free / 1024, 1)
        mem_alloc_kb = round(mem_alloc / 1024, 1)

        # Draw title (customizable)
        title = params.get("title", "System Info")
        self.display.text(title, 10, 10)

        # Determine which stats to show (all enabled by default)
        show_memory = params.get("show_memory", True)
        show_display = params.get("show_display", True)

        # Start position for stats
        y_pos = 35

        # Draw memory stats if enabled
        if show_memory:
            self.display.text(f"Free: {mem_free_kb} KB", 10, y_pos)
            y_pos += 20
            self.display.text(f"Used: {mem_alloc_kb} KB", 10, y_pos)
            y_pos += 20
            self.display.text(f"Usage: {mem_percent}%", 10, y_pos)
            y_pos += 20

        # Draw display info if enabled
        if show_display:
            self.display.text(f"Display: {self.width}x{self.height}", 10, y_pos)

        # Draw navigation
        self.draw_navigation()

        self.display.update()


class TextRenderer(BaseRenderer):
    """Renderer for static text display"""

    def render(self, params):
        """Render static text content"""
        self.display.set_pen(self.colors["BLACK"])
        self.display.clear()
        self.display.set_pen(self.colors["WHITE"])

        # Draw border
        self.draw_border()

        # Get text content and title from params
        title = params.get("title", "Message")
        text = params.get("text", "No message content")

        # Draw title
        self.display.text(title, 10, 10)

        # Draw text content (handle multi-line)
        lines = []
        if isinstance(text, str):
            # Split by newlines or wrap at ~25 chars
            for line in text.split("\n"):
                while len(line) > 25:
                    # Try to break at space
                    break_point = line[:25].rfind(" ")
                    if break_point == -1:  # No space found
                        break_point = 25
                    lines.append(line[:break_point])
                    line = line[break_point:].strip()
                if line:
                    lines.append(line)
        else:
            # Handle a list of lines
            lines = text

        # Draw lines
        y_pos = 40
        for line in lines:
            if y_pos < self.height - 30:  # Ensure we don't overlap with bottom text
                self.display.text(line, 10, y_pos)
                y_pos += 20

        # Draw navigation
        self.draw_navigation()

        self.display.update()
