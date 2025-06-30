#!/bin/bash/


# set global vars
PKG_NAME="udas"
PKG_VERSION="0.0-0"
PKG_ARCHITECTURE="amd64"
PKG_FOLDER=$PKG_NAME-$PKG_VERSION-$PKG_ARCHITECTURE
CONFIG_FOLDER=$PKG_FOLDER/etc/udas/config
DEBIAN_FOLDER=$PKG_FOLDER/DEBIAN
LIBUSB_NAME="libusb-1.0.0-dev"
LIBUSB_VERSION=2:1.0.27-1
UDEV_RULE_FOLDER=$PKG_FOLDER/etc/udev/rules.d


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

# check config file
check_config_file () {
  echo -n "* Check config file: "
  if [[ ! -e config.ini ]]; then
    echo -e "\e[1;31mNot Exist\e[0;0m"
    echo -e "\e[1;31m\n[ERROR] File 'config.ini' is missing.\n\e[0;0m"
    exit 1
  else
    echo -e "\e[1;32mChecked\e[0;0m"
  fi
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
check_libusb () {
  echo -n "* Check libusb installed: "

  dpkg -l | grep $LIBUSB_NAME | grep $LIBUSB_VERSION > /dev/null
  if [ $? -eq 0 ]; then
    echo -e "\e[1;32mInstalled\e[0;0m"
    return 0
  else
    echo -e "\e[1;33mNot Installed\e[0;0m."
    return 1
  fi
}

# check libxcb
# return 0 for installed, 1 for not installed.
# if return 1, execute install_libxcb_cursor()
check_libxcb_cursor() {
  echo -n "* Check libxcb-cursor0 installed: "
  dpkg -l | grep libxcb-cursor0 > /dev/null
  if [ $? -eq 0 ]; then
    echo -e "\e[1;32mInstalled\e[0;0m"
    return 0
  else
    echo -e "\e[1;33mNot Installed"
    return 1
  fi
}

# check source code of C
check_source_c () {
  C_SOURCE_FOLDER="src/c/"
  C_SOURCE_LIST=("Makefile" "udas.c" "udas.h" "udas_common.c" "udas_common.h" "das_detector.c" "udas_detector.h", "udas_listener.c", "udas_listener.h")

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
    if [[ ! -e $PYTHON_SOURCE_PATH$file ]]; then
      echo -e "\e[1;31mNot Exist\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] File $file is not exist. Stop creating package.\n\e[0;0m"
      exit 1
    else
      echo -e "\e[1;32mchecked\e[0;0m"
    fi
    done
}

# check source code of scripts
check_source_script () {
  echo -n "* Check scripts files: "
  if [[ ! -e postinst ]]; then
    echo -e "\e[1;31mNot Exist\e[0;0m"
    echo -e "\e[1;31m\n[ERROR] File $file is not exist. Stop creating package.\n\e[0;0m"
    exit 1
  else
    echo -e "\e[1;32mchecked\e[0;0m"
  fi
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
    pyinstaller -F -w udas_alert.py --name=udas_alert --distpath=../../$PKG_FOLDER/usr/bin/. --add-data=udas:udas --collect-data=PySide6 2> /dev/null
    if [ $? -ne 0 ]; then
      echo -e "\e[1;31mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to compile 'udas-alert'.\n\e[0;0m"
      exit 1
    else
      echo -e "\e[1;32mOK\e[0;0m"
    fi

    echo -n "  - udas_gui: "
    pyinstaller -F -w udas_gui.py --name=udas_gui --distpath=../../$PKG_FOLDER/usr/bin/. --add-data=udas:udas --collect-data=PySide6 2> /dev/null

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

# copy config_template file
copy_config_file () {
  echo -n "* Copy config template: "
  cp config.ini $CONFIG_FOLDER
  if [ $? -ne 0 ]; then
    echo -e "\e[1;31mFail\e[0;0m"
    echo -e "\e[1;31m\n[ERROR] Fail to copy config file to config folder.\n\e[0;0m"
    exit 1
  else
    echo -e "\e[1;32mOK\e[0;0m"
  fi
}

# copy postinst scripts
copy_scripts () {
  echo "* Copy script files"

  echo -n "  - postinst: "
  cp postinst $PKG_FOLDER/DEBIAN
  if [ $? -ne 0 ]; then
    echo -e "\e[1;31mFail\e[0;0m"
    echo -e "\e[1;31m\n[ERROR] Fail to copy scripts for post installation\n\e[0;0m"
    exit 1
  else
    chmod 755 $PKG_FOLDER/DEBIAN/postinst
    echo -e "\e[1;32mOK\e[0;0m"
  fi

  echo -n "  - prerm: "
  cp prerm $PKG_FOLDER/DEBIAN
  if [ $? -ne 0 ]; then
    echo -e "\e[1;31mFail\e[0;0m"
    echo -e "\e[1;31m\n[ERROR] Fail to copy scripts for pre uninstallation\n\e[0;0m"
    exit 1
  else
    chmod 755 $PKG_FOLDER/DEBIAN/prerm
    echo -e "\e[1;32mOK\e[0;0m"
  fi
}

# create pgk folder
create_pkg_folder() {
  echo -n "* Create package folder: "
  if [ ! -d $PKG_FOLDER ]; then
    mkdir $PKG_FOLDER
    if [ $? -eq 0 ]; then
      echo -e "\e[1;32mOK\e[0;0m"
    else
      echo -e "\e[1;32mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to create package folder.\e[0;0m"
      exit 1
    fi
  else
    echo -e "\e[1;33mAlready Exist\e[0;0m"
  fi
}

# create bin folder
create_bin_folder () {
  bin_folder=$PKG_FOLDER/usr/bin

  echo -n "* Create command folder: "
  if [[ ! -d $bin_folder ]]; then
    mkdir -p $bin_folder
    if [ $? == 0 ]; then
      echo -e "\e[1;32mOK\e[0;0m"
    else
      echo -e "\e[1;31mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to create command folder.\e[0;0m"
      exit 1
    fi
  else
    echo -e "\e[1;33mAlready Exist\e[0;0m"
  fi
}

# create control file
create_control_file () {
  control_file=$DEBIAN_FOLDER/control

  echo -n "* Create control file: "
  touch $control_file
  if [ $? -ne 0 ]; then
    echo -e "\e[1;31mFail\e[0;0m"
    echo -e "\e[1;31m\n[ERROR] Fail to create control file.\e[0;0m"
    exit 1
  else
    echo "Package: $PKG_NAME" > $control_file
    echo "Version: $PKG_VERSION" >> $control_file
    echo "Architecture: $PKG_ARCHITECTURE" >> $control_file
    echo "Maintainer: luna-negra <anonymous@mail.non>" >> $control_file
    echo "Description: Debian package for USB Docker Authentication System." >> $control_file
    echo -e "\e[1;32mOK\e[0;0m"
  fi
}

# create config folder
create_config_folder () {
  echo -n "* Create config folder: "
  if [[ ! -d $CONFIG_FOLDER ]]; then
    mkdir -p $CONFIG_FOLDER
    if [ $? -eq 0 ]; then
      echo -e "\e[1;32mOK\e[0;0m"
    else
      echo -e "\e[1;33mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to create config folder.\e[0;0m"
      exit 1
    fi
  else
    echo -e "\e[1;33mAlready Exist\e[0;0m"
  fi
}

# create DEBIAN folder
create_debian_folder () {
  echo -n "* Create DEBIAN folder: "
  if [[ ! -d $DEBIAN_FOLDER ]]; then
    mkdir $DEBIAN_FOLDER
    if [ $? -eq 0 ]; then
      echo -e "\e[1;32mOK\e[0;0m"
    else
      echo -e "\e[1;33mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to create DEBIAN folder.\e[0;0m"
      exit 1
    fi
  else
    echo -e "\e[1;33mAlready Exist\e[0;0m"
  fi
}

# create log path
create_logfile () {
  echo "* Create Logfile"
  LOG_PATH=$PKG_FOLDER/var/log/udas/
  LOG_FILE=udas.log
  LOG=$LOG_PATH$LOG_FILE

  echo -n "  - Create log folder: "
  if [[ ! -d $LOG_PATH ]]; then
    mkdir -p $LOG_PATH
    if [ $? == 0 ]; then
      echo -e "\e[1;32mSuccess\e[0;0m"
    else
      echo -e "\e[1;31mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to create folder.\e[0;0m"
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

# create udev rule files: 644
create_rule_files () {
  RULE_FILE_LIST=("99-udas.blacklist.rules" "99-udas.custom.rules" "99-udas.default.rules")

  echo "* Create udev rule files"
  for file in ${RULE_FILE_LIST[@]}; do
    echo -n "  - $file: "
    touch $UDEV_RULE_FOLDER/$file
    if [ $? -ne 0 ]; then
      echo -e "\e[1;31mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to create $file.\n\e[0;0m"
      exit 1
    fi
      echo -e "\e[1;32mOK\e[0;0m"
    done

  echo "ACTION==\"add\", SUBSYSTEM==\"block\", ENV{UDISKS_IGNORE}!=\"0\", ENV{UDISKS_IGNORE}=\"1\"" > $UDEV_RULE_FOLDER/${RULE_FILE_LIST[2]}
}

# create udev rule folder
create_rule_folder () {
  echo -n "* Create udev rule folder: "
  if [[ ! -d $UDEV_RULE_FOLDER ]]; then
    mkdir -p $UDEV_RULE_FOLDER
    if [ $? -eq 0 ]; then
      echo -e "\e[1;32mOK\e[0;0m"
    else
      echo -e "\e[1;33mFail\e[0;0m"
      echo -e "\e[1;31m\n[ERROR] Fail to create udev rule folder.\e[0;0m"
      exit 1
    fi
  else
    echo -e "\e[1;33mAlready Exist\e[0;0m"
  fi
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

# remove trash
remove_trash () {
  rm -rf src/python/build
  rm -rf src/python/*.spec
}


# main function
main () {
  clear;
  echo "[Pre-Flight Check]"
  check_source_c
  check_source_python
  check_source_script
  check_config_file

  check_build_essential
  result_build_essential=$?

  check_libusb
  result_libusb=$?

  check_libxcb_cursor
  result_libxcb_cursor0=$?

  if [ $result_build_essential -eq 1 ] || [ $result_libusb -eq 1 ] || [ $result_libxcb_cursor0 -eq 1 ]; then
    echo -e "\e[1;33m[WARNING] You have to install ubuntu package first. Please refer to the command below.\n\e[0;0m"
    echo -n " - Command: sudo apt-get install -y "
    if [ $result_build_essential -eq 1 ]; then
      echo -n "build_essential "
    fi
    if [ $result_libusb -eq 1 ]; then
      echo -n "libusb-1.0.0-dev "
    fi
    if [ $result_libxcb_cursor0 -eq 1 ]; then
      echo -n "libxcb-cursor0 "
    fi
    echo ""
    exit 1
  fi

  echo ""
  echo "[Engine On]"
  create_bin_folder
  create_logfile
  create_config_folder
  copy_config_file
  create_rule_folder
  create_rule_files
  create_debian_folder
  create_control_file
  copy_scripts

  echo ""
  echo "[Taxing to Runway 09]"
  check_activate_pyvenv
  if [ $? -eq 1 ]; then
    activate_pyvenv
  fi
  install_requirements

  echo ""
  echo "[Take Off]"
  compile_c_source
  compile_python_source
  remove_trash

  echo ""
  echo "COMPLETE Process"
}

main