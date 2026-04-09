import subprocess

# --- THE MAXIMUM SECURITY BLOCKLIST ---
DANGEROUS_KEYWORDS = [
    # 1. File & Disk Destruction
    'remove', 'delete', 'del', 'rmdir', 'rd', 'erase', 'format', 
    'diskpart', 'clear-content', 'remove-item', 'move-item', 'rename-item',
    
    # 2. Process & Power Controls
    'stop-process', 'kill', 'taskkill', 'shutdown', 'restart-computer', 
    'stop-computer', 'logoff', 'suspend',
    
    # 3. Network Alteration
    'netsh', 'disable-netadapter', 'remove-netroute', 'set-net', 
    'firewall', 'ipconfig /release', 'ipconfig /renew',
    
    # 4. Registry & Core Configuration
    'reg ', 'reg.exe', 'registry', 'set-itemproperty', 'set-executionpolicy', 
    'bcdedit', 'schtasks', 'wmic', 'icacls', 'takeown',
    
    # 5. Service & User Alteration
    'stop-service', 'set-service', 'disable-localuser', 'net user', 
    'set-localuser', 'add-localgroupmember', 'remove-localgroupmember',
    
    # 6. Software Removal
    'uninstall', 'winget uninstall', 'msiexec /x'
]

def execute_powershell(command: str, safety_bypassed: bool = False):
    """
    Executes raw PowerShell commands. If the command modifies or deletes system settings/files,
    it returns a confirmation request instead of executing.
    """
    cmd_lower = command.lower()
    
    # 1. The Safety Catch
    if not safety_bypassed:
        for word in DANGEROUS_KEYWORDS:
            if word in cmd_lower:
                # We return this exact string so Llama knows to ask you out loud
                return (
                    f"REQUIRES_CONFIRMATION: The command contains a modifying keyword '{word}'. "
                    f"You MUST ask the user: 'You ordered me to perform a potentially destructive task. "
                    f"Is it correct what you thought? Reply with yes for final confirmation.'"
                )
                
    # 2. The Execution (Runs if safe, or if you said 'Yes')
    try:
        result = subprocess.run(
            ["powershell", "-Command", command], 
            capture_output=True, 
            text=True, 
            timeout=15
        )
        
        if result.returncode == 0:
            return f"Execution successful. Output: {result.stdout.strip()}"
        else:
            return f"Execution failed. Error: {result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return "Command timed out after 15 seconds."
    except Exception as e:
        return f"System error executing command: {str(e)}"