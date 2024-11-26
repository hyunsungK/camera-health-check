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

    def v2_runner_on_ok(self, result, **kwargs):
        """Handle successful results."""
        host = result._host
        task_result = result._result
        self.results.append({'host': host.name, 'result': task_result})

    def v2_runner_on_failed(self, result, **kwargs):
        """Handle failed results."""
        host = result._host
        task_result = result._result
        self.results.append({'host': host.name, 'result': task_result, 'failed': True})


def check_camera_device(hosts_file, target_host):
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
    passwords = {}
    results_callback = ResultCallback()  # Custom callback for capturing results

    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=passwords,
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
            if 'lsusb_output' in result['result']:
                usb_devices = result['result']['lsusb_output']
                print(f"USB Devices: {usb_devices}")
            else:
                print(f"Result: {result['result']}")

# 실행
if __name__ == "__main__":
    hosts_file = 'hosts'  # Ansible hosts 파일 경로
    target_host = '127.0.0.1'  # 타겟 호스트 이름
    check_camera_device(hosts_file, target_host)
