"""
MicroDashboard - A workspace-based dashboard system for PicoDash
"""

# Import required libraries
import time
import json

# Constants
SCROLL_ANIMATION_MS = 500  # Animation time in milliseconds

class WorkspaceManager:
    """Manages multiple workspaces with configurable scrolling"""
    
    def __init__(self, display, width, height):
        """Initialize the workspace manager"""
        self.display = display
        self.display_width = width
        self.display_height = height
        self.workspaces = []
        self.current_index = 0
        self.last_change_time = time.ticks_ms()
        self.is_transitioning = False
        self.transition_start = 0
        self.transition_progress = 0
        # Print debug info during initialization
        print(f"WorkspaceManager initialized with display size: {width}x{height}")
        
    def add_workspace(self, workspace):
        """Add a workspace to the manager"""
        self.workspaces.append(workspace)
        workspace.set_display(self.display, self.display_width, self.display_height)
        
    def load_from_config(self, config_dict):
        """Load workspaces from a configuration dictionary"""
        if not isinstance(config_dict, dict) or 'workspaces' not in config_dict:
            print("Invalid configuration format")
            return False
        
        # Clear existing workspaces
        self.workspaces = []
        
        # Create workspaces from config
        for ws_config in config_dict.get('workspaces', []):
            name = ws_config.get('name', 'Unnamed')
            display_time = ws_config.get('display_time', 10)
            renderer_type = ws_config.get('renderer', 'TextRenderer')
            
            # Create a workspace with appropriate renderer
            workspace = Workspace(name, display_time)
            
            if renderer_type == 'TimeRenderer':
                renderer = TimeRenderer()
                workspace.set_renderer(renderer)
            elif renderer_type == 'DateRenderer':
                renderer = DateRenderer()
                workspace.set_renderer(renderer)
            elif renderer_type == 'TextRenderer':
                text = ws_config.get('text', 'Default Text')
                renderer = TextRenderer(text)
                workspace.set_renderer(renderer)
            else:
                print(f"Unknown renderer type: {renderer_type}")
                renderer = TextRenderer(f"Error: Unknown renderer {renderer_type}")
                workspace.set_renderer(renderer)
            
            # Add the configured workspace
            self.add_workspace(workspace)
        
        return len(self.workspaces) > 0
    
    def update(self):
        """Update the workspace manager"""
        current_time = time.ticks_ms()
        
        # No workspaces defined
        if not self.workspaces:
            return
        
        current_workspace = self.workspaces[self.current_index]
        
        # Handle transitions
        if self.is_transitioning:
            elapsed = time.ticks_diff(current_time, self.transition_start)
            if elapsed >= SCROLL_ANIMATION_MS:
                # Transition complete
                self.is_transitioning = False
                self.last_change_time = current_time
            else:
                # Update transition progress (0.0 to 1.0)
                self.transition_progress = elapsed / SCROLL_ANIMATION_MS
                self._render_transition()
                return
        
        # Check if it's time to switch workspaces
        if time.ticks_diff(current_time, self.last_change_time) >= current_workspace.display_time * 1000:
            self._start_transition()
            return
        
        # Regular update - let the current workspace render
        try:
            print(f"Updating workspace {self.current_index}")
            current_workspace.update()
            print(f"Rendering workspace {self.current_index}")
            current_workspace.render()
            print(f"Workspace {self.current_index} rendered successfully")
        except Exception as e:
            print(f"ERROR in workspace {self.current_index} render: {type(e).__name__}: {e}")
    
    def _start_transition(self):
        """Start a transition to the next workspace"""
        self.is_transitioning = True
        self.transition_start = time.ticks_ms()
        self.transition_progress = 0.0
        
        # Calculate the next workspace index
        self.next_index = (self.current_index + 1) % len(self.workspaces)
        
        # Prepare both workspaces
        self.workspaces[self.current_index].update()
        self.workspaces[self.next_index].update()
    
    def _render_transition(self):
        """Render the transition between workspaces"""
        try:
            # Calculate offset based on transition progress
            offset = int(self.transition_progress * self.display_width)
            print(f"Rendering transition: progress={self.transition_progress}, offset={offset}")
            
            # Render current workspace sliding out
            self.display.set_pen(0, 0, 0)  # Black background
            self.display.clear()
            
            # Use a function to handle the actual rendering with offset
            try:
                print(f"Rendering workspace {self.current_index} with offset {-offset}")
                self._render_workspace_with_offset(self.current_index, -offset)
                print(f"Rendering workspace {self.next_index} with offset {self.display_width - offset}")
                self._render_workspace_with_offset(self.next_index, self.display_width - offset)
                
                # Update the display
                self.display.update()
                print("Transition rendered successfully")
            except Exception as e:
                print(f"ERROR rendering workspace in transition: {e}")
            
            # If transition is complete, update current index
            if self.transition_progress >= 1.0:
                self.current_index = self.next_index
                self.is_transitioning = False
                print(f"Transition complete, current workspace now: {self.current_index}")
        except Exception as e:
            print(f"ERROR in transition rendering: {type(e).__name__}: {e}")
    
    def _render_workspace_with_offset(self, index, offset_x):
        """Render a workspace with a horizontal offset"""
        try:
            # Save current state
            print(f"Rendering workspace {index} with offset {offset_x}")
            self.workspaces[index].render_with_offset(offset_x, 0)
            print(f"Workspace {index} rendered with offset successfully")
        except Exception as e:
            print(f"ERROR rendering workspace {index} with offset: {type(e).__name__}: {e}")
        

class Workspace:
    """Represents a single configurable dashboard workspace"""
    
    def __init__(self, name, display_time=10):
        """Initialize a workspace"""
        self.name = name
        self.display_time = display_time  # in seconds
        self.renderer = None
        self.display = None
        self.width = 0
        self.height = 0
        print(f"Created workspace: {name}, display time: {display_time}s")
        
    def set_renderer(self, renderer):
        """Set the renderer for this workspace"""
        if renderer is None:
            print(f"ERROR: Trying to set None renderer for workspace {self.name}")
            return
            
        self.renderer = renderer
        print(f"Setting renderer of type {type(renderer).__name__} for workspace {self.name}")
        
        if self.display:
            try:
                self.renderer.set_display(self.display, self.width, self.height)
                print(f"Display set for renderer in workspace {self.name}")
            except Exception as e:
                print(f"Error setting display for renderer: {e}")
        
    def set_display(self, display, width, height):
        """Set the display for this workspace"""
        self.display = display
        self.width = width
        self.height = height
        print(f"Setting display for workspace {self.name}: {width}x{height}")
        
        if self.renderer:
            try:
                self.renderer.set_display(display, width, height)
                print(f"Display updated for renderer in workspace {self.name}")
            except Exception as e:
                print(f"Error updating display for renderer: {e}")
    
    def update(self):
        """Update the workspace content"""
        if self.renderer:
            self.renderer.update()
    
    def render(self):
        """Render the workspace"""
        if self.renderer:
            self.renderer.render()
    
    def render_with_offset(self, offset_x, offset_y):
        """Render the workspace with an offset"""
        if self.renderer:
            self.renderer.render_with_offset(offset_x, offset_y)


# Base Renderer class
class BaseRenderer:
    """Base class for all renderers"""
    
    def __init__(self):
        """Initialize the renderer"""
        self.display = None
        self.width = 0
        self.height = 0
        
    def set_display(self, display, width, height):
        """Set the display for this renderer"""
        self.display = display
        self.width = width
        self.height = height
    
    def update(self):
        """Update the renderer's content"""
        pass
    
    def render(self):
        """Render the content to the display"""
        if not self.display:
            return
            
        # Default implementation - clear the display
        self.display.set_pen(0, 0, 0)  # Black background
        self.display.clear()
        self.display.update()
    
    def render_with_offset(self, offset_x, offset_y):
        """Render with a position offset (for transitions)"""
        # This will be overridden by specific renderers
        pass


class TimeRenderer(BaseRenderer):
    """Renders the current time"""
    
    def __init__(self):
        """Initialize the time renderer"""
        super().__init__()
        self.current_time = ""
        
    def update(self):
        """Update the time"""
        current = time.localtime()
        self.current_time = "{:02d}:{:02d}".format(current[3], current[4])  # HH:MM
    
    def render(self):
        """Render the time"""
        if not self.display:
            print("No display set for TimeRenderer")
            return
            
        try:
            # Clear the display
            self.display.set_pen(0, 0, 0)  # Black background
            self.display.clear()
            
            # Draw a border
            self.display.set_pen(255, 255, 255)  # White border
            self.display.line(0, 0, self.width-1, 0)
            self.display.line(0, 0, 0, self.height-1)
            self.display.line(self.width-1, 0, self.width-1, self.height-1)
            self.display.line(0, self.height-1, self.width-1, self.height-1)
            
            # Try different approaches for text rendering
            try:
                # Draw title with 2 arguments
                self.display.text("Current Time", 10, 10)
                # Draw time with 2 arguments
                self.display.text(self.current_time, 10, 50)
            except TypeError:
                # If that fails, try with just 3 arguments
                try:
                    self.display.text("Current Time", 10, 10, self.width-20)
                    self.display.text(self.current_time, 10, 50, self.width-20)
                except TypeError:
                    # Last resort - try with all arguments
                    self.display.text("Current Time", 10, 10, self.width-20, 2)
                    self.display.text(self.current_time, 10, 50, self.width-20, 4)
            
            # Update the display
            self.display.update()
        except Exception as e:
            print(f"ERROR in TimeRenderer.render: {type(e).__name__}: {e}")
    
    def render_with_offset(self, offset_x, offset_y):
        """Render the time with an offset"""
        if not self.display:
            print("No display set for TimeRenderer with offset")
            return
            
        try:
            # Draw a border with offset
            self.display.set_pen(255, 255, 255)  # White border
            self.display.line(offset_x, offset_y, offset_x + self.width-1, offset_y)
            self.display.line(offset_x, offset_y, offset_x, offset_y + self.height-1)
            self.display.line(offset_x + self.width-1, offset_y, offset_x + self.width-1, offset_y + self.height-1)
            self.display.line(offset_x, offset_y + self.height-1, offset_x + self.width-1, offset_y + self.height-1)
            
            # Try different approaches for text rendering
            try:
                # Try with 2 arguments
                self.display.text("Current Time", offset_x + 10, offset_y + 10)
                self.display.text(self.current_time, offset_x + 10, offset_y + 50)
            except TypeError:
                # If that fails, try with 3 arguments
                try:
                    self.display.text("Current Time", offset_x + 10, offset_y + 10, self.width-20)
                    self.display.text(self.current_time, offset_x + 10, offset_y + 50, self.width-20)
                except TypeError:
                    # Last resort - try with all arguments
                    self.display.text("Current Time", offset_x + 10, offset_y + 10, self.width-20, 2)
                    self.display.text(self.current_time, offset_x + 10, offset_y + 50, self.width-20, 4)
        except Exception as e:
            print(f"ERROR in TimeRenderer.render_with_offset: {type(e).__name__}: {e}")


class DateRenderer(BaseRenderer):
    """Renders the current date"""
    
    def __init__(self):
        """Initialize the date renderer"""
        super().__init__()
        self.current_date = ""
        
    def update(self):
        """Update the date"""
        current = time.localtime()
        self.current_date = "{:04d}-{:02d}-{:02d}".format(current[0], current[1], current[2])  # YYYY-MM-DD
    
    def render(self):
        """Render the date"""
        if not self.display:
            print("No display set for DateRenderer")
            return
            
        try:
            # Clear the display
            self.display.set_pen(0, 0, 0)  # Black background
            self.display.clear()
            
            # Draw a border
            self.display.set_pen(255, 255, 255)  # White border
            self.display.line(0, 0, self.width-1, 0)
            self.display.line(0, 0, 0, self.height-1)
            self.display.line(self.width-1, 0, self.width-1, self.height-1)
            self.display.line(0, self.height-1, self.width-1, self.height-1)
            
            # Try different approaches for text rendering
            try:
                # Try with 2 arguments
                self.display.text("Current Date", 10, 10)
                self.display.text(self.current_date, 10, 50)
            except TypeError:
                # If that fails, try with 3 arguments
                try:
                    self.display.text("Current Date", 10, 10, self.width-20)
                    self.display.text(self.current_date, 10, 50, self.width-20) 
                except TypeError:
                    # Last resort - try with all arguments
                    self.display.text("Current Date", 10, 10, self.width-20, 2)
                    self.display.text(self.current_date, 10, 50, self.width-20, 3)
            
            # Update the display
            self.display.update()
        except Exception as e:
            print(f"ERROR in DateRenderer.render: {type(e).__name__}: {e}")
    
    def render_with_offset(self, offset_x, offset_y):
        """Render the date with an offset"""
        if not self.display:
            print("No display set for DateRenderer with offset")
            return
            
        try:
            # Draw a border with offset
            self.display.set_pen(255, 255, 255)  # White border
            self.display.line(offset_x, offset_y, offset_x + self.width-1, offset_y)
            self.display.line(offset_x, offset_y, offset_x, offset_y + self.height-1)
            self.display.line(offset_x + self.width-1, offset_y, offset_x + self.width-1, offset_y + self.height-1)
            self.display.line(offset_x, offset_y + self.height-1, offset_x + self.width-1, offset_y + self.height-1)
            
            # Try different approaches for text rendering
            try:
                # Try with 2 arguments
                self.display.text("Current Date", offset_x + 10, offset_y + 10)
                self.display.text(self.current_date, offset_x + 10, offset_y + 50)
            except TypeError:
                # If that fails, try with 3 arguments
                try:
                    self.display.text("Current Date", offset_x + 10, offset_y + 10, self.width-20)
                    self.display.text(self.current_date, offset_x + 10, offset_y + 50, self.width-20)
                except TypeError:
                    # Last resort - try with all arguments
                    self.display.text("Current Date", offset_x + 10, offset_y + 10, self.width-20, 2)
                    self.display.text(self.current_date, offset_x + 10, offset_y + 50, self.width-20, 3)
        except Exception as e:
            print(f"ERROR in DateRenderer.render_with_offset: {type(e).__name__}: {e}")


class TextRenderer(BaseRenderer):
    """Renders static text"""
    
    def __init__(self, text="Welcome"):
        """Initialize the text renderer"""
        super().__init__()
        self.text = text
    
    def update(self):
        """Update the renderer (nothing to update for static text)"""
        pass
    
    def render(self):
        """Render the text"""
        if not self.display:
            print("No display set for TextRenderer")
            return
            
        try:
            # Clear the display
            self.display.set_pen(0, 0, 0)  # Black background
            self.display.clear()
            
            # Draw a border
            self.display.set_pen(255, 255, 255)  # White border
            self.display.line(0, 0, self.width-1, 0)
            self.display.line(0, 0, 0, self.height-1)
            self.display.line(self.width-1, 0, self.width-1, self.height-1)
            self.display.line(0, self.height-1, self.width-1, self.height-1)
            
            # Draw the text - handle different implementations of text method
            print(f"Drawing text: '{self.text}' at position (10, 50)")
            
            # Try different approaches to accommodate different implementations
            try:
                # Method 1: Try with just text and position (x, y)
                print("Trying text method with 2 arguments")
                self.display.text(self.text, 10, 50)
                print("Text drawn with 2 arguments successfully")
            except TypeError:
                try:
                    # Method 2: Try with 3 arguments (text, x, y)
                    print("Method 1 failed. Trying with 3 arguments")
                    self.display.text(self.text, 10, 50)
                    print("Text drawn with 3 arguments successfully")
                except TypeError:
                    try:
                        # Method 3: Try with 4 arguments (text, x, y, width)
                        print("Method 2 failed. Trying with 4 arguments")
                        self.display.text(self.text, 10, 50, self.width-20)
                        print("Text drawn with 4 arguments successfully")
                    except TypeError:
                        # Method 4: Try with all 5 arguments (text, x, y, width, scale)
                        print("Method 3 failed. Trying with 5 arguments")
                        self.display.text(self.text, 10, 50, self.width-20, 2)
                        print("Text drawn with 5 arguments successfully")
            
            # Update the display
            self.display.update()
            print("Display updated successfully")
        except Exception as e:
            print(f"ERROR in TextRenderer.render: {type(e).__name__}: {e}")
    
    def render_with_offset(self, offset_x, offset_y):
        """Render the text with an offset"""
        if not self.display:
            print("No display set for TextRenderer with offset")
            return
            
        try:
            # Draw a border with offset
            self.display.set_pen(255, 255, 255)  # White border
            self.display.line(offset_x, offset_y, offset_x + self.width-1, offset_y)
            self.display.line(offset_x, offset_y, offset_x, offset_y + self.height-1)
            self.display.line(offset_x + self.width-1, offset_y, offset_x + self.width-1, offset_y + self.height-1)
            self.display.line(offset_x, offset_y + self.height-1, offset_x + self.width-1, offset_y + self.height-1)
            
            # Draw the text with offset - try different argument patterns
            print(f"Drawing offset text: '{self.text}' at position ({offset_x+10}, {offset_y+50})")
            
            # Try different approaches to accommodate different implementations
            try:
                # Method 1: Try with just text and position (x, y)
                print("Trying offset text method with 2 arguments")
                self.display.text(self.text, offset_x + 10, offset_y + 50)
                print("Offset text drawn with 2 arguments successfully")
            except TypeError:
                try:
                    # Method 2: Try with 3 arguments (text, x, y)
                    print("Offset method 1 failed. Trying with 3 arguments")
                    self.display.text(self.text, offset_x + 10, offset_y + 50)
                    print("Offset text drawn with 3 arguments successfully")
                except TypeError:
                    try:
                        # Method 3: Try with 4 arguments (text, x, y, width)
                        print("Offset method 2 failed. Trying with 4 arguments")
                        self.display.text(self.text, offset_x + 10, offset_y + 50, self.width-20)
                        print("Offset text drawn with 4 arguments successfully")
                    except TypeError:
                        # Method 4: Try with all 5 arguments (text, x, y, width, scale)
                        print("Offset method 3 failed. Trying with 5 arguments")
                        self.display.text(self.text, offset_x + 10, offset_y + 50, self.width-20, 2)
                        print("Offset text drawn with 5 arguments successfully")
        except Exception as e:
            print(f"ERROR in TextRenderer.render_with_offset: {type(e).__name__}: {e}")