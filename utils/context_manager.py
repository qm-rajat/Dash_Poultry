from PyQt6.QtCore import QObject, pyqtSignal, QDateTime
from typing import Dict, Any, Optional

class ContextManager(QObject):
    """Manages context data for cross-module navigation"""
    
    context_changed = pyqtSignal(str, dict)  # module_name, context_data
    
    def __init__(self):
        super().__init__()
        self._context = {}
        self._navigation_history = []
    
    def set_context(self, module_name: str, context_data: Dict[str, Any]):
        """Set context data for a specific module"""
        self._context[module_name] = context_data
        self.context_changed.emit(module_name, context_data)
        
        # Add to navigation history
        self._navigation_history.append({
            'module': module_name,
            'context': context_data.copy(),
            'timestamp': QDateTime.currentDateTime()
        })
        
        # Keep only last 10 entries
        if len(self._navigation_history) > 10:
            self._navigation_history.pop(0)
    
    def get_context(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get context data for a specific module"""
        return self._context.get(module_name)
    
    def clear_context(self, module_name: str = None):
        """Clear context data"""
        if module_name:
            self._context.pop(module_name, None)
        else:
            self._context.clear()
    
    def get_navigation_history(self) -> list:
        """Get navigation history"""
        return self._navigation_history.copy()
    
    def get_last_context(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent context for a module from history"""
        for entry in reversed(self._navigation_history):
            if entry['module'] == module_name:
                return entry['context']
        return None

# Global context manager instance
context_manager = ContextManager() 