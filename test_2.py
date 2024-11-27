import paramiko

def count_cameras_remote(host, port, username, password, camera_prefix="/dev/camera"):
    try:
        # SSH 클라이언트 생성
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 호스트 키 자동 추가
        ssh_client.connect(hostname=host, port=port, username=username, password=password)

        # 원격 명령 실행
        command = "ls -al /dev | grep camera"
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # 명령 출력 읽기
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        # 에러가 있다면 출력
        if error:
            print(f"Error: {error}")
            return 0, 0

        # EO 및 IR 카메라의 기준에 따라 필터링
        lines = output.splitlines()
        eo_cameras = [line for line in lines if line.startswith(camera_prefix) and int(line.split(camera_prefix)[1]) in [0,1,2] ]
        ir_cameras = [line for line in lines if line.startswith(camera_prefix) and int(line.split(camera_prefix)[1]) in [4,6,8] ]

        # EO 및 IR 카메라 개수 반환
        return len(eo_cameras), len(ir_cameras)

    except Exception as e:
        print(f"Exception: {e}")
        return 0, 0  # 기본값 반환

    finally:
        ssh_client.close()  # 연결 종료

# 원격 서버 정보
if __name__ == "__main__":
    host = "192.168.1.100"
    port = 22
    username = "your_user"
    password = "your_password"

    eo_count, ir_count = count_cameras_remote(host, port, username, password)
    print(f"EO Cameras: {eo_count}")
    print(f"IR Cameras: {ir_count}")