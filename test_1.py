import paramiko

def execute_remote_command(host, port, username, password, command):
    try:
        # Create an SSH client
        ssh_client = paramiko.SSHClient()
        
        # Automatically add the server's host key if not already known
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the remote server
        ssh_client.connect(hostname=host, port=port, username=username, password=password)
        
        # Execute the command
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Read the output and error streams
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        
        # Close the connection
        ssh_client.close()
        
        return output, error

    except Exception as e:
        return None, str(e)


# Example usage
if __name__ == "__main__":
    host = "192.168.1.100"
    port = 22
    username = "your_user"
    password = "your_password"
    command = "uname -a"
    
    output, error = execute_remote_command(host, port, username, password, command)
    
    if output:
        print(f"Command Output:\n{output}")
    if error:
        print(f"Command Error:\n{error}")