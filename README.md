HAProxy Deployment
==================

This repository holds both the `spojenet.haproxy` Ansible role (`roles/haproxy/`) and a
ready-to-run playbook (`playbook.yml`) that deploys/reconfigures `haproxy.spojenet.cz`. It is
designed to be self-contained: cloning this repo and running the playbook is enough to manage
that HAProxy instance, no other repo required.

Production deployment runs automatically via Semaphore (semaphore.proxy.spojenet.cz): a push to
the `main` branch triggers a webhook that re-runs `playbook.yml` against `haproxy.spojenet.cz`.

Repository layout
------------------

```
playbook.yml          # entry-point playbook (hosts: haproxy.spojenet.cz)
vars/haproxy.yml       # haproxy_backend_servers, certbot_admin_email, nodes
inventory/hosts        # static inventory for local/manual runs
requirements.yml       # external galaxy role dependencies (geerlingguy.certbot)
roles/haproxy/         # the spojenet.haproxy role itself
```

Local usage
-----------

```bash
ansible-galaxy install -r requirements.yml
ansible-playbook -i inventory/hosts playbook.yml
# or: make haproxy
```

Requirements
------------

- Ansible 2.9 or higher.
- The target system should be a Linux-based operating system.
- Ensure the `haproxy` package is available in the system's package manager or provide a custom source.

Role Variables
--------------

The following variables can be customized to suit your needs:

- `haproxy_global_config`: A dictionary defining global HAProxy settings (e.g., `log`, `maxconn`, etc.).
- `haproxy_defaults_config`: A dictionary defining default HAProxy settings (e.g., `timeout`, `retries`, etc.).
- `haproxy_frontends`: A list of frontend configurations, including ports and ACLs.
- `haproxy_backends`: A list of backend configurations, including servers and load-balancing algorithms. Each backend server can include:
  - `name`: The name of the backend server.
  - `address`: The address of the backend server (e.g., `10.11.56.151:8080`).
  - `httpchk` (optional): The HTTP path to check for health monitoring (e.g., `/api/json`).
  - `expect` (optional): The expected HTTP status code for health checks (e.g., `200`).
  - `ssl`: Whether SSL is enabled for the backend server (`true` or `false`).
- `haproxy_service_state`: Desired state of the HAProxy service (`started`, `stopped`, etc.).

For a full list of variables, refer to `defaults/main.yml` and `vars/main.yml`.

Dependencies
------------

This role does not have any external dependencies. However, ensure that the target system meets the requirements mentioned above.

Example Playbook
----------------

Here is an example of how to use this role:

```yaml
- hosts: load_balancers
  become: yes
  roles:
    - role: spojenet.haproxy
      haproxy_global_config:
        log: "/dev/log local0"
        maxconn: 2048
      haproxy_frontends:
        - name: http_front
          bind: "*:80"
          default_backend: web_servers
      haproxy_backends:
        - name: web_servers
          servers:
            - name: jenkins.proxy.spojenet.cz
              address: 10.11.56.151:8080
              httpchk: /api/json
              expect: 200
              ssl: false
            - name: www.domain.com
              address: https://domain.com
```

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
