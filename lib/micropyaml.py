"""
MicroPYAML - A minimal YAML parser for MicroPython
"""

class MicroYAML:
    """A simple YAML parser with limited functionality"""
    
    @staticmethod
    def parse(yaml_str):
        """Parse a YAML string into a Python dictionary"""
        # Remove comments and handle empty lines
        lines = []
        for line in yaml_str.split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                lines.append(line)
        
        # Parse the yaml structure
        result = {}
        current_list = None
        current_key = None
        indent_stack = [0]  # Start with root level indent (0)
        key_stack = []
        
        for line in lines:
            # Count leading spaces for indentation
            indent = len(line) - len(line.lstrip())
            line = line.strip()
            
            # Handle list items
            if line.startswith('-'):
                item_content = line[1:].strip()
                
                # If it's a simple list item
                if ':' not in item_content:
                    if current_list is None:
                        # Starting a new list
                        if not key_stack:
                            # Root level list not supported
                            continue
                        target = result
                        for k in key_stack[:-1]:
                            if k not in target:
                                target[k] = {}
                            target = target[k]
                        
                        if key_stack[-1] not in target:
                            target[key_stack[-1]] = []
                        current_list = target[key_stack[-1]]
                    
                    current_list.append(item_content.strip('"'))
                    continue
                
                # It's a list item with properties (mapping)
                if ':' in item_content:
                    # Start a new dictionary in the list
                    if current_list is None:
                        # Create a new list if needed
                        target = result
                        for k in key_stack[:-1]:
                            if k not in target:
                                target[k] = {}
                            target = target[k]
                        
                        if key_stack[-1] not in target:
                            target[key_stack[-1]] = []
                        current_list = target[key_stack[-1]]
                    
                    new_item = {}
                    current_list.append(new_item)
                    
                    # Process the first key-value pair in this item
                    key, value = item_content.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle values
                    if value:
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]  # Remove quotes
                        elif value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        else:
                            # Try to convert to number if possible
                            try:
                                if '.' in value:
                                    value = float(value)
                                else:
                                    value = int(value)
                            except ValueError:
                                pass  # Keep as string
                        
                        new_item[key] = value
                    else:
                        # Empty value
                        new_item[key] = None
                    
                    continue
                    
            # Handle regular key-value pairs
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Adjust the stack based on indentation
                while indent_stack[-1] >= indent and len(indent_stack) > 1:
                    indent_stack.pop()
                    key_stack.pop()
                
                # If this is a new indent level, update stacks
                if indent > indent_stack[-1]:
                    indent_stack.append(indent)
                    key_stack.append(current_key)
                
                current_key = key
                current_list = None  # Reset list context when we see a key
                
                # Handle values
                if value:
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]  # Remove quotes
                    elif value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    else:
                        # Try to convert to number if possible
                        try:
                            if '.' in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except ValueError:
                            pass  # Keep as string
                    
                    # Update the nested dictionary
                    target = result
                    for k in key_stack:
                        if k is not None:  # Skip None keys (root level)
                            if k not in target:
                                target[k] = {}
                            target = target[k]
                    
                    target[key] = value
                else:
                    # Empty value - this will become a dictionary or list
                    target = result
                    for k in key_stack:
                        if k is not None:  # Skip None keys (root level)
                            if k not in target:
                                target[k] = {}
                            target = target[k]
                    
                    if key not in target:
                        target[key] = {}
        
        return result

    @staticmethod
    def load_file(filename):
        """Load and parse a YAML file"""
        try:
            with open(filename, 'r') as f:
                yaml_str = f.read()
                
            # Add better error handling
            if not yaml_str or yaml_str.strip() == "":
                print(f"YAML file {filename} is empty")
                return {}
                
            result = MicroYAML.parse(yaml_str)
            return result
        except OSError as e:
            print(f"Error loading YAML file {filename}: {e}")
            return {}
        except IndexError as e:
            print(f"YAML parsing error (index error) in {filename}: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error parsing YAML {filename}: {e}")
            return {}