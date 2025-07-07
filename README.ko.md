### 번역: [영어](README.md) | [일본어](README.ja.md) |　[한국어](README.ko.md)
<hr>

# USB 접속 인증 시스템 (UDAS)

## 1. 소개
<div>
UDAS - USB Docking Authentication System은 Labtop, Desktop 등 USB 포트 블로커를 사용하지 않는 개인 PC에 대해, 
의심스러운 USB 저장 장치의 자동 연결로 인한 데이터 유출 혹은 변조를 방지하기 위해 개발된 프로그램입니다.
</div><br>

<div>
[ 제공 기능 ]<br>
- USB 저장 장치의 연결 감지<br> 
- 연결된 장치에 대한 사용자 확인<br>
- 장체에 대한 Blacklist & Whitelist 등록<br>
</div>

## 2. 사용 가능 OS 및 환경
<table>
    <th>
        <td>Version</td>
        <td>Operating System</td>
        <td>Distribution</td>
    </th>
    <tr>
        <td>1</td>
        <td>0.0.0 (Beta)</td>
        <td>Ubuntu 24.04</td>
        <td>Debian Package</td>
    </tr>
</table>

## 3. 설치
### (1) 수동 설치
① Git Reponsitory 다운로드
```commandline
git clone --branch main https://github.com/luna-negra/UDAS/
```
<br>
② Debian 패키지 파일 시스템 생성

```commandline
cd UDAS;
bash ./create_pkg.sh
```
![img.png](img.png)

* Debian 패키지 생성 중 에러 발생 시, 화면의 가이드에 따라 조치해 주십시오.
<br>

③ Debian 패키지 생성
```commandline
dpkg-deb --build udas-0.0-0-amd64/
```
<br>
④ UDAS Debian 패키지 설치

```commandline
sudo dpkg -i udas-0.0.0-amd64.deb
```
* 본 패키지 파일은 일반 사용자 계정으로 sudo를 사용하여 설치하는 것을 권장합니다.<br>
* 설치 중 화면의 가이드에 따라 비밀번호 변경 작업 및 설치 후 명령어 입력 작업을 진행해 주십시오.<br>

⑤ 설치 확인
* 설치를 진행한 계정의 홈 폴더에서 UDAS/udas_gui 실행.
```commandline
~/udas/udas_gui
```

![img_1.png](img_1.png)

* GUI 화면에서 Main > 서비스 구동 여부 확인
![img_2.png](img_2.png)

* UDAS Detector 및 UDAS Listener 서비스가 구동 중인 경우, PC에 USB 저장 장치 연결 시 whitelist 등록 여부를 확인하는 메세지 창이 생성됩니다.
![img_3.png](img_3.png)