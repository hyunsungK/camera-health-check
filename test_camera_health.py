from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook.play import Play
from ansible.module_utils.common.collections import ImmutableDict
from ansible.plugins.callback import CallbackBase


# Custom callback to capture results
class ResultCallback(CallbackBase):
    def __init__(self):
        super(ResultCallback, self).__init__()
        self.results = []

    def runner_on_ok(self, host, res):
        """Handle successful results."""
        host = res._host
        task_result = res._result
        self.results.append({'host': host.name, 'res': task_result})

    def runner_on_failed(self, host, res, ignore_errors=False):
        """Handle failed results."""
        host = res._host
        task_result = res._result
        self.results.append({'host': host.name, 'result': task_result, 'failed': True})


def check_camera_device(hosts_file, target_host, expected_cameras=3):
    # Ansible 환경 설정
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=[hosts_file])
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # Task 정의
    play_source = {
        'name': "Check Camera Device",
        'hosts': target_host,
        'gather_facts': False,
        'tasks': [
            {
                'name': "Check USB Devices",
                'action': {
                    'module': 'command',
                    'args': {
                        'cmd': 'lsusb'
                    }
                },
                'register': 'lsusb_output'
            },
            {
                'name': "Check for Camera Device",
                'action': {
                    'module': 'debug',
                    'args': {
                        'msg': '{{ lsusb_output.stdout_lines | select("search", "Camera") | list }}'
                    }
                }
            }
        ]
    }

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # Task 실행
    passwords = {
        'conn_pass': 'your_password_here'  # SSH 비밀번호
    }
    results_callback = ResultCallback()  # Custom callback for capturing results

    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=passwords,  # 비밀번호 전달
            stdout_callback=results_callback  # Attach custom callback
        )
        tqm.run(play)
    finally:
        if tqm:
            tqm.cleanup()

    # Analyze results
    for result in results_callback.results:
        print(f"Host: {result['host']}")
        if 'failed' in result:
            print(f"Task Failed: {result['result']}")
        else:
            # Check for camera devices
            lsusb_output = result['result'].get('stdout', '')
            if lsusb_output:
                # Filter for lines containing "Camera"
                camera_devices = [
                    line for line in lsusb_output.splitlines() if "Camera" in line
                ]
                num_detected_cameras = len(camera_devices)
                print(f"Detected Cameras: {num_detected_cameras}")
                print(f"Camera Details: {camera_devices}")

                # Compare with expected cameras
                if num_detected_cameras < expected_cameras:
                    missing_cameras = expected_cameras - num_detected_cameras
                    print(f"Warning: {missing_cameras} camera(s) not detected!")
                else:
                    print("All expected cameras detected!")
            else:
                print("No USB devices found.")

# 실행
if __name__ == "__main__":
    hosts_file = 'hosts'  # Ansible hosts 파일 경로
    target_host = '127.0.0.1'  # 타겟 호스트 이름
    expected_cameras = 3  # 예상 카메라 드라이버 갯수
    check_camera_device(hosts_file, target_host, expected_cameras)