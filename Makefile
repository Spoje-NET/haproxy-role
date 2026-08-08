inventory = inventory/hosts

.PHONY: requirements haproxy

requirements:
	ansible-galaxy install -r requirements.yml

haproxy:
	ansible-playbook -i ${inventory} playbook.yml
