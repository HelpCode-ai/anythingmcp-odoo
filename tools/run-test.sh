#!/bin/sh
# usage: tools/run-test.sh 17.0   (starts a throwaway Postgres + Odoo, installs and tests the module)
set -e
V=$1; T=$(mktemp -d); cp -R "$(dirname "$0")/../anythingmcp_connector" $T/; sed -i.bak "s/\"version\": \"[0-9.]*\"/\"version\": \"$V.1.0.0\"/" $T/anythingmcp_connector/__manifest__.py; rm $T/anythingmcp_connector/__manifest__.py.bak; N=amcp-odoo-test-$(echo $V | tr -d .)
docker rm -f $N-db $N >/dev/null 2>&1 || true
docker network create $N-net >/dev/null 2>&1 || true
docker run -d --name $N-db --network $N-net -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres postgres:16 >/dev/null
sleep 6
docker run --rm --name $N --network $N-net -e HOST=$N-db -e USER=odoo -e PASSWORD=odoo -v "$T":/mnt/extra-addons:ro odoo:$V \
  odoo --db_host=$N-db --db_user=odoo --db_password=odoo -d test -i anythingmcp_connector \
  --test-enable --test-tags /anythingmcp_connector --stop-after-init --without-demo=all --log-level=test 2>&1 \
  | tail -40
docker rm -f $N-db >/dev/null; docker network rm $N-net >/dev/null; rm -rf $T
