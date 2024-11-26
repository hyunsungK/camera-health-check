import ansible_runner

def event_handler(event):
    """
    Ansible 실행 중 발생하는 각 이벤트를 처리합니다.

    Args:
        event (dict): Ansible 이벤트 데이터.
    """
    event_type = event.get('event')
    if event_type == 'runner_on_ok':
        host = event['event_data']['host']
        task = event['event_data']['task']
        print(f"호스트 '{host}'에서 작업 '{task}' 성공")
    elif event_type == 'runner_on_failed':
        host = event['event_data']['host']
        task = event['event_data']['task']
        print(f"호스트 '{host}'에서 작업 '{task}' 실패")

def finished_callback(runner):
    """
    Ansible 실행이 완료된 후 호출됩니다.

    Args:
        runner (ansible_runner.Runner): 실행된 Runner 객체.
    """
    stats = runner.stats
    print("=== 실행 요약 ===")
    print(stats)
    # for host, summary in stats.items():
        # print(f"{host}: {summary}")

def run_ansible_ping():
    """
    Ansible의 ping 모듈을 실행하여 호스트와의 연결을 확인합니다.
    """
    # 인벤토리 데이터 정의
    inventory_data = {
        "all": {
            "hosts": {
                "server1": {
                    "ansible_host": "127.0.0.1",
                }
            }
        }
    }

    # 플레이북 정의
    playbook = [
        {
            "name": "Ping Test",
            "hosts": "all",
            "gather_facts": False,
            "tasks": [
                {
                    "name": "Ping all hosts",
                    "ansible.builtin.ping": {}
                }
            ]
        }
    ]

    # Ansible Runner 실행
    result = ansible_runner.run(
        inventory=inventory_data,
        playbook=playbook,
        quiet=True,
        event_handler=event_handler,
        finished_callback=finished_callback
    )

    # 결과 처리
    if result.rc == 0:
        print("모든 호스트에 대한 핑 테스트 성공")
    else:
        print("일부 호스트에 대한 핑 테스트 실패")

if __name__ == "__main__":
    run_ansible_ping()