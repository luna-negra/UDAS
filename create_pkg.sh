#!/bin/bash/


# set global vars
LIBRARY_NAME="libusb-1.0.0-dev"
LIBRARY_VERSION=2:1.0.27-1


# activate pyvenv
activate_pyvenv () {
  echo -n "* Activate pyvenv: "
  source .venv/bin/activate
  if [ $? -ne 0 ]; then
    echo -e "\e[1;Fail to activate\e[0;0m"
    echo -e "\n[ERROR]\nProject file does not have pyvenv. Please create pyvenv with command 'python -m venv venv'.\e[0;0m\n"
    exit 1;
  else
    echo -e "\e[1;32mActivate\e[0;0m"
  fi
}

# check pyvenv activation
check_activate_pyvenv () {
  echo -n "* Pyvenv status: "
  if [[ "$VIRTUAL_ENV" == "" ]];then
    echo -e "\e[1;31mNot Activated\e[0;0m"
    return 1;
  fi

  echo -e "\e[1;33mActivated\e[0;0m"
  return 0;
}

# check root or sudo privilege.
# return 0 if there is issue with privilege.
check_privilege () {
  echo -n "* Check privilege: "
  if [ "$EUID" -ne 0 ]; then
    echo -e "\e[1;31mNot Authorized."
    echo -e "\n[ERROR]\nYou have to run this command with root or sudo privilege.\e[0;0m\n"
    exit 1;
  fi

  echo -e "\e[1;32mAuthorized\e[0;0m"
}

# check tools to compile source codes.
check_build_essential () {
  echo -n "* Check build-essential installed: "
  dpkg -l | grep build-essential > /dev/null
  if [ $? -eq 0 ]; then
    echo -e "\e[1;32mInstalled\e[0;0m"
    return 0
  else
    echo -e "\e[1;31mNot Installed\e[0;0m."
    return 1
  fi
}

# check library.
# check library libusb-1.0.0 is exist and version equal or up to 1.0.27
# return 0 for installed, 1 for not installed.
# if return 1, execute install_libusb()
check_library () {
  echo -n "* Check libusb installed: "

  dpkg -l | grep $LIBRARY_NAME | grep $LIBRARY_VERSION > /dev/null
  if [ $? -eq 0 ]; then
    echo -e "\e[1;32mInstalled\e[0;0m"
    return 0
  else
    echo -e "\e[1;31mNot Installed\e[0;0m."
    return 1
  fi
}

# check source code of C
check_source_c () {
  C_SOURCE_FOLDER="src/c/"
  C_SOURCE_LIST=("Makefile" "udas.c" "udas.h" "udas_common.c" "udas_common.h" "das_detector.c" "udas_detector.h")

  echo "* Check C source files"
  for file in ${C_SOURCE_LIST[@]}; do
    echo -n "  - $file: "
    if [[ ! -e $C_SOURCE_FOLDER$C_SOURCE_LIST ]]; then
      echo -e "\e[1;31mNot Exist\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] File $file is not exist. Stop creating package.\n\e[0;0m"
      exit 1
    else
      echo -e "\e[1;32mchecked\e[0;0m"
    fi
    done
}

# check source code of Python
check_source_python () {
  PYTHON_SOURCE_PATH="src/python/"
  PYTHON_SOURCE_LIST=("udas/__init__.py" "udas/udas_custom_widget.py" "udas/udas_pytool.py" "udas_alert.py" "udas_gui.py")

  echo "* Check Python source files"
  for file in ${PYTHON_SOURCE_LIST[@]}; do
    echo -n "  - $file: "
    if [[ ! -e $PYTHON_SOURCE_PATH$PYTHON_SOURCE_LIST ]]; then
      echo -e "\e[1;31mNot Exist\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] File $file is not exist. Stop creating package.\n\e[0;0m"
      exit 1
    else
      echo -e "\e[1;32mchecked\e[0;0m"
    fi
    done
}

# compile_c
compile_c_source () {
  echo -n "* Compile C source: "
  cd src/c
  if [ $? -eq 0 ]; then
    make clean > /dev/null
    make > /dev/null
    if [ $? -eq 0 ]; then
      echo -e "\e[1;32mOK\e[0;0m"
      cd ../..
      return 0
    fi
  fi

  echo -e "\e[1;31mFail\e[0;0m"
  echo -e "\e[1;31m\n[ERROR] Fail to compile C source files.\n\e[0;0m"
  cd ../..
  exit 1;
}

# compile_python
compile_python_source () {
  echo "* Compile Python source (will take approx 10 ~ 15 mins)"
  cd src/python
  if [ $? -eq 0 ]; then
    echo -n "  - udas_alert: "
    pyinstaller -F -w udas_alert.py --name=udas_alert --distpath=../../usr/bin/. --add-data=udas:udas --collect-data=PySide6 2> /dev/null
    if [ $? -ne 0 ]; then
      echo -e "\e[1;31mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to compile 'udas-alert'.\n\e[0;0m"
      exit 1
    else
      echo -e "\e[1;32mOK\e[0;0m"
    fi

    echo -n "  - udas_gui: "
    pyinstaller -F -w udas_gui.py --name=udas_gui --distpath=../../usr/bin/. --add-data=udas:udas --collect-data=PySide6 2> /dev/null

    if [ $? -ne 0 ]; then
      echo -e "\e[1;32mOK\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to compile 'udas-gui'.\n\e[0;0m"
      exit 1
    else
      echo -e "\e[1;32mOK\e[0;0m"
    fi

    return 0
  fi
}

# create bin folder
create_bin_folder () {
  bin_folder="usr/bin"

  echo -n "* Create command folder: "
  if [[ ! -d $bin_folder ]]; then
    mkdir -p $bin_folder
    if [ $? == 0 ]; then
      echo -e "\e[1;32mOK\e[0;0m"
    else
      echo -e "\e[1;31mFail\e[0;0m"
    fi
  else
    echo -e "\e[1;33mAlready Exist\e[0;0m"
  fi
}

# create log path
create_logfile () {
  echo "* Create Logfile"
  LOG_PATH=var/log/udas/
  LOG_FILE=udas.log
  LOG=$LOG_PATH$LOG_FILE

  echo -n "  - Create log folder: "
  if [[ ! -d $LOG_PATH ]]; then
    mkdir -p $LOG_PATH
    if [ $? == 0 ]; then
      echo -e "\e[1;32mSuccess\e[0;0m"
    else
      echo -e "\e[1;31mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to create folder for log file."
      exit 1
    fi
  else
    echo -e "\e[1;33mAlready Exist\e[0;0m"
  fi

  echo -n "  - Create log file: "
  if [[ ! -e $LOG ]]; then
    touch $LOG
    if [ $? == 0 ]; then
      echo -e "\e[1;32mOK\e[0;0m"
    else
      echo -e "\e[1;31mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to create log file."
      exit 1
    fi
  else
    echo -e "\e[1;33mAlready Exist\e[0;0m"
  fi

  echo -n "  - change chmod for logfile: "
  chmod 644 $LOG
  if [ $? == 0 ]; then
    echo -e "\e[1;32mOK\e[0;0m"
  else
    echo -e "\e[1;33mFail\e[0;0m"
    echo -e "\e[1;33m\n[Warning] Fail to change permission for log file.."
  fi
  
  return 0
}

# install build-essential
install_build_essential () {
  echo -n "  * Install build-essential: "
  apt-get install -y build-essential
  if [ $? - ne 0 ]; then
    echo -e "\e[1;31mFail\e[0;0m"
    echo -e "\e[1;31m\n[ERROR} Fail to install build-essential\n\e[0;0m"
    exit 1
  fi

  echo -e "\e[1;32mOK\e[0;0m"
  return 0
}

# install libusb-1.0.0-dev
# return 0 for install successfully, 1 for fail
install_libusb () {
  apt-get install -y $LIBRARY_NAME=$LIBRARY_VERSION
  if [ $? -ne 0 ]; then
    echo -e "\e[1;31mFail\e[0;0m"
    echo -e "\e[1;31m\n[ERROR} Fail to install libusb-1.0.0-dev\n\e[0;0m"
    exit 1
  fi

  echo -e "\e[1;32mOK\e[0;0m"
  return 0
}

# install requirements
install_requirements () {
  echo -n "* Install python packages: "
  pip install -r src/python/requirements.txt 1> /dev/null
  if [ $? -ne 0 ]; then
    echo -e "\e[1;31mFailed\e[0;0m"
    echo -e "\e[1;31m[ERROR] Fail to install requirements.txt in src/python.\e[0;0m"
    exit 1
  else
    echo -e "\e[1;32mOK\e[0;0m"
  fi
}

# main function
main () {
  clear;
  echo "[Pre-Flight Check]"
  check_privilege
  check_source_c
  check_source_python
  check_build_essential
  if [[ $? -ne 0 ]]; then
    install_build_essential
  fi

  check_library
  if [[ $? -ne 0 ]]; then
    install_libusb
  fi

  echo ""
  echo "[Engine On]"
  create_bin_folder
  create_logfile
  check_activate_pyvenv
  if [ $? -eq 1 ]; then
    activate_pyvenv
  fi
  install_requirements

  echo ""
  echo "[START COMPILE]"
  compile_c_source
  compile_python_source

  echo ""
  echo "COMPLETE Process"
}

main