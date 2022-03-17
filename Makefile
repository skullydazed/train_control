FILES?=*.py
PICO_PORT?=/dev/pico

# What happens if you run make without any args
default: upload console

# Commands that do things to the Raspberry Pi Pico
upload:
	for file in $(FILES); do \
		ampy --port $(PICO_PORT) put $$file; \
	done

upload_mods:
	cd site-packages; ampy --port $(PICO_PORT) put src lib; cd ..

console:
	tio $(PICO_PORT)

ls:
	ampy --port $(PICO_PORT) ls -lr

reset:
	ampy --port $(PICO_PORT) reset

rm-rf:
	ampy --port $(PICO_PORT) rmdir /

# Commands for the local machine
udev_rules:
	sudo install --backup -D -o root -g root -m 0644 99-pico.rules /etc/udev/rules.d/99-pico.rules

install_deps: udev_rules
	sudo apt install micropython tio
	python3 -m pip install adafruit-ampy

upip:
	@if [ -n "$(PACKAGE)" ]; then micropython -m upip install -p site-packages $(PACKAGE); else printf "You must set PACKAGE when running this command. Example: make upip PACKAGE=microdot"; fi;
	if [ -z "$(NOUPLOAD)" ]; then make upload_packages; fi

help:
	@echo "Usage: make [command]"
	@echo
	@echo "Commands for the Raspberry Pi Pico:"
	@echo
	@echo "    make              - Runs make upload followed by make console"
	@echo "    make console      - Opens the serial console for the RPi Pico"
	@echo "    make ls           - List all files on the RPi Pico"
	@echo "    make reset        - Soft reboot the RPi Pico and run main.py"
	@echo "    make rm-rf        - Removes all files from the Raspberry Pi Pico"
	@echo "    make upload       - Upload user code from the current directory"
	@echo "    make upload_mods  - Upload 3rd party modules installed with make upip"
	@echo
	@echo "Commands for the Local Machine:"
	@echo
	@echo "    make install_deps - Install dependencies needed for development"
	@echo "    make upip         - Install a 3rd party micropython library"
	@echo "    make help         - This output"
	@echo
	@echo "Detailed help for upip:"
	@echo
	@echo "    This command will install a 3rd party package and upload it to your RPi Pico."
	@echo "    You must pass PACKAGE=<package_name> to the command. If you don't want to"
	@echo "    install it to your RPi Pico just yet you can also pass NOUPLOAD=true."
	@echo
	@echo "    make upip PACKAGE=<package_name> [NOUPLOAD=true]"
